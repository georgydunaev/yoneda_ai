# yoneda_ai — Automated Category Theory & Yoneda Lemma Proof Synthesis

## Overview
`yoneda_ai` houses LaTeX and ML developments for the Yoneda Lemma (`yoneda.tex`, `yoneda_lemma_2_4.tex`, `yoneda_agy_fixed.tex`), natural transformations (`definitions/natural_transformations.tex`), small limits (`sections/yoneda_agy_small_limits.tex`), and quantifier/limit verification tests (`src/quantifiers.ml`, `tests/test_limits.py`).

## Running Verification Tests
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
