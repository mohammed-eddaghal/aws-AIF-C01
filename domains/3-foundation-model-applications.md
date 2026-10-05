# Domain 3 — Applications of Foundation Models (28%, biggest domain)

## Official objectives (v1.1, condensed)

- **3.1 Design:** FM selection (cost, modality, latency, multilingual, size, complexity, customization,
  input/output length, prompt caching) · inference parameters (temperature, length) · **RAG** and
  **Bedrock Knowledge Bases** · vector stores (**OpenSearch Service, Aurora, Neptune, RDS for PostgreSQL**) ·
  cost of customization (pre-training, fine-tuning, in-context learning, RAG, **distillation**) · AI agents.
- **3.2 Prompting:** context, instruction, negative prompts · zero/single/few-shot, chain-of-thought, templates ·
  best practices (specific, concise, experiment, guardrails) · risks (**exposure, poisoning, hijacking, jailbreaking**) ·
  **Bedrock Prompt Management** (versioning).
- **3.3 Training/fine-tuning:** pre-training, fine-tuning, continued pre-training, distillation · instruction
  tuning, domain adaptation, transfer learning · data prep (curation, governance, size, labeling,
  representativeness, **RLHF**).
- **3.4 Evaluation:** human-in-the-loop, benchmark datasets, **Bedrock Model Evaluation** · metrics
  (**ROUGE, BLEU, BERTScore, LLM-as-a-judge**) · business fit · evaluating RAG/agents/workflows ·
  alignment metrics (task completion rate, user satisfaction, cost per interaction).

## Must-know concepts

### Inference parameters
| Parameter | Effect |
|---|---|
| Temperature | Randomness. Low (0–0.3) = factual, consistent. High (0.7–1) = creative, varied |
| Top-p | Sample only from the smallest token set whose probability sums to p |
| Top-k | Sample only from the k most likely tokens |
| Max tokens | Caps output length (and cost); too low truncates answers |
| Stop sequences | Strings that end generation |

### Customization ladder (cheapest/fastest → most expensive)
1. **Prompt engineering / in-context learning** — no training, instant.
2. **RAG** — add fresh/private knowledge at query time; no training; cites sources; best for changing data.
3. **Fine-tuning** (labeled prompt→response pairs) — change *behavior/style/format*, task specialization.
4. **Continued pre-training** (unlabeled domain text) — teach domain *vocabulary/knowledge*.
5. **Pre-training from scratch** — almost never; huge cost.
- **Distillation** — a large *teacher* model generates data to train a smaller *student* → near-teacher quality at lower cost/latency.
- Fine-tuned models on Bedrock generally need **Provisioned Throughput** to serve.

### RAG
Ingest: documents (S3) → chunk → embed → store in vector DB. Query: embed question → similarity search →
put top-k chunks in prompt → FM answers with citations. **Bedrock Knowledge Bases** does this managed.
AWS vector options: OpenSearch Service/Serverless, Aurora PostgreSQL & RDS for PostgreSQL (pgvector),
Neptune Analytics (graph RAG), plus MongoDB/Pinecone/Redis partners and S3 Vectors.

### Prompting techniques
- **Zero-shot** — just the instruction. **One/few-shot** — include 1/several input→output examples.
- **Chain-of-thought** — ask the model to reason step by step (multi-step math/logic).
- **Prompt template** — reusable prompt with variables. **Negative prompt** — what to avoid (common in image gen).
- Structure: role/context + instruction + input data + output format.

### Prompt attacks
| Attack | What |
|---|---|
| Prompt injection / hijacking | Input overrides your instructions ("ignore previous instructions…"), incl. indirect via retrieved docs/web |
| Jailbreaking | Trick model past its safety rules (role-play, encoding) |
| Exposure / leaking | Model reveals system prompt or sensitive training/context data |
| Poisoning | Malicious data in training/fine-tuning or the RAG corpus |
Defenses: Bedrock Guardrails (prompt-attack filter), input validation, separate trusted vs untrusted content, least-privilege tools, output filtering.

### Training data & RLHF
Fine-tuning data must be curated, labeled, representative, governed, enough of it. **RLHF** = humans rank
outputs → reward model → RL optimizes the FM toward preferred answers (helpfulness/harmlessness).

### Evaluation
| Metric | Use |
|---|---|
| ROUGE | Summarization (recall of reference n-grams) |
| BLEU | Translation (precision of n-grams vs reference) |
| BERTScore | Semantic similarity via embeddings (meaning, not exact words) |
| Perplexity | How well a model predicts text (lower = better) |
| LLM-as-a-judge | Another FM grades outputs against criteria — scalable, cheaper than humans |
| Human evaluation | Subjective quality, brand voice, nuance — slowest, best for final calls |
**Bedrock Model Evaluation**: automatic (built-in metrics/datasets), LLM-as-a-judge, human (your team or AWS-managed), and RAG (Knowledge Base) evaluation.
RAG eval: retrieval (context relevance/coverage) + generation (faithfulness/groundedness, answer relevance).
Agent eval: task completion rate, tool-call correctness, steps/cost per task.

## AWS services for this domain

Bedrock Knowledge Bases · Bedrock Agents / AgentCore · Bedrock Guardrails · Bedrock Prompt Management
(versioned prompt templates, variants, compare) · Bedrock Flows (visual workflows) · Bedrock Model Evaluation ·
Bedrock custom models (fine-tuning, continued pre-training, distillation) · OpenSearch Service · Aurora/RDS PostgreSQL ·
Neptune · SageMaker JumpStart (fine-tune open models) · SageMaker Ground Truth (human labeling / RLHF data).

## Repo lessons

- `phases/11-llm-engineering/01-prompt-engineering`, `02-few-shot-cot` ← core
- `phases/11-llm-engineering/06-rag`, `07-advanced-rag` ← core; `phases/05-nlp-foundations-to-advanced/23-chunking-strategies-rag`
- `phases/11-llm-engineering/08-fine-tuning-lora`, `phases/10-llms-from-scratch/06-instruction-tuning-sft`, `07-rlhf`
- `phases/11-llm-engineering/10-evaluation`, `phases/05-nlp-foundations-to-advanced/27-llm-evaluation-frameworks`
- `phases/05-nlp-foundations-to-advanced/11-machine-translation` (BLEU), `12-text-summarization` (ROUGE)
- `phases/11-llm-engineering/15-prompt-caching`, `phases/17-infrastructure-and-production/16-model-routing`
- `phases/14-agent-engineering/27-prompt-injection-defense`, `30-eval-driven-agent-development`

## Exercises

1. `python labs/lab03_rag.py` — RAG from scratch: chunk, embed (Titan), cosine search, grounded answer with sources.
   Then ask something not in the docs and confirm it says "I don't know".
2. `python labs/lab01_ml_metrics.py` — the ROUGE-1 / BLEU-1 section: score two candidate summaries.
3. **Prompting drill** in the Bedrock chat playground: same task as zero-shot, few-shot (3 examples), and CoT. Note differences.
4. **Console:** Bedrock → Prompt Management: create a prompt with a `{{variable}}`, save version 1, edit, save version 2, compare.
5. **Console (look, don't run):** Bedrock → Evaluations → create job screen: note automatic vs human vs LLM-as-judge vs RAG options.
6. **Paper:** for each, pick prompt eng / RAG / fine-tune / continued pre-training:
   answers from a policy wiki updated daily · always reply in our JSON schema & brand tone · understand
   unlabeled oncology papers · translate a single email.
7. **Quiz:** `python quiz/quiz.py --domain 3`

## Traps

- "Data changes frequently" → RAG, not fine-tuning.
- Fine-tuning = labeled pairs; continued pre-training = unlabeled domain text.
- ROUGE↔summarization, BLEU↔translation (mnemonic: **B**LEU = **B**ilingual).
- Higher temperature does not make answers more accurate.
