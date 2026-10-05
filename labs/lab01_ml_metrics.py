"""Lab 01 (offline) - classification metrics and text-generation metrics from scratch.

Domains 1.3 (accuracy, precision, recall, F1) and 3.4 (ROUGE, BLEU).
Run: python labs/lab01_ml_metrics.py
"""

import math
from collections import Counter

# --- Part A: a fraud model's scores (probability of fraud) and the true labels (1 = fraud) ---
SCORES = [0.95, 0.91, 0.85, 0.80, 0.72, 0.66, 0.61, 0.55, 0.48, 0.42,
          0.38, 0.33, 0.29, 0.22, 0.18, 0.12, 0.09, 0.07, 0.04, 0.02]
LABELS = [1, 1, 0, 1, 1, 0, 1, 0, 0, 1,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


def confusion(labels, preds):
    tp = sum(1 for y, p in zip(labels, preds) if y == 1 and p == 1)
    fp = sum(1 for y, p in zip(labels, preds) if y == 0 and p == 1)
    fn = sum(1 for y, p in zip(labels, preds) if y == 1 and p == 0)
    tn = sum(1 for y, p in zip(labels, preds) if y == 0 and p == 0)
    return tp, fp, fn, tn


def metrics(tp, fp, fn, tn):
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / (tp + fp + fn + tn)
    return accuracy, precision, recall, f1


# --- Part B: ROUGE-1 (recall-oriented, summarization) and BLEU-1 (precision-oriented, translation) ---

def rouge1_recall(candidate, reference):
    """Share of reference words that appear in the candidate (clipped counts)."""
    c, r = Counter(candidate.lower().split()), Counter(reference.lower().split())
    return sum((c & r).values()) / sum(r.values())


def bleu1(candidate, reference):
    """Unigram precision with brevity penalty (real BLEU averages 1-4 grams)."""
    c_tokens, r_tokens = candidate.lower().split(), reference.lower().split()
    overlap = sum((Counter(c_tokens) & Counter(r_tokens)).values())
    precision = overlap / len(c_tokens)
    bp = 1.0 if len(c_tokens) > len(r_tokens) else math.exp(1 - len(r_tokens) / len(c_tokens))
    return bp * precision


def main():
    print("Part A - threshold vs precision/recall (fraud: 6 positives out of 20)")
    print(f"{'threshold':>9} {'TP':>3} {'FP':>3} {'FN':>3} {'acc':>5} {'prec':>5} {'rec':>5} {'F1':>5}")
    for threshold in (0.9, 0.7, 0.5, 0.3):
        preds = [1 if s >= threshold else 0 for s in SCORES]
        tp, fp, fn, tn = confusion(LABELS, preds)
        acc, p, r, f1 = metrics(tp, fp, fn, tn)
        print(f"{threshold:>9} {tp:>3} {fp:>3} {fn:>3} {acc:>5.2f} {p:>5.2f} {r:>5.2f} {f1:>5.2f}")
    always_no = metrics(*confusion(LABELS, [0] * len(LABELS)))
    print(f"'Always not fraud' model: accuracy {always_no[0]:.2f}, recall {always_no[2]:.2f}  <- why accuracy lies on imbalanced data")
    print("Takeaway: lower threshold -> recall up, precision down. Fraud/medical: favor recall.\n")

    print("Part B - ROUGE-1 vs BLEU-1")
    reference = "the customer was refunded because the parcel arrived damaged"
    for cand in ("the parcel arrived damaged so the customer was refunded",
                 "customer refunded"):
        print(f"  {cand!r}\n    ROUGE-1 recall {rouge1_recall(cand, reference):.2f}   BLEU-1 {bleu1(cand, reference):.2f}")
    print("Takeaway: short answers can be precise yet miss content; ROUGE catches that, BLEU's brevity penalty too.")


def _self_check():
    assert metrics(15, 15, 5, 965)[1:] == (0.5, 0.75, 0.6)  # domain 1 paper exercise 2
    assert rouge1_recall("a b c", "a b c") == 1.0
    assert bleu1("a b", "a b c d") < 1.0  # brevity penalty kicks in


if __name__ == "__main__":
    _self_check()
    main()
