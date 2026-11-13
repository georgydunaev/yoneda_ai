"""
Unified Test Runner for yoneda_ai.
Runs all Python unittests and SML tests.
"""

import sys
import os
import unittest
import subprocess


def run_python_tests() -> bool:
    print("Running Python test suite...")
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), "tests")
    suite = loader.discover(start_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_sml_tests() -> bool:
    print("Running SML test suite...")
    test_files = [
        os.path.join(os.path.dirname(__file__), "tests", "test_quantifiers.ml")
    ]
    sml_cat = os.path.join(os.path.dirname(__file__), "tests", "test_category.ml")
    if os.path.exists(sml_cat):
        test_files.append(sml_cat)

    all_passed = True
    for tf in test_files:
        print(f"Testing {os.path.basename(tf)} with Poly/ML...")
        res = subprocess.run(["poly", "-q", "--use", tf], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"FAILED: {tf}\n{res.stderr}\n{res.stdout}")
            all_passed = False
        else:
            print(res.stdout.strip())
    return all_passed


def main():
    py_ok = run_python_tests()
    sml_ok = run_sml_tests()

    if py_ok and sml_ok:
        print("\nAll yoneda_ai verification suites passed successfully.")
        sys.exit(0)
    else:
        print("\nTest failures detected in yoneda_ai verification suites.")
        sys.exit(1)


if __name__ == "__main__":
    main()
