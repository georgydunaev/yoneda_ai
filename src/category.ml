(*
  Standard ML Category Theory and Yoneda Lemma Engine for yoneda_ai.
  Compatible with CakeML and Poly/ML.
*)

structure CategoryTheory =
struct

  datatype morphism = Morphism of string * string * string

  fun mor_name (Morphism (n, _, _)) = n
  fun mor_src (Morphism (_, s, _)) = s
  fun mor_tgt (Morphism (_, _, t)) = t

  fun mor_eq (Morphism (n1, s1, t1), Morphism (n2, s2, t2)) =
      n1 = n2 andalso s1 = s2 andalso t1 = t2

  type comp_rule = (morphism * morphism) * morphism

  datatype category =
    Cat of {
      name : string,
      objects : string list,
      morphisms : morphism list,
      identities : (string * morphism) list,
      compositions : comp_rule list
    }

  fun find_id (Cat {identities, ...}) obj =
    case List.find (fn (o_name, _) => o_name = obj) identities of
        SOME (_, m) => m
      | NONE => raise Fail ("Identity not found for object: " ^ obj)

  fun hom (Cat {morphisms, ...}) (src, tgt) =
    List.filter (fn m => mor_src m = src andalso mor_tgt m = tgt) morphisms

  fun compose (c as Cat {compositions, ...}) (g, f) =
    if mor_tgt f <> mor_src g then
      raise Fail ("Domain mismatch in composition: " ^ mor_tgt f ^ " <> " ^ mor_src g)
    else
      let
        val g_src = mor_src g
        val g_tgt = mor_tgt g
        val f_src = mor_src f
        val id_g_src = find_id c g_src
        val id_g_tgt = find_id c g_tgt
      in
        if mor_eq (f, id_g_src) then g
        else if mor_eq (g, id_g_tgt) then f
        else
          case List.find (fn ((g0, f0), _) => mor_eq (g0, g) andalso mor_eq (f0, f)) compositions of
              SOME (_, gf) => gf
            | NONE => raise Fail ("Undefined composition for: " ^ mor_name g ^ " o " ^ mor_name f)
      end

  (* Opposite category C^op *)
  fun opposite (Cat {name, objects, morphisms, identities, compositions}) =
    let
      fun op_mor (Morphism (n, s, t)) =
        if String.isPrefix "id_" n then Morphism (n, t, s)
        else Morphism (n ^ "^op", t, s)

      val op_morphisms = List.map op_mor morphisms
      val op_identities = List.map (fn (o_name, m) => (o_name, op_mor m)) identities
      val op_compositions = List.map (fn ((g, f), gf) => ((op_mor f, op_mor g), op_mor gf)) compositions
    in
      Cat {
        name = name ^ "^op",
        objects = objects,
        morphisms = op_morphisms,
        identities = op_identities,
        compositions = op_compositions
      }
    end

  (* Representable presheaf h_A : C^op -> Set *)
  (* For object X in C, h_A(X) = Hom_C(X, A) *)
  fun representable_obj cat a x = hom cat (x, a)

  (* Pre-composition: for f: Y -> X in C (f^op: X -> Y in C^op), and g in Hom_C(X, A), g o f in Hom_C(Y, A) *)
  fun representable_mor cat a (f_c, g) =
    compose cat (g, f_c)

  (* Yoneda Evaluation Phi(alpha) = alpha_A(id_A) *)
  fun yoneda_eval (alpha_A : morphism -> morphism) (cat : category) (a : string) : morphism =
    let
      val id_a = find_id cat a
    in
      alpha_A id_a
    end

  (* Natural Transformation representation *)
  datatype nat_trans =
    NatTrans of {
      name : string,
      components : (string * (morphism -> morphism)) list
    }

  (* Induced natural transformation h_f : h_A => h_B for f: A -> B *)
  (* Component at X: (h_f)_X(g) = f o g *)
  fun make_yoneda_morphism cat (f : morphism) =
    let
      val a = mor_src f
      val b = mor_tgt f
      fun comp_at x (g : morphism) =
        compose cat (f, g)
    in
      comp_at
    end

  (* Adjunction triangle identities check *)
  fun verify_triangle_identities
        (cat_c : category)
        (cat_d : category)
        (f_obj : string -> string)
        (f_mor : morphism -> morphism)
        (g_obj : string -> string)
        (g_mor : morphism -> morphism)
        (eta : string -> morphism)       (* eta_X : X -> G(F(X)) *)
        (epsilon : string -> morphism)   (* eps_Y : F(G(Y)) -> Y *)
        =
    let
      val Cat {objects = c_objs, ...} = cat_c
      val Cat {objects = d_objs, ...} = cat_d

      (* Triangle 1: eps_{F(X)} o F(eta_X) = id_{F(X)} in D *)
      val t1_ok = List.all (fn x =>
        let
          val fx = f_obj x
          val eta_x = eta x
          val f_eta_x = f_mor eta_x
          val eps_fx = epsilon fx
          val comp1 = compose cat_d (eps_fx, f_eta_x)
          val id_fx = find_id cat_d fx
        in
          mor_eq (comp1, id_fx)
        end) c_objs

      (* Triangle 2: G(eps_Y) o eta_{G(Y)} = id_{G(Y)} in C *)
      val t2_ok = List.all (fn y =>
        let
          val gy = g_obj y
          val eps_y = epsilon y
          val g_eps_y = g_mor eps_y
          val eta_gy = eta gy
          val comp2 = compose cat_c (g_eps_y, eta_gy)
          val id_gy = find_id cat_c gy
        in
          mor_eq (comp2, id_gy)
        end) d_objs
    in
      t1_ok andalso t2_ok
    end

end;
