import re
from dataclasses import dataclass, field

POSITIVE = {
    "отлично": 1.0, "хорошо": 0.8, "супер": 1.0, "замечательно": 1.0,
    "прекрасно": 1.0, "понравилось": 0.9, "доволен": 0.9, "довольна": 0.9,
    "удобно": 0.8, "качественно": 0.8, "быстро": 0.7, "профессионально": 0.9,
    "рекомендую": 1.0, "спасибо": 0.7, "благодарю": 0.7, "класс": 0.9,
    "интересно": 0.7, "полезно": 0.8, "понятно": 0.6, "доступно": 0.6,
    "вежливо": 0.7, "помогли": 0.8, "отзывчивый": 0.8, "комфортно": 0.7,
}
NEGATIVE = {
    "плохо": -1.0, "ужасно": -1.0, "отвратительно": -1.0, "недоволен": -0.9,
    "недовольна": -0.9, "проблема": -0.7, "ошибка": -0.6, "долго": -0.7,
    "медленно": -0.7, "неудобно": -0.8, "непонятно": -0.7, "разочарован": -1.0,
    "разочарована": -1.0, "жалоба": -0.9, "грубо": -0.9, "хамство": -1.0,
    "задержка": -0.7, "сложно": -0.6, "запутанно": -0.7, "некачественно": -0.9,
}
NEGATIONS = {"не", "нет", "ни", "никогда"}
INTENSIFIERS = {"очень": 1.5, "крайне": 1.8, "слишком": 1.4, "совсем": 1.3}

TOKEN_RE = re.compile(r"[А-Яа-яЁёA-Za-z]+", re.UNICODE)


@dataclass
class SentimentResult:
    text: str
    score: float
    label: str
    positives: list = field(default_factory=list)
    negatives: list = field(default_factory=list)


def analyze(text: str) -> SentimentResult:
    tokens = [t.lower() for t in TOKEN_RE.findall(text or "")]
    score = 0.0
    hits_pos, hits_neg = [], []

    for i, tok in enumerate(tokens):
        base = POSITIVE.get(tok) or NEGATIVE.get(tok)
        if base is None:
            continue

        mult = 1.0
        for j in range(max(0, i - 2), i):
            if tokens[j] in INTENSIFIERS:
                mult *= INTENSIFIERS[tokens[j]]

        negated = any(tokens[j] in NEGATIONS for j in range(max(0, i - 2), i))

        val = base * mult
        if negated:
            val = -val

        score += val
        (hits_pos if val > 0 else hits_neg).append(tok)

    if score > 0.3:
        label = "positive"
    elif score < -0.3:
        label = "negative"
    else:
        label = "neutral"

    return SentimentResult(text=text, score=round(score, 3),
                           label=label, positives=hits_pos, negatives=hits_neg)


def batch_analyze(texts):
    return [analyze(t) for t in texts]