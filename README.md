# yoneda_ai — Automated Category Theory & Yoneda Lemma Proof Synthesis

## Overview
`yoneda_ai` houses rigorous LaTeX mathematical foundations, Standard ML formalizations, and Python computational category theory engines for the Yoneda Lemma and universal categorical constructions:
- **Foundations & Proofs**: Complete proofs for the Yoneda Lemma, full and faithful Yoneda embedding (`yoneda_lemma_2_4.tex`), functor categories and natural transformation composition algebra (`definitions/natural_transformations.tex`), small limits in $\Set$ as compatible subsets of dependent products (`sections/yoneda_agy_small_limits.tex`), and set-theoretic $\Sigma/\Pi$ conversions (`yoneda.tex`).
- **Computational Category Theory Engine (`src/`)**:
  - `src/category.py`: Formal abstractions for Categories, Morphisms, Functors, Presheaves, Opposite Categories, and Natural Transformations with automatic verification of associativity, identity laws, and naturality squares.
  - `src/yoneda.py`: Computational Yoneda embedding functor $h_- : C \to [C^\op, \Set]$, contravariant representable presheaves $h_A$, natural transformation mappings $h_f$, and the two-sided Yoneda isomorphism $\Nat(h_A, F) \cong F(A)$ with evaluation and reconstruction maps.
  - `src/limits.py`: Explicit construction of small limits in $\Set$ as compatible subsets of dependent products $\Pi_{j \in \Ob(J)} D(j)$, projection cones, universal mediating morphisms, equalizers, and binary products.
  - `src/quantifiers.ml`: SML module for first-order syntax, capture-avoiding substitution, quantifier expansions ($\exists!$, $!$), and NBG definite description calculus ($\iota$).

## Running Verification Tests
Run the automated Python test suite:
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Run the Standard ML quantifier test suite via Poly/ML:
```bash
poly -q --use tests/test_quantifiers.ml
```
