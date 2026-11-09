from src.integration.lms_client import LMSClient, StudentProgress


def test_lms_at_risk_logic():
    lms = LMSClient()

    # Добавляем студентов
    lms.upsert(StudentProgress("S-001", "Python", 80, 2))  # Хорошист
    lms.upsert(StudentProgress("S-002", "Python", 15, 20))  # В зоне риска (низкий прогресс)
    lms.upsert(StudentProgress("S-003", "Python", 50, 30))  # В зоне риска (долго не заходил)

    # Получаем список отстающих
    risk = lms.at_risk()

    # Проверяем, что вернулись именно те, кто должен
    assert len(risk) == 2
    assert any(s.student_id == "S-002" for s in risk)
    assert any(s.student_id == "S-003" for s in risk)
    assert not any(s.student_id == "S-001" for s in risk)