# AWS Certified AI Practitioner (AIF-C01) — Prep Path

> Learn the concepts by building small things on AWS, then prove it with original practice questions.

Study path for **AIF-C01**, built on top of the
[AI Engineering from Scratch](https://github.com/mohammed-eddaghal/ai-engineering-from-scratch)
curriculum (`phases/`). The repo gives depth (how things work); this folder narrows it to
what the AWS exam measures, plus the AWS services and console practice the repo does not cover.

**Exam guide version:** 1.1 (published 2026-04-30) · **Last verified:** 2026-10-05

## Exam at a glance (official)

| Item | Value |
|---|---|
| Questions | 65 (50 scored + 15 unscored, not identified) |
| Duration | 90 minutes |
| Cost | 100 USD |
| Passing score | 700 / 1000 (scaled, compensatory — no per-domain minimum) |
| Question types | Multiple choice, multiple response, ordering, matching |
| Delivery | Pearson VUE test center or online proctored |
| Languages | incl. English, French (France), Arabic |
| Target candidate | ≤ 6 months exposure to AI/ML on AWS; *uses* AI, does not build models |

**Out of scope:** coding models, feature engineering, hyperparameter tuning, building pipelines,
math/stats analysis, implementing security or governance. → Don't over-study the math phases of the repo.

## Domains

| # | Domain | Weight | ≈ scored Qs | Notes |
|---|---|---:|---:|---|
| 1 | Fundamentals of AI and ML | 20% | 10 | [domains/1-ai-ml-fundamentals.md](domains/1-ai-ml-fundamentals.md) |
| 2 | Fundamentals of GenAI | 24% | 12 | [domains/2-genai-fundamentals.md](domains/2-genai-fundamentals.md) |
| 3 | Applications of Foundation Models | **28%** | 14 | [domains/3-foundation-model-applications.md](domains/3-foundation-model-applications.md) |
| 4 | Guidelines for Responsible AI | 14% | 7 | [domains/4-responsible-ai.md](domains/4-responsible-ai.md) |
| 5 | Security, Compliance, Governance | 14% | 7 | [domains/5-security-compliance-governance.md](domains/5-security-compliance-governance.md) |

Domains 2 + 3 = 52% of the exam: that is where Bedrock, RAG, prompting, agents and evaluation live.

**New in v1.1** (older courses/dumps miss these): agentic AI, MCP, multi-agent patterns, context
engineering, token pricing, Kiro, Strands Agents, Amazon Bedrock AgentCore (+ AgentCore Identity / Policy),
Amazon Quick, Bedrock Prompt Management, LLM-as-a-judge, model distillation, hallucination grounding,
traditional ML vs FM choice. Amazon Bedrock PartyRock and SageMaker Data Wrangler/Feature Store examples were dropped.

## 6-week path (~6–8 h/week)

| Week | Focus | Read (domain note + repo lessons) | Do | Gate |
|---|---|---|---|---|
| 0 | Setup | [labs/README.md](labs/README.md) | AWS account, Budget alarm, IAM user, CLI, Bedrock in `us-east-1` | `aws sts get-caller-identity` works |
| 1 | D1 AI/ML fundamentals | Domain 1 + repo phase 02 | [lab01](labs/lab01_ml_metrics.py) (offline), AI-services lab [lab04](labs/lab04_ai_services.py) | `python quiz/quiz.py --domain 1` ≥ 80% |
| 2 | D2 GenAI fundamentals | Domain 2 + repo phases 07, 10, 11, 13, 14 (selected) | [lab02](labs/lab02_bedrock_basics.py): tokens, temperature, cost | `--domain 2` ≥ 80% |
| 3 | D3 FM applications (1/2) | Domain 3: prompting, RAG, customization | [lab03](labs/lab03_rag.py): RAG from scratch on Bedrock | — |
| 4 | D3 FM applications (2/2) | Domain 3: fine-tuning, evaluation, agents | lab01 ROUGE/BLEU part, Bedrock console: Prompt Management, Model Evaluation | `--domain 3` ≥ 80% |
| 5 | D4 + D5 | Domains 4, 5 + repo phase 18, 17 (selected) | [lab05](labs/lab05_guardrails.py) Guardrails; read the GenAI Security Scoping Matrix | `--domain 4`, `--domain 5` ≥ 80% |
| 6 | Capstone + exam sim | [capstone/README.md](capstone/README.md) | Capstone; AWS Official Practice Exam; `python quiz/quiz.py --mock` | ≥ 85% everywhere → book the exam |

Track progress in [PROGRESS.md](PROGRESS.md).

## Official AWS resources (use these, they're free unless noted)

1. **Exam guide** — https://docs.aws.amazon.com/aws-certification/latest/ai-practitioner-01/ai-practitioner-01.html
   (also the in-scope services list: `.../aif-01-in-scope-services.html` and the v1.0→v1.1 diff: `.../aif-01-revisions.html`)
2. **Skill Builder 4-step Exam Prep Plan** — https://skillbuilder.aws/category/exam-prep/ai-practitioner-AIF-C01
   1. Get to know the exam: exam guide + **Official Practice Question Set** (free)
   2. Learn the topics: **Exam Prep Standard Course (AIF-C01)** (free) and the companion courses
      *Fundamentals of ML and AI*, *Exploring AI Use Cases and Applications*, *Responsible AI Practices*,
      *Developing ML Solutions*, *Developing GenAI Solutions*, *Essentials of Prompt Engineering*,
      *Optimizing Foundation Models*, *Security, Compliance, and Governance for AI Solutions*
   3. Practice on AWS: AWS Builder Labs, AWS Jam, AWS Cloud Quest, AWS SimuLearn, AWS Escape Room
      (the Enhanced plan with labs/pretest/flashcards needs a Skill Builder subscription)
   4. Assess readiness: **Official Pretest** and **Official Practice Exam**
3. **Certification page / booking** — https://aws.amazon.com/certification/certified-ai-practitioner/

Course names on Skill Builder change often; check the plan page for the current list.

## Folder layout

```
aws-ai-practitioner-prep/
├── README.md            this roadmap
├── PROGRESS.md          checklist you tick off
├── domains/             one study note per exam domain (objectives, concepts, services, repo lessons, exercises, traps)
├── labs/                hands-on: 1 offline + 4 cheap AWS labs (cents), setup and cleanup
├── quiz/                50 original questions weighted like the exam + stdlib runner
└── capstone/            end-to-end project tying all 5 domains together
```

## Rules (same as the repo's certification tracks)

- The public exam guide defines coverage; AWS docs define current behavior.
- Every practice question here is original. No dumps.
- Quiz scores are raw percentages, not AWS scaled scores.
- Build > read. Each week ends with something you ran.

Independent study material, not affiliated with or endorsed by AWS.
