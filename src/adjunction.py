"""
Adjunctions and Freyd's Adjoint Functor Theorem for yoneda_ai.
Provides formal abstractions for Adjunctions F -| G, unit and counit natural
transformations, triangle identities, hom-set adjunction isomorphism,
preservation of limits by right adjoints, and Freyd's theorem verification.
"""

from typing import Dict, Set, Tuple, Any, Optional, Callable, List
from category import (
    Category,
    Morphism,
    Functor,
    NaturalTransformation,
    identity_functor,
    compose_functors,
    identity_natural_transformation,
)


class Adjunction:
    """
    Formal Adjunction F -| G between categories C and D.
    F: C -> D (Left Adjoint)
    G: D -> C (Right Adjoint)
    eta: Id_C => G o F (Unit)
    epsilon: F o G => Id_D (Counit)
    """

    def __init__(
        self,
        name: str,
        left_adjoint: Functor,
        right_adjoint: Functor,
        unit: NaturalTransformation,
        counit: NaturalTransformation,
    ):
        self.name = name
        self.F = left_adjoint
        self.G = right_adjoint
        self.unit = unit
        self.counit = counit
        self.C = self.F.source_cat
        self.D = self.F.target_cat

    def validate(self) -> bool:
        """
        Validates functor categories, unit/counit naturality, and triangle identities:
        1. epsilon_{F(X)} o F(eta_X) == id_{F(X)}  for all X in Ob(C)
        2. G(epsilon_Y) o eta_{G(Y)} == id_{G(Y)}  for all Y in Ob(D)
        """
        if self.D is None or self.G.target_cat is None:
            raise AssertionError("Adjoint functors must have explicit target categories")
        if self.G.source_cat.name != self.D.name:
            raise AssertionError(f"Source of G ({self.G.source_cat.name}) must match target of F ({self.D.name})")
        if self.G.target_cat.name != self.C.name:
            raise AssertionError(f"Target of G ({self.G.target_cat.name}) must match source of F ({self.C.name})")

        # Validate functors
        self.F.validate()
        self.G.validate()

        # Validate unit and counit
        self.unit.validate()
        self.counit.validate()

        # Triangle Identity 1: epsilon_{F(X)} o F(eta_X) = id_{F(X)}
        for X in self.C.objects:
            fx = self.F.apply_obj(X)
            eta_x = self.unit.component(X)
            f_eta_x = self.F.apply_mor(eta_x)
            eps_fx = self.counit.component(fx)
            comp1 = self.D.compose(eps_fx, f_eta_x)
            id_fx = self.D.identities[fx]
            if comp1 != id_fx:
                raise AssertionError(
                    f"Triangle Identity 1 failed at object {X}: "
                    f"epsilon_{{F({X})}} o F(eta_{X}) = {comp1} != {id_fx}"
                )

        # Triangle Identity 2: G(epsilon_Y) o eta_{G(Y)} = id_{G(Y)}
        for Y in self.D.objects:
            gy = self.G.apply_obj(Y)
            eps_y = self.counit.component(Y)
            g_eps_y = self.G.apply_mor(eps_y)
            eta_gy = self.unit.component(gy)
            comp2 = self.C.compose(g_eps_y, eta_gy)
            id_gy = self.C.identities[gy]
            if comp2 != id_gy:
                raise AssertionError(
                    f"Triangle Identity 2 failed at object {Y}: "
                    f"G(epsilon_{Y}) o eta_{{G({Y})}} = {comp2} != {id_gy}"
                )

        return True

    def phi(self, X: str, Y: str, f: Morphism) -> Morphism:
        """
        Adjunction hom-isomorphism Phi: Hom_D(F(X), Y) -> Hom_C(X, G(Y))
        Phi(f) = G(f) o eta_X
        """
        fx = self.F.apply_obj(X)
        if f.source != fx or f.target != Y:
            raise ValueError(f"Morphism {f} is not in Hom_D(F({X}), {Y})")
        gf = self.G.apply_mor(f)
        eta_x = self.unit.component(X)
        return self.C.compose(gf, eta_x)

    def psi(self, X: str, Y: str, g: Morphism) -> Morphism:
        """
        Inverse adjunction hom-isomorphism Psi: Hom_C(X, G(Y)) -> Hom_D(F(X), Y)
        Psi(g) = epsilon_Y o F(g)
        """
        gy = self.G.apply_obj(Y)
        if g.source != X or g.target != gy:
            raise ValueError(f"Morphism {g} is not in Hom_C({X}, G({Y}))")
        fg = self.F.apply_mor(g)
        eps_y = self.counit.component(Y)
        return self.D.compose(eps_y, fg)

    def verify_hom_isomorphism(self, X: str, Y: str) -> bool:
        """
        Verifies round-trip bijection between Hom_D(F(X), Y) and Hom_C(X, G(Y)):
        Psi(Phi(f)) == f  and  Phi(Psi(g)) == g
        """
        fx = self.F.apply_obj(X)
        gy = self.G.apply_obj(Y)
        hom_d = self.D.hom(fx, Y)
        hom_c = self.C.hom(X, gy)

        for f in hom_d:
            g_cand = self.phi(X, Y, f)
            f_recovered = self.psi(X, Y, g_cand)
            if f_recovered != f:
                raise AssertionError(f"Hom-isomorphism failed on {f}: recovered {f_recovered}")

        for g in hom_c:
            f_cand = self.psi(X, Y, g)
            g_recovered = self.phi(X, Y, f_cand)
            if g_recovered != g:
                raise AssertionError(f"Hom-isomorphism failed on {g}: recovered {g_recovered}")

        return True

    def verify_naturality(
        self,
        X: str,
        Y: str,
        X_prime: str,
        Y_prime: str,
        h: Morphism,
        k: Morphism,
    ) -> bool:
        """
        Verifies naturality of Phi in both arguments:
        For h: X' -> X in C and k: Y -> Y' in D,
        and f: F(X) -> Y in D:
        Phi_{X', Y'}(k o f o F(h)) == G(k) o Phi_{X, Y}(f) o h
        """
        if h.source != X_prime or h.target != X:
            raise ValueError(f"Morphism h must be X' -> X ({X_prime} -> {X})")
        if k.source != Y or k.target != Y_prime:
            raise ValueError(f"Morphism k must be Y -> Y' ({Y} -> {Y_prime})")

        fx = self.F.apply_obj(X)
        fh = self.F.apply_mor(h)
        gk = self.G.apply_mor(k)

        for f in self.D.hom(fx, Y):
            # LHS: k o f o F(h) : F(X') -> Y'
            kf = self.D.compose(k, f)
            k_f_fh = self.D.compose(kf, fh)
            lhs = self.phi(X_prime, Y_prime, k_f_fh)

            # RHS: G(k) o Phi(f) o h : X' -> G(Y')
            phi_f = self.phi(X, Y, f)
            gk_phi = self.C.compose(gk, phi_f)
            rhs = self.C.compose(gk_phi, h)

            if lhs != rhs:
                raise AssertionError(
                    f"Naturality violated for f={f}, h={h}, k={k}: {lhs} != {rhs}"
                )

        return True

    def verify_limit_preservation(
        self,
        diagram: Functor,
        lim_apex: str,
        lim_legs: Dict[str, Morphism],
    ) -> bool:
        """
        Verifies that right adjoint G preserves the limit of diagram D: J -> D.
        If (lim_apex, lim_legs) is a limit cone in D, then
        (G(lim_apex), {j: G(lim_legs[j])}) is a limit cone for G o D in C.
        """
        j_cat = diagram.source_cat
        # Form image cone in C
        g_lim_apex = self.G.apply_obj(lim_apex)
        g_legs = {j: self.G.apply_mor(lim_legs[j]) for j in j_cat.objects}

        # Check that g_legs form a cone over G o D in C
        # For u: j -> k in J, (G o D)(u) o G(pi_j) == G(pi_k)
        for (src, tgt), mors in j_cat.morphisms.items():
            for u in mors:
                d_u = diagram.apply_mor(u)
                g_d_u = self.G.apply_mor(d_u)
                leg_src = g_legs[src]
                leg_tgt = g_legs[tgt]
                comp = self.C.compose(g_d_u, leg_src)
                if comp != leg_tgt:
                    raise AssertionError(f"G did not preserve cone triangle on {u}")

        # Check universal factorization for any test cone in C
        # For test apex S in C and legs psi_j: S -> G(D(j))
        for S in self.C.objects:
            # Generate possible cones from S to G o D
            # A tuple of morphisms (psi_j)_{j in J} where psi_j in Hom_C(S, G(D(j)))
            candidate_legs_list = []
            import itertools
            sorted_j = sorted(j_cat.objects)
            choices = [list(self.C.hom(S, self.G.apply_obj(diagram.apply_obj(j)))) for j in sorted_j]
            for tuple_legs in itertools.product(*choices):
                candidate_legs = {sorted_j[idx]: tuple_legs[idx] for idx in range(len(sorted_j))}
                is_cone = True
                for (src, tgt), mors in j_cat.morphisms.items():
                    for u in mors:
                        g_d_u = self.G.apply_mor(diagram.apply_mor(u))
                        if self.C.compose(g_d_u, candidate_legs[src]) != candidate_legs[tgt]:
                            is_cone = False
                            break
                    if not is_cone:
                        break
                if is_cone:
                    # By adjunction, each psi_j: S -> G(D(j)) corresponds to
                    # psi_bar_j = Psi(psi_j): F(S) -> D(j)
                    # Because (lim_apex, lim_legs) is limit in D, there is unique mu_bar: F(S) -> lim_apex
                    # Then mu = Phi(mu_bar): S -> G(lim_apex) is the unique mediating arrow in C.
                    mediators = []
                    for mu_cand in self.C.hom(S, g_lim_apex):
                        factored = True
                        for j in sorted_j:
                            if self.C.compose(g_legs[j], mu_cand) != candidate_legs[j]:
                                factored = False
                                break
                        if factored:
                            mediators.append(mu_cand)

                    if len(mediators) != 1:
                        raise AssertionError(
                            f"Preservation of limit failed: expected unique mediator from {S}, got {len(mediators)}"
                        )

        return True


def make_adjunction_from_unit_counit(
    name: str,
    F: Functor,
    G: Functor,
    unit: NaturalTransformation,
    counit: NaturalTransformation,
) -> Adjunction:
    """Constructs and validates an Adjunction from unit and counit."""
    adj = Adjunction(
        name=name,
        left_adjoint=F,
        right_adjoint=G,
        unit=unit,
        counit=counit,
    )
    adj.validate()
    return adj


def verify_solution_set_condition(
    G: Functor,
    solution_sets: Dict[str, Tuple[Set[str], Dict[str, Morphism]]],
) -> bool:
    """
    Verifies Freyd's Solution Set Condition for functor G: D -> C:
    For each X in Ob(C), there exists a set S_X of objects of D and morphisms
    f_i: X -> G(A_i) with A_i in S_X such that for any morphism h: X -> G(Y),
    there exists some A_i in S_X and t: A_i -> Y in D such that h == G(t) o f_i.
    """
    C = G.target_cat
    D = G.source_cat
    if C is None or D is None:
        raise ValueError("G must have explicit source and target categories")

    for X in C.objects:
        if X not in solution_sets:
            raise AssertionError(f"Missing solution set specification for object {X}")
        s_x_objs, generating_arrows = solution_sets[X]
        for a in s_x_objs:
            if a not in D.objects:
                raise AssertionError(f"Solution set object {a} not in category {D.name}")

        # Check each arrow h: X -> G(Y)
        for Y in D.objects:
            gy = G.apply_obj(Y)
            for h in C.hom(X, gy):
                # Must find A_i in S_X and t: A_i -> Y such that G(t) o f_i == h
                factored = False
                for a_i in s_x_objs:
                    f_i = generating_arrows[a_i]
                    for t in D.hom(a_i, Y):
                        gt = G.apply_mor(t)
                        if C.compose(gt, f_i) == h:
                            factored = True
                            break
                    if factored:
                        break
                if not factored:
                    raise AssertionError(
                        f"Solution Set Condition failed for X={X}, Y={Y}, h={h}: "
                        f"no factorisation through solution set {s_x_objs}"
                    )
    return True


def verify_freyd_adjoint_functor_theorem(
    G: Functor,
    limits_dict: Dict[str, Tuple[Functor, str, Dict[str, Morphism]]],
    solution_sets: Dict[str, Tuple[Set[str], Dict[str, Morphism]]],
) -> bool:
    """
    Verifies the conditions of Freyd's Adjoint Functor Theorem (FAFT):
    Let D be a small, complete category. A functor G: D -> C has a left adjoint
    if and only if:
    1. G preserves all small limits in D.
    2. G satisfies the Solution Set Condition.
    """
    # 1. Solution Set Condition
    verify_solution_set_condition(G, solution_sets)

    # 2. Limit preservation check
    D = G.source_cat
    C = G.target_cat
    for diag_name, (diag, lim_apex, lim_legs) in limits_dict.items():
        j_cat = diag.source_cat
        g_lim_apex = G.apply_obj(lim_apex)
        g_legs = {j: G.apply_mor(lim_legs[j]) for j in j_cat.objects}

        # Check cone condition
        for (src, tgt), mors in j_cat.morphisms.items():
            for u in mors:
                d_u = diag.apply_mor(u)
                g_d_u = G.apply_mor(d_u)
                if C.compose(g_d_u, g_legs[src]) != g_legs[tgt]:
                    raise AssertionError(f"Limit preservation failed on diagram {diag_name}")

    return True
