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


def _find_matching_parenthesis(expression: str, start: int) -> int:
    """Находит позицию закрывающей скобки для открывающей на позиции start."""
    depth = 1
    pos = start + 1
    while pos < len(expression) and depth > 0:
        if expression[pos] == '(':
            depth += 1
        elif expression[pos] == ')':
            depth -= 1
        pos += 1
    if depth == 0:
        return pos - 1
    raise CalculatorError("Несбалансированные скобки")


def _tokenize_expression(expression: str) -> List[str]:
    """Разбивает выражение на токены, сохраняя вложенные выражения."""
    tokens = []
    i = 0
    length = len(expression)

    while i < length:
        char = expression[i]

        if char.isspace():
            i += 1
            continue

        # Если встретили '(', ищем соответствующую ')'
        if char == '(':
            end = _find_matching_parenthesis(expression, i)
            tokens.append(expression[i:end + 1])
            i = end + 1
            continue

        if char.isdigit() or (char == '-' and i + 1 < length and expression[i + 1].isdigit()):
            start = i
            i += 1
            while i < length and (expression[i].isdigit() or expression[i] == '.'):
                i += 1
            tokens.append(expression[start:i])
            continue

        if char in ALLOWED_OPERATORS or char.isalpha():
            start = i
            i += 1
            while i < length and (expression[i] in ALLOWED_OPERATORS or
                                 expression[i].isalnum() or expression[i] == '_'):
                i += 1
            tokens.append(expression[start:i])
            continue

        # Унарные символы ($ — унарный плюс, ~ — унарный минус)
        if char in ('$', '~'):
            tokens.append(char)
            i += 1
            continue

        raise CalculatorError(f"Неизвестный символ: {char!r}")

    return tokens


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


def _evaluate_tokens(tokens: List[str]) -> Any:
    """Рекурсивно вычисляет выражение из токенов."""
    stack: List[Any] = []

    for token in tokens:
        # Вложенное выражение — рекурсивный вызов evaluate_rpn_input()
        if token.startswith('(') and token.endswith(')'):
            result = evaluate_rpn_input(token)
            stack.append(result)
            continue

        if _NUMBER_RE.fullmatch(token):
            value = float(token) if "." in token else int(token)
            stack.append(value)
            continue

        if token in ("$", "~"):
            if not stack:
                raise CalculatorError("Недостаточно операндов для унарной операции")
            a = stack.pop()
            stack.append(+a if token == "$" else -a)
            continue

        if token in ALLOWED_OPERATORS:
            if len(stack) < 2:
                raise CalculatorError(f"Недостаточно операндов для оператора {token}")
            b = stack.pop()
            a = stack.pop()
            stack.append(_apply_operator(a, b, token))
            continue

        if token in BUILTIN_FUNCTIONS:
            min_args, max_args = BUILTIN_FUNCTIONS[token]

            if max_args > min_args:
                if len(stack) < min_args:
                    raise CalculatorError(f"Недостаточно аргументов для функции {token!r}")
                num_args = min(len(stack), max_args)
            else:
                if len(stack) < min_args:
                    raise CalculatorError(f"Недостаточно аргументов для функции {token!r}")
                num_args = min_args

            args = [stack.pop() for _ in range(num_args)][::-1]
            stack.append(_call_builtin(token, args))
            continue

        raise CalculatorError(f"Неизвестный токен: {token!r}")

    # После вычисления в стеке должно остаться ровно одно значение
    if len(stack) != 1:
        raise CalculatorError("Неправильное выражение: стек не свёлся к одному значению")

    return stack[0]


def evaluate_rpn_input(rpn_expression: str) -> Any:
    """Вычисляет выражение, записанное в обратной польской нотации (RPN)."""
    try:
        if not isinstance(rpn_expression, str):
            raise CalculatorError("Входное выражение должно быть строкой.")

        text = rpn_expression.strip()

        # Автоматически добавляем внешние скобки если их нет
        if not (text.startswith("(") and text.endswith(")")):
            text = f"({text})"

        # Извлекаем содержимое скобок и токенизируем
        inner_text = text[1:-1].strip()
        tokens = _tokenize_expression(inner_text)

        return _evaluate_tokens(tokens)

    except IndexError:
        raise CalculatorError("Недостаточно операндов для операции")
    except ZeroDivisionError:
        raise CalculatorError("Деление на ноль")
    except CalculatorError:
        raise
    except Exception as exc:
        raise CalculatorError(f"Ошибка вычисления: {exc}")
