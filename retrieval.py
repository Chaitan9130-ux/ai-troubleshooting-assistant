"""Local TF-IDF retrieval. Similarity scores are not probabilities."""
from dataclasses import dataclass
import json
from pathlib import Path
import re

from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity

KB_PATH = Path(__file__).with_name("knowledge_base.json")


def load_knowledge_base(path=KB_PATH):
    records = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(records, list) or not records:
        raise ValueError("Knowledge base must be a non-empty list.")
    ids = set()
    for item in records:
        for field in ("id", "title", "resolution", "escalation_team", "source"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"Missing or invalid field: {field}")
        for field in ("symptoms", "keywords", "diagnostic_checks"):
            if not isinstance(item.get(field), list) or not item[field] or any(
                not isinstance(value, str) or not value.strip() for value in item[field]
            ):
                raise ValueError(f"Invalid list: {field}")
        if item["id"] in ids:
            raise ValueError("Duplicate knowledge-base ID.")
        ids.add(item["id"])
    return records


@dataclass(frozen=True)
class Match:
    entry: dict
    score: float


@dataclass(frozen=True)
class SearchResult:
    status: str
    matches: tuple[Match, ...] = ()
    message: str = ""


class Retriever:
    def __init__(self, entries=None, threshold=0.20, ambiguity_margin=0.06):
        if not 0 <= threshold <= 1 or not 0 <= ambiguity_margin <= 1:
            raise ValueError("Threshold and ambiguity margin must be between 0 and 1.")
        self.entries = load_knowledge_base() if entries is None else entries
        if not self.entries:
            raise ValueError("Knowledge base cannot be empty.")
        self.threshold = threshold
        self.ambiguity_margin = ambiguity_margin
        # Index observable symptoms; fixes should not distort symptom matching.
        documents = [" ".join([e["title"], *e["symptoms"], *e["keywords"]]) for e in self.entries]
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform(documents)

    def search(self, query):
        query = query.strip()
        if not query:
            return SearchResult("empty", message="Describe the service, symptom, and any error message.")
        if len(query) > 2000:
            return SearchResult("invalid", message="Keep the description under 2,000 characters.")
        scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix).ravel()
        ranked = sorted(range(len(scores)), key=lambda i: (-scores[i], self.entries[i]["id"]))[:3]
        matches = tuple(Match(self.entries[i], float(scores[i])) for i in ranked if scores[i] >= self.threshold)
        if not matches:
            return SearchResult("unknown", message="The sample knowledge base has insufficient evidence. Share the affected service, exact error, time of failure, and recent changes.")
        # Short generic inputs need clarification even if one entry happens to rank first.
        meaningful = {t for t in re.findall(r"[a-z0-9]+", query.lower()) if t not in ENGLISH_STOP_WORDS}
        generic = {"app", "application", "service", "issue", "problem", "error", "working", "work", "broken", "help", "failed", "failure", "server", "slow", "down"}
        vague = not (meaningful - generic) and len(meaningful) <= 4
        close = len(matches) > 1 and matches[0].score - matches[1].score < self.ambiguity_margin
        if vague or close:
            return SearchResult("ambiguous", matches, "Several causes are possible. Which service is affected, what is the exact error, and when did it start? Select a candidate only if its symptoms fit.")
        return SearchResult("matched", matches[:1], "Possible matching issue; confirm the symptoms before applying a resolution.")
