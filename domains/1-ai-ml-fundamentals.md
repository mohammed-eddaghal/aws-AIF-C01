# Domain 1 — Fundamentals of AI and ML (20%)

Repo paths below are relative to a clone of
`https://github.com/mohammed-eddaghal/ai-engineering-from-scratch` (read `docs/en.md` in each lesson).
For this exam read the **concept** and **problem** sections; skim the from-scratch code.

## Official objectives (v1.1, condensed)

- **1.1 Concepts:** AI, ML, deep learning, neural networks, CV, NLP, model, algorithm, training vs inference,
  bias, fairness, fit, LLM, GenAI, agentic AI · inference types (batch, real-time, asynchronous, serverless) ·
  data types (labeled/unlabeled, tabular, time-series, image, text, structured/unstructured) ·
  supervised / unsupervised / reinforcement learning.
- **1.2 Use cases:** where AI adds value (decision support, scale, automation) · when **not** to use AI
  (cost/benefit, need an exact outcome instead of a prediction) · regression vs classification vs clustering ·
  real-world apps (CV, NLP, speech, recommendations, fraud, forecasting, knowledge bases, agents) ·
  AWS managed AI services · **traditional ML vs foundation model** (regulation, explainability, ops constraints).
- **1.3 Lifecycle:** AI/ML pipeline components · sources of models (open-source pre-trained vs custom) ·
  serving (managed API vs self-hosted) · AWS service per stage (Bedrock, Quick, Kiro, SageMaker AI) ·
  MLOps (experimentation, repeatability, scale, tech debt, monitoring, re-training) ·
  metrics (accuracy, precision, recall, F1) and business metrics (cost per user, dev cost, feedback, ROI).

## Must-know concepts

**Nesting:** AI ⊃ ML ⊃ Deep learning ⊃ GenAI (FMs/LLMs). *Agentic AI* = a model in a loop that plans, calls
tools and acts toward a goal.

**Learning types**
| Type | Data | Typical task | Example |
|---|---|---|---|
| Supervised | labeled | classification (category), regression (number) | spam y/n, house price |
| Unsupervised | unlabeled | clustering, dimensionality reduction, anomaly detection | customer segments |
| Reinforcement | reward signal | sequential decisions | robotics, RLHF, games |
| Self-supervised | raw text/images | predict masked/next token | how FMs are pre-trained |

**Inference types (SageMaker AI terms — very testable)**
| Need | Choose |
|---|---|
| Low latency, steady traffic, per-request | Real-time endpoint |
| Big dataset, no one waiting, offline | Batch transform / batch inference |
| Large payloads (≤ 1 GB) or long processing (minutes), queue it | Asynchronous inference |
| Spiky/intermittent traffic, tolerate cold starts, pay per use | Serverless inference |

**Fit:** overfitting = great on train, poor on test (high variance). Underfitting = poor on both (high bias).
Fixes: more/better data, regularization, simpler model (overfit) · more features, bigger model (underfit).

**Metrics** (from the confusion matrix)
- Accuracy = correct / all — misleading on imbalanced data.
- Precision = TP / (TP+FP) — "when I say yes, am I right?" → optimize when **false positives** are costly (spam filter hiding real mail).
- Recall = TP / (TP+FN) — "did I catch them all?" → optimize when **false negatives** are costly (fraud, cancer screening).
- F1 = harmonic mean of precision and recall. AUC-ROC = threshold-independent ranking quality.
- Regression: MAE, RMSE, R².

**When NOT to use ML:** a deterministic rule gives the exact answer (tax calc, pricing formula), not enough data,
cost > benefit, or the decision must be fully explainable and a simple rule does it.

**Traditional ML vs FM:** tabular prediction, strict explainability/regulation, low latency/cost → traditional ML
(e.g. XGBoost on SageMaker). Open-ended language/vision, little labeled data, fast to prototype → FM on Bedrock.

**ML pipeline:** business problem → data collection → EDA → pre-processing → feature engineering → training →
tuning → evaluation → deployment → monitoring (drift) → re-training. MLOps makes this repeatable and automated.

## AWS services for this domain

| Service | One-liner |
|---|---|
| Amazon SageMaker AI | Build, train, deploy, monitor your own ML models (Canvas = no-code, Studio, Pipelines, Model Monitor, Clarify, Model Cards, Ground Truth = labeling) |
| SageMaker JumpStart | Hub of pre-trained/open models you deploy into your account |
| Amazon Bedrock | Serverless API access to foundation models (Anthropic, Amazon Nova, Meta, Mistral…) |
| Amazon Rekognition | Image/video analysis: objects, faces, moderation |
| Amazon Textract | Extract text, forms, tables from documents (beyond OCR) |
| Amazon Comprehend | NLP: sentiment, entities, key phrases, language, PII, topic modeling |
| Amazon Transcribe | Speech → text |
| Amazon Polly | Text → speech |
| Amazon Translate | Neural machine translation |
| Amazon Lex | Chatbots / voice bots (same tech as Alexa) |
| Amazon Personalize | Recommendations |
| Amazon Quick | Agentic business workspace (research, BI dashboards from QuickSight, automations) for non-developers |
| Kiro | AWS agentic IDE: spec-driven development with AI agents |
| AWS Transform | Agentic AI for migrating/modernizing legacy code and workloads |

Exam pattern: "**without ML expertise**" → a managed AI service (Comprehend, Rekognition…) or Bedrock, not SageMaker.

## Repo lessons

- `phases/02-ml-fundamentals/01-what-is-machine-learning`
- `phases/02-ml-fundamentals/07-unsupervised-learning`
- `phases/02-ml-fundamentals/09-model-evaluation` ← metrics, core
- `phases/02-ml-fundamentals/10-bias-variance` ← fit, core
- `phases/02-ml-fundamentals/13-ml-pipelines`
- `phases/02-ml-fundamentals/15-time-series`, `16-anomaly-detection`, `17-imbalanced-data`
- `phases/03-deep-learning-core/01-the-perceptron`, `02-multi-layer-networks` (neural network intuition only)
- `phases/09-reinforcement-learning/01-mdps-states-actions-rewards`
- `phases/17-infrastructure-and-production/01-managed-llm-platforms`, `15-batch-apis`

Skip for this exam: phase 01 (math), backprop/optimizer internals, hyperparameter tuning code.

## Exercises

1. **Paper:** for each, pick supervised/unsupervised/RL and regression/classification/clustering:
   churn yes/no · next month's sales · group support tickets by theme · robot learns to walk · detect odd card transactions with no labels.
2. **Paper:** a model flags fraud; 1,000 transactions, 20 frauds; it flags 30, 15 truly fraud. Compute precision, recall, F1. (Answer: P=0.50, R=0.75, F1=0.60)
3. **Code (offline):** `python labs/lab01_ml_metrics.py` — confusion matrix + metrics from scratch, then change the threshold and watch precision/recall trade off.
4. **AWS:** `python labs/lab04_ai_services.py` — Comprehend + Translate + Polly on one review.
5. **Console tour (free to look):** SageMaker AI → Inference → endpoint config options (real-time / serverless / async). Don't deploy.
6. **Quiz:** `python quiz/quiz.py --domain 1`

## Traps

- Accuracy on imbalanced data (99% "not fraud" model is useless).
- Textract ≠ Rekognition (documents vs images/video). Comprehend ≠ Lex (analysis vs conversation).
- "Real-time" is not the default answer — read for payload size, latency, traffic shape.
