"""Демонстрация всех трёх модулей проекта."""
import json
from pathlib import Path

import pandas as pd

from src.chatbot.assistant import SynergyAssistant
from src.feedback_analysis.report import build_report, report_to_markdown
from src.integration.directum_client import DirectumClient
from src.integration.lms_client import LMSClient, StudentProgress

ROOT = Path(__file__).resolve().parent


def demo_chatbot():
    print("\n=== 1. ИИ-ассистент приёмной комиссии / поддержки ===")
    bot = SynergyAssistant()
    print(f"LLM-режим: {'вкл' if bot.llm_enabled else 'выкл (FAQ-фолбэк)'}")
    for q in [
        "Как поступить в Синергию?",
        "Где посмотреть расписание?",
        "Как восстановить пароль от личного кабинета?",
        "Сколько стоит обучение?",
    ]:
        r = bot.answer(q)
        print(f"\nВопрос: {q}")
        print(f"[{r['source']}, conf={r['confidence']:.2f}] {r['answer']}")


def demo_feedback():
    print("\n=== 2. Анализ обратной связи ===")
    df = pd.read_csv(ROOT / "src" / "data" / "feedback_sample.csv")
    report = build_report(df)
    md = report_to_markdown(report)
    print(md)
    out = ROOT / "feedback_report.md"
    out.write_text(md, encoding="utf-8")
    print(f"\nОтчёт сохранён: {out}")


def demo_integration():
    print("\n=== 3. Мок-интеграции Directum RX и LMS ===")
    drx = DirectumClient()
    t = drx.create_ticket("Не приходит письмо для сброса пароля",
                          "Студент не может войти в ЛК")
    print(f"Создан тикет Directum RX: {t}")

    lms = LMSClient()
    lms.upsert(StudentProgress("S-001", "Python", 72, 2))
    lms.upsert(StudentProgress("S-002", "Python", 18, 21))
    lms.upsert(StudentProgress("S-003", "Python", 5, 30))
    risk = lms.at_risk()
    print("Студенты в зоне риска:")
    for p in risk:
        print(f"  - {p.student_id}: прогресс {p.progress_pct}%, "
              f"последняя активность {p.last_active_days} дн. назад")


if __name__ == "__main__":
    demo_chatbot()
    demo_feedback()
    demo_integration()
    print("\nГотово. Все артефакты можно коммитить в GitHub.")