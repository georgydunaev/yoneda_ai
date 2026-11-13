"""
Automated Verification Suite for Adjunctions and Freyd's Adjoint Functor Theorem.
Formalizes Ticket TKT-010.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from category import (
    Category,
    Morphism,
    Functor,
    NaturalTransformation,
    identity_functor,
    compose_functors,
)
from adjunction import (
    Adjunction,
    make_adjunction_from_unit_counit,
    verify_solution_set_condition,
    verify_freyd_adjoint_functor_theorem,
)


class TestAdjunction(unittest.TestCase):
    def setUp(self):
        """
        Construct a concrete finite adjunction between category C and category D.
        Let C have objects {C0, C1} and arrow f: C0 -> C1.
        Let D have objects {D0, D1} and arrow g: D0 -> D1.

        Consider the equivalence/adjunction where:
        F: C -> D maps C0 to D0, C1 to D1, f to g.
        G: D -> C maps D0 to C0, D1 to C1, g to f.
        Unit eta_X = id_X.
        Counit epsilon_Y = id_Y.
        """
        self.C = Category("CatC")
        self.C.add_object("C0")
        self.C.add_object("C1")
        self.f = Morphism("f", "C0", "C1")
        self.C.add_morphism(self.f)
        self.assertTrue(self.C.validate())

        self.D = Category("CatD")
        self.D.add_object("D0")
        self.D.add_object("D1")
        self.g = Morphism("g", "D0", "D1")
        self.D.add_morphism(self.g)
        self.assertTrue(self.D.validate())

        # Functor F: C -> D
        self.F = Functor(
            name="F",
            source_cat=self.C,
            target_cat=self.D,
            obj_map={"C0": "D0", "C1": "D1"},
            mor_map={
                self.C.identities["C0"]: self.D.identities["D0"],
                self.C.identities["C1"]: self.D.identities["D1"],
                self.f: self.g,
            },
        )
        self.assertTrue(self.F.validate())

        # Functor G: D -> C
        self.G = Functor(
            name="G",
            source_cat=self.D,
            target_cat=self.C,
            obj_map={"D0": "C0", "D1": "C1"},
            mor_map={
                self.D.identities["D0"]: self.C.identities["C0"],
                self.D.identities["D1"]: self.C.identities["C1"],
                self.g: self.f,
            },
        )
        self.assertTrue(self.G.validate())

        # G o F: C -> C
        self.GoF = compose_functors(self.G, self.F)
        self.id_C = identity_functor(self.C)

        # F o G: D -> D
        self.FoG = compose_functors(self.F, self.G)
        self.id_D = identity_functor(self.D)

        # Unit eta: Id_C => G o F
        self.eta = NaturalTransformation(
            name="eta",
            source_functor=self.id_C,
            target_functor=self.GoF,
            components={
                "C0": self.C.identities["C0"],
                "C1": self.C.identities["C1"],
            },
        )
        self.assertTrue(self.eta.validate())

        # Counit epsilon: F o G => Id_D
        self.epsilon = NaturalTransformation(
            name="epsilon",
            source_functor=self.FoG,
            target_functor=self.id_D,
            components={
                "D0": self.D.identities["D0"],
                "D1": self.D.identities["D1"],
            },
        )
        self.assertTrue(self.epsilon.validate())

        self.adj = make_adjunction_from_unit_counit(
            name="Adj_F_G",
            F=self.F,
            G=self.G,
            unit=self.eta,
            counit=self.epsilon,
        )

    def test_triangle_identities(self):
        # Verification that triangle identities are enforced by validate()
        self.assertTrue(self.adj.validate())

    def test_hom_set_isomorphism(self):
        # Hom_D(F(X), Y) ~= Hom_C(X, G(Y))
        for x in self.C.objects:
            for y in self.D.objects:
                self.assertTrue(self.adj.verify_hom_isomorphism(x, y))

    def test_naturality_of_hom_isomorphism(self):
        # Naturality with respect to h: C0 -> C0 and k: D0 -> D1
        h = self.C.identities["C0"]
        k = self.g
        self.assertTrue(self.adj.verify_naturality("C0", "D0", "C0", "D1", h, k))

    def test_limit_preservation_by_right_adjoint(self):
        # Test diagram in D: discrete 2-object diagram {D0, D1}
        # In D, let D0 x D1 have product apex (say D0 if there is a projection)
        # Let's create a diagram in D consisting of a single morphism g: D0 -> D1
        j = Category("J")
        j.add_object("0")
        j.add_object("1")
        u = Morphism("u", "0", "1")
        j.add_morphism(u)

        diag = Functor(
            name="DiagramInD",
            source_cat=j,
            target_cat=self.D,
            obj_map={"0": "D0", "1": "D1"},
            mor_map={
                j.identities["0"]: self.D.identities["D0"],
                j.identities["1"]: self.D.identities["D1"],
                u: self.g,
            },
        )
        self.assertTrue(diag.validate())

        # Limit cone in D: apex is D0, legs: pi_0 = id_D0, pi_1 = g
        lim_apex = "D0"
        lim_legs = {"0": self.D.identities["D0"], "1": self.g}

        self.assertTrue(self.adj.verify_limit_preservation(diag, lim_apex, lim_legs))

    def test_freyd_solution_set_and_adjoint_functor_theorem(self):
        # Solution set for G: D -> C
        # For C0: S_{C0} = {D0} with f_i = id_{C0}: C0 -> G(D0) = C0
        # For C1: S_{C1} = {D1} with f_i = id_{C1}: C1 -> G(D1) = C1
        solution_sets = {
            "C0": ({"D0"}, {"D0": self.C.identities["C0"]}),
            "C1": ({"D1"}, {"D1": self.C.identities["C1"]}),
        }

        self.assertTrue(verify_solution_set_condition(self.G, solution_sets))

        # Check FAFT
        j = Category("J")
        j.add_object("0")
        j.add_object("1")
        u = Morphism("u", "0", "1")
        j.add_morphism(u)

        diag = Functor(
            name="DiagramInD",
            source_cat=j,
            target_cat=self.D,
            obj_map={"0": "D0", "1": "D1"},
            mor_map={
                j.identities["0"]: self.D.identities["D0"],
                j.identities["1"]: self.D.identities["D1"],
                u: self.g,
            },
        )

        limits_dict = {
            "SingleArrowLimit": (diag, "D0", {"0": self.D.identities["D0"], "1": self.g})
        }

        self.assertTrue(
            verify_freyd_adjoint_functor_theorem(self.G, limits_dict, solution_sets)
        )


if __name__ == "__main__":
    unittest.main()
