"""
Automated Verification Suite for Category Diagram Commutativity Checker.
Formalizes Ticket TKT-012.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))

from category import Category, Morphism
from diagram_checker import (
    DiagramChecker,
    DiagramPath,
    create_commutative_square_example,
    create_non_commutative_square_example,
    load_category_from_dict,
)


class TestDiagramChecker(unittest.TestCase):
    def setUp(self):
        self.comm_cat = create_commutative_square_example()
        self.non_comm_cat = create_non_commutative_square_example()

    def test_commutative_square_check(self):
        checker = DiagramChecker(self.comm_cat)
        res = checker.check_pair("A", "D")
        self.assertTrue(res["commutes"])
        self.assertGreaterEqual(res["path_count"], 2)
        self.assertIsNone(res["counterexample"])

        all_res = checker.check_all()
        self.assertTrue(all_res["all_commute"])
        self.assertEqual(all_res["pairs_checked"], 1)

    def test_non_commutative_square_check(self):
        checker = DiagramChecker(self.non_comm_cat)
        res = checker.check_pair("A", "D")
        self.assertFalse(res["commutes"])
        self.assertIsNotNone(res["counterexample"])
        self.assertIn("diag1", res["unique_composites"])
        self.assertIn("diag2", res["unique_composites"])

        all_res = checker.check_all()
        self.assertFalse(all_res["all_commute"])

    def test_path_finding_and_evaluation(self):
        checker = DiagramChecker(self.comm_cat)
        paths = checker.find_paths("A", "D", max_depth=3)
        self.assertGreaterEqual(len(paths), 2)
        for p in paths:
            self.assertEqual(p.source, "A")
            self.assertEqual(p.target, "D")
            self.assertEqual(p.composite.name, "diag")

    def test_load_from_dict(self):
        data = {
            "name": "TriangleCat",
            "objects": ["X", "Y", "Z"],
            "morphisms": [
                {"name": "u", "source": "X", "target": "Y"},
                {"name": "v", "source": "Y", "target": "Z"},
                {"name": "w", "source": "X", "target": "Z"},
            ],
            "compositions": [
                {"g": "v", "f": "u", "result": "w"}
            ]
        }
        cat = load_category_from_dict(data)
        self.assertTrue(cat.validate())
        checker = DiagramChecker(cat)
        res = checker.check_pair("X", "Z")
        self.assertTrue(res["commutes"])
        self.assertEqual(res["path_count"], 2)


if __name__ == "__main__":
    unittest.main()
