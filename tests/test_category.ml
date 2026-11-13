(*
  Automated SML Verification Suite for Category Theory and Yoneda Lemma.
*)

use "/botworkspace/yoneda_ai/src/category.ml";

structure TestCategory =
struct
  open CategoryTheory

  fun assert_true msg b =
    if b then ()
    else (print ("FAILED: " ^ msg ^ "\n"); OS.Process.exit OS.Process.failure)

  fun run_all () =
    let
      val _ = print "Running Category SML tests...\n"

      val id_A = Morphism ("id_A", "A", "A")
      val id_B = Morphism ("id_B", "B", "B")
      val id_C = Morphism ("id_C", "C", "C")
      val f = Morphism ("f", "A", "B")
      val g = Morphism ("g", "B", "C")
      val gf = Morphism ("gf", "A", "C")

      val cat = Cat {
        name = "ThreeCat",
        objects = ["A", "B", "C"],
        morphisms = [id_A, id_B, id_C, f, g, gf],
        identities = [("A", id_A), ("B", id_B), ("C", id_C)],
        compositions = [((g, f), gf)]
      }

      (* Test 1: hom sets *)
      val hom_ab = hom cat ("A", "B")
      val _ = assert_true "Hom(A, B) has f" (List.exists (fn m => mor_eq (m, f)) hom_ab)

      (* Test 2: composition *)
      val comp_gf = compose cat (g, f)
      val _ = assert_true "g o f == gf" (mor_eq (comp_gf, gf))

      (* Test 3: Yoneda evaluation *)
      val h_f = make_yoneda_morphism cat f
      val eval_res = yoneda_eval (h_f "A") cat "A"
      val _ = assert_true "Yoneda eval of h_f at id_A recovers f" (mor_eq (eval_res, f))

      (* Test 4: Opposite category *)
      val op_cat = opposite cat
      val Cat {name = op_name, ...} = op_cat
      val _ = assert_true "Opposite category name" (op_name = "ThreeCat^op")

      (* Test 5: Adjunction Triangle identities on identity adjunction *)
      val id_map = fn (s : string) => s
      val id_mor_map = fn (m : morphism) => m
      val eta = fn (s : string) => find_id cat s
      val epsilon = fn (s : string) => find_id cat s
      val adj_ok = verify_triangle_identities cat cat id_map id_mor_map id_map id_mor_map eta epsilon
      val _ = assert_true "Identity adjunction satisfies triangle identities" adj_ok

      val _ = print "All Category SML tests passed successfully!\n"
    in
      ()
    end
end;

val _ = TestCategory.run_all ();
val _ = OS.Process.exit OS.Process.success;
