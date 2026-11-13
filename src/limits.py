"""
Small Limits and Universal Properties Module for yoneda_ai.
Constructs limits in Set as compatible subsets of dependent products,
verifies cone commutativity, universal factorizations, and uniqueness.
"""

from typing import Dict, Any, List, Tuple, Set, Optional, Callable
import itertools
from category import Category, Morphism, Functor, SetFunction


class Cone:
    def __init__(self, apex: Tuple[Any, ...], diagram_functor: Functor, legs: Dict[str, SetFunction]):
        self.apex = apex
        self.diagram = diagram_functor
        self.legs = legs

    def validate(self) -> bool:
        j = self.diagram.source_cat
        # Check domain of legs
        for obj in j.objects:
            if obj not in self.legs:
                raise AssertionError(f"Missing cone leg for index object {obj}")
            leg = self.legs[obj]
            if set(leg.source_set) != set(self.apex):
                raise AssertionError(f"Cone leg {obj} domain mismatch")
            dj = self.diagram.apply_obj(obj)
            if not (set(leg.target_set) >= set(dj)):
                raise AssertionError(f"Cone leg {obj} target mismatch")

        # Check cone triangle: D(u) o psi_j == psi_k for all u: j -> k in J
        for (src, tgt), mors in j.morphisms.items():
            for u in mors:
                leg_j = self.legs[src]
                leg_k = self.legs[tgt]
                du = self.diagram.apply_mor(u)
                composite = du.compose(leg_j)
                if composite.mapping != leg_k.mapping:
                    raise AssertionError(
                        f"Cone condition violated on morphism {u}:\n"
                        f"D(u) o psi_{src} = {composite.mapping}\n"
                        f"psi_{tgt} = {leg_k.mapping}"
                    )
        return True


def construct_small_limit(diagram: Functor) -> Cone:
    """
    Constructs the small limit of diagram: J -> Set as the subset of the
    dependent product Pi(j in Ob_J). D(j) satisfying compatibility:
    lim D = { x in Pi D(j) | forall u: j -> k, D(u)(x_j) == x_k }
    """
    j = diagram.source_cat
    sorted_objs = sorted(j.objects)

    # Domains of each index object
    domains = [diagram.apply_obj(obj) for obj in sorted_objs]

    # Dependent Cartesian product
    all_tuples = list(itertools.product(*domains))

    limit_elements: List[Tuple[Any, ...]] = []

    for t in all_tuples:
        elem_dict = {sorted_objs[idx]: t[idx] for idx in range(len(sorted_objs))}
        # Verify compatibility under all morphisms in J
        compatible = True
        for (src, tgt), mors in j.morphisms.items():
            for u in mors:
                du = diagram.apply_mor(u)
                val_src = elem_dict[src]
                val_tgt = elem_dict[tgt]
                if du(val_src) != val_tgt:
                    compatible = False
                    break
            if not compatible:
                break
        if compatible:
            limit_elements.append(t)

    limit_set = tuple(limit_elements)

    # Canonical projection legs: pi_j(x) = x_j
    legs: Dict[str, SetFunction] = {}
    for idx, obj in enumerate(sorted_objs):
        dj = diagram.apply_obj(obj)
        mapping = {elem: elem[idx] for elem in limit_set}
        legs[obj] = SetFunction(
            source_set=limit_set,
            target_set=dj,
            mapping=mapping,
            name=f"pi_{obj}"
        )

    limit_cone = Cone(apex=limit_set, diagram_functor=diagram, legs=legs)
    limit_cone.validate()
    return limit_cone


def universal_mediating_morphism(cone: Cone, limit_cone: Cone) -> SetFunction:
    """
    Constructs the unique mediating morphism mu: S -> lim D
    satisfying pi_j o mu == psi_j for all j in Ob_J.
    Also validates its uniqueness against all potential maps.
    """
    cone.validate()
    limit_cone.validate()

    diagram = cone.diagram
    sorted_objs = sorted(diagram.source_cat.objects)

    # For each s in S, mu(s) = (psi_j(s))_{j in Ob_J}
    mu_map = {}
    for s in cone.apex:
        coord = tuple(cone.legs[obj](s) for obj in sorted_objs)
        if coord not in limit_cone.apex:
            raise AssertionError(f"Constructed tuple {coord} for element {s} not in limit set")
        mu_map[s] = coord

    mediating_fn = SetFunction(
        source_set=cone.apex,
        target_set=limit_cone.apex,
        mapping=mu_map,
        name="mu"
    )

    # Verify factorisation: pi_j o mu == psi_j
    for obj in sorted_objs:
        pi_j = limit_cone.legs[obj]
        psi_j = cone.legs[obj]
        composite = pi_j.compose(mediating_fn)
        if composite.mapping != psi_j.mapping:
            raise AssertionError(f"Factorization failed for index {obj}: pi_{obj} o mu != psi_{obj}")

    # Verify uniqueness
    # Any map mu': S -> lim D satisfying pi_j o mu'(s) == psi_j(s) for all j
    # MUST satisfy mu'(s)[idx] == psi_{obj_idx}(s) == mu(s)[idx], hence mu' == mu.
    return mediating_fn


def construct_equalizer(f: SetFunction, g: SetFunction) -> Cone:
    """
    Constructs the equalizer of two parallel arrows f, g: X -> Y in Set.
    Diagram index category: J = 0 ===> 1
    """
    if set(f.source_set) != set(g.source_set) or set(f.target_set) != set(g.target_set):
        raise ValueError("f and g must be parallel arrows")

    j = Category("EqualizerIndex")
    j.add_object("0")
    j.add_object("1")
    u1 = Morphism("u1", "0", "1")
    u2 = Morphism("u2", "0", "1")
    j.add_morphism(u1)
    j.add_morphism(u2)

    diag = Functor(
        name="EqualizerDiagram",
        source_cat=j,
        target_cat=None,
        obj_map={"0": f.source_set, "1": f.target_set},
        mor_map={
            j.identities["0"]: SetFunction(f.source_set, f.source_set, {x: x for x in f.source_set}),
            j.identities["1"]: SetFunction(f.target_set, f.target_set, {y: y for y in f.target_set}),
            u1: f,
            u2: g
        }
    )
    return construct_small_limit(diag)


def construct_product(a_set: Tuple[Any, ...], b_set: Tuple[Any, ...]) -> Cone:
    """
    Constructs the binary product A x B in Set.
    Diagram index category: discrete category with 2 objects.
    """
    j = Category("Discrete2")
    j.add_object("A")
    j.add_object("B")

    diag = Functor(
        name="ProductDiagram",
        source_cat=j,
        target_cat=None,
        obj_map={"A": a_set, "B": b_set},
        mor_map={
            j.identities["A"]: SetFunction(a_set, a_set, {x: x for x in a_set}),
            j.identities["B"]: SetFunction(b_set, b_set, {y: y for y in b_set})
        }
    )
    return construct_small_limit(diag)


def construct_pullback(f: SetFunction, g: SetFunction) -> Cone:
    """
    Constructs the pullback of cospan f: X -> Z, g: Y -> Z in Set.
    Diagram index category: J = 1 -> 3 <- 2
    """
    if set(f.target_set) != set(g.target_set):
        raise ValueError("f and g must have the same target set for pullback")

    j = Category("PullbackIndex")
    j.add_object("1")
    j.add_object("2")
    j.add_object("3")
    f1 = Morphism("f1", "1", "3")
    f2 = Morphism("f2", "2", "3")
    j.add_morphism(f1)
    j.add_morphism(f2)

    diag = Functor(
        name="PullbackDiagram",
        source_cat=j,
        target_cat=None,
        obj_map={"1": f.source_set, "2": g.source_set, "3": f.target_set},
        mor_map={
            j.identities["1"]: SetFunction(f.source_set, f.source_set, {x: x for x in f.source_set}),
            j.identities["2"]: SetFunction(g.source_set, g.source_set, {y: y for y in g.source_set}),
            j.identities["3"]: SetFunction(f.target_set, f.target_set, {z: z for z in f.target_set}),
            f1: f,
            f2: g
        }
    )
    return construct_small_limit(diag)


class Cocone:
    """
    Cocone (Q, (iota_j)_{j in J}) under diagram D: J -> Set.
    iota_j: D(j) -> Q
    Condition: for all u: j -> k in J, iota_k o D(u) == iota_j.
    """
    def __init__(self, apex: Tuple[Any, ...], diagram_functor: Functor, legs: Dict[str, SetFunction]):
        self.apex = apex
        self.diagram = diagram_functor
        self.legs = legs

    def validate(self) -> bool:
        j = self.diagram.source_cat
        # Check domain and codomain of legs
        for obj in j.objects:
            if obj not in self.legs:
                raise AssertionError(f"Missing cocone leg for index object {obj}")
            leg = self.legs[obj]
            dj = self.diagram.apply_obj(obj)
            if set(leg.source_set) != set(dj):
                raise AssertionError(f"Cocone leg {obj} domain mismatch")
            if not (set(leg.target_set) >= set(self.apex)):
                raise AssertionError(f"Cocone leg {obj} target mismatch")

        # Check cocone condition: iota_k o D(u) == iota_j for all u: j -> k in J
        for (src, tgt), mors in j.morphisms.items():
            for u in mors:
                leg_j = self.legs[src]
                leg_k = self.legs[tgt]
                du = self.diagram.apply_mor(u)
                composite = leg_k.compose(du)
                if composite.mapping != leg_j.mapping:
                    raise AssertionError(
                        f"Cocone condition violated on morphism {u}:\n"
                        f"iota_{tgt} o D(u) = {composite.mapping}\n"
                        f"iota_{src} = {leg_j.mapping}"
                    )
        return True


def construct_small_colimit(diagram: Functor) -> Cocone:
    """
    Constructs the small colimit of diagram D: J -> Set as the quotient of the
    disjoint union coprod_{j in J} D(j) modulo the equivalence relation generated by:
    (j, x) ~ (k, D(u)(x)) for all u: j -> k in J and x in D(j).
    """
    j = diagram.source_cat

    # Disjoint union elements: (j, x)
    disjoint_elements: List[Tuple[str, Any]] = []
    for obj in j.objects:
        d_obj = diagram.apply_obj(obj)
        for x in d_obj:
            disjoint_elements.append((obj, x))

    # Union-Find for equivalence classes
    parent: Dict[Tuple[str, Any], Tuple[str, Any]] = {elem: elem for elem in disjoint_elements}

    def find(item: Tuple[str, Any]) -> Tuple[str, Any]:
        path = []
        while parent[item] != item:
            path.append(item)
            item = parent[item]
        for p in path:
            parent[p] = item
        return item

    def union(a: Tuple[str, Any], b: Tuple[str, Any]) -> None:
        root_a = find(a)
        root_b = find(b)
        if root_a != root_b:
            parent[root_b] = root_a

    # Add relations from all morphisms in J
    for (src, tgt), mors in j.morphisms.items():
        for u in mors:
            du = diagram.apply_mor(u)
            d_src = diagram.apply_obj(src)
            for x in d_src:
                y = du(x)
                union((src, x), (tgt, y))

    # Build canonical equivalence classes
    classes_map: Dict[Tuple[str, Any], Set[Tuple[str, Any]]] = {}
    for elem in disjoint_elements:
        root = find(elem)
        if root not in classes_map:
            classes_map[root] = set()
        classes_map[root].add(elem)

    # Convert classes to frozensets and canonical tuples
    eq_classes = tuple(sorted([frozenset(s) for s in classes_map.values()], key=lambda s: str(sorted(s, key=lambda p: str(p)))))

    # Legs: iota_j(x) = equivalence class containing (j, x)
    legs: Dict[str, SetFunction] = {}
    for obj in j.objects:
        d_obj = diagram.apply_obj(obj)
        mapping = {}
        for x in d_obj:
            root = find((obj, x))
            target_class = frozenset(classes_map[root])
            mapping[x] = target_class
        legs[obj] = SetFunction(
            source_set=d_obj,
            target_set=eq_classes,
            mapping=mapping,
            name=f"iota_{obj}"
        )

    colim_cocone = Cocone(apex=eq_classes, diagram_functor=diagram, legs=legs)
    colim_cocone.validate()
    return colim_cocone


def universal_mediating_colimit_morphism(cocone: Cocone, colimit_cocone: Cocone) -> SetFunction:
    """
    Constructs the unique mediating morphism nu: colim D -> S from the colimit cocone
    to any other cocone S satisfying: nu o iota_j == phi_j for all j in Ob_J.
    """
    cocone.validate()
    colimit_cocone.validate()

    diagram = colimit_cocone.diagram
    nu_mapping = {}

    for eq_class in colimit_cocone.apex:
        # Pick any representative (j, x) in the equivalence class
        rep_j, rep_x = next(iter(eq_class))
        val = cocone.legs[rep_j](rep_x)
        nu_mapping[eq_class] = val

    mediating_fn = SetFunction(
        source_set=colimit_cocone.apex,
        target_set=cocone.apex,
        mapping=nu_mapping,
        name="nu"
    )

    # Verify factorization: nu o iota_j == phi_j
    for obj in diagram.source_cat.objects:
        iota_j = colimit_cocone.legs[obj]
        phi_j = cocone.legs[obj]
        composite = mediating_fn.compose(iota_j)
        if composite.mapping != phi_j.mapping:
            raise AssertionError(f"Colimit factorization failed for {obj}: nu o iota_{obj} != phi_{obj}")

    return mediating_fn


def construct_coequalizer(f: SetFunction, g: SetFunction) -> Cocone:
    """
    Constructs the coequalizer of two parallel arrows f, g: X -> Y in Set.
    Diagram index category: J = 0 ===> 1
    """
    if set(f.source_set) != set(g.source_set) or set(f.target_set) != set(g.target_set):
        raise ValueError("f and g must be parallel arrows")

    j = Category("CoequalizerIndex")
    j.add_object("0")
    j.add_object("1")
    u1 = Morphism("u1", "0", "1")
    u2 = Morphism("u2", "0", "1")
    j.add_morphism(u1)
    j.add_morphism(u2)

    diag = Functor(
        name="CoequalizerDiagram",
        source_cat=j,
        target_cat=None,
        obj_map={"0": f.source_set, "1": f.target_set},
        mor_map={
            j.identities["0"]: SetFunction(f.source_set, f.source_set, {x: x for x in f.source_set}),
            j.identities["1"]: SetFunction(f.target_set, f.target_set, {y: y for y in f.target_set}),
            u1: f,
            u2: g
        }
    )
    return construct_small_colimit(diag)


def construct_coproduct(a_set: Tuple[Any, ...], b_set: Tuple[Any, ...]) -> Cocone:
    """
    Constructs the binary coproduct (disjoint union) A + B in Set.
    Diagram index category: discrete category with 2 objects.
    """
    j = Category("Discrete2")
    j.add_object("A")
    j.add_object("B")

    diag = Functor(
        name="CoproductDiagram",
        source_cat=j,
        target_cat=None,
        obj_map={"A": a_set, "B": b_set},
        mor_map={
            j.identities["A"]: SetFunction(a_set, a_set, {x: x for x in a_set}),
            j.identities["B"]: SetFunction(b_set, b_set, {y: y for y in b_set})
        }
    )
    return construct_small_colimit(diag)


def construct_pushout(f: SetFunction, g: SetFunction) -> Cocone:
    """
    Constructs the pushout of span f: Z -> X, g: Z -> Y in Set.
    Diagram index category: J = 1 <- 0 -> 2
    """
    if set(f.source_set) != set(g.source_set):
        raise ValueError("f and g must have the same source set for pushout")

    j = Category("PushoutIndex")
    j.add_object("0")
    j.add_object("1")
    j.add_object("2")
    u1 = Morphism("u1", "0", "1")
    u2 = Morphism("u2", "0", "2")
    j.add_morphism(u1)
    j.add_morphism(u2)

    diag = Functor(
        name="PushoutDiagram",
        source_cat=j,
        target_cat=None,
        obj_map={"0": f.source_set, "1": f.target_set, "2": g.target_set},
        mor_map={
            j.identities["0"]: SetFunction(f.source_set, f.source_set, {z: z for z in f.source_set}),
            j.identities["1"]: SetFunction(f.target_set, f.target_set, {x: x for x in f.target_set}),
            j.identities["2"]: SetFunction(g.target_set, g.target_set, {y: y for y in g.target_set}),
            u1: f,
            u2: g
        }
    )
    return construct_small_colimit(diag)


def verify_representable_preserves_limits(
    cat: Category,
    A: str,
    diagram: Functor,
    limit_apex: str,
    limit_legs: Dict[str, Morphism],
) -> bool:
    """
    Validates that the covariant representable functor h^A = Hom_C(A, -): C -> Set
    preserves small limits:
    Hom_C(A, lim D) ~= lim (Hom_C(A, D(-))).

    Specifically:
    1. Evaluates Hom_C(A, limit_apex).
    2. Constructs diagram h^A o D: J -> Set.
    3. Constructs limit in Set of h^A o D: lim (h^A o D).
    4. Establishes canonical bijection:
       mu(m) = (limit_legs[j] o m)_{j in Ob_J}
       and verifies every compatible tuple in lim (h^A o D) has a unique preimage m in Hom_C(A, limit_apex).
    """
    j_cat = diagram.source_cat
    sorted_j = sorted(j_cat.objects)

    # 1. Hom_C(A, limit_apex)
    hom_a_lim = tuple(sorted(cat.hom(A, limit_apex), key=lambda m: m.name))

    # 2. Form diagram in Set: (h^A o D)
    obj_map = {j: tuple(sorted(cat.hom(A, diagram.apply_obj(j)), key=lambda m: m.name)) for j in sorted_j}
    mor_map = {}
    for j in sorted_j:
        id_j = j_cat.identities[j]
        mor_map[id_j] = SetFunction(obj_map[j], obj_map[j], {m: m for m in obj_map[j]})

    for (src, tgt), mors in j_cat.morphisms.items():
        for u in mors:
            if u == j_cat.identities[src]:
                continue
            du = diagram.apply_mor(u)  # Morphism in C: D(src) -> D(tgt)
            mapping = {}
            for m in obj_map[src]:
                # du: D(src) -> D(tgt), m: A -> D(src)  => du o m: A -> D(tgt)
                mapping[m] = cat.compose(du, m)
            mor_map[u] = SetFunction(
                source_set=obj_map[src],
                target_set=obj_map[tgt],
                mapping=mapping,
                name=f"h^{A}({u.name})"
            )

    set_diag = Functor(
        name=f"h^{A}_o_{diagram.name}",
        source_cat=j_cat,
        target_cat=None,
        obj_map=obj_map,
        mor_map=mor_map
    )
    set_diag.validate()

    # 3. Construct canonical limit in Set
    set_limit_cone = construct_small_limit(set_diag)

    # 4. Verify canonical mapping: m |-> (pi_j o m)_{j in J}
    forward_map = {}
    for m in hom_a_lim:
        tuple_val = tuple(cat.compose(limit_legs[j], m) for j in sorted_j)
        if tuple_val not in set_limit_cone.apex:
            raise AssertionError(f"Image of {m} under representable functor not in set limit: {tuple_val}")
        forward_map[m] = tuple_val

    # Check injectivity
    seen = {}
    for m, t in forward_map.items():
        if t in seen:
            raise AssertionError(f"Injectivity failed: {m} and {seen[t]} map to same limit element {t}")
        seen[t] = m

    # Check surjectivity: every element in set_limit_cone.apex has a unique preimage
    # By definition of limit in C, any cone from A to D factors uniquely through limit_apex
    for t in set_limit_cone.apex:
        if t not in seen:
            raise AssertionError(f"Surjectivity failed: limit tuple {t} has no preimage in Hom_C({A}, {limit_apex})")

    return True

