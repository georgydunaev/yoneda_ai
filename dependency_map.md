# Phase 0 — Complete Inventory, Foundational Conventions, and Dependency Map

## 1. Foundational Conventions Record
- **Base Logical Calculus:** Classical first-order predicate calculus with equality (`=`), formulated in Hilbert style with 14 axiom schemata (`impI`, `impE`, `andE1`, `andE2`, `andI`, `orI1`, `orI2`, `orE`, `negI`, `negE`, `LEM`, `\forall E`, `\exists I`, `=refl`, `=subs` in Table 1 `tab:axiompltab`) and 3 inference rules (`MP`, `\forall I`, `\exists E` in Table 2 `tab:rulestab`).
- **Law of Excluded Middle (`LEM`):** Explicitly assumed as an axiom schema (`A \lor \neg A` in Table 1). Used in set intersection `\inter K \in \Set` (case split `K = \emptyset \lor K \neq \emptyset`), dual quantifier `?x. P(x)`, characteristic functions `\chi_S : X \to 2` in Theorem `thm:set_reps`(1), and epimorphism characterization in `\Set` in Theorem `thm:mono_epi_yoneda`(1).
- **Set and Class Theory:** von Neumann–Bernays–Gödel (`NBG`) conservative class-set extension of `ZFC` (Subsection `sec:foundations` and Subsection `sec:axioms`), with explicit dual interpretation in `ZFC` + Grothendieck universes `\mathcal{U} \in \mathcal{U}^+`.
- **Axioms Explicitly Assumed (Subsection `sec:axioms`):**
  1. Predicative Class Comprehension (`{x \in \Set : \phi(x)}` with bound variables restricted to `\Set`)
  2. Extensionality (for classes and sets)
  3. Empty Set (`\emptyset \in \Set`)
  4. Pairing (`{x, y} \in \Set`, `{x} \in \Set` for `x, y \in \Set`)
  5. Union (`\bigcup X \in \Set`, `A \cup B \in \Set` for `X, A, B \in \Set`)
  6. Power Set (`\Pow(X) \in \Set` for `X \in \Set`)
  7. Separation / Aussonderung (`A \cap K \in \Set` for `A \in \Set` and class `K`)
  8. Replacement (`F[A] \in \Set` for functional class `F` and `A \in \Set`)
  9. Infinity (`\omega = \mathbb{N} \in \Set`)
  10. Foundation / Regularity (`A \neq \emptyset \to \exists x \in A.\ x \cap A = \emptyset`)
- **Axiom of Choice (`AC`):** *Not* assumed globally. Inverses of bijections in `\Set` (Lemma `lem:set_iso_bij`) are constructed without `AC` via Russell's definite description binder `\The` using unique existence `\exists !a \in A.\ f(a) = b`. Epimorphisms in `\Set` (Theorem `thm:mono_epi_yoneda`(1)) are proved surjective via characteristic maps into `2 = \{0, 1\}` using `LEM`, rather than choosing a section via `AC`.
- **Size of `\Set`, Smallness, and Local Smallness:**
  - `\Set = \{x : \exists K.\ x \in K\}` is a proper class in `NBG` (`\Set \notin \Set`), or a Grothendieck universe `\mathcal{U}` in `ZFC + \mathcal{U}`.
  - Every element of a class in `NBG` is a set (`x \in K \implies x \in \Set`). Thus for any category `C` in `NBG`, individual objects `X \in \Ob_C` and morphisms `f \in \Hom_C(X,Y)` are sets, while `\Ob_C` and `\Hom_C(X,Y)` are classes.
  - `C` is *locally small* if `\Hom_C(X, Y) \in \Set` for all `X, Y \in \Ob_C`.
  - `C` is *small* if both `\Ob_C \in \Set` and `\Hom_C(X, Y) \in \Set` for all `X, Y \in \Ob_C`.
  - Functor categories `[C, D]` are locally small categories in `NBG` when `C` is small and `D` is locally small; when `C` is only locally small, `[C, D]` is a *metacategory* in `NBG` (or a locally `\mathcal{U}^+`-small category in `ZFC` with universes `\mathcal{U} \in \mathcal{U}^+`), while `\Nat(h_A, G)` is bijective with the set `G(A) \in \Set` by the Yoneda Lemma.

---

## 2. Complete Inventory and Dependency Table

| Item / Label | Type & Title | Section | Direct Dependencies | Downstream Dependents |
|---|---|---|---|---|
| `tab:axiompltab` | Table 1: Axiom schemata of predicate calculus with equality | 1.1 | Primitive syntax (`\Var, \Term, \Fm, \FV, \textrm{FFI}`) | All of Part I & Part II |
| `tab:rulestab` | Table 2: Rules of inference (`MP`, `\forall I`, `\exists E`) | 1.1 | `tab:axiompltab` | All of Part I & Part II |
| `def:hilbert_deriv` | Definition 1.1: Formal derivation `\Gamma \vdash B` (added in `AUD-002`) | 1.2 | `tab:axiompltab`, `tab:rulestab` | `lem:id_law`–`thm:quant_dist` |
| `lem:id_law` | Lemma: Hilbert derivation of `\vdash A \to A` | 1.2 | `impI`, `impE`, `MP` | `thm:deduction` |
| `thm:eq_equiv` | Theorem: Reflexivity, symmetry, transitivity of `=` | 1.2 | `=refl`, `=subs`, `\forall E`, `impI`, `impE`, `MP` | All equality proofs in Sec. 1–2 |
| `lem:import_export` | Lemma: Syllogism, Import/Export for `\land`, Commutation of antecedents | 1.2 | `impI`, `impE`, `andI`, `andE1`, `andE2`, `MP` | `thm:deduction`, `thm:quant_dist` |
| `thm:deduction` | Theorem: Deduction Metatheorem | 1.2 | `lem:id_law`, `lem:import_export`, `\forall I`, `\exists E` | `thm:quant_dist`, `lem:classical_neg` |
| `thm:quant_dist` | Theorem: Quantifier distribution laws over `\to` | 1.2 | `\forall E`, `\exists I`, `\forall I`, `\exists E`, `lem:import_export` | Set/category proofs |
| `lem:classical_neg` | Lemma: Classical negation & quantifier De Morgan laws (added in `AUD-002`) | 1.2 | `negI`, `negE`, `LEM`, `orE`, `thm:deduction`, `thm:quant_dist` | `ex:inter_set`, `sec:binders`, `thm:set_reps` |
| `sec:axioms` | Axioms (1)–(10) of `NBG` / `ZFC` | 1.3 | `sec:hilbert_logic` | All of Sec. 1.4–2.7 |
| Def. (`\interclass K`) | Definition: Class intersection `\interclass K` | 1.4 | Predicative comprehension | `ex:interclass_set`, `ex:interclass_empty` |
| `ex:interclass_set` | Exercise: `K \neq \emptyset \to \interclass K \in \Set` | 1.4 | Extensionality, Separation | `ex:inter_set` |
| Ex. (`\interclass \emptyset`) | Exercise: `K = \emptyset \to \interclass K = \Set` | 1.4 | Extensionality | `lem:the_default` |
| Def. (`\inter K`) | Definition: Set intersection `\inter K` | 1.4 | Predicative comprehension | `ex:inter_set`, `def:the_binder` |
| Ex. (`\inter K \in \Set`) | Exercise: `\inter K \in \Set` | 1.4 | `LEM`, Empty Set, `ex:interclass_set` | `def:the_binder`, `thm:tord_closure` |
| `def:unique_q` | Definition: Uniqueness quantifier `!x \in \Set.\ P(x)` | 1.5 | Predicate logic | `exists!`, `def:dual_q`, `The`, `\Fun` |
| Def. (`\exists !x`) | Definition: Exists-unique quantifier `\exists !x \in \Set.\ P(x)` | 1.5 | `def:unique_q` | `ex:the_prop`, `lem:the_default`, `lem:set_iso_bij`, `thm:univ_elem_char`, `def:term_init` |
| `def:dual_q` | Definition: Dual quantifier `?x \in \Set.\ P(x)` | 1.5 | `def:unique_q` | Ex. (`!x \LRA \neg ?x \neg`), Lemma (`?x` char.) |
| Def. (`\The x.\ P(x)`) | Definition: Definite description `\The x.\ P(x)` | 1.5 | `\inter K`, `def:unique_q` | `ex:the_eq`, `ex:the_prop`, `lem:the_default`, `g(x)`, `lem:set_iso_bij` |
| `ex:the_eq` | Exercise: `(a \in \Set \land P(a) \land !w.\ P(w)) \to (\The x.\ P(x)) = a` | 1.5 | `\The`, Extensionality | `ex:the_prop`, `lem:fun_comp`, `lem:sigma_pi`, `thm:fun_incl`, `lem:set_iso_bij` |
| `ex:the_prop` | Exercise: `(\exists !w \in \Set.\ P(w)) \to P(\The x.\ P(x))` | 1.5 | `ex:the_eq`, `=subs`, `\exists E` | `lem:fun_comp`, `thm:fun_incl`, `lem:set_iso_bij` |
| `lem:the_default` | Lemma: `\neg(\exists !w \in \Set.\ P(w)) \to (\The x.\ P(x)) = \emptyset` | 1.5 | `\The`, `\inter \emptyset = \emptyset` | Ex. (`x \notin \dom(g) \to g(x) = \emptyset`) |
| `def:pair_rel` | Definition: `\langle x,y\rangle`, `X \times Y`, `\dom`, `\ran`, `f \circ g`, `\Rel`, `\Fun` | 1.6 | Pairing, Comprehension, `def:unique_q` | `lem:pair_prop`, `lem:fun_comp`, `sec:sigma_pi`, `sec:extensionality`, Sec. 2 |
| `lem:pair_prop` | Lemma: Injectivity of `\langle x,y\rangle` and `X \times Y \in \Set` | 1.6 | `def:pair_rel`, Pairing, Union, Power Set, Separation | `lem:sigma_pi`, `lem:set_and_op`, `thm:set_reps`, `lem:presheaf_product` |
| `lem:fun_comp` | Lemma: Closure of functional relations under `f \circ g` | 1.6 | `def:pair_rel`, `ex:the_eq`, `ex:the_prop` | `lem:set_and_op` |
| Def. (`\Sigma R`, `\Pi R`) | Definitions: Dependent sum `\Sigma R` and Dependent product `\Pi R` | 1.7 | `def:pair_rel`, `\Pow`, `\Fun` | `lem:sigma_pi`, `lem:set_and_op`, `def:functor`, `def:nat`, `def:cat_of_elements`, `thm:yoneda_limits` |
| `lem:sigma_pi` | Lemma: Characterization, set-hood, and `\beta/\eta`-conversion for `\Sigma R, \Pi R` | 1.7 | `lem:pair_prop`, Replacement, Union, Power Set, Separation, `ex:the_eq` | `lem:set_and_op`, `lem:fun_cat`, `lem:cat_of_elements`, `thm:yoneda_limits`, `thm:cartesian_closed` |
| `thm:fun_incl` | Theorem: Inclusion of functions `g_1 \subseteq g_2` | 1.8 | `def:pair_rel`, `ex:the_eq`, `ex:the_prop`, `=subs` | `thm:fun_ext` |
| `thm:fun_ext` | Theorem: Functional extensionality `g_1 = g_2` | 1.8 | `thm:fun_incl`, Extensionality | Every equality of functions/morphisms in Sec. 2 |
| `def:htr_ord` | Definitions: `\Tr(A)`, `\mysucc(A)`, `\HTr(A)` (`\TOrd(A)`), `\Ord(A)` | 1.9 | Union, Pairing, Foundation | `thm:ord_htr_equiv`–`thm:tord_closure`, `thm:set_reps`, `thm:grothendieck_rep` |
| `thm:ord_htr_equiv` | Theorem: `\Ord(A) \LRA \HTr(A)` under Foundation | 1.9 | `def:htr_ord`, Foundation, Extensionality | `thm:tord_closure` |
| Thm. (`\Tr \land \neg\HTr`) | Theorem: Counterexample `A = \{0, 1, \{1\}\}` | 1.9 | `def:htr_ord`, Empty Set, Pairing | Exposition of `\Tr` vs. `\HTr` |
| `thm:tr_succ`, `thm:tord_succ` | Theorems: Closure of `\Tr` and `\HTr` under `\mysucc` | 1.9 | `def:htr_ord`, Union | `thm:tord_closure` |
| `thm:tord_closure` | Theorem: Closure of `\Tr, \HTr, \Ord` under `\emptyset, \mysucc, \bigcup, \inter` | 1.9 | `thm:tord_succ`, `thm:ord_htr_equiv` | Finite ordinals `0, 1, 2` used in Sec. 2 |
| `def:category` | Definition: Category, locally small category, small category | 2.0 | `sec:foundations`, `def:pair_rel` | All of Part II |
| `lem:set_and_op` | Lemma: Category `\Set` and opposite category `C^\op` | 2.0 | `def:category`, `lem:pair_prop`, `lem:fun_comp`, `lem:sigma_pi`, `thm:fun_ext` | All of Part II |
| `def:functor` | Definition: Covariant and contravariant functors, `[C, D]` | 2.1 | `def:category`, `lem:set_and_op`, `\Pi` | All of Part II |
| `def:hommor`, `lem:contra_hom` | Definition & Lemma: Contravariant Hom-functor `\Hom_C(-, x) \in [C^\op, \Set]` | 2.1 | `def:functor`, `lem:set_and_op`, `thm:fun_ext` | `lem:eta_nat`, `lem:yoneda_functor`, `thm:yoneda_contra` |
| `def:nat`, `lem:fun_cat` | Definition & Lemma: Natural transformations `\Nat(F,G)` and functor category `[C,D]` | 2.1 | `def:functor`, `lem:sigma_pi`, `thm:fun_ext`, Separation | All of Part II |
| `def:iso`, `thm:nat_iso` | Definition & Theorem: Isomorphisms and pointwise natural isomorphism criterion | 2.1 | `def:category`, `def:functor`, `def:nat` | `lem:ff_reflects_iso`, `thm:yoneda_iso`, `thm:univ_elem_char`, `thm:slice_el` |
| Def. (`h_x`, `\eta^f`), `lem:eta_nat` | Definitions & Lemma: Representable presheaf `h_x` and naturality of `\eta^f` | 2.1 | `lem:contra_hom`, `def:nat`, `thm:fun_ext` | `lem:yoneda_functor`, `thm:yoneda_emb` |
| `lem:yoneda_functor` | Lemma: Functoriality of Yoneda embedding `h_- : C \to [C^\op, \Set]` | 2.1 | `lem:contra_hom`, `lem:eta_nat`, `thm:fun_ext` | `thm:yoneda_emb`, `thm:yoneda_nat`, `thm:density`, `thm:kan_unification` |
| `thm:yoneda_contra` | Theorem: Contravariant Yoneda Lemma `\Nat(h_A, G) \cong G(A)` | 2.1 | `lem:contra_hom`, `def:nat`, `thm:fun_ext` | `thm:yoneda_emb`, `thm:yoneda_nat`, `thm:yoneda_cov`, Sec. 2.2–2.6 |
| `thm:yoneda_emb` | Theorem: Full faithfulness of Yoneda embedding `h_-` | 2.1 | `lem:yoneda_functor`, `thm:yoneda_contra` | `thm:yoneda_iso`, `thm:retract_yoneda`, `thm:yoneda_limits` |
| `lem:ff_reflects_iso`, `thm:yoneda_iso` | Lemma & Theorem: Reflection of isomorphisms and `A \cong B \LRA h_A \cong h_B \LRA h^A \cong h^B` | 2.1 | `thm:nat_iso`, `thm:yoneda_emb`, `thm:yoneda_cov` | `thm:rep_unique` |
| `thm:yoneda_nat` | Theorem: Naturality of Yoneda bijection `\Phi_{A,G}` in `A` and `G` | 2.1 | `thm:yoneda_contra`, `lem:yoneda_functor`, `thm:fun_ext` | `thm:rep_unique`, `thm:mono_epi_yoneda`, `thm:density`, `thm:cartesian_closed`, `thm:kan_unification` |
| `thm:yoneda_cov` | Definition & Theorem: Covariant Hom-functor `h^A` and Covariant Yoneda Lemma | 2.1 | `lem:set_and_op`, `thm:yoneda_contra`, `thm:yoneda_emb`, `thm:yoneda_nat` | `thm:yoneda_iso`, `thm:univ_elem_char`, `thm:adj_yoneda` |
| `def:representable`, `lem:set_iso_bij` | Definition & Lemma: Universal elements and `Iso_\Set(A,B) \LRA` bijections | 2.2 | `thm:yoneda_contra`, `ex:the_eq`, `ex:the_prop`, `lem:sigma_pi`, `thm:fun_ext` | `thm:univ_elem_char` |
| `thm:univ_elem_char` | Theorem: Universal Element Characterization Theorem | 2.2 | `thm:nat_iso`, `lem:set_iso_bij`, `thm:yoneda_contra` | `thm:rep_unique`, `thm:set_reps`, `thm:grothendieck_rep`, `def:limits`, `thm:adj_yoneda` |
| `thm:rep_unique` | Theorem: Uniqueness of representing objects up to unique isomorphism | 2.2 | `thm:univ_elem_char`, `thm:yoneda_nat` | `thm:grothendieck_rep`, `thm:limit_unique`, `thm:triangle_id` |
| `thm:set_reps` | Theorem: Representations of `\Pow^*` by `2 = \{0,1\}` and `G_{A,B}` by `A \times B` | 2.2 | `thm:tord_closure`, `LEM`, `lem:pair_prop`, `thm:univ_elem_char` | `thm:mono_epi_yoneda`, `lem:presheaf_product` |
| `def:retract`, `thm:retract_yoneda` | Definition & Theorem: Retracts of `h_A` and idempotent splitting `h_A^e` | 2.2 | `thm:yoneda_contra`, `thm:yoneda_emb` | Idempotent completion remarks |
| `def:mono_epi`, `thm:mono_epi_yoneda` | Definition & Theorem: Yoneda characterization of monomorphisms & epimorphisms | 2.2 | `thm:set_reps`, `thm:yoneda_contra`, `thm:yoneda_nat` | Subobject/quotient structure in `[C^\op, \Set]` |
| `def:cat_of_elements`, `lem:cat_of_elements` | Definition & Lemma: Category of elements `\int_C G` and faithfulness of `\pi_G` | 2.3 | `lem:sigma_pi`, Separation, `def:category`, `def:functor` | `thm:grothendieck_rep`, `thm:slice_el`, `thm:density`, `thm:kan_unification` |
| `def:term_init`, `thm:grothendieck_rep` | Definition & Theorem: Terminal/initial objects and Grothendieck's terminality criterion | 2.3 | `thm:univ_elem_char`, `thm:rep_unique`, `lem:cat_of_elements` | `thm:slice_el`, `thm:kan_unification` |
| `def:slice_cat`, `thm:slice_el` | Definition & Theorem: Slice category `\int_C h_A = C/A` and functoriality of `\int_C` | 2.3 | `lem:cat_of_elements`, `thm:grothendieck_rep`, `thm:nat_iso` | `thm:kan_unification` |
| `def:limits`, `thm:limit_unique` | Definition & Theorem: Cones, cocones, limits, colimits, and uniqueness | 2.4 | `lem:fun_cat`, `thm:univ_elem_char`, `thm:rep_unique` | `thm:hom_continuity`, `thm:yoneda_limits`, `thm:density`, `thm:rapl_lapc`, `thm:kan_unification` |
| `thm:hom_continuity` | Theorem: Continuity of covariant & contravariant Hom-functors | 2.4 | `def:limits`, `lem:sigma_pi`, `lem:set_and_op` | `thm:yoneda_limits`, `thm:rapl_lapc` |
| `thm:yoneda_limits` | Theorem: Small limits in `\Set` via `\Pi`, pointwise limits in `[C^\op,\Set]`, preservation/reflection by `h_-` | 2.4 | `lem:sigma_pi`, `def:limits`, `thm:hom_continuity` | `lem:presheaf_product` |
| `thm:density` | Theorem: Density Theorem / Co-Yoneda Lemma `G \cong \mathrm{colim}_{\int_C G} h_A` | 2.4 | `lem:cat_of_elements`, `thm:yoneda_contra`, `thm:yoneda_nat`, `def:limits` | `thm:kan_unification` |
| `def:adjunction`, `thm:adj_yoneda` | Definition & Theorem: Adjoint functors `L \dashv R` and universal arrow characterization | 2.5 | `thm:yoneda_cov`, `thm:univ_elem_char` | `thm:triangle_id`, `thm:rapl_lapc`, `def:kan_ext` |
| `thm:triangle_id` | Theorem: Unit, counit, triangle identities, and uniqueness of adjoints | 2.5 | `thm:adj_yoneda`, `thm:rep_unique` | `thm:rapl_lapc`, `thm:cartesian_closed`, `def:kan_ext` |
| `thm:rapl_lapc` | Theorem: RAPL, LAPC, and `\mathrm{colim}_J \dashv \Delta \dashv \lim_J` | 2.5 | `thm:adj_yoneda`, `thm:hom_continuity`, `def:limits` | `thm:kan_unification` |
| `lem:presheaf_product` | Lemma: Pointwise binary products `F \times G` in `[C^\op, \Set]` | 2.6 | `lem:pair_prop`, `thm:set_reps`, `thm:yoneda_limits` | `thm:cartesian_closed` |
| `thm:cartesian_closed` | Theorem: Cartesian closure of `\Set` and `[C^\op, \Set]` (`H^G(A) = \Nat(h_A \times G, H)`) | 2.6 | `lem:sigma_pi`, `lem:presheaf_product`, `lem:fun_cat`, `thm:yoneda_contra`, `thm:yoneda_nat` | `tab:synthesis` |
| `def:kan_ext`, `thm:kan_unification` | Definition & Theorem: Left/Right Kan extensions and unification of Yoneda, limits, and Density | 2.6 | `thm:adj_yoneda`, `thm:yoneda_contra`, `thm:yoneda_nat`, `thm:slice_el`, `thm:density` | `tab:synthesis` |
| `tab:synthesis` | Table 3: Foundational synthesis connecting Part I and Part II | 2.7 | All of Part I and Part II | Conclusion |
