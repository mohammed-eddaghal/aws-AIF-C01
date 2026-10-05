# Domain 4 — Guidelines for Responsible AI (14%)

## Official objectives (v1.1, condensed)

- **4.1 Responsible development:** features of responsible AI (bias, fairness, inclusivity, robustness, safety,
  veracity) · tools (**Bedrock Guardrails**) · responsible model selection (environmental impact, sustainability) ·
  legal risks of GenAI (IP infringement, biased output, loss of trust, end-user risk, hallucinations) ·
  dataset characteristics (inclusive, diverse, curated, balanced) · effects of bias and variance
  (demographic impact, inaccuracy, over/underfitting) · detect/monitor bias (label quality, human audits, subgroup analysis).
- **4.2 Transparency & explainability:** transparent vs opaque models · tools (**SageMaker Model Cards,
  SageMaker Clarify, Bedrock Model Evaluation**, open-source models/data/licensing) · safety vs transparency
  tradeoffs (interpretability vs performance) · human-centered design (user feedback, decision transparency).

## Must-know concepts

**AWS dimensions of responsible AI:** fairness, explainability, privacy & security, safety, controllability,
veracity & robustness, governance, transparency.

- **Bias** (data or model) → unfair outcomes for groups. Sources: unrepresentative/imbalanced data, biased labels,
  historical bias, proxies (zip code ≈ ethnicity). Detect: subgroup metrics, label audits, Clarify bias metrics.
- **Transparent model** = you can see how it decides (linear regression, decision tree). **Explainable** = you can
  explain a given output, even for a black box (SHAP feature attributions, partial dependence).
  Tradeoff: simple models are interpretable but often less accurate; deep nets/FMs perform better but are opaque.
  High-stakes regulated decisions (credit, hiring) → favor interpretability.
- **Human-centered explainable AI:** show *why*, show confidence, let users give feedback/override, human in the loop
  for consequential decisions (**Amazon Augmented AI (A2I)** for human review workflows).
- **Legal risks:** copyright/IP of generated content, defamation/hallucinations, privacy, bias/discrimination,
  loss of customer trust. Mitigate: guardrails, citations, human review, licensing checks, indemnified models.
- **Sustainability:** choose the smallest model that meets requirements, reuse FMs instead of training,
  efficient hardware (Graviton, Inferentia, Trainium), regions with lower carbon.

### Bedrock Guardrails (know every policy)
| Policy | Does |
|---|---|
| Content filters | Hate, insults, sexual, violence, misconduct + **prompt attack** filter, configurable strength |
| Denied topics | Block topics you define ("no investment advice") |
| Word filters | Block words/profanity |
| Sensitive information filters | Detect & block/mask **PII** or custom regex |
| Contextual grounding check | Flag responses not grounded in source / not relevant → hallucination control |
| Automated Reasoning checks | Verify answers against formal policy rules |
Works on input and output, with any FM, also via `ApplyGuardrail` API without invoking a model.

### SageMaker tools
| Tool | Purpose |
|---|---|
| SageMaker Clarify | Bias detection (pre/post training) + explainability (SHAP); also FM evaluation |
| SageMaker Model Cards | Document intended use, risk rating, training details, eval results (governance record) |
| SageMaker Model Monitor | Detect drift in data/quality/bias in production |
| SageMaker Ground Truth | Human labeling (+ RLHF data) |
| Amazon A2I | Human review loop for low-confidence predictions |

**AWS AI Service Cards** — AWS's own transparency docs for its AI services (intended use, limits, fairness).

## Repo lessons

- `phases/18-ethics-safety-alignment/20-bias-representational-harm`, `21-fairness-criteria-group-individual-counterfactual` ← core
- `phases/18-ethics-safety-alignment/26-model-system-dataset-cards` ← core (maps to Model Cards)
- `phases/18-ethics-safety-alignment/27-data-provenance-training-governance`
- `phases/18-ethics-safety-alignment/23-watermarking-synthid-stable-signature-c2pa`, `29-moderation-systems-openai-perspective-llamaguard`
- `phases/02-ml-fundamentals/10-bias-variance`, `17-imbalanced-data`
- `phases/11-llm-engineering/12-guardrails`

Skip for this exam: alignment research lessons 06–11, 17–19, 28 (interesting, not tested).

## Exercises

1. `python labs/lab05_guardrails.py` — create a guardrail with a denied topic, PII masking and grounding check; test 4 inputs.
2. **Paper:** a loan model approves 70% of group A, 40% of group B with equal qualifications. Name 3 possible causes and 2 AWS tools to investigate. (Clarify, Model Monitor bias drift, label audit)
3. **Write a model card** (half page) for the capstone assistant: intended use, out-of-scope use, data, risks, eval.
4. **Read:** one AWS AI Service Card (e.g. Amazon Rekognition face matching).
5. **Quiz:** `python quiz/quiz.py --domain 4`

## Traps

- Clarify = bias + explainability. Model Cards = documentation. Model Monitor = production drift. Don't swap them.
- Guardrails don't retrain the model; they filter inputs/outputs.
