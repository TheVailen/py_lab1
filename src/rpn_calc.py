from __future__ import annotations
import math
import re
from typing import Any, List
from src.constants import BUILTIN_FUNCTIONS
from src.constants import ALLOWED_OPERATORS



class CalculatorError(Exception):
    """Общее исключение, выбрасываемое калькулятором при ошибках."""
    pass


_NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")
_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _call_builtin(name: str, args: List[Any]) -> Any:
    """Вызов встроенной функции."""
    if name not in BUILTIN_FUNCTIONS:
        raise CalculatorError(f"Неизвестная функция: {name!r}")
    min_args, max_args = BUILTIN_FUNCTIONS[name]
    if not (min_args <= len(args) <= max_args):
        raise CalculatorError(
            f"Функция {name} ожидает от {min_args} до {max_args} аргументов; получено {len(args)}."
        )
    try:
        if name == "abs":
            return abs(args[0])
        if name == "sqrt":
            return math.sqrt(args[0])
        if name == "pow":
            return pow(args[0], args[1])
        if name == "max":
            return max(args)
        if name == "min":
            return min(args)
    except Exception as exc:
        raise CalculatorError(f"Ошибка при выполнении {name}: {exc}") from exc


def _apply_operator(a: Any, b: Any, op: str) -> Any:
    """Выполнение бинарных операций."""
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            raise CalculatorError("Деление на ноль")
        return a / b
    if op == "//":
        if not isinstance(a, int) or not isinstance(b, int):
            raise CalculatorError("// требует целых операндов")
        if b == 0:
            raise CalculatorError("Деление на ноль")
        return a // b
    if op == "%":
        if not isinstance(a, int) or not isinstance(b, int):
            raise CalculatorError("% требует целых операндов")
        if b == 0:
            raise CalculatorError("Деление на ноль")
        return a % b
    if op == "**":
        return a ** b
    raise CalculatorError(f"Неизвестный оператор: {op!r}")


def evaluate_rpn_input(rpn_expression: str) -> Any:
    """Вычисляет выражение, записанное в обратной польской нотации (RPN)."""
    try:
        if not isinstance(rpn_expression, str):
            raise CalculatorError("Входное выражение должно быть строкой.")

        text = rpn_expression.strip()
        if not (text.startswith("(") and text.endswith(")")):
            raise CalculatorError("Выражение должно быть заключено в круглые скобки.")

        text = text[1:-1].strip()
        parts = text.split()
        stack: List[Any] = []

        for part in parts:
            if _NUMBER_RE.fullmatch(part):
                value = float(part) if "." in part else int(part)
                stack.append(value)
                continue

            if part in ("u+", "u-"):
                a = stack.pop()
                stack.append(+a if part == "u+" else -a)
                continue

            if part in ALLOWED_OPERATORS:
                b = stack.pop()
                a = stack.pop()
                stack.append(_apply_operator(a, b, part))
                continue

            if part in BUILTIN_FUNCTIONS:
                num_args = BUILTIN_FUNCTIONS[part][1]
                if len(stack) < num_args:
                    raise CalculatorError(f"Недостаточно аргументов для функции {part!r}.")
                args = [stack.pop() for _ in range(num_args)][::-1]
                stack.append(_call_builtin(part, args))
                continue

            raise CalculatorError(f"Неизвестный токен: {part!r}")

        if len(stack) != 1:
            raise CalculatorError("Неправильное выражение: стек не свёлся к одному значению.")

        return stack[0]

    except IndexError:
        raise CalculatorError("Недостаточно операндов для операции.")
    except ZeroDivisionError:
        raise CalculatorError("Деление на ноль.")
    except CalculatorError:
        raise
    except Exception as exc:
        raise CalculatorError(f"Ошибка вычисления: {exc}")
