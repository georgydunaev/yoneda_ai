# Yoneda AI Architecture, Foundational Conventions, and Verification Index

- **Repository**: `yoneda_ai` (`/botworkspace/yoneda_ai`)
- **Primary Branch**: `main`
- **Remotes**: `gitlab`, `github`

---

## 1. Architectural Overview

The `yoneda_ai` repository contains a self-contained formalization and mechanized verification suite for the **Yoneda Lemma**, **Yoneda Embedding**, and **Representable Functors** in von Neumann-Bernays-Godel (`NBG`) class theory (and `ZFC` with Grothendieck Universes $\mathcal{U} \in \mathcal{U}^+$), built directly upon a classical first-order Hilbert predicate calculus with equality (`=`) and Russell's definite description binder (`\The`).

| Component / Directory | Primary Files | Role and Verification Scope |
| :--- | :--- | :--- |
| **LaTeX Manuscripts** | [yoneda.tex](file:///botworkspace/yoneda_ai/yoneda.tex), [yoneda_agy.tex](file:///botworkspace/yoneda_ai/yoneda_agy.tex), [yoneda_lemma_2_4.tex](file:///botworkspace/yoneda_ai/yoneda_lemma_2_4.tex), [gdmath.sty](file:///botworkspace/yoneda_ai/gdmath.sty) | Complete self-contained formalization from first-order Hilbert axioms (`tab:axiompltab`) and inference rules (`MP`, `\forall I`, `\exists E`), through NBG class-set axioms, to categories, functors, natural transformations, and the Yoneda Lemma. All compiled `.pdf` files are strictly immutable per Fact 11. |
| **Dependency Inventory** | [dependency_map.md](file:///botworkspace/yoneda_ai/dependency_map.md) | Complete dependency graph of all definitions, lemmas, and theorems across Part I (Logic and Set Foundations) and Part II (Category Theory and Yoneda Lemma). |
| **Python Category Engine & Tools** | `src/category.py`, [tools/diagram_checker.py](file:///botworkspace/yoneda_ai/tools/diagram_checker.py), [tools/presheaf_hom_verifier.py](file:///botworkspace/yoneda_ai/tools/presheaf_hom_verifier.py) | Finite category composition verifier, commutative diagram path analyzer, and explicit executable verification of the Yoneda bijection $\mathrm{Nat}(\mathrm{Hom}_{\mathcal{C}}(A, -), F) \cong F(A)$. |
| **Standard ML & Python Tests** | `tests/test_quantifiers.ml`, `tests/test_*.py` | Automated unit test suites verifying quantifier rules, substitution hygiene (`FFI`), diagram commutativity, and natural transformation bijection laws. |

---

## 2. Foundational Highlights

1. **Choice-Free Bijection Inversion (`lem:set_iso_bij`)**:
   - Inverses of bijections in $\mathrm{Set}$ are constructed without assuming the global Axiom of Choice (`AC`), using Russell's definite description binder $(\iota a \in A.\, f(a) = b)$ justified by unique existence $\exists! a \in A.\, f(a) = b$.
2. **Local Smallness and Set-Sized Hom-Classes in NBG**:
   - For any locally small category $\mathcal{C}$ in `NBG` and any functor $F : \mathcal{C} \to \mathrm{Set}$, the Yoneda maps $\Phi_{A,F}(\eta) = \eta_A(\mathrm{id}_A) \in F(A)$ and $\Psi_{A,F}(x)_X(f) = F(f)(x)$ establish an explicit set-theoretic bijection between the class of natural transformations $\mathrm{Nat}(\mathrm{Hom}_{\mathcal{C}}(A, -), F)$ and the set $F(A) \in \mathrm{Set}$, proving that $\mathrm{Nat}(\mathrm{Hom}_{\mathcal{C}}(A, -), F)$ is a set.

---

## 3. Verification Commands

```bash
python3 /botworkspace/yoneda_ai/tools/presheaf_hom_verifier.py
```
