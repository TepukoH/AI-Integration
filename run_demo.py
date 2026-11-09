from pathlib import Path
import pandas as pd

from src.scraper import update_feedback_csv
from src.chatbot.assistant import SynergyAssistant
from src.feedback_analysis.report import build_report, report_to_markdown
from src.integration.directum_client import DirectumClient
from src.integration.lms_client import LMSClient, StudentProgress

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "src" / "data" / "feedback_sample.csv"

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

    # 1. Пытаемся обновить данные (вызываем функцию из scraper.py)
    updated = update_feedback_csv(CSV_PATH)

    # 2. Если не удалось скачать новые, но есть старые — работаем со старыми
    if not updated and not CSV_PATH.exists():
        print("❌ Ошибка: Файл с отзывами отсутствует, и скачать новые не удалось.")
        return

    # 3. Читаем данные
    df = pd.read_csv(CSV_PATH)

    # Страховка от дубликатов
    initial_count = len(df)
    df = df.drop_duplicates(subset=['text'])
    if initial_count != len(df):
        print(f"Удалено дубликатов при чтении: {initial_count - len(df)}")

    # 4. Анализируем и сохраняем отчет
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
    # Загружаем данные из CSV файла
    csv_path = ROOT / "src" / "data" / "students_progress.csv"
    lms.load_from_csv(csv_path)

    # Ищем студентов в зоне риска
    risk = lms.at_risk()
    print(f"Загружены данные о студентах из {csv_path.name}.")
    print("Студенты в зоне риска (ИИ-мониторинг):")
    for p in risk:
        print(f"  - {p.student_id} ({p.course}): прогресс {p.progress_pct}%, "
              f"последняя активность {p.last_active_days} дн. назад")

if __name__ == "__main__":
    demo_chatbot()
    demo_feedback()
    demo_integration()
    print("\nГотово.")