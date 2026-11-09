from src.chatbot.assistant import SynergyAssistant


def test_faq_hit():
    bot = SynergyAssistant()
    r = bot.answer("как поступить?", use_llm=False)
    assert r["source"] in ("faq", "fallback")
    assert r["answer"]
    assert "поступ" in r["answer"].lower() or "приём" in r["answer"].lower()


def test_fallback():
    bot = SynergyAssistant()
    r = bot.answer("абракадабра-квхт", use_llm=False)
    assert r["source"] in ("faq", "fallback")