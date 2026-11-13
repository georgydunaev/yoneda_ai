"""
Automated Verification Suite for Small Limits and Universal Properties in Set.
Formalizes Ticket 7704.
"""

import sys
import os
import unittest

# Ensure src/ is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from category import Category, Morphism, Functor, SetFunction
from limits import (
    Cone,
    construct_small_limit,
    universal_mediating_morphism,
    construct_equalizer,
    construct_product,
    construct_pullback,
    Cocone,
    construct_small_colimit,
    universal_mediating_colimit_morphism,
    construct_coequalizer,
    construct_coproduct,
    construct_pushout,
    verify_representable_preserves_limits,
)


class TestSmallLimits(unittest.TestCase):
    def setUp(self):
        # Build index category for a cospan diagram (Pullback):
        # 1 -> 3 <- 2
        self.j = Category("CospanIndex")
        self.j.add_object("1")
        self.j.add_object("2")
        self.j.add_object("3")
        self.f1 = Morphism("f1", "1", "3")
        self.f2 = Morphism("f2", "2", "3")
        self.j.add_morphism(self.f1)
        self.j.add_morphism(self.f2)
        self.assertTrue(self.j.validate())

    def test_dependent_product_construction(self):
        # Diagram: D(1) = {a, b}, D(2) = {c, d}, D(3) = {0, 1}
        # f1(a) = 0, f1(b) = 1
        # f2(c) = 0, f2(d) = 1
        d1 = ("a", "b")
        d2 = ("c", "d")
        d3 = ("0", "1")

        fn1 = SetFunction(source_set=d1, target_set=d3, mapping={"a": "0", "b": "1"}, name="f1")
        fn2 = SetFunction(source_set=d2, target_set=d3, mapping={"c": "0", "d": "1"}, name="f2")

        diag = Functor(
            name="PullbackDiagram",
            source_cat=self.j,
            target_cat=None,
            obj_map={"1": d1, "2": d2, "3": d3},
            mor_map={
                self.j.identities["1"]: SetFunction(d1, d1, {"a": "a", "b": "b"}),
                self.j.identities["2"]: SetFunction(d2, d2, {"c": "c", "d": "d"}),
                self.j.identities["3"]: SetFunction(d3, d3, {"0": "0", "1": "1"}),
                self.f1: fn1,
                self.f2: fn2
            }
        )
        self.assertTrue(diag.validate())

        # Construct small limit as subset of dependent product D(1) x D(2) x D(3)
        limit_cone = construct_small_limit(diag)
        self.assertTrue(limit_cone.validate())

        # Elements should be compatible tuples (x1, x2, x3) where f1(x1) == x3 and f2(x2) == x3
        # Compatible tuples: ('a', 'c', '0') and ('b', 'd', '1')
        expected_elements = {("a", "c", "0"), ("b", "d", "1")}
        actual_elements = set(limit_cone.apex)
        self.assertEqual(actual_elements, expected_elements)

    def test_limit_universal_property(self):
        # Construct an external cone S = {p, q} over the diagram
        d1 = ("a", "b")
        d2 = ("c", "d")
        d3 = ("0", "1")
        fn1 = SetFunction(source_set=d1, target_set=d3, mapping={"a": "0", "b": "1"}, name="f1")
        fn2 = SetFunction(source_set=d2, target_set=d3, mapping={"c": "0", "d": "1"}, name="f2")

        diag = Functor(
            name="PullbackDiagram",
            source_cat=self.j,
            target_cat=None,
            obj_map={"1": d1, "2": d2, "3": d3},
            mor_map={
                self.j.identities["1"]: SetFunction(d1, d1, {"a": "a", "b": "b"}),
                self.j.identities["2"]: SetFunction(d2, d2, {"c": "c", "d": "d"}),
                self.j.identities["3"]: SetFunction(d3, d3, {"0": "0", "1": "1"}),
                self.f1: fn1,
                self.f2: fn2
            }
        )
        limit_cone = construct_small_limit(diag)

        s_set = ("p", "q")
        # psi_1: p |-> a, q |-> b
        psi1 = SetFunction(source_set=s_set, target_set=d1, mapping={"p": "a", "q": "b"}, name="psi1")
        # psi_2: p |-> c, q |-> d
        psi2 = SetFunction(source_set=s_set, target_set=d2, mapping={"p": "c", "q": "d"}, name="psi2")
        # psi_3: p |-> 0, q |-> 1
        psi3 = SetFunction(source_set=s_set, target_set=d3, mapping={"p": "0", "q": "1"}, name="psi3")

        ext_cone = Cone(
            apex=s_set,
            diagram_functor=diag,
            legs={"1": psi1, "2": psi2, "3": psi3}
        )
        self.assertTrue(ext_cone.validate())

        # Factor through limit
        mu = universal_mediating_morphism(ext_cone, limit_cone)
        self.assertEqual(mu("p"), ("a", "c", "0"))
        self.assertEqual(mu("q"), ("b", "d", "1"))

        # Verify projections: pi_j o mu == psi_j
        for j_obj in self.j.objects:
            pi_j = limit_cone.legs[j_obj]
            psi_j = ext_cone.legs[j_obj]
            self.assertEqual(pi_j.compose(mu).mapping, psi_j.mapping)

    def test_equalizer_construction(self):
        # Equalizer of f, g: {1, 2, 3, 4} -> {True, False}
        # f: is_even? 1->F, 2->T, 3->F, 4->T
        # g: is_gt2?  1->F, 2->F, 3->T, 4->T
        # Equalizer set where f(x) == g(x): {1, 4}
        src = (1, 2, 3, 4)
        tgt = (True, False)
        f = SetFunction(src, tgt, {1: False, 2: True, 3: False, 4: True}, name="is_even")
        g = SetFunction(src, tgt, {1: False, 2: False, 3: True, 4: True}, name="is_gt2")

        eq_cone = construct_equalizer(f, g)
        eq_elements = {elem[0] for elem in eq_cone.apex}
        self.assertEqual(eq_elements, {1, 4})

    def test_product_construction(self):
        # Product of {0, 1} and {'x', 'y'}
        set_a = (0, 1)
        set_b = ("x", "y")
        prod_cone = construct_product(set_a, set_b)
        self.assertEqual(len(prod_cone.apex), 4)
        self.assertEqual(set(prod_cone.apex), {(0, "x"), (0, "y"), (1, "x"), (1, "y")})

    def test_pullback_construction(self):
        # Cospan: X = {1, 2, 3} -> Z = {True, False} <- Y = {'a', 'b'}
        # f: 1->T, 2->F, 3->T
        # g: 'a'->T, 'b'->F
        # Pullback consists of pairs (x, y) with f(x) == g(y):
        # (1, 'a'), (2, 'b'), (3, 'a')
        src_x = (1, 2, 3)
        src_y = ("a", "b")
        tgt_z = (True, False)
        f = SetFunction(src_x, tgt_z, {1: True, 2: False, 3: True}, name="f")
        g = SetFunction(src_y, tgt_z, {"a": True, "b": False}, name="g")

        pb_cone = construct_pullback(f, g)
        self.assertTrue(pb_cone.validate())
        pb_pairs = {(elem[0], elem[1]) for elem in pb_cone.apex}
        expected = {(1, "a"), (2, "b"), (3, "a")}
        self.assertEqual(pb_pairs, expected)

    def test_coproduct_construction(self):
        # Coproduct of A = {1, 2} and B = {'x', 'y'}
        set_a = (1, 2)
        set_b = ("x", "y")
        coprod_cocone = construct_coproduct(set_a, set_b)
        self.assertTrue(coprod_cocone.validate())
        self.assertEqual(len(coprod_cocone.apex), 4)

    def test_coequalizer_construction(self):
        # Parallel arrows f, g: {1, 2, 3} -> {'a', 'b', 'c'}
        # f: 1->'a', 2->'b', 3->'b'
        # g: 1->'b', 2->'b', 3->'c'
        # Identifies 'a' ~ 'b' and 'b' ~ 'c', so all {'a', 'b', 'c'} collapse to one class
        src = (1, 2, 3)
        tgt = ("a", "b", "c")
        f = SetFunction(src, tgt, {1: "a", 2: "b", 3: "b"}, name="f")
        g = SetFunction(src, tgt, {1: "b", 2: "b", 3: "c"}, name="g")

        coeq_cocone = construct_coequalizer(f, g)
        self.assertTrue(coeq_cocone.validate())
        self.assertEqual(len(coeq_cocone.apex), 1)

    def test_pushout_construction(self):
        # Span: X = {'x1', 'x2'} <- Z = {0} -> Y = {'y1', 'y2'}
        # f: 0 |-> 'x1'
        # g: 0 |-> 'y1'
        # Pushout glues 'x1' and 'y1'. Resulting classes:
        # {'x1', 'y1'}, {'x2'}, {'y2'} => 3 equivalence classes
        src_z = (0,)
        tgt_x = ("x1", "x2")
        tgt_y = ("y1", "y2")
        f = SetFunction(src_z, tgt_x, {0: "x1"}, name="f")
        g = SetFunction(src_z, tgt_y, {0: "y1"}, name="g")

        po_cocone = construct_pushout(f, g)
        self.assertTrue(po_cocone.validate())
        self.assertEqual(len(po_cocone.apex), 3)

    def test_colimit_universal_property(self):
        # Test universal mediating arrow nu: colim D -> S
        set_a = (1, 2)
        set_b = ("x", "y")
        coprod = construct_coproduct(set_a, set_b)

        # Test target set S = {'num', 'letter'}
        s_set = ("num", "letter")
        phi_a = SetFunction(set_a, s_set, {1: "num", 2: "num"}, name="phi_a")
        phi_b = SetFunction(set_b, s_set, {"x": "letter", "y": "letter"}, name="phi_b")

        test_cocone = Cocone(
            apex=s_set,
            diagram_functor=coprod.diagram,
            legs={"A": phi_a, "B": phi_b}
        )
        self.assertTrue(test_cocone.validate())

        nu = universal_mediating_colimit_morphism(test_cocone, coprod)
        for a in set_a:
            cls = coprod.legs["A"](a)
            self.assertEqual(nu(cls), "num")
        for b in set_b:
            cls = coprod.legs["B"](b)
            self.assertEqual(nu(cls), "letter")

    def test_representable_preserves_limits(self):
        # In a category C with terminal object / product / pullback:
        # Let C have objects P, A, B, X
        # P is product of A and B with projections pi_a: P -> A, pi_b: P -> B
        cat = Category("CatWithProduct")
        for obj in ["P", "A", "B", "X"]:
            cat.add_object(obj)

        pi_a = Morphism("pi_a", "P", "A")
        pi_b = Morphism("pi_b", "P", "B")
        cat.add_morphism(pi_a)
        cat.add_morphism(pi_b)

        # Add arrows from X: f: X -> A, g: X -> B, and pair <f, g>: X -> P
        f = Morphism("f", "X", "A")
        g = Morphism("g", "X", "B")
        fg = Morphism("pair_fg", "X", "P")
        cat.add_morphism(f)
        cat.add_morphism(g)
        cat.add_morphism(fg)

        cat.set_composition(pi_a, fg, f)
        cat.set_composition(pi_b, fg, g)
        cat.validate()

        # Product diagram of A and B
        j = Category("Discrete2")
        j.add_object("A")
        j.add_object("B")

        diag = Functor(
            name="ProdDiag",
            source_cat=j,
            target_cat=cat,
            obj_map={"A": "A", "B": "B"},
            mor_map={
                j.identities["A"]: cat.identities["A"],
                j.identities["B"]: cat.identities["B"],
            }
        )
        diag.validate()

        lim_apex = "P"
        lim_legs = {"A": pi_a, "B": pi_b}

        # Verify that Hom_C(X, -) preserves this limit
        self.assertTrue(verify_representable_preserves_limits(cat, "X", diag, lim_apex, lim_legs))



if __name__ == '__main__':
    unittest.main()
