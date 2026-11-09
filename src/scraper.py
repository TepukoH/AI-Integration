# src/scraper.py
import asyncio
import csv
import re
from pathlib import Path
from playwright.async_api import async_playwright

SYNERGY_REVIEWS_URL = "https://yandex.ru/maps/org/universitet_sinergiya/1086906378/reviews/"


async def _scrape_yandex_reviews_async():
    """Внутренняя асинхронная функция для сбора отзывов."""
    reviews_data = []
    seen_texts = set()

    async with async_playwright() as p:
        # headless=True означает, что окно браузера не будет открываться на экране
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="ru-RU",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            await page.goto(SYNERGY_REVIEWS_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_selector('[class*="business-review-view"]', timeout=15000)

            # Прокрутка страницы для подгрузки
            for _ in range(3):
                await page.mouse.wheel(0, 3000)
                await page.wait_for_timeout(1000)

            review_elements = await page.query_selector_all('[class*="business-review-view"]')

            for element in review_elements:
                text = ""
                for selector in ['.business-review-view__body-text', '[class*="body-text"]', '[itemprop="reviewBody"]']:
                    text_element = await element.query_selector(selector)
                    if text_element:
                        text = await text_element.inner_text()
                        break

                text = re.sub(r'\s+', ' ', text).strip()

                if text and text not in seen_texts:
                    seen_texts.add(text)
                    reviews_data.append(text)
        except Exception as e:
            print(f"⚠️ Ошибка при парсинге: {e}")
        finally:
            await browser.close()

    return reviews_data


def update_feedback_csv(csv_path: Path) -> bool:
    """
    Собирает отзывы и сохраняет их в CSV.
    Возвращает True, если данные были обновлены, и False, если произошла ошибка.
    """
    print("\n--- Запуск автоматического сбора свежих отзывов с Яндекс.Карт ---")
    reviews = asyncio.run(_scrape_yandex_reviews_async())

    if reviews:
        # Убедимся, что папка существует
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'text'])
            for idx, review_text in enumerate(reviews, start=1):
                writer.writerow([idx, review_text])
        print(f"✅ Успешно собрано и сохранено {len(reviews)} уникальных отзывов в {csv_path.name}.")
        return True
    else:
        print("ℹ️ Не удалось собрать новые отзывы (возможно, капча или нет интернета).")
        return False