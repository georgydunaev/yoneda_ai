"""
Automated Verification Suite for the Yoneda Lemma, Presheaves, and Full Faithfulness.
Formalizes Tickets 7698 and 7701.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from category import Category, Morphism, Functor, SetFunction, NaturalTransformation
from yoneda import (
    make_representable_presheaf,
    make_covariant_representable,
    make_yoneda_morphism,
    yoneda_evaluation,
    yoneda_reconstruction,
    verify_yoneda_isomorphism,
    verify_yoneda_full_faithful,
    YonedaEmbedding,
    verify_yoneda_embedding,
)


class TestYoneda(unittest.TestCase):
    def setUp(self):
        # Construct small category C:
        # Objects: A, B, C_obj
        # Morphisms: id_A, id_B, id_C, f: A -> B, g: B -> C_obj, gf: A -> C_obj
        self.c = Category("ThreeCategory")
        self.c.add_object("A")
        self.c.add_object("B")
        self.c.add_object("C_obj")

        self.f = Morphism("f", "A", "B")
        self.g = Morphism("g", "B", "C_obj")
        self.gf = Morphism("gf", "A", "C_obj")

        self.c.add_morphism(self.f)
        self.c.add_morphism(self.g)
        self.c.set_composition(self.g, self.f, self.gf)
        self.assertTrue(self.c.validate())

    def test_opposite_category(self):
        op = self.c.opposite()
        self.assertTrue(op.validate())
        self.assertEqual(op.objects, self.c.objects)
        # Check arrow reversal
        self.assertEqual(len(op.hom("B", "A")), 1)
        self.assertEqual(len(op.hom("C_obj", "B")), 1)
        self.assertEqual(len(op.hom("C_obj", "A")), 1)

    def test_representable_presheaves(self):
        # h_A, h_B, h_C
        h_a = make_representable_presheaf(self.c, "A")
        h_b = make_representable_presheaf(self.c, "B")
        h_c = make_representable_presheaf(self.c, "C_obj")

        self.assertTrue(h_a.validate())
        self.assertTrue(h_b.validate())
        self.assertTrue(h_c.validate())

        # Check hom-set sizes
        # Hom(A, B) has {f}, Hom(B, B) has {id_B}, Hom(C_obj, B) has empty
        self.assertEqual(set(h_b.apply_obj("A")), {self.f})
        self.assertEqual(set(h_b.apply_obj("B")), {self.c.identities["B"]})
        self.assertEqual(set(h_b.apply_obj("C_obj")), set())

        # Hom(A, C_obj) has {gf}, Hom(B, C_obj) has {g}, Hom(C_obj, C_obj) has {id_C}
        self.assertEqual(set(h_c.apply_obj("A")), {self.gf})
        self.assertEqual(set(h_c.apply_obj("B")), {self.g})
        self.assertEqual(set(h_c.apply_obj("C_obj")), {self.c.identities["C_obj"]})

    def test_yoneda_lemma_isomorphism_on_representable(self):
        # Yoneda lemma states Nat(h_A, h_B) \cong h_B(A) = Hom(A, B)
        h_b = make_representable_presheaf(self.c, "B")
        self.assertTrue(verify_yoneda_isomorphism(h_b, "A", self.c))
        self.assertTrue(verify_yoneda_isomorphism(h_b, "B", self.c))

        h_c = make_representable_presheaf(self.c, "C_obj")
        self.assertTrue(verify_yoneda_isomorphism(h_c, "A", self.c))
        self.assertTrue(verify_yoneda_isomorphism(h_c, "B", self.c))
        self.assertTrue(verify_yoneda_isomorphism(h_c, "C_obj", self.c))

    def test_yoneda_embedding_full_and_faithful(self):
        # Test full faithfulness between all pairs of objects
        for a in self.c.objects:
            for b in self.c.objects:
                self.assertTrue(verify_yoneda_full_faithful(self.c, a, b))

    def test_yoneda_functoriality_on_morphisms(self):
        # For f: A -> B and g: B -> C_obj, check h_{g o f} == h_g o h_f
        hf = make_yoneda_morphism(self.c, self.f)
        hg = make_yoneda_morphism(self.c, self.g)
        hgf = make_yoneda_morphism(self.c, self.gf)

        composite_nat = hg.vertical_compose(hf)
        self.assertTrue(composite_nat.validate())

        # Compare components at all objects
        for x in self.c.objects:
            c1 = composite_nat.component(x).mapping
            c2 = hgf.component(x).mapping
            self.assertEqual(c1, c2)

    def test_covariant_representable_functor(self):
        # h^A = Hom(A, -): C -> Set
        h_sup_a = make_covariant_representable(self.c, "A")
        self.assertTrue(h_sup_a.validate())

        # h^A(A) = {id_A}, h^A(B) = {f}, h^A(C_obj) = {gf}
        self.assertEqual(set(h_sup_a.apply_obj("A")), {self.c.identities["A"]})
        self.assertEqual(set(h_sup_a.apply_obj("B")), {self.f})
        self.assertEqual(set(h_sup_a.apply_obj("C_obj")), {self.gf})

        # Morphism mapping: for g: B -> C_obj, h^A(g) maps f to g o f = gf
        map_g = h_sup_a.apply_mor(self.g)
        self.assertEqual(map_g(self.f), self.gf)

    def test_yoneda_embedding_mechanization(self):
        # Mechanize y: C -> PSh(C)
        embedding = YonedaEmbedding(self.c)
        self.assertTrue(embedding.verify_functoriality())
        self.assertTrue(embedding.verify_full_and_faithful())
        self.assertTrue(verify_yoneda_embedding(self.c))



if __name__ == '__main__':
    unittest.main()
