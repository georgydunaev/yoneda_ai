(* File: tests/test_quantifiers.ml
 * Automated test suite for SML Quantifiers and Definite Description calculus.
 *)

use "/botworkspace/yoneda_ai/src/quantifiers.ml";

structure TestQuantifiers =
struct
  open Quantifiers

  fun assert_true msg b =
    if b then ()
    else (print ("FAILED: " ^ msg ^ "\n"); OS.Process.exit OS.Process.failure)

  val sample_model : model = {
    domain = ["0", "1", "2"],
    rel_interp = fn ("Even", [x]) => (x = "0" orelse x = "2")
                  | ("Odd", [x]) => (x = "1")
                  | ("Zero", [x]) => (x = "0")
                  | _ => false,
    fun_interp = fn ("succ", ["0"]) => "1"
                  | ("succ", ["1"]) => "2"
                  | ("succ", ["2"]) => "0"
                  | _ => "0",
    default_const = "0"
  }

  fun run_all () =
    let
      val _ = print "Running Quantifiers SML tests...\n"

      (* Test 1: Even elements exist *)
      val phi1 = Exists ("x", Atom ("Even", [Var "x"]))
      val _ = assert_true "Exists Even" (eval_form sample_model [] phi1)

      (* Test 2: Odd element is unique *)
      val phi2 = ExistsUnique ("x", Atom ("Odd", [Var "x"]))
      val _ = assert_true "ExistsUnique Odd" (eval_form sample_model [] phi2)

      (* Test 3: Zero is unique *)
      val phi3 = Unique ("x", Atom ("Zero", [Var "x"]))
      val _ = assert_true "Unique Zero" (eval_form sample_model [] phi3)

      (* Test 4: Definite description The x. Odd(x) evaluates to "1" *)
      val t1 = The ("x", Atom ("Odd", [Var "x"]))
      val _ = assert_true "The x. Odd(x) == 1" (eval_term sample_model [] t1 = "1")

      (* Test 5: Definite description on non-unique predicate returns default_const "0" *)
      val t2 = The ("x", Atom ("Even", [Var "x"]))
      val _ = assert_true "The x. Even(x) == default 0" (eval_term sample_model [] t2 = "0")

      (* Test 6: Quantifier expansion of ExistsUnique matches eval *)
      val phi_eu = expand_exists_unique "x" (Atom ("Odd", [Var "x"]))
      val _ = assert_true "expand_exists_unique preserves semantics"
                (eval_form sample_model [] phi_eu = eval_form sample_model [] phi2)

      (* Test 7: Quantifier expansion of Unique matches eval *)
      val phi_u = expand_unique "x" (Atom ("Zero", [Var "x"]))
      val _ = assert_true "expand_unique preserves semantics"
                (eval_form sample_model [] phi_u = eval_form sample_model [] phi3)

      val _ = print "All Quantifiers SML tests passed successfully!\n"
    in
      ()
    end
end;

val _ = TestQuantifiers.run_all ();
val _ = OS.Process.exit OS.Process.success;
