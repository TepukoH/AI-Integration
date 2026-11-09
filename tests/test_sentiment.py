from src.feedback_analysis.sentiment import analyze
from src.feedback_analysis.topics import detect_topic


def test_positive():
    assert analyze("Очень удобно, спасибо!").label == "positive"


def test_negative():
    assert analyze("Ужасно долго не отвечают, разочарован").label == "negative"


def test_topic():
    assert detect_topic("Не работает личный кабинет LMS") == "LMS / платформа"