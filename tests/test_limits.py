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
from limits import Cone, construct_small_limit, universal_mediating_morphism, construct_equalizer, construct_product


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


if __name__ == '__main__':
    unittest.main()
