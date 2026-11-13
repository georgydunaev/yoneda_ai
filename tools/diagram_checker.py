"""
Interactive Category Diagram Commutativity Checker for yoneda_ai.
Formalizes Ticket TKT-012.

Validates whether directed paths in a categorical diagram commute under
the category composition laws. Provides both programmatic and CLI interfaces.
"""

import sys
import os
import argparse
import json
from typing import Dict, List, Set, Tuple, Any, Optional

# Add src to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from category import Category, Morphism


class DiagramPath:
    """Represents a directed path of composable morphisms in a category."""

    def __init__(self, steps: List[Morphism], composite: Morphism):
        self.steps = tuple(steps)
        self.composite = composite
        self.source = steps[0].source if steps else composite.source
        self.target = steps[-1].target if steps else composite.target

    def __repr__(self) -> str:
        names = " ; ".join(m.name for m in self.steps)
        return f"Path({self.source} to {self.target} via [{names}], composite={self.composite.name})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "steps": [m.name for m in self.steps],
            "composite": self.composite.name
        }


class DiagramChecker:
    """
    Analyzes commutativity of diagrams in a finite Category.
    Finds all paths between vertices and validates if all parallel paths yield
    identical composite morphisms.
    """

    def __init__(self, cat: Category):
        self.cat = cat

    def evaluate_path(self, steps: List[Morphism]) -> Morphism:
        """
        Evaluates the composition of a path of morphisms.
        For steps [f_1, f_2, ..., f_n], composition is f_n o ... o f_1.
        """
        if not steps:
            raise ValueError("Empty path cannot be evaluated")
        res = steps[0]
        for next_mor in steps[1:]:
            res = self.cat.compose(next_mor, res)
        return res

    def find_paths(
        self,
        source: str,
        target: str,
        max_depth: int = 5,
        exclude_identities: bool = True
    ) -> List[DiagramPath]:
        """
        Finds all directed paths from source to target up to max_depth.
        """
        if source not in self.cat.objects:
            raise ValueError(f"Source object {source} not in category {self.cat.name}")
        if target not in self.cat.objects:
            raise ValueError(f"Target object {target} not in category {self.cat.name}")

        paths: List[DiagramPath] = []

        def dfs(current: str, current_steps: List[Morphism], visited_edges: Set[Morphism], depth: int):
            if current == target and current_steps:
                composite = self.evaluate_path(current_steps)
                paths.append(DiagramPath(current_steps, composite))

            if depth >= max_depth:
                return

            for (s, t), mors in self.cat.morphisms.items():
                if s != current:
                    continue
                for m in mors:
                    if exclude_identities and m == self.cat.identities[s]:
                        continue
                    if m in visited_edges:
                        continue
                    dfs(t, current_steps + [m], visited_edges | {m}, depth + 1)

        dfs(source, [], set(), 0)
        return paths

    def check_pair(
        self,
        source: str,
        target: str,
        max_depth: int = 5,
        exclude_identities: bool = True
    ) -> Dict[str, Any]:
        """
        Checks commutativity for all paths between a specific source and target.
        """
        paths = self.find_paths(source, target, max_depth, exclude_identities)
        if len(paths) < 2:
            return {
                "source": source,
                "target": target,
                "commutes": True,
                "path_count": len(paths),
                "paths": [p.to_dict() for p in paths],
                "message": f"Fewer than 2 paths found between {source} and {target}"
            }

        first_composite = paths[0].composite
        all_equal = True
        counterexample = None

        for p in paths[1:]:
            if p.composite != first_composite:
                all_equal = False
                counterexample = {
                    "path_1": paths[0].to_dict(),
                    "path_2": p.to_dict(),
                    "composite_1": first_composite.name,
                    "composite_2": p.composite.name
                }
                break

        return {
            "source": source,
            "target": target,
            "commutes": all_equal,
            "path_count": len(paths),
            "paths": [p.to_dict() for p in paths],
            "unique_composites": list({p.composite.name for p in paths}),
            "counterexample": counterexample
        }

    def check_all(
        self,
        max_depth: int = 5,
        exclude_identities: bool = True
    ) -> Dict[str, Any]:
        """
        Checks commutativity across all pairs of objects in the category.
        """
        results = {}
        all_commute = True
        pairs_with_multiple_paths = 0

        for src in self.cat.objects:
            for tgt in self.cat.objects:
                pair_key = f"{src}_to_{tgt}"
                res = self.check_pair(src, tgt, max_depth, exclude_identities)
                if res["path_count"] >= 2:
                    pairs_with_multiple_paths += 1
                    results[pair_key] = res
                    if not res["commutes"]:
                        all_commute = False

        return {
            "category": self.cat.name,
            "all_commute": all_commute,
            "pairs_checked": pairs_with_multiple_paths,
            "details": results
        }


def load_category_from_dict(data: Dict[str, Any]) -> Category:
    """
    Builds a Category from a dictionary specification:
    {
        "name": "SquareCat",
        "objects": ["A", "B", "C", "D"],
        "morphisms": [
            {"name": "f", "source": "A", "target": "B"},
            ...
        ],
        "compositions": [
            {"g": "h", "f": "f", "result": "k"}
        ]
    }
    """
    cat = Category(data.get("name", "DiagramCategory"))
    for obj in data.get("objects", []):
        cat.add_object(obj)

    mor_dict = {}
    for m_data in data.get("morphisms", []):
        m = Morphism(name=m_data["name"], source=m_data["source"], target=m_data["target"])
        cat.add_morphism(m)
        mor_dict[m.name] = m

    for c_data in data.get("compositions", []):
        g = mor_dict[c_data["g"]]
        f = mor_dict[c_data["f"]]
        res = mor_dict[c_data["result"]]
        cat.set_composition(g, f, res)

    return cat


def create_commutative_square_example() -> Category:
    """
    Creates a standard commuting square:
    Top: f: A to B
    Bottom: g: C to D
    Left: h: A to C
    Right: k: B to D
    Diagonal composite: k o f = g o h = diag
    """
    cat = Category("CommutativeSquare")
    for obj in ["A", "B", "C", "D"]:
        cat.add_object(obj)

    f = Morphism("f", "A", "B")
    h = Morphism("h", "A", "C")
    k = Morphism("k", "B", "D")
    g = Morphism("g", "C", "D")
    diag = Morphism("diag", "A", "D")

    cat.add_morphism(f)
    cat.add_morphism(h)
    cat.add_morphism(k)
    cat.add_morphism(g)
    cat.add_morphism(diag)

    cat.set_composition(k, f, diag)
    cat.set_composition(g, h, diag)
    cat.validate()
    return cat


def create_non_commutative_square_example() -> Category:
    """
    Creates a non-commuting square where top-right path != bottom-left path:
    k o f = diag1
    g o h = diag2 (diag1 != diag2)
    """
    cat = Category("NonCommutativeSquare")
    for obj in ["A", "B", "C", "D"]:
        cat.add_object(obj)

    f = Morphism("f", "A", "B")
    h = Morphism("h", "A", "C")
    k = Morphism("k", "B", "D")
    g = Morphism("g", "C", "D")
    diag1 = Morphism("diag1", "A", "D")
    diag2 = Morphism("diag2", "A", "D")

    cat.add_morphism(f)
    cat.add_morphism(h)
    cat.add_morphism(k)
    cat.add_morphism(g)
    cat.add_morphism(diag1)
    cat.add_morphism(diag2)

    cat.set_composition(k, f, diag1)
    cat.set_composition(g, h, diag2)
    cat.validate()
    return cat


def main():
    parser = argparse.ArgumentParser(description="Categorical Diagram Commutativity Checker")
    parser.add_argument("--category", type=str, default="square_commutes",
                        help="Built-in example ('square_commutes', 'square_fails') or path to JSON category file")
    parser.add_argument("--source", type=str, default=None, help="Source object to check")
    parser.add_argument("--target", type=str, default=None, help="Target object to check")
    parser.add_argument("--max-depth", type=int, default=5, help="Maximum path search depth")
    parser.add_argument("--check-all", action="store_true", help="Check all object pairs in category")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    if args.category == "square_commutes":
        cat = create_commutative_square_example()
    elif args.category == "square_fails":
        cat = create_non_commutative_square_example()
    elif os.path.exists(args.category):
        with open(args.category, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        cat = load_category_from_dict(data)
    else:
        print(f"Error: Unknown category specification '{args.category}'", file=sys.stderr)
        sys.exit(1)

    checker = DiagramChecker(cat)

    if args.check_all or (args.source is None and args.target is None):
        res = checker.check_all(max_depth=args.max_depth)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            status = "COMMUTATIVE" if res["all_commute"] else "NON-COMMUTATIVE"
            print(f"Category: {res['category']} Status: {status}")
            print(f"Parallel path pairs checked: {res['pairs_checked']}")
            for pair, details in res["details"].items():
                p_status = "Commutes" if details["commutes"] else "FAILS"
                print(f"  {pair}: {p_status} ({details['path_count']} paths)")
                if not details["commutes"]:
                    ce = details["counterexample"]
                    print(f"    Discrepancy: {ce['path_1']['steps']} yields {ce['composite_1']} vs {ce['path_2']['steps']} yields {ce['composite_2']}")
    else:
        if args.source is None or args.target is None:
            print("Error: Both --source and --target are required when not using --check-all", file=sys.stderr)
            sys.exit(1)
        res = checker.check_pair(args.source, args.target, max_depth=args.max_depth)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            status = "Commutes" if res["commutes"] else "FAILS"
            print(f"Path pair {args.source} to {args.target}: {status}")
            print(f"Total paths: {res['path_count']}")
            if not res["commutes"]:
                ce = res["counterexample"]
                print(f"Counterexample found:")
                print(f"  Path 1: {ce['path_1']['steps']} evaluates to {ce['composite_1']}")
                print(f"  Path 2: {ce['path_2']['steps']} evaluates to {ce['composite_2']}")


if __name__ == "__main__":
    main()
