"""Lab 02 - Bedrock Converse API: tokens, cost per call, inference parameters, nondeterminism.

Domains 2.1 (tokens, token pricing), 2.2 (nondeterminism), 3.1 (temperature, max tokens).
Run: python labs/lab02_bedrock_basics.py      (6 tiny calls on Nova Micro, well under 1 cent)
"""

import os

import boto3

MODEL_ID = os.environ.get("AIF_MODEL_ID", "us.amazon.nova-micro-v1:0")
# USD per 1M tokens for Nova Micro on-demand; check https://aws.amazon.com/bedrock/pricing/ and edit for other models.
PRICE_IN, PRICE_OUT = 0.035, 0.14

client = boto3.client("bedrock-runtime")


def ask(prompt, temperature=0.5, max_tokens=200, system=None):
    kwargs = {
        "modelId": MODEL_ID,
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"temperature": temperature, "maxTokens": max_tokens},
    }
    if system:
        kwargs["system"] = [{"text": system}]
    resp = client.converse(**kwargs)
    usage = resp["usage"]
    cost = usage["inputTokens"] * PRICE_IN / 1e6 + usage["outputTokens"] * PRICE_OUT / 1e6
    return resp["output"]["message"]["content"][0]["text"], usage, resp["stopReason"], cost


def main():
    print(f"Model: {MODEL_ID}\n")

    print("1) Tokens and cost")
    text, usage, stop, cost = ask("Explain what a foundation model is in two sentences.")
    print(text)
    print(f"   in={usage['inputTokens']} out={usage['outputTokens']} tokens, stop={stop}, cost=${cost:.7f}")
    print(f"   x 1,000,000 calls/month = ${cost * 1e6:,.2f}  <- why token pricing matters\n")

    print("2) max_tokens too small -> truncated output")
    text, usage, stop, _ = ask("List the 5 AIF-C01 exam domains.", max_tokens=15)
    print(f"   {text!r}\n   stopReason={stop} (max_tokens = cut off)\n")

    prompt = "Invent a name for a coffee shop run by robots. Reply with the name only."
    for temp in (0.0, 1.0):
        names = [ask(prompt, temperature=temp, max_tokens=20)[0].strip() for _ in range(2)]
        print(f"3) temperature={temp}: {names}")
    print("   Low temperature -> consistent; high -> varied. Neither guarantees truth.")


if __name__ == "__main__":
    main()
