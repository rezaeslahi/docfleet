from sklearn.feature_extraction.text import TfidfVectorizer


def make_vectorizer(max_features: int, ngram_min: int, ngram_max: int) -> TfidfVectorizer:
    return TfidfVectorizer(
        max_features=max_features,
        ngram_range=(ngram_min, ngram_max),
        lowercase=True,
        stop_words="english",
    )