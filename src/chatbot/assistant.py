import os
from pathlib import Path
from dotenv import load_dotenv  # Добавляем загрузку .env

# Загружаем переменные окружения из файла .env
load_dotenv()

from .knowledge_base import KnowledgeBase

DEFAULT_FAQ = Path(__file__).resolve().parent.parent / "data" / "faq.json"

SYSTEM_PROMPT = (
    "Ты — вежливый ассистент Московского финансово-промышленного университета "
    "«Синергия». Отвечай кратко, по делу, опираясь ТОЛЬКО на предоставленный "
    "контекст. Если в контексте нет ответа — попроси уточнить у приёмной комиссии "
    "(8 800 100-00-11) или через личный кабинет."
)


class SynergyAssistant:
    def __init__(self, faq_path: str | Path = DEFAULT_FAQ, top_k: int = 3):
        self.kb = KnowledgeBase(faq_path)
        self.top_k = top_k

        # Пытаемся подключить GigaChat
        self.gigachat_credentials = os.getenv("GIGACHAT_CREDENTIALS")
        self._client = None

        if self.gigachat_credentials:
            try:
                from gigachat import GigaChat
                # verify_ssl_certs=False нужен только если на компьютере нет сертификатов Минцифры
                self._client = GigaChat(credentials=self.gigachat_credentials, verify_ssl_certs=False)
            except ImportError:
                print("Библиотека gigachat не установлена.")
            except Exception as e:
                print(f"Ошибка инициализации GigaChat: {e}")

    @property
    def llm_enabled(self) -> bool:
        return self._client is not None

    def answer(self, question: str, use_llm: bool | None = None) -> dict:
        candidates = self.kb.search(question, top_k=self.top_k)
        best = candidates[0] if candidates else None

        if use_llm is None:
            use_llm = self.llm_enabled

        if use_llm and self._client and candidates:
            context = "\n\n".join(
                f"Вопрос: {c['question']}\nОтвет: {c['answer']}"
                for c in candidates
            )
            prompt = f"Контекст:\n{context}\n\nВопрос: {question}"
            try:
                # Запрос к GigaChat
                response = self._client.chat(prompt)
                answer_text = response.choices[0].message.content

                return {
                    "answer": answer_text,
                    "source": "gigachat+rag",
                    "confidence": best["score"] if best else 0.0,
                    "retrieved": candidates,
                }
            except Exception as e:
                print(f"Ошибка при запросе к GigaChat: {e}")
                pass  # Если ошибка - идем в фолбэк

        # Фолбэк на локальную базу знаний (если LLM выключен или упал)
        if best:
            return {
                "answer": best["answer"],
                "source": "faq",
                "confidence": best["score"],
                "retrieved": candidates,
            }
        return {
            "answer": ("К сожалению, точного ответа не нашлось. "
                       "Пожалуйста, свяжитесь с приёмной комиссией: "
                       "8 (800) 100-00-11 или через личный кабинет."),
            "source": "fallback",
            "confidence": 0.0,
            "retrieved": [],
        }