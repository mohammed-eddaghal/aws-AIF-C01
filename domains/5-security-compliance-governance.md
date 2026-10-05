# Domain 5 — Security, Compliance, and Governance for AI (14%)

## Official objectives (v1.1, condensed)

- **5.1 Securing AI:** IAM roles/policies/permissions, encryption, **Amazon Macie**, **AWS PrivateLink**,
  shared responsibility model, **AgentCore Identity**, **Policy in AgentCore**, Bedrock Guardrails · source
  citation & data origins (lineage, cataloging, Model Cards) · secure data engineering (quality, privacy-enhancing
  tech, access control, integrity) · security & privacy (app security, threat detection, vulnerability management,
  infra protection, **prompt injection**, encryption at rest/in transit, **data leakage prevention**, output
  filtering, **audit logging of AI interactions**, toxicity) · **hallucination detection & grounding** (RAG,
  output validation, confidence scoring).
- **5.2 Governance & compliance:** **AWS Config, Amazon Inspector, AWS Artifact, AWS CloudTrail, AWS Trusted Advisor** ·
  data governance (lifecycle, logging, residency, monitoring, observation, retention) · governance processes
  (policies, review cadence, frameworks like the **Generative AI Security Scoping Matrix**, transparency standards, training).

## Must-know concepts

**Shared responsibility:** AWS = security *of* the cloud (hardware, facilities, managed-service infrastructure,
the Bedrock service itself). Customer = security *in* the cloud (IAM, data, encryption choices, network config,
prompts, guardrails, how outputs are used).

**Bedrock data privacy facts:** prompts and outputs are not used to train base models and are not shared with
model providers; data stays in the region; encrypted in transit (TLS) and at rest (KMS, optional customer-managed keys);
fine-tuned models are private copies.

### Service → when the question says…
| Service | Trigger phrase |
|---|---|
| IAM (roles, policies, least privilege) | who/what can call `bedrock:InvokeModel`, restrict models |
| AWS KMS | encryption keys, customer-managed keys |
| AWS Secrets Manager | store API keys/credentials, rotation |
| Amazon Macie | discover **PII/sensitive data in S3** (e.g. before training) |
| AWS PrivateLink / VPC endpoints | reach Bedrock/SageMaker **without the public internet** |
| AWS CloudTrail | **who called which API when** — audit trail |
| Amazon CloudWatch | metrics, logs, alarms (Bedrock **model invocation logging** → CloudWatch Logs/S3) |
| AWS Config | track resource configuration changes, evaluate compliance rules |
| Amazon Inspector | automated **vulnerability scanning** (EC2, ECR images, Lambda) |
| AWS Artifact | download **AWS compliance reports** (SOC, ISO, PCI) and agreements |
| AWS Trusted Advisor | best-practice checks (cost, security, limits, resilience) |
| AWS Audit Manager | continuously collect evidence for audits (has a GenAI framework) |
| Amazon GuardDuty | threat detection |
| AgentCore Identity | agent identity & credential management for accessing AWS/third-party tools on a user's behalf |
| Policy in AgentCore | deterministic rules on what tools/actions an agent may take |
| Bedrock Guardrails | prompt-attack filtering, PII redaction, toxicity, grounding |
| Lake Formation / Glue Data Catalog | data access control and cataloging (lineage) |

### Generative AI Security Scoping Matrix (AWS)
| Scope | You… | Example |
|---|---|---|
| 1 Consumer app | use a public GenAI app | public chatbot |
| 2 Enterprise app | use a SaaS app with GenAI features | SaaS with built-in AI |
| 3 Pre-trained models | build your app on an FM via API | app on Bedrock base model |
| 4 Fine-tuned models | fine-tune an FM on your data | Bedrock custom model |
| 5 Self-trained models | train from scratch | your own LLM |
Responsibility and control grow from 1 → 5. Scopes 1–2 = "buy", 3–5 = "build".

### Hallucination & grounding
RAG grounding with citations · Guardrails contextual grounding check · output validation (schema, rules, second-model check) ·
confidence scoring / thresholds → route low-confidence to humans.

### Data governance
Lifecycle (create → store → use → archive → delete), retention policies (S3 Lifecycle, Glacier), residency
(choose region), logging & monitoring, lineage (where training data came from), cataloging.

## Repo lessons

- `phases/14-agent-engineering/27-prompt-injection-defense`, `phases/18-ethics-safety-alignment/15-indirect-prompt-injection` ← core
- `phases/18-ethics-safety-alignment/12-red-teaming-pair-automated-attacks`, `13-many-shot-jailbreaking`
- `phases/17-infrastructure-and-production/25-security-secrets-audit`, `26-compliance-frameworks`, `13-llm-observability`
- `phases/18-ethics-safety-alignment/22-differential-privacy-for-llms`, `24-regulatory-frameworks-eu-us-uk-korea`
- `phases/13-tools-and-protocols/15-mcp-security-tool-poisoning`, `16-mcp-security-oauth-2-1`

## Exercises

1. **IAM:** create a policy that allows `bedrock:InvokeModel` only on Nova Micro (see [labs/README.md](../labs/README.md#least-privilege-policy)), attach it to your lab user, and confirm a call to another model is denied.
2. **Audit:** after running a lab, open CloudTrail → Event history → filter Event source `bedrock.amazonaws.com`. Find your calls.
3. **Console:** Bedrock → Settings → Model invocation logging (read the options; enable to CloudWatch only if you want, then disable).
4. **Console (free):** AWS Artifact → Reports → find the SOC 2 report.
5. **Paper:** place 5 example use cases on the Scoping Matrix.
6. **Quiz:** `python quiz/quiz.py --domain 5`

## Traps

- CloudTrail (API audit) ≠ CloudWatch (metrics/logs) ≠ Config (resource config history).
- Artifact = AWS's compliance documents, not your artifacts.
- Macie scans S3 for sensitive data; Inspector scans workloads for vulnerabilities.
