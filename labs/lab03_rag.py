"""Lab 03 - Retrieval Augmented Generation from scratch on Bedrock.

Same pipeline Bedrock Knowledge Bases manages for you: chunk -> embed -> store -> retrieve -> ground the answer.
Domains 2.1 (chunking, embeddings, vectors), 3.1 (RAG), 5.1 (grounding, citations).
Run: python labs/lab03_rag.py   or   python labs/lab03_rag.py "your question"
"""

import json
import math
import os
import sys

import boto3

MODEL_ID = os.environ.get("AIF_MODEL_ID", "us.amazon.nova-micro-v1:0")
EMBED_MODEL_ID = os.environ.get("AIF_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")

# A fictional company's policy docs. Swap in your own text to experiment.
DOCS = {
    "returns.md": """Customers can return any item within 30 days of delivery for a full refund.
Items must be unused and in original packaging. Refunds are issued to the original payment method within 5 business days.

Damaged items can be returned at any time within 90 days. The customer must send a photo of the damage to support@example.com.
We pay return shipping for damaged items only.""",
    "shipping.md": """Standard shipping takes 3 to 5 business days and costs 4.99 EUR. Orders above 50 EUR ship for free.

Express shipping delivers next business day if ordered before 14:00 and costs 12.99 EUR.
We currently ship to France, Belgium, Luxembourg and Morocco.""",
    "warranty.md": """All electronics carry a 2-year warranty covering manufacturing defects.
The warranty does not cover water damage, drops or unauthorized repairs.

To claim the warranty, open a ticket with the order number and serial number.""",
}

runtime = boto3.client("bedrock-runtime")


def chunk(docs):
    """Paragraph chunking. Real systems also use fixed-size + overlap, semantic or hierarchical chunking."""
    return [{"source": name, "text": p.strip()} for name, body in docs.items() for p in body.split("\n\n") if p.strip()]


def embed(text):
    body = json.dumps({"inputText": text, "dimensions": 256, "normalize": True})
    resp = runtime.invoke_model(modelId=EMBED_MODEL_ID, body=body)
    return json.loads(resp["body"].read())["embedding"]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def build_index(docs=DOCS):
    # ponytail: in-memory list + linear scan; a vector DB (OpenSearch, Aurora pgvector) once you have thousands of chunks
    chunks = chunk(docs)
    for c in chunks:
        c["vector"] = embed(c["text"])
    return chunks


def retrieve(index, question, k=2):
    q = embed(question)
    return sorted(index, key=lambda c: cosine(q, c["vector"]), reverse=True)[:k]


SYSTEM = ("You answer customer questions using ONLY the numbered context passages. "
          "Cite passages like [1]. If the answer is not in the context, say exactly: I don't know.")


def answer(index, question):
    hits = retrieve(index, question)
    context = "\n".join(f"[{i}] ({h['source']}) {h['text']}" for i, h in enumerate(hits, 1))
    resp = runtime.converse(
        modelId=MODEL_ID,
        system=[{"text": SYSTEM}],
        messages=[{"role": "user", "content": [{"text": f"Context:\n{context}\n\nQuestion: {question}"}]}],
        inferenceConfig={"temperature": 0.0, "maxTokens": 300},
    )
    return resp["output"]["message"]["content"][0]["text"], hits, context


def main():
    index = build_index()
    print(f"Indexed {len(index)} chunks, {len(index[0]['vector'])}-dim vectors\n")
    questions = sys.argv[1:] or [
        "My blender arrived broken 2 months ago, can I still return it?",
        "Do you deliver to Morocco and how much is express?",
        "Do you ship to Canada?",          # partially answerable: list says where we ship
        "What is the CEO's name?",         # not in docs -> should say I don't know
    ]
    for q in questions:
        text, hits, _ = answer(index, q)
        print(f"Q: {q}\n   retrieved: {[h['source'] for h in hits]}\nA: {text}\n")


if __name__ == "__main__":
    main()
