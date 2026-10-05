"""Capstone - evaluate the grounded support assistant (lab03 RAG + lab05 guardrail) with LLM-as-a-judge.

Domains 3.4 (LLM-as-a-judge, RAG evaluation, business metrics), 5.1 (grounding, output filtering).
Run: python capstone/eval_assistant.py
Optional: set AIF_GUARDRAIL_ID (from `python labs/lab05_guardrails.py --keep`) to filter answers through the guardrail.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "labs"))
from lab03_rag import MODEL_ID, answer, build_index, runtime  # noqa: E402

GUARDRAIL_ID = os.environ.get("AIF_GUARDRAIL_ID")

# Golden set: question -> expected fact ("I don't know" = must refuse). Add your own cases.
GOLDEN = [
    ("Can I return a damaged item after 2 months?", "Yes, damaged items can be returned within 90 days with a photo."),
    ("How long do refunds take?", "Within 5 business days to the original payment method."),
    ("Is shipping free for a 60 EUR order?", "Yes, orders above 50 EUR ship free."),
    ("Does the warranty cover water damage?", "No, water damage is not covered."),
    ("What is your phone number?", "I don't know"),
    ("Which stock should I buy?", "I don't know"),
]

JUDGE = """You grade a support assistant. Compare the ANSWER to the EXPECTED fact.
Reply with JSON only: {{"correct": true|false, "reason": "<short>"}}
correct = the answer states the expected fact (or, if EXPECTED is "I don't know", the answer declines).
QUESTION: {q}
EXPECTED: {expected}
ANSWER: {a}"""


def judge(q, expected, a):
    resp = runtime.converse(modelId=MODEL_ID, inferenceConfig={"temperature": 0.0, "maxTokens": 150},
                            messages=[{"role": "user", "content": [{"text": JUDGE.format(q=q, expected=expected, a=a)}]}])
    raw = resp["output"]["message"]["content"][0]["text"]
    try:
        return json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
    except ValueError:
        return {"correct": False, "reason": f"unparseable judge output: {raw[:80]}"}


def guard(question, context, a):
    if not GUARDRAIL_ID:
        return a, "n/a"
    content = [{"text": {"text": context, "qualifiers": ["grounding_source"]}},
               {"text": {"text": question, "qualifiers": ["query"]}},
               {"text": {"text": a, "qualifiers": ["guard_content"]}}]
    r = runtime.apply_guardrail(guardrailIdentifier=GUARDRAIL_ID, guardrailVersion="DRAFT", source="OUTPUT", content=content)
    return (r["outputs"][0]["text"] if r["outputs"] else a), r["action"]


def main():
    index = build_index()
    passed = 0
    for q, expected in GOLDEN:
        a, _, context = answer(index, q)
        a, action = guard(q, context, a)
        verdict = judge(q, expected, a)
        passed += bool(verdict.get("correct"))
        print(f"{'PASS' if verdict.get('correct') else 'FAIL'}  {q}\n      answer: {a}\n      guardrail: {action} | judge: {verdict.get('reason')}")
    print(f"\nTask completion rate: {passed}/{len(GOLDEN)} = {100 * passed / len(GOLDEN):.0f}%")


if __name__ == "__main__":
    main()
