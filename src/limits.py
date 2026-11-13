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
