# Lab 02 — Bedrock basics (Converse API, tokens, cost, temperature, nondeterminism)

| | |
|---|---|
| **Needs AWS?** | Yes — [Lab 00](lab-00.md) completed (`aif-lab` user, `us-east-1`, Nova Micro accessible) |
| **Cost** | Well under 1 US cent (6 short calls to Amazon Nova Micro, on-demand) |
| **Time** | 30–45 min, plus 15 min for the console playground |
| **Exam domains** | Domain 2 — **2.1** (tokens, token-based pricing), **2.2** (nondeterminism, hallucination limits), **2.3** (cost trade-offs, cross-region inference) · Domain 3 — **3.1** (inference parameters: temperature, max tokens; model selection by cost) |

Code: [`../labs/lab02_bedrock_basics.py`](../labs/lab02_bedrock_basics.py)

## What you'll learn

- How to call a foundation model on Amazon Bedrock with the **Converse API** using `boto3`.
- What **input and output tokens** are, where Bedrock reports them, and how to turn them into a **cost per call**.
- What **`maxTokens`** does and what a truncated answer looks like (`stopReason = max_tokens`).
- How **temperature** (and top-p) change the output, and why the same prompt can give different answers (**nondeterminism**).
- How to do the same thing in the **Bedrock console playground**.

## Background

**Foundation model (FM) and Amazon Bedrock.** An FM is a large model pre-trained on broad data that you can use for many tasks. Amazon Bedrock is a fully managed service that gives you API access to FMs from Amazon and other providers, without managing servers. You pay per use.

**Tokens.** Models don't read characters or words; they read **tokens** — chunks of text (a short word, part of a long word, punctuation). As a rough rule, one English token is about three-quarters of a word, but each model has its own tokenizer, so the only reliable count is the one the API returns.

- **Input tokens** = everything you send: system prompt, conversation history, the user message (plus formatting the model adds).
- **Output tokens** = everything the model generates.
- The **context window** is the maximum number of tokens the model can handle per request.

**Token-based pricing.** On-demand Bedrock text models charge a price per input token and a (usually higher) price per output token, typically quoted per 1,000 or per 1,000,000 tokens. So:

```text
cost per call = input_tokens × input_price + output_tokens × output_price
```

Prices differ by model and region and change over time. **Always check the current [Amazon Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/).** This lab's script hard-codes two numbers for Nova Micro — verify them before trusting the dollar figures.

**Converse API.** One request/response format that works across Bedrock chat models, so you can switch models by changing the model ID. You send `messages` (each with a `role` — `user` or `assistant` — and a list of `content` blocks), an optional `system` prompt, and `inferenceConfig`. IAM-wise, it is authorized by `bedrock:InvokeModel`.

**How text generation works, in one paragraph.** At each step the model computes a probability for every possible next token, then *samples* one. Inference parameters shape that sampling:

| Parameter (Converse name) | What it does |
|---|---|
| `temperature` | Flattens (high) or sharpens (low) the probability distribution. Low (≈0–0.3) → more predictable, repeatable. High (≈0.7–1) → more varied, creative. |
| `topP` | Only sample from the smallest set of tokens whose probabilities add up to *p* (e.g. 0.9). Lower → safer word choices. |
| `maxTokens` | Hard cap on output length. Limits cost and latency; too low cuts the answer mid-sentence. |
| `stopSequences` | Strings that end generation when produced. |

*Top-k* (sample from the k most likely tokens) is not part of the common `inferenceConfig`; models that support it take it as a model-specific field (`additionalModelRequestFields`).

**Nondeterminism.** Because the next token is sampled, the same prompt can produce different outputs. Lower temperature makes outputs more consistent, but even temperature 0 is not a hard guarantee of identical output, and **no setting guarantees the output is true** — a confident, consistent answer can still be a hallucination.

## Steps

1. Finish [Lab 00](lab-00.md). Check you are the lab user, in the right region:

```bash
aws sts get-caller-identity
aws configure get region
```

The ARN should end in `user/aif-lab`; the region should be `us-east-1`.

2. From the repository root, activate your virtual environment (if you made one in Lab 00).

```powershell
.\.venv\Scripts\Activate.ps1
```

```bash
source .venv/bin/activate
```

3. Optional: confirm the model ID (the default is used if the variable is unset).

```powershell
$env:AIF_MODEL_ID = "us.amazon.nova-micro-v1:0"
```

```bash
export AIF_MODEL_ID="us.amazon.nova-micro-v1:0"
```

4. Run the lab:

```powershell
python labs/lab02_bedrock_basics.py
```

```bash
python3 labs/lab02_bedrock_basics.py
```

5. Expected output **shape**. This is illustrative — the model's wording, the token counts, the cost and the invented names **will differ** on your run:

```text
Model: us.amazon.nova-micro-v1:0

1) Tokens and cost
A foundation model is a large AI model trained on broad data that can be adapted to many tasks. ...
   in=12 out=60 tokens, stop=end_turn, cost=$0.0000088
   x 1,000,000 calls/month = $8.82  <- why token pricing matters

2) max_tokens too small -> truncated output
   '1. Fundamentals of AI and ML\n2. Fundamentals of Gener'
   stopReason=max_tokens (max_tokens = cut off)

3) temperature=0.0: ['RoboBrew', 'RoboBrew']
3) temperature=1.0: ['Circuit Bean Café', 'Byte & Brew']
   Low temperature -> consistent; high -> varied. Neither guarantees truth.
```

What to check on *your* output:

- Section 1: `stop=end_turn` (the model finished on its own) and a cost of a tiny fraction of a cent.
- Section 2: the text is cut off and `stopReason=max_tokens`.
- Section 3: the two temperature-0 names are usually identical; the two temperature-1 names usually differ. Run the script two or three times — the pattern holds even though the names change.

6. Write down your own numbers from section 1 (`in`, `out`, `cost`). You'll use them in the experiments.

## What just happened

### Configuration (top of the file)

```python
MODEL_ID = os.environ.get("AIF_MODEL_ID", "us.amazon.nova-micro-v1:0")
PRICE_IN, PRICE_OUT = 0.035, 0.14
client = boto3.client("bedrock-runtime")
```

- `MODEL_ID` — read from the environment, falling back to the Nova Micro **US cross-region inference profile**. The `us.` prefix lets Bedrock route the request to one of several US regions for capacity.
- `PRICE_IN`, `PRICE_OUT` — the script's assumed **USD per 1 million tokens** for Nova Micro on-demand (input 0.035, output 0.14). The comment in the code tells you to verify them on the pricing page and edit them for other models. Notice output is priced 4× input here — output tokens are typically the more expensive side, which is why capping output length matters.
- `boto3.client("bedrock-runtime")` — `bedrock-runtime` is the *data plane* client for inference (Converse, InvokeModel). The separate `bedrock` client is the *control plane* (guardrails, model customization, listing models). No region or keys are passed: `boto3` takes them from `~/.aws/` (Lab 00).

### `ask()` — the Converse request

```python
kwargs = {
    "modelId": MODEL_ID,
    "messages": [{"role": "user", "content": [{"text": prompt}]}],
    "inferenceConfig": {"temperature": temperature, "maxTokens": max_tokens},
}
if system:
    kwargs["system"] = [{"text": system}]
resp = client.converse(**kwargs)
```

- `messages` — the conversation. Here it is a single `user` turn. For a multi-turn chat you would append the model's reply as an `assistant` message and the next `user` message; the model itself is **stateless**, so you resend the whole history each time (and pay for those input tokens again).
- `content` — a list of blocks. Text here; multimodal models also accept image or document blocks.
- `inferenceConfig` — `temperature` (default 0.5 in this script) and `maxTokens` (default 200).
- `system` — optional instructions that frame every answer (role, tone, rules). It's supported by `ask()` but none of the six calls uses it — you'll try it in the experiments.

### `ask()` — the Converse response

The response is a dictionary. The fields that matter:

```text
resp["output"]["message"]["role"]           -> "assistant"
resp["output"]["message"]["content"][0]["text"]  -> the generated text
resp["stopReason"]                          -> why generation stopped
resp["usage"]["inputTokens"]                -> tokens you sent
resp["usage"]["outputTokens"]               -> tokens generated
resp["usage"]["totalTokens"]                -> sum of the two
resp["metrics"]["latencyMs"]                -> time the model took, in ms
```

Common `stopReason` values: `end_turn` (model finished naturally), `max_tokens` (hit your `maxTokens` cap), `stop_sequence` (produced one of your stop strings), `guardrail_intervened` (a guardrail blocked it — Lab 05), `tool_use` (the model wants to call a tool — agents).

### Cost per call

```python
cost = usage["inputTokens"] * PRICE_IN / 1e6 + usage["outputTokens"] * PRICE_OUT / 1e6
```

Worked example with the illustrative numbers above (in = 12, out = 60) and the script's prices:

```text
input : 12 × 0.035 / 1,000,000 = 0.00000042 USD
output: 60 × 0.14  / 1,000,000 = 0.0000084  USD
total                          = 0.00000882 USD  -> printed $0.0000088
× 1,000,000 calls              = 8.82 USD
```

Two lessons: output tokens dominate the bill even though there are only 60 of them, and a cost that looks like nothing per call becomes a real line item at scale. Redo this with **your** numbers.

### Section 1 — tokens and cost

Calls `ask()` with defaults (temperature 0.5, max 200 tokens) and prints the text, the token counts, the stop reason and the cost, then multiplies by one million to simulate a month of production traffic.

### Section 2 — `max_tokens` too small

Asks for a five-item list but allows only **15 output tokens**. The model is cut off mid-answer and `stopReason` is `max_tokens`. In an application you should check `stopReason`: a truncated answer can look complete to a user, and truncated JSON will fail to parse.

### Section 3 — temperature and nondeterminism

```python
for temp in (0.0, 1.0):
    names = [ask(prompt, temperature=temp, max_tokens=20)[0].strip() for _ in range(2)]
```

The same creative prompt runs twice at temperature 0.0 and twice at 1.0. At 0.0 the model nearly always picks its single most likely continuation, so the answers usually match. At 1.0 it samples more widely, so they usually differ. The final printed line is the key exam idea: *consistent* is not the same as *correct*.

Total: 1 + 1 + 4 = **6 calls**, each with a short prompt and a small output cap.

## Experiments

Copy the script and edit the copy (don't commit it):

```powershell
Copy-Item labs/lab02_bedrock_basics.py labs/lab02_play.py
python labs/lab02_play.py
```

```bash
cp labs/lab02_bedrock_basics.py labs/lab02_play.py
python3 labs/lab02_play.py
```

Every run costs a fraction of a cent. **Write your prediction before each run.**

**1. Add a system prompt.** In section 1 change the call to:

```python
text, usage, stop, cost = ask("Explain what a foundation model is in two sentences.",
                              system="You are a terse tutor. Answer in at most 20 words.")
```

Predict: do input tokens go up or down? Output tokens? Total cost?

<details><summary>What to expect</summary>

Input tokens **go up** (the system prompt is sent and billed on every call). Output tokens usually **go down** (shorter answer). Because output is the pricier side, total cost often drops. This is the context-engineering trade-off: a few more input tokens can save more output tokens.
</details>

**2. Repeat the temperature test more times.** Change `range(2)` to `range(5)`. Predict how many distinct names you'll get at 0.0 and at 1.0.

<details><summary>What to expect</summary>

At 0.0, usually 1 distinct name (occasionally 2 — temperature 0 is not a strict guarantee). At 1.0, usually 4–5 distinct names. Nondeterminism is a property of sampling, not a bug.
</details>

**3. Add top-p.** In `ask()`, change `inferenceConfig` to `{"temperature": temperature, "maxTokens": max_tokens, "topP": 0.1}` and run section 3 again. Predict the effect at temperature 1.0.

<details><summary>What to expect</summary>

With `topP` 0.1, only the few most likely tokens are eligible, so even temperature 1.0 gives much less varied names. Temperature and top-p both narrow or widen sampling; tune one at a time. Some models don't accept every parameter combination — check the model's inference-parameter docs if you get a `ValidationException`.
</details>

**4. Stop sequence.** In section 2, raise `max_tokens` to 200 and add `"stopSequences": ["3."]` to `inferenceConfig` (in your copy of `ask()`). Predict the `stopReason`.

<details><summary>What to expect</summary>

Output stops just before item 3, and `stopReason` becomes `stop_sequence`. Stop sequences are a cheap way to end output at a known boundary.
</details>

**5. Paper exercise — the system-prompt tax.** A chatbot sends a 3,000-token system prompt on every call, 1,000,000 calls per month. Using the script's `PRICE_IN` (verify it first), how much does the system prompt alone cost per month? Name three ways to reduce it.

<details><summary>Answer</summary>

3,000 × 0.035 / 1,000,000 = 0.000105 USD per call → × 1,000,000 = **105 USD/month**, before any user message or output. Reductions: shorten the prompt; use **prompt caching** for the repeated prefix (where the model supports it); use a smaller/cheaper model; move offline workloads to **batch inference**.
</details>

**6. Switch models.** Set `AIF_MODEL_ID` to `us.amazon.nova-lite-v1:0` and run. Predict what happens with the Lab 00 policy.

<details><summary>What to expect</summary>

`AccessDeniedException` — `AifLabPolicy` only allows Nova Micro and Titan embeddings. That's least privilege doing its job. To really compare models, add the new model's foundation-model and inference-profile ARNs to the policy **and** update `PRICE_IN`/`PRICE_OUT` from the pricing page — otherwise the printed cost is wrong. (Or compare models in the console, below.) Reset the variable afterwards: `Remove-Item Env:AIF_MODEL_ID` (PowerShell) or `unset AIF_MODEL_ID` (bash).
</details>

### Same exercise in the Bedrock console playground

Use your **admin** identity (playgrounds need more permissions than `aif-lab` has), region **us-east-1**.

1. Amazon Bedrock → **Playgrounds** → **Chat / Text**.
2. **Select model** → provider **Amazon** → **Nova Micro** → apply. If asked for an inference type, choose the cross-region inference profile.
3. Open the configuration panel. Find **Temperature**, **Top P**, the maximum response length setting, and **Stop sequences**.
4. Prompt: `Explain what a foundation model is in two sentences.` → **Run**. Look at the metrics shown with the response (latency and input/output token counts). Compute the cost with the formula above and current prices.
5. Set the max length very low (e.g. 15) and ask `List the 5 AIF-C01 exam domains.` → the answer is cut off.
6. Set temperature to 0, ask `Invent a name for a coffee shop run by robots. Reply with the name only.` three times. Then temperature 1, three times. Compare.
7. Optional: turn on **Compare mode** and run the same prompt on Nova Micro and a second model. Compare latency, token counts and quality — this is Domain 2 exercise 3. Calls made from the playground are billed like API calls; keep prompts short.

Console labels change from time to time; if a name differs slightly, look for the equivalent control.

## Exam connection

- **"Reduce the cost of a GenAI app"** → fewer input tokens (shorter prompts, less history), cap output (`maxTokens`), smaller model, prompt caching, batch inference for offline jobs. Output tokens usually cost more than input tokens.
- **"Steady high-volume traffic needing guaranteed throughput"** → Provisioned Throughput; **"variable/unknown traffic, prototyping"** → on-demand.
- **"Answers are cut off"** → `maxTokens` too low (`stopReason = max_tokens`).
- **"Responses must be consistent/factual"** → lower temperature / top-p. **"Creative variety"** → higher temperature.
- **"Model gives different answers to the same prompt"** → nondeterminism from sampling — expected behavior.
- **"One API across many models"** → the Bedrock Converse API.
- **"More capacity / resilience across regions"** → cross-region inference (inference profiles).

> **Exam tip:** Temperature controls *randomness*, not *accuracy*. To reduce hallucinations, look for grounding (RAG, Guardrails contextual grounding check, human review), not just "set temperature to 0".

> **Exam tip:** Token pricing is per input token **and** per output token. If a question asks how to cut cost without changing the model, look at prompt length, `maxTokens`, prompt caching and batch.

> **Exam tip:** A model with a larger context window can accept longer prompts — but you pay for every input token you actually send.

## Check yourself

**1.** A company's support chatbot on Amazon Bedrock often returns answers that end mid-sentence. The response metadata shows `stopReason` = `max_tokens`. What should the team change?

A. Lower the temperature
B. Increase the maximum output tokens
C. Add a stop sequence
D. Switch to Provisioned Throughput

<details><summary>Answer</summary>

**B.** The model hit the output cap. Temperature (A) affects randomness, not length. A stop sequence (C) would end output even earlier. Provisioned Throughput (D) affects capacity, not response length.
</details>

**2.** A legal team wants the same question to produce the most consistent wording possible across repeated runs. Which inference-parameter change helps MOST?

A. Increase temperature to 1.0
B. Decrease temperature (toward 0)
C. Increase the context window
D. Increase `maxTokens`

<details><summary>Answer</summary>

**B.** Lower temperature makes sampling favor the most likely tokens, reducing variation. Higher temperature (A) increases variety. C and D don't affect randomness.
</details>

**3.** An application sends a long, identical system prompt with every request to an on-demand Bedrock model. Monthly cost is too high. Which change MOST directly reduces cost without changing the model or the answers?

A. Use prompt caching for the repeated system-prompt prefix
B. Raise the temperature
C. Move the model to a different region
D. Increase `maxTokens`

<details><summary>Answer</summary>

**A.** Prompt caching reuses the repeated prefix so you don't pay full price to process it on every call (on models that support it). Temperature (B) doesn't change cost. A region move (C) isn't a direct lever. More output tokens (D) costs more.
</details>

**4.** With on-demand pricing, a Bedrock call uses 1,000 input tokens and 500 output tokens. The model's price is X per 1,000 input tokens and 4X per 1,000 output tokens. What is the cost of the call?

A. 1.5X
B. 3X
C. 5X
D. 6X

<details><summary>Answer</summary>

**B.** Input: 1 × X = X. Output: 0.5 × 4X = 2X. Total = 3X. Fewer output tokens than input tokens, yet output is two-thirds of the bill.
</details>

## Cleanup

- Nothing persistent is created; there is nothing to delete in AWS.
- Delete `labs/lab02_play.py` if you made it.
- Reset any environment variables you changed (`Remove-Item Env:AIF_MODEL_ID` / `unset AIF_MODEL_ID`).
- Optional: Billing → Bills (or Cost Explorer) the next day — Bedrock charges for this lab should round to 0.00 USD.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `NoRegionError: You must specify a region` (at start-up) | No default region | `aws configure` → `us-east-1`, or set `AWS_REGION=us-east-1`. |
| `NoCredentialsError` / `Unable to locate credentials` | Lab 00 not done, or wrong profile | Run `aws sts get-caller-identity`; set `AWS_PROFILE` if you used a named profile. |
| `AccessDeniedException ... not authorized to perform: bedrock:InvokeModel` | IAM policy missing the model / profile ARN, or not attached | Compare the ARN in the error with `AifLabPolicy` (Lab 00, step 5). |
| `AccessDeniedException` saying you don't have access to the model | Model access not enabled | Bedrock console → Model catalog → Nova Micro; request access if offered. |
| `ValidationException` — invalid model identifier | Wrong region (a `us.` profile only works from US regions) or typo in `AIF_MODEL_ID` | `aws configure get region`; `echo $env:AIF_MODEL_ID` / `echo "$AIF_MODEL_ID"`. |
| `ValidationException` about inference parameters (your copy) | Parameter name/value not accepted by the model | Check spelling (`maxTokens`, `topP`, `stopSequences`) and allowed ranges in the model docs. |
| `ThrottlingException` | Too many requests in a short time | Wait and re-run. |
| `ExpiredTokenException` | Temporary (SSO) credentials expired | `aws sso login`, or use the IAM user's access key from Lab 00. |
| `ModuleNotFoundError: No module named 'boto3'` | Dependencies not installed in this environment | Activate the venv; `pip install -r labs/requirements.txt`. |
| Printed cost looks wrong | Prices in the script don't match the model/region/date | Update `PRICE_IN` / `PRICE_OUT` from https://aws.amazon.com/bedrock/pricing/. |

---

[Next: Lab 03](lab-03.md) · Back to the course: [Domain 2 — GenAI fundamentals](domain-2.md) · [Domain 3 — Applications of foundation models](domain-3.md) · Previous: [Lab 01](lab-01.md)
