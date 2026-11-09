import pandas as pd

from .sentiment import analyze
from .topics import detect_topic


def build_report(df: pd.DataFrame, text_col: str = "text") -> dict:
    records = []
    for _, row in df.iterrows():
        s = analyze(row[text_col])
        records.append(
            {
                "text": row[text_col],
                "topic": detect_topic(row[text_col]),
                "sentiment": s.label,
                "score": s.score,
            }
        )
    res = pd.DataFrame(records)

    by_topic = (
        res.groupby("topic")
        .agg(
            count=("text", "count"),
            avg_score=("score", "mean"),
            negative_share=("sentiment", lambda x: (x == "negative").mean()),
        )
        .round(2)
        .reset_index()
        .sort_values("negative_share", ascending=False)
    )

    summary = {
        "total": len(res),
        "positive": int((res["sentiment"] == "positive").sum()),
        "neutral": int((res["sentiment"] == "neutral").sum()),
        "negative": int((res["sentiment"] == "negative").sum()),
    }
    return {"summary": summary, "by_topic": by_topic, "rows": res}


def report_to_markdown(report: dict) -> str:
    s = report["summary"]
    lines = [
        "# Отчёт по обратной связи",
        "",
        f"- Всего обращений: **{s['total']}**",
        f"- Позитивных: **{s['positive']}**",
        f"- Нейтральных: **{s['neutral']}**",
        f"- Негативных: **{s['negative']}**",
        "",
        "## По темам",
        "",
    ]
    df = report["by_topic"]
    lines.append("| Тема | Кол-во | Ср. балл | Доля негатива |")
    lines.append("|---|---|---|---|")
    for _, r in df.iterrows():
        lines.append(
            f"| {r['topic']} | {r['count']} | {r['avg_score']} | {r['negative_share']:.0%} |"
        )
    return "\n".join(lines)