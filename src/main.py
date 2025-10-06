from __future__ import annotations
import argparse
from src.rpn_calc import evaluate_rpn_input, CalculatorError


def _run_repl() -> None:
    """Интерактивный режим работы калькулятора."""
    print("RPN REPL. Введите выражение в обратной польской нотации. 'exit' для выхода.")
    while True:
        try:
            line = input("RPN> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line or line.lower() in ("exit", "quit"):
            break
        try:
            res = evaluate_rpn_input(line)
        except CalculatorError as exc:
            print("Ошибка:", exc)
        else:
            print("=", res)


def main() -> None:
    """Точка входа программы."""
    parser = argparse.ArgumentParser(description="Калькулятор в обратной польской нотации (M3)")
    parser.add_argument("--expr", "-e", help="Выражение в RPN для вычисления")
    args = parser.parse_args()
    if args.expr:
        try:
            print(evaluate_rpn_input(args.expr))
        except CalculatorError as exc:
            print("Ошибка:", exc)
    else:
        _run_repl()


if __name__ == "__main__":
    main()
