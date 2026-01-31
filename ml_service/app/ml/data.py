import pandas as pd
from dataclasses import dataclass
from typing import List, Tuple
import random
@dataclass(frozen=True)
class Document:
    id:int
    title: str
    text: str
    tags: List[str]

    def _make_positive_query(self)->str:
        bits = [self.title]
        if self.tags:
            bits.append(" ".join(self.tags[:3]))
        return " ".join(bits)

def build_pair_dataset(
    docs: List[Document],
    negative_sampling_ratio: int,
    seed: int,
) -> pd.DataFrame:
    rnd = random.Random(seed)

    rows: List[Tuple[str, str, int, int]] = []

    # positives: query from doc -> same doc labeled relevant
    for d in docs:
        q = d._make_positive_query()
        rows.append((q, d.title + "\n" + d.text, 1, d.id))

    # negatives: same query paired with other docs labeled not relevant
    for d in docs:
        q = d._make_positive_query()
        others = [x for x in docs if x.id != d.id]
        for _ in range(negative_sampling_ratio):
            neg = rnd.choice(others)
            rows.append((q, neg.title + "\n" + neg.text, 0, neg.id))

    df = pd.DataFrame(rows, columns=["query", "doc_text", "label", "doc_id"])
    return df
