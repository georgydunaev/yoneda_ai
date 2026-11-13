(* File: src/quantifiers.ml
 * Formalization of First-Order Terms, Formulas, Quantifiers, and Definite Descriptions in Standard ML.
 * Compatible with Poly/ML and CakeML.
 *)

structure Quantifiers =
struct

  datatype term =
      Var of string
    | Const of string
    | App of string * term list
    | The of string * form (* Definite description: The x. P(x) *)

  and form =
      True
    | False
    | Atom of string * term list
    | Eq of term * term
    | Not of form
    | And of form * form
    | Or of form * form
    | Imp of form * form
    | Iff of form * form
    | Forall of string * form
    | Exists of string * form
    | ExistsUnique of string * form
    | Unique of string * form

  (* Fresh variable generation *)
  local
    val counter = ref 0
  in
    fun reset_fresh () = counter := 0
    fun fresh_var base =
      let
        val n = !counter
        val _ = counter := n + 1
      in
        base ^ "_" ^ Int.toString n
      end
  end

  (* Free variables *)
  fun fv_term (Var x) = [x]
    | fv_term (Const _) = []
    | fv_term (App (_, ts)) = List.concat (List.map fv_term ts)
    | fv_term (The (x, p)) = List.filter (fn y => y <> x) (fv_form p)

  and fv_form True = []
    | fv_form False = []
    | fv_form (Atom (_, ts)) = List.concat (List.map fv_term ts)
    | fv_form (Eq (t1, t2)) = fv_term t1 @ fv_term t2
    | fv_form (Not p) = fv_form p
    | fv_form (And (p, q)) = fv_form p @ fv_form q
    | fv_form (Or (p, q)) = fv_form p @ fv_form q
    | fv_form (Imp (p, q)) = fv_form p @ fv_form q
    | fv_form (Iff (p, q)) = fv_form p @ fv_form q
    | fv_form (Forall (x, p)) = List.filter (fn y => y <> x) (fv_form p)
    | fv_form (Exists (x, p)) = List.filter (fn y => y <> x) (fv_form p)
    | fv_form (ExistsUnique (x, p)) = List.filter (fn y => y <> x) (fv_form p)
    | fv_form (Unique (x, p)) = List.filter (fn y => y <> x) (fv_form p)

  (* Capture-avoiding substitution t[s/x] *)
  fun subst_term s x (Var y) = if x = y then s else Var y
    | subst_term _ _ (Const c) = Const c
    | subst_term s x (App (f, ts)) = App (f, List.map (subst_term s x) ts)
    | subst_term s x (The (y, p)) =
        if x = y then The (y, p)
        else
          let
            val fvs = fv_term s
          in
            if List.exists (fn v => v = y) fvs then
              let
                val y' = fresh_var y
                val p' = subst_form (Var y') y p
              in
                The (y', subst_form s x p')
              end
            else
              The (y, subst_form s x p)
          end

  and subst_form s x True = True
    | subst_form s x False = False
    | subst_form s x (Atom (r, ts)) = Atom (r, List.map (subst_term s x) ts)
    | subst_form s x (Eq (t1, t2)) = Eq (subst_term s x t1, subst_term s x t2)
    | subst_form s x (Not p) = Not (subst_form s x p)
    | subst_form s x (And (p, q)) = And (subst_form s x p, subst_form s x q)
    | subst_form s x (Or (p, q)) = Or (subst_form s x p, subst_form s x q)
    | subst_form s x (Imp (p, q)) = Imp (subst_form s x p, subst_form s x q)
    | subst_form s x (Iff (p, q)) = Iff (subst_form s x p, subst_form s x q)
    | subst_form s x (Forall (y, p)) =
        if x = y then Forall (y, p)
        else
          let
            val fvs = fv_term s
          in
            if List.exists (fn v => v = y) fvs then
              let
                val y' = fresh_var y
                val p' = subst_form (Var y') y p
              in
                Forall (y', subst_form s x p')
              end
            else
              Forall (y, subst_form s x p)
          end
    | subst_form s x (Exists (y, p)) =
        if x = y then Exists (y, p)
        else
          let
            val fvs = fv_term s
          in
            if List.exists (fn v => v = y) fvs then
              let
                val y' = fresh_var y
                val p' = subst_form (Var y') y p
              in
                Exists (y', subst_form s x p')
              end
            else
              Exists (y, subst_form s x p)
          end
    | subst_form s x (ExistsUnique (y, p)) =
        if x = y then ExistsUnique (y, p)
        else
          let
            val fvs = fv_term s
          in
            if List.exists (fn v => v = y) fvs then
              let
                val y' = fresh_var y
                val p' = subst_form (Var y') y p
              in
                ExistsUnique (y', subst_form s x p')
              end
            else
              ExistsUnique (y, subst_form s x p)
          end
    | subst_form s x (Unique (y, p)) =
        if x = y then Unique (y, p)
        else
          let
            val fvs = fv_term s
          in
            if List.exists (fn v => v = y) fvs then
              let
                val y' = fresh_var y
                val p' = subst_form (Var y') y p
              in
                Unique (y', subst_form s x p')
              end
            else
              Unique (y, subst_form s x p)
          end

  (* Quantifier expansion definitions *)
  (* !x. P(x) <=> forall y. forall z. (P(y) /\ P(z) ==> y = z) *)
  fun expand_unique x p =
    let
      val y = fresh_var "y"
      val z = fresh_var "z"
      val py = subst_form (Var y) x p
      val pz = subst_form (Var z) x p
    in
      Forall (y, Forall (z, Imp (And (py, pz), Eq (Var y, Var z))))
    end

  (* exists! x. P(x) <=> exists x. (P(x) /\ forall y. (P(y) ==> y = x)) *)
  fun expand_exists_unique x p =
    let
      val y = fresh_var "y"
      val py = subst_form (Var y) x p
    in
      Exists (x, And (p, Forall (y, Imp (py, Eq (Var y, Var x)))))
    end

  (* Dual quantifier ?x1, x2. P <=> exists x1. exists x2. (~P(x1) /\ ~P(x2) /\ x1 <> x2) *)
  fun make_dual_quantifier x1 x2 p =
    let
      val px1 = subst_form (Var x1) "x" p
      val px2 = subst_form (Var x2) "x" p
    in
      Exists (x1, Exists (x2, And (Not px1, And (Not px2, Not (Eq (Var x1, Var x2))))))
    end

  (* String representation *)
  fun term_to_string (Var x) = x
    | term_to_string (Const c) = c
    | term_to_string (App (f, [])) = f
    | term_to_string (App (f, ts)) = f ^ "(" ^ String.concatWith ", " (List.map term_to_string ts) ^ ")"
    | term_to_string (The (x, p)) = "(The " ^ x ^ ". " ^ form_to_string p ^ ")"

  and form_to_string True = "True"
    | form_to_string False = "False"
    | form_to_string (Atom (r, [])) = r
    | form_to_string (Atom (r, ts)) = r ^ "(" ^ String.concatWith ", " (List.map term_to_string ts) ^ ")"
    | form_to_string (Eq (t1, t2)) = "(" ^ term_to_string t1 ^ " = " ^ term_to_string t2 ^ ")"
    | form_to_string (Not p) = "(~ " ^ form_to_string p ^ ")"
    | form_to_string (And (p, q)) = "(" ^ form_to_string p ^ " /\\ " ^ form_to_string q ^ ")"
    | form_to_string (Or (p, q)) = "(" ^ form_to_string p ^ " \\/ " ^ form_to_string q ^ ")"
    | form_to_string (Imp (p, q)) = "(" ^ form_to_string p ^ " ==> " ^ form_to_string q ^ ")"
    | form_to_string (Iff (p, q)) = "(" ^ form_to_string p ^ " <=> " ^ form_to_string q ^ ")"
    | form_to_string (Forall (x, p)) = "(forall " ^ x ^ ". " ^ form_to_string p ^ ")"
    | form_to_string (Exists (x, p)) = "(exists " ^ x ^ ". " ^ form_to_string p ^ ")"
    | form_to_string (ExistsUnique (x, p)) = "(exists! " ^ x ^ ". " ^ form_to_string p ^ ")"
    | form_to_string (Unique (x, p)) = "(! " ^ x ^ ". " ^ form_to_string p ^ ")"

  (* Finite interpretation evaluation *)
  type domain = string list
  type env = (string * string) list
  type model = {
    domain : domain,
    rel_interp : string * string list -> bool,
    fun_interp : string * string list -> string,
    default_const : string
  }

  fun eval_term (m : model) (env : env) (Var x) =
        (case List.find (fn (v, _) => v = x) env of
           SOME (_, val_) => val_
         | NONE => x)
    | eval_term m env (Const c) = c
    | eval_term (m as {fun_interp, ...}) env (App (f, ts)) =
        let val args = List.map (eval_term m env) ts
        in fun_interp (f, args) end
    | eval_term (m as {domain, default_const, ...}) env (The (x, p)) =
        let
          val satisfying = List.filter (fn d => eval_form m ((x, d) :: env) p) domain
        in
          case satisfying of
            [unique_elem] => unique_elem
          | _ => default_const (* NBG default empty set convention *)
        end

  and eval_form (m as {domain, ...}) (env : env) True = true
    | eval_form m env False = false
    | eval_form (m as {rel_interp, ...}) env (Atom (r, ts)) =
        rel_interp (r, List.map (eval_term m env) ts)
    | eval_form m env (Eq (t1, t2)) =
        (eval_term m env t1 = eval_term m env t2)
    | eval_form m env (Not p) = not (eval_form m env p)
    | eval_form m env (And (p, q)) = eval_form m env p andalso eval_form m env q
    | eval_form m env (Or (p, q)) = eval_form m env p orelse eval_form m env q
    | eval_form m env (Imp (p, q)) = (not (eval_form m env p)) orelse eval_form m env q
    | eval_form m env (Iff (p, q)) = (eval_form m env p = eval_form m env q)
    | eval_form (m as {domain, ...}) env (Forall (x, p)) =
        List.all (fn d => eval_form m ((x, d) :: env) p) domain
    | eval_form (m as {domain, ...}) env (Exists (x, p)) =
        List.exists (fn d => eval_form m ((x, d) :: env) p) domain
    | eval_form (m as {domain, ...}) env (ExistsUnique (x, p)) =
        let
          val count = List.length (List.filter (fn d => eval_form m ((x, d) :: env) p) domain)
        in
          count = 1
        end
    | eval_form (m as {domain, ...}) env (Unique (x, p)) =
        let
          val count = List.length (List.filter (fn d => eval_form m ((x, d) :: env) p) domain)
        in
          count <= 1
        end

end;
