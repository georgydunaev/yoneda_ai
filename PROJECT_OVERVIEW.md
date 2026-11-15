# Project Overview: Automated Category Theory and Yoneda Lemma Synthesis (`yoneda_ai`)

## 1. Purpose and Scope
`yoneda_ai` (`/botworkspace/yoneda_ai`) combines LaTeX mathematical manuscripts, portable Standard ML formalizations, and Python computational category theory engines verifying the Yoneda Lemma, representable presheaves, small limits in `Set`, and adjoint functors. All stored `.pdf` files are strictly immutable per Fact 11.

## 2. Architecture and Key Files
- [ARCHITECTURE_AND_THEOREMS.md](file:///botworkspace/yoneda_ai/ARCHITECTURE_AND_THEOREMS.md) and [ARCHITECTURE_AND_INDEX.md](file:///botworkspace/yoneda_ai/ARCHITECTURE_AND_INDEX.md) — Complete theorem inventory and file catalog.
- **Computational Category Theory (`src/` and `tools/`)**:
  - [src/category.py](file:///botworkspace/yoneda_ai/src/category.py) — Finite categories, functors, opposite categories, presheaves, and natural transformations with automated axiom checking.
  - [src/yoneda.py](file:///botworkspace/yoneda_ai/src/yoneda.py) — Contravariant hom-functors, the Yoneda embedding, and explicit verification of the bijection `Nat(h_A, F) ~= F(A)`.
  - [src/limits.py](file:///botworkspace/yoneda_ai/src/limits.py) — Construction of small limits in `Set` as compatible subsets of dependent products, equalizers, pullbacks, and products.
  - [src/adjunction.py](file:///botworkspace/yoneda_ai/src/adjunction.py) — Adjunctions, unit/counit triangle identities, hom-set bijections, and right-adjoint limit preservation.
  - [src/category.ml](file:///botworkspace/yoneda_ai/src/category.ml) and [src/quantifiers.ml](file:///botworkspace/yoneda_ai/src/quantifiers.ml) — Portable Standard ML implementations of category theory and first-order quantifier/iota-descriptor expansions.
  - [tools/diagram_checker.py](file:///botworkspace/yoneda_ai/tools/diagram_checker.py) — CLI and library tool for checking categorical diagram commutativity.
- **LaTeX Manuscripts**: `yoneda.tex`, `yoneda_lemma_2_4.tex`, `definitions/natural_transformations.tex`, and `sections/yoneda_agy_small_limits.tex`.

## 3. Verification
```bash
python3 -m unittest discover -s /botworkspace/yoneda_ai/tests -p "test_*.py"
```
