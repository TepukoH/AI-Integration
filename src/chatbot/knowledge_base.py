import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class KnowledgeBase:
    """Поиск по FAQ вуза через TF-IDF + косинусную близость."""

    def __init__(self, faq_path: str | Path):
        self.faq_path = Path(faq_path)
        with self.faq_path.open(encoding="utf-8") as f:
            self.items = json.load(f)
        self.questions = [it["question"] for it in self.items]
        self.answers = [it["answer"] for it in self.items]
        self.tags = [it.get("tags", []) for it in self.items]

        self._vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            lowercase=True,
            token_pattern=r"(?u)\b\w+\b",
        )
        self._matrix = self._vectorizer.fit_transform(self.questions)

    def search(self, query: str, top_k: int = 3):
        if not query.strip():
            return []
        q_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self._matrix).flatten()
        order = np.argsort(sims)[::-1][:top_k]
        results = []
        for i in order:
            if sims[i] <= 0:
                continue
            results.append(
                {
                    "question": self.questions[i],
                    "answer": self.answers[i],
                    "tags": self.tags[i],
                    "score": float(sims[i]),
                }
            )
        return results