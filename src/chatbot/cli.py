import argparse
from .assistant import SynergyAssistant


def main():
    parser = argparse.ArgumentParser(description="Ассистент «Синергия»")
    parser.add_argument("-q", "--question", help="Вопрос одной строкой")
    parser.add_argument("--no-llm", action="store_true", help="Только FAQ (без LLM)")
    args = parser.parse_args()

    bot = SynergyAssistant()
    if args.question:
        r = bot.answer(args.question, use_llm=not args.no_llm)
        print(f"[{r['source']}, conf={r['confidence']:.2f}]")
        print(r["answer"])
        return

    print("Ассистент «Синергия». Пустая строка — выход.")
    print(f"LLM-режим: {'вкл' if bot.llm_enabled else 'выкл (используется FAQ)'}")
    while True:
        q = input("\nВы: ").strip()
        if not q:
            break
        r = bot.answer(q)
        print(f"Бот [{r['source']}, conf={r['confidence']:.2f}]: {r['answer']}")


if __name__ == "__main__":
    main()