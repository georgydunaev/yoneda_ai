"""
Yoneda Lemma and Yoneda Embedding Formalization for yoneda_ai.
Provides computational mechanization of representable presheaves h_A,
morphism mappings h_f, the Yoneda bijection Nat(h_A, F) <-> F(A),
and automated full faithfulness verification.
"""

from typing import Dict, Any, List, Tuple
from category import Category, Morphism, Functor, SetFunction, NaturalTransformation


def make_representable_presheaf(cat: Category, A: str) -> Functor:
    """
    Constructs the contravariant representable functor h_A: C^op -> Set.
    h_A(X) = Hom_C(X, A)
    For f_op: Y -> X in C^op (corresponding to f: X -> Y in C),
    h_A(f_op): Hom_C(X, A) -> Hom_C(Y, A) is pre-composition: g |-> g o f.
    """
    if A not in cat.objects:
        raise ValueError(f"Object {A} not in category {cat.name}")

    op_cat = cat.opposite()

    # Object map: X in C^op |-> Hom_C(X, A)
    obj_map: Dict[str, Tuple[Morphism, ...]] = {}
    for x in cat.objects:
        obj_map[x] = tuple(sorted(cat.hom(x, A), key=lambda m: m.name))

    # Morphism map: for each morphism in C^op
    mor_map: Dict[Morphism, SetFunction] = {}

    # Map identity morphisms
    for x in cat.objects:
        id_op = op_cat.identities[x]
        hom_xa = obj_map[x]
        mor_map[id_op] = SetFunction(
            source_set=hom_xa,
            target_set=hom_xa,
            mapping={g: g for g in hom_xa},
            name=f"h_{A}(id_{x})"
        )

    # Map non-identity morphisms
    # An arrow in C^op from Y to X is f_op where f: X -> Y in C
    for (src_c, tgt_c), mors in cat.morphisms.items():
        for f in mors:
            # f: X -> Y in C, so f_op: Y -> X in C^op
            # Precomposition: g in Hom_C(X, A) |-> g o f in Hom_C(Y, A)
            X = src_c
            Y = tgt_c
            hom_xa = obj_map[X]
            hom_ya = obj_map[Y]

            # In op_cat:
            f_op = op_cat.identities[X] if f == cat.identities[X] else [
                m for m in op_cat.hom(Y, X) if m.name == f"{f.name}^op"
            ][0]

            mapping = {}
            for g in hom_xa:
                # g: X -> A in C, f: X -> Y in C
                # wait! If f: Y -> X in C, then g: X -> A can be composed with f: g o f: Y -> A
                # Let's check variance:
                # If f in Hom_C(Y, X), then f_op in Hom_{C^op}(X, Y)
                pass

    # Let's do the variance strictly according to category theory:
    # A morphism in C^op from X to Y corresponds to f: Y -> X in C.
    # For g in Hom_C(X, A), g o f is in Hom_C(Y, A).
    # Thus h_A(f_op) maps Hom_C(X, A) to Hom_C(Y, A).
    for (src_op, tgt_op), mors_op in op_cat.morphisms.items():
        X = src_op
        Y = tgt_op
        hom_xa = obj_map[X]
        hom_ya = obj_map[Y]

        for m_op in mors_op:
            if m_op == op_cat.identities[X]:
                continue
            # Find original f in C: Hom_C(Y, X)
            orig_name = m_op.name[:-3] if m_op.name.endswith("^op") else m_op.name
            f_c = [m for m in cat.hom(Y, X) if m.name == orig_name][0]

            mapping = {}
            for g in hom_xa:
                # g: X -> A, f_c: Y -> X  => g o f_c: Y -> A
                gf = cat.compose(g, f_c)
                mapping[g] = gf

            mor_map[m_op] = SetFunction(
                source_set=hom_xa,
                target_set=hom_ya,
                mapping=mapping,
                name=f"h_{A}({m_op.name})"
            )

    presheaf = Functor(
        name=f"h_{A}",
        source_cat=op_cat,
        target_cat=None,
        obj_map=obj_map,
        mor_map=mor_map
    )
    presheaf.validate()
    return presheaf


def make_yoneda_morphism(cat: Category, f: Morphism) -> NaturalTransformation:
    """
    Constructs the natural transformation h_f: h_A => h_B induced by f: A -> B.
    Component at X in C^op: (h_f)_X: Hom_C(X, A) -> Hom_C(X, B)
    defined by post-composition: (h_f)_X(g) = f o g.
    """
    A = f.source
    B = f.target
    h_A = make_representable_presheaf(cat, A)
    h_B = make_representable_presheaf(cat, B)

    components: Dict[str, SetFunction] = {}
    for X in cat.objects:
        hom_xa = h_A.apply_obj(X)
        hom_xb = h_B.apply_obj(X)
        mapping = {}
        for g in hom_xa:
            # f: A -> B, g: X -> A  => f o g: X -> B
            mapping[g] = cat.compose(f, g)
        components[X] = SetFunction(
            source_set=hom_xa,
            target_set=hom_xb,
            mapping=mapping,
            name=f"(h_{f.name})_{X}"
        )

    nat_trans = NaturalTransformation(
        name=f"h_{f.name}",
        source_functor=h_A,
        target_functor=h_B,
        components=components
    )
    nat_trans.validate()
    return nat_trans


def yoneda_evaluation(alpha: NaturalTransformation, A: str, cat: Category) -> Any:
    """
    Yoneda evaluation map Phi: Nat(h_A, F) -> F(A)
    Phi(alpha) = alpha_A(id_A)
    """
    id_a = cat.identities[A]
    comp_a = alpha.component(A)
    return comp_a(id_a)


def yoneda_reconstruction(
    F: Functor, A: str, cat: Category, u: Any
) -> NaturalTransformation:
    """
    Yoneda inverse map Psi: F(A) -> Nat(h_A, F)
    Given u in F(A), constructs alpha^u: h_A => F
    with components (alpha^u)_X(g) = F(g^op)(u) for g: X -> A in C.
    """
    h_A = make_representable_presheaf(cat, A)
    op_cat = cat.opposite()

    components: Dict[str, SetFunction] = {}
    for X in cat.objects:
        hom_xa = h_A.apply_obj(X)
        fx = F.apply_obj(X)
        mapping = {}
        for g in hom_xa:
            # g: X -> A in C, so g^op: A -> X in C^op
            if g == cat.identities[A]:
                g_op = op_cat.identities[A]
            else:
                g_op = [m for m in op_cat.hom(A, X) if m.name == f"{g.name}^op"][0]
            # F(g^op): F(A) -> F(X)
            fg = F.apply_mor(g_op)
            mapping[g] = fg(u)

        components[X] = SetFunction(
            source_set=hom_xa,
            target_set=tuple(fx) if isinstance(fx, (tuple, list, set)) else (fx,),
            mapping=mapping,
            name=f"alpha^{u}_{X}"
        )

    alpha_u = NaturalTransformation(
        name=f"alpha^{u}",
        source_functor=h_A,
        target_functor=F,
        components=components
    )
    alpha_u.validate()
    return alpha_u


def verify_yoneda_isomorphism(F: Functor, A: str, cat: Category) -> bool:
    """
    Validates round-trip Yoneda bijection on presheaf F: C^op -> Set:
    1. For every u in F(A): Phi(Psi(u)) == u
    2. Checks naturality of Psi(u)
    """
    fa = F.apply_obj(A)
    for u in fa:
        alpha_u = yoneda_reconstruction(F, A, cat, u)
        u_recovered = yoneda_evaluation(alpha_u, A, cat)
        if u_recovered != u:
            raise AssertionError(f"Yoneda round-trip failed for element {u}: got {u_recovered}")
    return True


def verify_yoneda_full_faithful(cat: Category, A: str, B: str) -> bool:
    """
    Validates that the Yoneda embedding h_- is full and faithful on Hom_C(A, B):
    f |-> h_f is a bijection between Hom_C(A, B) and Nat(h_A, h_B).
    """
    hom_ab = cat.hom(A, B)
    # Check faithfulness (injectivity)
    seen_nats = {}
    for f in hom_ab:
        hf = make_yoneda_morphism(cat, f)
        # Check evaluation recovers f
        f_eval = yoneda_evaluation(hf, A, cat)
        if f_eval != f:
            raise AssertionError(f"Evaluation of h_{f} at id_{A} did not recover {f}, got {f_eval}")
        # Key representing component mappings
        key = tuple((x, tuple(sorted(hf.component(x).mapping.items(), key=lambda p: p[0].name))) for x in sorted(cat.objects))
        if key in seen_nats:
            raise AssertionError(f"Faithfulness violated: {f} and {seen_nats[key]} yield same natural transformation")
        seen_nats[key] = f

    # Check fullness (surjectivity)
    # Every u in h_B(A) = Hom_C(A, B) induces alpha^u which matches h_u
    for u in hom_ab:
        alpha_u = yoneda_reconstruction(make_representable_presheaf(cat, B), A, cat, u)
        hu = make_yoneda_morphism(cat, u)
        for x in cat.objects:
            if alpha_u.component(x).mapping != hu.component(x).mapping:
                raise AssertionError(f"Fullness check failed: alpha^{u} != h_{u} at object {x}")

    return True


def make_covariant_representable(cat: Category, A: str) -> Functor:
    """
    Constructs the covariant representable functor h^A: C -> Set.
    h^A(X) = Hom_C(A, X)
    For f: X -> Y in C,
    h^A(f): Hom_C(A, X) -> Hom_C(A, Y) is post-composition: g |-> f o g.
    """
    if A not in cat.objects:
        raise ValueError(f"Object {A} not in category {cat.name}")

    obj_map: Dict[str, Tuple[Morphism, ...]] = {}
    for x in cat.objects:
        obj_map[x] = tuple(sorted(cat.hom(A, x), key=lambda m: m.name))

    mor_map: Dict[Morphism, SetFunction] = {}

    for x in cat.objects:
        id_x = cat.identities[x]
        hom_ax = obj_map[x]
        mor_map[id_x] = SetFunction(
            source_set=hom_ax,
            target_set=hom_ax,
            mapping={g: g for g in hom_ax},
            name=f"h^{A}(id_{x})"
        )

    for (src, tgt), mors in cat.morphisms.items():
        for f in mors:
            if f == cat.identities[src]:
                continue
            hom_asrc = obj_map[src]
            hom_atgt = obj_map[tgt]
            mapping = {}
            for g in hom_asrc:
                # g: A -> src, f: src -> tgt => f o g: A -> tgt
                mapping[g] = cat.compose(f, g)
            mor_map[f] = SetFunction(
                source_set=hom_asrc,
                target_set=hom_atgt,
                mapping=mapping,
                name=f"h^{A}({f.name})"
            )

    cov_functor = Functor(
        name=f"h^{A}",
        source_cat=cat,
        target_cat=None,
        obj_map=obj_map,
        mor_map=mor_map
    )
    cov_functor.validate()
    return cov_functor


class YonedaEmbedding:
    """
    The Yoneda Embedding Functor y: C -> PSh(C) = [C^op, Set].
    y(A) = h_A (contravariant representable presheaf Hom_C(-, A))
    y(f) = h_f (natural transformation h_A => h_B induced by f: A -> B)
    """
    def __init__(self, cat: Category):
        self.cat = cat
        self.presheaves: Dict[str, Functor] = {}
        for obj in cat.objects:
            self.presheaves[obj] = make_representable_presheaf(cat, obj)

    def apply_obj(self, A: str) -> Functor:
        if A not in self.presheaves:
            self.presheaves[A] = make_representable_presheaf(self.cat, A)
        return self.presheaves[A]

    def apply_mor(self, f: Morphism) -> NaturalTransformation:
        return make_yoneda_morphism(self.cat, f)

    def verify_functoriality(self) -> bool:
        # Check identity preservation: y(id_A) == id_{h_A}
        for obj in self.cat.objects:
            id_a = self.cat.identities[obj]
            y_id = self.apply_mor(id_a)
            h_a = self.apply_obj(obj)
            for x in self.cat.objects:
                comp = y_id.component(x)
                if not comp.is_identity():
                    raise AssertionError(f"Yoneda embedding does not preserve identity on {obj}")

        # Check composition preservation: y(g o f) == y(g) o y(f)
        for (g, f), gf in self.cat.composition_table.items():
            y_f = self.apply_mor(f)
            y_g = self.apply_mor(g)
            y_gf = self.apply_mor(gf)
            comp_nat = y_g.vertical_compose(y_f)
            for x in self.cat.objects:
                if comp_nat.component(x).mapping != y_gf.component(x).mapping:
                    raise AssertionError(f"Yoneda embedding violates composition on {g} o {f} at object {x}")
        return True

    def verify_full_and_faithful(self) -> bool:
        for a in self.cat.objects:
            for b in self.cat.objects:
                verify_yoneda_full_faithful(self.cat, a, b)
        return True


def verify_yoneda_embedding(cat: Category) -> bool:
    """Convenience verifier for full faithfulness and functoriality of Yoneda embedding."""
    y = YonedaEmbedding(cat)
    y.verify_functoriality()
    y.verify_full_and_faithful()
    return True

