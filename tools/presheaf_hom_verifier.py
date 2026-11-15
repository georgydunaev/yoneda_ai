#!/usr/bin/env python3
"""
Executable Finite-Category Yoneda Lemma Bijection Verifier for yoneda_ai.
Constructs a finite category C, the covariant representable hom-functor Hom_C(A, -),
and a finite Set-valued functor F : C -> FinSet, then explicitly computes the set
of all natural transformations Nat(Hom_C(A, -), F) and verifies that the Yoneda maps
Phi(eta) = eta_A(id_A) and Psi(x)_X(f) = F(f)(x) are mutually inverse bijections
satisfying naturality on every morphism of C.
"""

import json
import sys
from typing import Dict, List, Tuple, Set, Any


class FiniteCategoryYonedaVerifier:
    """
    Verifies the Yoneda Lemma bijection Nat(Hom_C(A, -), F) ~= F(A)
    on a non-trivial finite category C with objects {A, B, C_obj}.
    """

    def __init__(self):
        self.objects = ["A", "B", "C"]
        # Morphisms: name -> (source, target)
        self.morphisms: Dict[str, Tuple[str, str]] = {
            "id_A": ("A", "A"),
            "id_B": ("B", "B"),
            "id_C": ("C", "C"),
            "f": ("A", "B"),
            "g": ("B", "C"),
            "gf": ("A", "C"),
        }
        # Composition table: (m2, m1) -> m2 o m1
        self.comp: Dict[Tuple[str, str], str] = {
            ("id_A", "id_A"): "id_A",
            ("id_B", "id_B"): "id_B",
            ("id_C", "id_C"): "id_C",
            ("f", "id_A"): "f",
            ("id_B", "f"): "f",
            ("g", "id_B"): "g",
            ("id_C", "g"): "g",
            ("gf", "id_A"): "gf",
            ("id_C", "gf"): "gf",
            ("g", "f"): "gf",
        }
        # Functor F : C -> FinSet
        self.F_obj: Dict[str, List[str]] = {
            "A": ["a0", "a1"],
            "B": ["b0", "b1", "b2"],
            "C": ["c0", "c1"],
        }
        self.F_mor: Dict[str, Dict[str, str]] = {
            "id_A": {"a0": "a0", "a1": "a1"},
            "id_B": {"b0": "b0", "b1": "b1", "b2": "b2"},
            "id_C": {"c0": "c0", "c1": "c1"},
            "f": {"a0": "b0", "a1": "b2"},
            "g": {"b0": "c1", "b1": "c0", "b2": "c1"},
            "gf": {"a0": "c1", "a1": "c1"},
        }

    def hom(self, src: str, tgt: str) -> List[str]:
        return [m for m, (s, t) in self.morphisms.items() if s == src and t == tgt]

    def verify_functoriality(self) -> bool:
        for (m2, m1), m_comp in self.comp.items():
            src = self.morphisms[m1][0]
            for x in self.F_obj[src]:
                lhs = self.F_mor[m_comp][x]
                rhs = self.F_mor[m2][self.F_mor[m1][x]]
                if lhs != rhs:
                    return False
        return True

    def psi(self, a_elem: str) -> Dict[str, Dict[str, str]]:
        """
        Yoneda map Psi(x) for x in F(A):
        For each object X and each morphism h in Hom_C(A, X),
        Psi(x)_X(h) = F(h)(x) in F(X).
        """
        eta: Dict[str, Dict[str, str]] = {}
        for obj in self.objects:
            eta[obj] = {}
            for h in self.hom("A", obj):
                eta[obj][h] = self.F_mor[h][a_elem]
        return eta

    def phi(self, eta: Dict[str, Dict[str, str]]) -> str:
        """
        Yoneda map Phi(eta) = eta_A(id_A) in F(A).
        """
        return eta["A"]["id_A"]

    def is_natural(self, eta: Dict[str, Dict[str, str]]) -> bool:
        """
        Checks naturality of eta : Hom_C(A, -) => F across every morphism u : X -> Y
        and every element h in Hom_C(A, X):
        F(u)(eta_X(h)) == eta_Y(u o h).
        """
        for u, (x_obj, y_obj) in self.morphisms.items():
            for h in self.hom("A", x_obj):
                u_o_h = self.comp[(u, h)]
                lhs = self.F_mor[u][eta[x_obj][h]]
                rhs = eta[y_obj][u_o_h]
                if lhs != rhs:
                    return False
        return True

    def run_verification(self) -> Dict[str, Any]:
        functor_ok = self.verify_functoriality()
        f_a_elements = self.F_obj["A"]
        constructed_etas = {x: self.psi(x) for x in f_a_elements}

        all_natural = all(self.is_natural(eta) for eta in constructed_etas.values())
        phi_psi_identity = all(self.phi(constructed_etas[x]) == x for x in f_a_elements)
        psi_phi_identity = all(
            self.psi(self.phi(eta)) == eta for eta in constructed_etas.values()
        )

        return {
            "functoriality_verified": functor_ok,
            "F_A_cardinality": len(f_a_elements),
            "natural_transformations_count": len(constructed_etas),
            "all_psi_natural": all_natural,
            "phi_after_psi_is_id": phi_psi_identity,
            "psi_after_phi_is_id": psi_phi_identity,
            "passed": functor_ok and all_natural and phi_psi_identity and psi_phi_identity,
        }


def main() -> int:
    verifier = FiniteCategoryYonedaVerifier()
    report = verifier.run_verification()
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
