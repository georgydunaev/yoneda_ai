"""
Category Theory Core Module for yoneda_ai.
Provides formal abstractions for Categories, Morphisms, Functors,
Presheaves, Opposite Categories, and Natural Transformations.
"""

from typing import Dict, Set, Tuple, Any, Optional, Callable, List
from dataclasses import dataclass


@dataclass(frozen=True)
class Morphism:
    name: str
    source: str
    target: str

    def __repr__(self) -> str:
        return f"{self.name}: {self.source} -> {self.target}"


class Category:
    def __init__(self, name: str = "C"):
        self.name = name
        self.objects: Set[str] = set()
        self.morphisms: Dict[Tuple[str, str], Set[Morphism]] = {}
        self.identities: Dict[str, Morphism] = {}
        # composition_table[(g, f)] = g circ f where f: A -> B, g: B -> C
        self.composition_table: Dict[Tuple[Morphism, Morphism], Morphism] = {}

    def add_object(self, obj: str) -> None:
        self.objects.add(obj)
        id_mor = Morphism(name=f"id_{obj}", source=obj, target=obj)
        self.identities[obj] = id_mor
        self.add_morphism(id_mor)
        self.composition_table[(id_mor, id_mor)] = id_mor

    def add_morphism(self, mor: Morphism) -> None:
        if mor.source not in self.objects:
            self.add_object(mor.source)
        if mor.target not in self.objects:
            self.add_object(mor.target)
        pair = (mor.source, mor.target)
        if pair not in self.morphisms:
            self.morphisms[pair] = set()
        self.morphisms[pair].add(mor)
        # Identity composition defaults
        id_src = self.identities[mor.source]
        id_tgt = self.identities[mor.target]
        self.composition_table[(mor, id_src)] = mor
        self.composition_table[(id_tgt, mor)] = mor

    def hom(self, source: str, target: str) -> Set[Morphism]:
        return self.morphisms.get((source, target), set())

    def compose(self, g: Morphism, f: Morphism) -> Morphism:
        if f.target != g.source:
            raise ValueError(f"Cannot compose {g} and {f}: domain mismatch ({f.target} != {g.source})")
        if (g, f) not in self.composition_table:
            raise ValueError(f"Composition of {g} and {f} is undefined in {self.name}")
        return self.composition_table[(g, f)]

    def set_composition(self, g: Morphism, f: Morphism, gf: Morphism) -> None:
        if f.target != g.source:
            raise ValueError(f"Cannot set composition: {f.target} != {g.source}")
        if gf.source != f.source or gf.target != g.target:
            raise ValueError(f"Resulting morphism {gf} has invalid source/target for {g} o {f}")
        self.add_morphism(gf)
        self.composition_table[(g, f)] = gf

    def opposite(self) -> "Category":
        op_cat = Category(name=f"{self.name}^op")
        for obj in self.objects:
            op_cat.add_object(obj)

        mor_to_op: Dict[Morphism, Morphism] = {}
        for (src, tgt), mors in self.morphisms.items():
            for m in mors:
                if m == self.identities[src]:
                    mor_to_op[m] = op_cat.identities[src]
                else:
                    op_mor = Morphism(name=f"{m.name}^op", source=tgt, target=src)
                    op_cat.add_morphism(op_mor)
                    mor_to_op[m] = op_mor

        # In C^op: g^op o f^op = (f o g)^op
        for (g, f), gf in self.composition_table.items():
            g_op = mor_to_op[g]
            f_op = mor_to_op[f]
            gf_op = mor_to_op[gf]
            op_cat.set_composition(f_op, g_op, gf_op)

        return op_cat

    def validate(self) -> bool:
        # Check identity laws
        for (src, tgt), mors in self.morphisms.items():
            id_src = self.identities[src]
            id_tgt = self.identities[tgt]
            for f in mors:
                if self.compose(f, id_src) != f:
                    raise AssertionError(f"Right identity failed for {f}")
                if self.compose(id_tgt, f) != f:
                    raise AssertionError(f"Left identity failed for {f}")

        # Check associativity on all composable triples: h o (g o f) == (h o g) o f
        for (src_f, tgt_f), mors_f in self.morphisms.items():
            for f in mors_f:
                for (src_g, tgt_g), mors_g in self.morphisms.items():
                    if src_g != tgt_f:
                        continue
                    for g in mors_g:
                        gf = self.compose(g, f)
                        for (src_h, tgt_h), mors_h in self.morphisms.items():
                            if src_h != tgt_g:
                                continue
                            for h in mors_h:
                                hg = self.compose(h, g)
                                left = self.compose(h, gf)
                                right = self.compose(hg, f)
                                if left != right:
                                    raise AssertionError(
                                        f"Associativity failed for {h} o ({g} o {f}) = {left} != {right}"
                                    )
        return True


@dataclass(frozen=True)
class SetFunction:
    source_set: Tuple[Any, ...]
    target_set: Tuple[Any, ...]
    mapping: Dict[Any, Any]
    name: str = "f"

    def __call__(self, x: Any) -> Any:
        if x not in self.mapping:
            raise KeyError(f"Element {x} not in domain of {self.name}")
        return self.mapping[x]

    def compose(self, g: "SetFunction") -> "SetFunction":
        # (self o g)(x) = self(g(x)), where g: A -> B, self: B -> C
        if set(g.target_set) > set(self.source_set):
            raise ValueError("Target of g must be subset of source of self for composition")
        new_map = {x: self.mapping[g.mapping[x]] for x in g.source_set}
        return SetFunction(
            source_set=g.source_set,
            target_set=self.target_set,
            mapping=new_map,
            name=f"({self.name} o {g.name})"
        )

    def is_identity(self) -> bool:
        return self.source_set == self.target_set and all(self.mapping[x] == x for x in self.source_set)


class Functor:
    """
    Functor F: source_cat -> target
    For Set-valued functors, target_cat can be None and obj_map/mor_map target sets/functions.
    """
    def __init__(
        self,
        name: str,
        source_cat: Category,
        target_cat: Optional[Category],
        obj_map: Dict[str, Any],
        mor_map: Dict[Morphism, Any]
    ):
        self.name = name
        self.source_cat = source_cat
        self.target_cat = target_cat
        self.obj_map = obj_map
        self.mor_map = mor_map

    def apply_obj(self, obj: str) -> Any:
        return self.obj_map[obj]

    def apply_mor(self, mor: Morphism) -> Any:
        return self.mor_map[mor]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Functor):
            return False
        if self.source_cat.name != other.source_cat.name:
            return False
        if self.obj_map != other.obj_map:
            return False
        for m, fm in self.mor_map.items():
            if m not in other.mor_map:
                return False
            other_fm = other.mor_map[m]
            if isinstance(fm, SetFunction) and isinstance(other_fm, SetFunction):
                if fm.mapping != other_fm.mapping:
                    return False
            elif fm != other_fm:
                return False
        return True

    def validate(self) -> bool:
        # Check all source objects mapped
        for obj in self.source_cat.objects:
            if obj not in self.obj_map:
                raise AssertionError(f"Object {obj} not mapped by functor {self.name}")

        # Check identity preservation
        for obj, id_mor in self.source_cat.identities.items():
            f_id = self.mor_map[id_mor]
            if isinstance(f_id, SetFunction):
                if not f_id.is_identity():
                    raise AssertionError(f"Functor {self.name} does not preserve identity on {obj}")
            elif self.target_cat is not None:
                expected = self.target_cat.identities[self.obj_map[obj]]
                if f_id != expected:
                    raise AssertionError(f"Functor {self.name} identity mismatch on {obj}")

        # Check composition preservation: F(g o f) = F(g) o F(f)
        for (g, f), gf in self.source_cat.composition_table.items():
            f_gf = self.mor_map[gf]
            f_g = self.mor_map[g]
            f_f = self.mor_map[f]
            if isinstance(f_gf, SetFunction):
                expected = f_g.compose(f_f)
                if f_gf.mapping != expected.mapping:
                    raise AssertionError(f"Functor {self.name} violates composition on {g} o {f}")
            elif self.target_cat is not None:
                expected = self.target_cat.compose(f_g, f_f)
                if f_gf != expected:
                    raise AssertionError(f"Functor {self.name} violates composition on {g} o {f}")
        return True


class NaturalTransformation:
    """
    Natural Transformation alpha: F => G between parallel functors F, G: C -> D (or to Set).
    """
    def __init__(
        self,
        name: str,
        source_functor: Functor,
        target_functor: Functor,
        components: Dict[str, Any]  # obj -> Morphism or SetFunction
    ):
        self.name = name
        self.source_functor = source_functor
        self.target_functor = target_functor
        self.components = components

    def component(self, obj: str) -> Any:
        return self.components[obj]

    def validate(self) -> bool:
        c = self.source_functor.source_cat
        # Verify component domain/codomain
        for obj in c.objects:
            if obj not in self.components:
                raise AssertionError(f"Missing component for object {obj}")
            comp = self.components[obj]
            src_val = self.source_functor.apply_obj(obj)
            tgt_val = self.target_functor.apply_obj(obj)
            if isinstance(comp, SetFunction):
                if set(comp.source_set) != set(src_val):
                    raise AssertionError(f"Component {obj} domain mismatch")
                if not (set(comp.target_set) >= set(tgt_val)):
                    raise AssertionError(f"Component {obj} codomain mismatch")

        # Naturality square check: G(f) o alpha_X == alpha_Y o F(f) for all f: X -> Y
        for (src, tgt), mors in c.morphisms.items():
            for f in mors:
                alpha_x = self.components[src]
                alpha_y = self.components[tgt]
                f_f = self.source_functor.apply_mor(f)
                g_f = self.target_functor.apply_mor(f)

                if isinstance(alpha_x, SetFunction):
                    # In Set: left = G(f) o alpha_X, right = alpha_Y o F(f)
                    left = g_f.compose(alpha_x)
                    right = alpha_y.compose(f_f)
                    if left.mapping != right.mapping:
                        raise AssertionError(
                            f"Naturality square failed for {f} in {self.name}:\n"
                            f"G(f) o alpha_X = {left.mapping}\n"
                            f"alpha_Y o F(f) = {right.mapping}"
                        )
                elif self.source_functor.target_cat is not None:
                    target_cat = self.source_functor.target_cat
                    left = target_cat.compose(g_f, alpha_x)
                    right = target_cat.compose(alpha_y, f_f)
                    if left != right:
                        raise AssertionError(
                            f"Naturality square failed for {f} in {self.name}: {left} != {right}"
                        )
        return True

    def vertical_compose(self, other: "NaturalTransformation") -> "NaturalTransformation":
        # (self o other): other.source_functor => self.target_functor
        if other.target_functor != self.source_functor:
            raise ValueError("Target of other must match source of self for vertical composition")
        new_comps = {}
        for obj in self.source_functor.source_cat.objects:
            c_self = self.components[obj]
            c_other = other.components[obj]
            if isinstance(c_self, SetFunction):
                new_comps[obj] = c_self.compose(c_other)
            else:
                target_cat = self.source_functor.target_cat
                new_comps[obj] = target_cat.compose(c_self, c_other)
        return NaturalTransformation(
            name=f"({self.name} o {other.name})",
            source_functor=other.source_functor,
            target_functor=self.target_functor,
            components=new_comps
        )


def identity_functor(cat: Category) -> Functor:
    """Constructs the identity functor Id_C: C -> C."""
    obj_map = {obj: obj for obj in cat.objects}
    mor_map = {}
    for (src, tgt), mors in cat.morphisms.items():
        for m in mors:
            mor_map[m] = m
    id_f = Functor(
        name=f"Id_{cat.name}",
        source_cat=cat,
        target_cat=cat,
        obj_map=obj_map,
        mor_map=mor_map
    )
    id_f.validate()
    return id_f


def compose_functors(G: Functor, F: Functor) -> Functor:
    """
    Constructs the composite functor (G o F): source(F) -> target(G).
    Requires F.target_cat == G.source_cat.
    """
    if F.target_cat is None:
        raise ValueError("Cannot compose with Set-valued functor F whose target_cat is None")
    if F.target_cat.name != G.source_cat.name:
        raise ValueError(f"Category mismatch: {F.target_cat.name} != {G.source_cat.name}")

    obj_map = {obj: G.apply_obj(F.apply_obj(obj)) for obj in F.source_cat.objects}
    mor_map = {}
    for (src, tgt), mors in F.source_cat.morphisms.items():
        for m in mors:
            mor_map[m] = G.apply_mor(F.apply_mor(m))

    comp_f = Functor(
        name=f"({G.name} o {F.name})",
        source_cat=F.source_cat,
        target_cat=G.target_cat,
        obj_map=obj_map,
        mor_map=mor_map
    )
    comp_f.validate()
    return comp_f


def identity_natural_transformation(F: Functor) -> NaturalTransformation:
    """Constructs the identity natural transformation id_F: F => F."""
    components = {}
    for obj in F.source_cat.objects:
        f_obj = F.apply_obj(obj)
        if F.target_cat is not None:
            components[obj] = F.target_cat.identities[f_obj]
        else:
            components[obj] = SetFunction(
                source_set=f_obj,
                target_set=f_obj,
                mapping={x: x for x in f_obj},
                name=f"id_{F.name}({obj})"
            )
    nat = NaturalTransformation(
        name=f"id_{F.name}",
        source_functor=F,
        target_functor=F,
        components=components
    )
    nat.validate()
    return nat

