from src.rpn_calc import evaluate_rpn_input, CalculatorError
import sys
import pathlib
import pytest  # type: ignore
repo_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))


def test_basic_operations() -> None:
    assert evaluate_rpn_input("3 4 2 * +") == 11
    assert evaluate_rpn_input("5 1 2 + 4 * + 3 -") == 14


def test_functions_and_unary() -> None:
    assert evaluate_rpn_input("2 3 pow") == 8
    assert evaluate_rpn_input("1 5 3 max3") == 5
    assert evaluate_rpn_input("9 sqrt") == 3.0
    assert evaluate_rpn_input("5 u-") == -5


def test_int_operations() -> None:
    assert evaluate_rpn_input("7 2 //") == 3
    assert evaluate_rpn_input("10 3 %") == 1


def test_division_by_zero() -> None:
    for expr in ["5 0 /", "5 0 //", "5 0 %"]:
        with pytest.raises(CalculatorError):
            evaluate_rpn_input(expr)


def test_not_enough_operands() -> None:
    for expr in ["2 +", "sqrt"]:
        with pytest.raises(CalculatorError):
            evaluate_rpn_input(expr)


def test_extra_elements() -> None:
    with pytest.raises(CalculatorError):
        evaluate_rpn_input("1 2")


def test_unknown_tokens() -> None:
    for expr in ["abc", "?"]:
        with pytest.raises(CalculatorError):
            evaluate_rpn_input(expr)


def test_wrong_number_args() -> None:
    for expr in ["1 max0", "1 2 min10000"]:
        with pytest.raises(CalculatorError):
            evaluate_rpn_input(expr)


def test_invalid_types_for_int_ops() -> None:
    for expr in ["7.5 2 //", "7.5 2 %"]:
        with pytest.raises(CalculatorError):
            evaluate_rpn_input(expr)
