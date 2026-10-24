import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return " ".join(text.split())


def evaluate_answer(question_data, user_answer):
    reference_answer = question_data["answer"]
    keywords = question_data["keywords"]

    user_answer = normalize(user_answer)
    reference_answer = normalize(reference_answer)

    if not user_answer.strip():
        return {
            "score": 0,
            "similarity": 0,
            "coverage": 0,
            "toc_score": 0,
            "found": [],
            "missing": keywords
        }

    try:
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(
            [user_answer, reference_answer]
        )
        similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
    except ValueError:
        similarity = 0

    found = [
        keyword for keyword in keywords
        if normalize(keyword) in user_answer
    ]

    missing = [
        keyword for keyword in keywords
        if keyword not in found
    ]

    coverage = len(found) / len(keywords) if keywords else 0

    if len(found) == 0:
        toc_score = 0
    elif len(found) == len(keywords):
        toc_score = 1
    else:
        toc_score = 0.5

    score = (
        similarity * 50
        + coverage * 30
        + toc_score * 20
    )

    return {
        "score": round(score, 2),
        "similarity": round(similarity * 100, 2),
        "coverage": round(coverage * 100, 2),
        "toc_score": round(toc_score * 100, 2),
        "found": found,
        "missing": missing
    }