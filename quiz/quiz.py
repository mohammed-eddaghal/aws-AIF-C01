"""Practice quiz runner (stdlib only).

  python quiz/quiz.py --domain 3        one domain
  python quiz/quiz.py --mock            all 50 questions, shuffled, timed (exam: 65 Qs / 90 min)
  python quiz/quiz.py --mock --review   show explanations as you go
Answer with option numbers; multiple response: 1,3
Scores are raw percentages on original questions, not AWS scaled scores.
"""

import argparse
import json
import random
import time
from pathlib import Path

QUESTIONS = json.loads((Path(__file__).parent / "questions.json").read_text(encoding="utf-8"))
DOMAINS = {1: "AI/ML fundamentals", 2: "GenAI fundamentals", 3: "FM applications", 4: "Responsible AI", 5: "Security & governance"}


def parse(raw, n_options):
    try:
        picks = sorted({int(x) - 1 for x in raw.replace(" ", "").split(",") if x})
    except ValueError:
        return None
    return picks if picks and all(0 <= p < n_options for p in picks) else None


def run(questions, review):
    results = []
    start = time.time()
    for i, q in enumerate(questions, 1):
        # shuffle options so the answer position carries no signal (ordering questions keep their sequences intact)
        order = random.sample(range(len(q["options"])), len(q["options"]))
        q = {**q, "options": [q["options"][o] for o in order], "answer": [order.index(a) for a in q["answer"]]}
        print(f"\n[{i}/{len(questions)}] (D{q['domain']}) {q['q']}")
        for j, opt in enumerate(q["options"], 1):
            print(f"  {j}. {opt}")
        picks = None
        while picks is None:
            picks = parse(input("> "), len(q["options"]))
        ok = picks == sorted(q["answer"])
        results.append((q, ok))
        if review:
            correct = ", ".join(str(a + 1) for a in q["answer"])
            print(("  Correct. " if ok else f"  Wrong - answer {correct}. ") + q["why"])
    return results, time.time() - start


def report(results, seconds):
    total = sum(ok for _, ok in results)
    print(f"\nScore {total}/{len(results)} = {100 * total / len(results):.0f}%   time {seconds / 60:.1f} min")
    for d, name in DOMAINS.items():
        rows = [ok for q, ok in results if q["domain"] == d]
        if rows:
            print(f"  D{d} {name:<22} {sum(rows)}/{len(rows)}")
    missed = [q for q, ok in results if not ok]
    if missed:
        print("\nReview these:")
        for q in missed:
            print(f"- {q['id']}: {q['q']}\n    -> {', '.join(q['options'][a] for a in q['answer'])}. {q['why']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", type=int, choices=DOMAINS)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--review", action="store_true")
    args = ap.parse_args()
    pool = [q for q in QUESTIONS if args.mock or args.domain in (None, q["domain"])]
    random.shuffle(pool)
    report(*run(pool, args.review or not args.mock))


if __name__ == "__main__":
    main()
