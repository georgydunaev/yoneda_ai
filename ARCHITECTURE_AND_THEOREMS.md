# Architecture and Theorems Guide (`yoneda_ai`)

This document summarizes the architecture, LaTeX mathematical manuscripts, Standard ML formalizations, Python computational category theory engines, verified theorems, and open tasks in `yoneda_ai`.

---

## 1. Repository Architecture

| Path | Language / Format | Role |
|---|---|---|
| `src/category.py` | Python 3 | Core abstractions for `Category`, `Morphism`, `Functor`, `SetFunction`, `NaturalTransformation`, opposite categories $\mathcal{C}^{\mathrm{op}}$, functor composition, vertical/horizontal natural transformation composition, and natural isomorphism checks |
| `src/yoneda.py` | Python 3 | Contravariant representable presheaves $h_A = \mathrm{Hom}_{\mathcal{C}}(-, A)$, induced natural transformations $h_f : h_A \Rightarrow h_B$, Yoneda evaluation $\Phi(\alpha) = \alpha_A(\mathrm{id}_A)$, Yoneda reconstruction $\Psi(x)_X(g) = F(g)(x)$, and full/faithful embedding verification |
| `src/limits.py` | Python 3 | Explicit construction of small limits in $\mathbf{Set}$ as compatible subsets of dependent Cartesian products $\prod_{j \in \mathrm{Ob}(J)} D(j)$, projection cones, universal mediating morphisms, binary products, equalizers, pullbacks, and terminal objects |
| `src/adjunction.py` | Python 3 | Formal adjunctions $F \dashv G$ between finite categories, unit $\eta : \mathrm{Id}_{\mathcal{C}} \Rightarrow G \circ F$, counit $\varepsilon : F \circ G \Rightarrow \mathrm{Id}_{\mathcal{D}}$, triangle identities, hom-set adjunction bijection $\Phi_{X,Y} : \mathrm{Hom}_{\mathcal{D}}(F(X), Y) \cong \mathrm{Hom}_{\mathcal{C}}(X, G(Y))$, right-adjoint limit preservation, and Freyd Adjoint Functor Theorem solution-set checks |
| `src/category.ml` | Standard ML (CakeML & Poly/ML) | SML'97 category theory and Yoneda Lemma engine (`structure CategoryTheory`) implementing finite categories, opposite categories, representable presheaves, Yoneda evaluation/reconstruction, and full/faithful bijection checks |
| `src/quantifiers.ml` | Standard ML (CakeML & Poly/ML) | SML'97 first-order syntax, fresh variable generation, capture-avoiding substitution, uniqueness quantifiers ($\exists! x.\,\varphi(x)$, $!x.\,\varphi(x)$), and Hilbert-Bernays / NBG definite description ($\iota x.\,\varphi(x)$) |
| `tools/diagram_checker.py` | Python 3 CLI & API | Interactive categorical diagram commutativity checker (`DiagramChecker`, `DiagramPath`) performing depth-bounded path enumeration and parallel composite equality verification |
| `yoneda.tex`, `yoneda_agy.tex`, `yoneda_lemma_2_4.tex` | LaTeX | Complete mathematical manuscripts proving the Yoneda Lemma, full and faithful Yoneda embedding, functor category laws, small limits in $\mathbf{Set}$, and set-theoretic $\Sigma/\Pi$ conversions |
| `definitions/natural_transformations.tex` | LaTeX | Formal definitions and proofs of vertical composition, horizontal composition, the interchange law, and functor categories $[\mathcal{C}, \mathcal{D}]$ |
| `sections/yoneda_agy_small_limits.tex` | LaTeX | Proof that $\mathbf{Set}$ is complete by constructing small limits as compatible subobjects of dependent products |
| `tests/test_*.py`, `tests/test_*.ml` | Python & SML | Automated test suites verifying categories, the Yoneda lemma, small limits, adjunctions, diagram commutativity, SML category theory, and SML quantifiers |

---

## 2. Formal Definitions, Axioms, and Verified Theorems

### 2.1 Categories, Functors, and Natural Transformations (`src/category.py`, `src/category.ml`, `definitions/natural_transformations.tex`)
- **Category Axioms**:
  1. **Domain/Codomain Closure**: For $f \in \mathrm{Hom}_{\mathcal{C}}(A, B)$ and $g \in \mathrm{Hom}_{\mathcal{C}}(B, C)$, $g \circ f \in \mathrm{Hom}_{\mathcal{C}}(A, C)$.
  2. **Identity Law**: For every $f : A \to B$, $f \circ \mathrm{id}_A = f = \mathrm{id}_B \circ f$.
  3. **Associativity**: For composable $f, g, h$, $(h \circ g) \circ f = h \circ (g \circ f)$.
- **Opposite Category ($\mathcal{C}^{\mathrm{op}}$)**:
  - $\mathrm{Ob}(\mathcal{C}^{\mathrm{op}}) = \mathrm{Ob}(\mathcal{C})$, $\mathrm{Hom}_{\mathcal{C}^{\mathrm{op}}}(A, B) = \mathrm{Hom}_{\mathcal{C}}(B, A)$, and $g^{\mathrm{op}} \circ_{\mathcal{C}^{\mathrm{op}}} f^{\mathrm{op}} = (f \circ_{\mathcal{C}} g)^{\mathrm{op}}$.
- **Functor Laws ($F : \mathcal{C} \to \mathcal{D}$)**:
  - $F(\mathrm{id}_A) = \mathrm{id}_{F(A)}$ and $F(g \circ f) = F(g) \circ F(f)$.
- **Naturality Square ($\alpha : F \Rightarrow G$)**:
  - For every $f : X \to Y$ in $\mathcal{C}$, $G(f) \circ \alpha_X = \alpha_Y \circ F(f)$.
- **Interchange Law**:
  - For horizontal ($\ast$) and vertical ($\circ$) composition of natural transformations:
    $$(\beta' \circ \alpha') \ast (\beta \circ \alpha) = (\beta' \ast \beta) \circ (\alpha' \ast \alpha)$$

### 2.2 The Yoneda Lemma and Yoneda Embedding (`src/yoneda.py`, `src/category.ml`, `yoneda_lemma_2_4.tex`)
- **Theorem (Contravariant Yoneda Lemma)**:
  - Let $\mathcal{C}$ be a locally small category, $A \in \mathrm{Ob}(\mathcal{C})$, and $F : \mathcal{C}^{\mathrm{op}} \to \mathbf{Set}$ a presheaf. There is a canonical bijection
    $$\Phi_{A,F} : \mathrm{Nat}(h_A, F) \xrightarrow{\sim} F(A), \qquad \Phi_{A,F}(\alpha) = \alpha_A(\mathrm{id}_A)$$
    with inverse $\Psi_{A,F} : F(A) \xrightarrow{\sim} \mathrm{Nat}(h_A, F)$ defined at object $X \in \mathrm{Ob}(\mathcal{C})$ and morphism $g \in \mathrm{Hom}_{\mathcal{C}}(X, A)$ by
    $$\Psi_{A,F}(x)_X(g) = F(g^{\mathrm{op}})(x)$$
  - Furthermore, this bijection is natural in both $A \in \mathcal{C}$ and $F \in [\mathcal{C}^{\mathrm{op}}, \mathbf{Set}]$.
- **Corollary (Full and Faithful Yoneda Embedding)**:
  - Specializing $F = h_B$ yields the canonical bijection $\mathrm{Nat}(h_A, h_B) \cong h_B(A) = \mathrm{Hom}_{\mathcal{C}}(A, B)$ mapping $f : A \to B$ to post-composition $(h_f)_X(g) = f \circ g$, proving that the Yoneda functor $y : \mathcal{C} \to [\mathcal{C}^{\mathrm{op}}, \mathbf{Set}]$ is fully faithful.

### 2.3 Small Limits in $\mathbf{Set}$ (`src/limits.py`, `sections/yoneda_agy_small_limits.tex`)
- **Theorem (Completeness of $\mathbf{Set}$)**:
  - For any small index category $J$ and diagram $D : J \to \mathbf{Set}$, the limit cone $(\lim_{\leftarrow J} D, (\pi_j)_{j \in \mathrm{Ob}(J)})$ is explicitly constructed as the compatible subset of the dependent product:
    $$\lim_{\leftarrow J} D = \left\{ (x_j)_{j \in \mathrm{Ob}(J)} \in \prod_{j \in \mathrm{Ob}(J)} D(j) \;\middle|\; \forall (u : j \to k) \in \mathrm{Mor}(J),\; D(u)(x_j) = x_k \right\}$$
  - For any cone $(W, (\psi_j)_{j \in \mathrm{Ob}(J)})$ over $D$, there exists a unique mediating function $\theta : W \to \lim_{\leftarrow J} D$ given by $\theta(w) = (\psi_j(w))_{j \in \mathrm{Ob}(J)}$ such that $\pi_j \circ \theta = \psi_j$ for all $j \in \mathrm{Ob}(J)$.
- **Special Cases Verified in `src/limits.py`**:
  - Terminal objects ($J = \emptyset$), binary products ($J = \{1, 2\}$ discrete), equalizers ($J = \{0 \rightrightarrows 1\}$), and pullbacks ($J = \{A \to C \leftarrow B\}$).

### 2.4 Adjunctions and Freyd's Adjoint Functor Theorem (`src/adjunction.py`)
- **Triangle Identities for $F \dashv G$ ($\eta : \mathrm{Id}_{\mathcal{C}} \Rightarrow G F$, $\varepsilon : F G \Rightarrow \mathrm{Id}_{\mathcal{D}}$)**:
  1. $\varepsilon_{F(X)} \circ F(\eta_X) = \mathrm{id}_{F(X)}$ for all $X \in \mathrm{Ob}(\mathcal{C})$.
  2. $G(\varepsilon_Y) \circ \eta_{G(Y)} = \mathrm{id}_{G(Y)}$ for all $Y \in \mathrm{Ob}(\mathcal{D})$.
- **Hom-Set Bijection**:
  - $\Phi_{X,Y}(f : F(X) \to Y) = G(f) \circ \eta_X$ and $\Phi_{X,Y}^{-1}(g : X \to G(Y)) = \varepsilon_Y \circ F(g)$ are mutually inverse and natural in $X$ and $Y$.
- **Theorem (Right Adjoints Preserve Limits — RAPL)**:
  - Mechanically verified across finite categories in `src/adjunction.py` alongside the solution-set condition for Freyd's Adjoint Functor Theorem.

### 2.5 First-Order Quantifiers and Definite Descriptions in SML (`src/quantifiers.ml`)
- Implements capture-avoiding substitution `subst_term` / `subst_form`, alpha-equivalence `alpha_eq_form`, uniqueness quantifier expansions (`expand_unique`, `expand_exists_unique`), and Russell/NBG contextual elimination of definite descriptions $\iota x.\,\varphi(x)$.

---

## 3. Stored PDFs and Historical Backups

- All compiled `.pdf` files in the repository root are treated as **strictly immutable** per workspace rules and must never be edited, patched, or overwritten.
- Historical iterative LaTeX snapshots are preserved intact in `backups/yoneda_agy_000.tex` through `backups/yoneda_agy_079.tex` corresponding to `tickets/000.txt` through `tickets/079.txt`.

---

## 4. Open Tasks and Future Enhancements

1. **Kan Extensions (`Lan_K F` and `Ran_K F`)**: Extend `src/limits.py` and `src/adjunction.py` to compute pointwise Left and Right Kan Extensions over finite categories via coends/ends and comma categories $(K \downarrow d)$ and $(d \downarrow K)$.
2. **Monad and Eilenberg-Moore / Kleisli Category Construction**: Extend `src/adjunction.py` to extract the monad $(T = G \circ F, \eta, \mu = G \varepsilon F)$ induced by an adjunction $F \dashv G$ and construct its Kleisli and Eilenberg-Moore categories.
