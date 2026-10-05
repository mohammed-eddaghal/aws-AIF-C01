# Labs

| Lab | Needs AWS | Cost | Domains |
|---|---|---|---|
| `lab01_ml_metrics.py` — confusion matrix, precision/recall/F1, threshold trade-off, ROUGE-1, BLEU-1 | no | free | 1, 3 |
| `lab02_bedrock_basics.py` — Converse API, tokens, cost per call, temperature & nondeterminism | yes | < $0.01 | 2, 3 |
| `lab03_rag.py` — RAG from scratch: chunk → Titan embeddings → cosine search → grounded answer | yes | < $0.01 | 2, 3, 5 |
| `lab04_ai_services.py` — Comprehend (sentiment, entities, PII), Translate, Polly | yes | < $0.01 (free tier covers it) | 1 |
| `lab05_guardrails.py` — Bedrock Guardrails: denied topic, PII mask, prompt attack, grounding check | yes | < $0.01 | 3, 4, 5 |

All labs are plain Python + `boto3`, no frameworks. Labs **don't** create Knowledge Bases or OpenSearch
Serverless on purpose: a vector collection bills by the hour (hundreds of $/month) even when idle. The exam
only needs you to *know* Knowledge Bases; lab03 shows the same mechanics locally.

## Setup (once, ~30 min)

1. **AWS account** — use a personal/sandbox account, not a work production account.
2. **Budget alarm first:** Billing → Budgets → *Create budget* → *Zero spend budget* or a 5 USD monthly cost budget with email alert.
3. **IAM user for labs** (don't use root): IAM → Users → create `aif-lab`, attach the policy below, create an access key (CLI use).
4. **AWS CLI + Python:**
   ```bash
   pip install -r labs/requirements.txt
   ```
   ```bash
   aws configure
   ```
   (region `us-east-1`; Bedrock model availability is broadest there)
   ```bash
   aws sts get-caller-identity
   ```
5. **Bedrock model access:** Bedrock console → Model catalog → open *Amazon Nova Micro* and *Titan Text Embeddings V2*.
   Serverless models are enabled on first use in most accounts; if the console shows a *Request access* button, request it.

### Least-privilege policy

Paste into IAM → Policies → Create (JSON). This is also Domain 5 exercise 1.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "InvokeOnlyLabModels",
      "Effect": "Allow",
      "Action": ["bedrock:InvokeModel"],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0",
        "arn:aws:bedrock:*:*:inference-profile/us.amazon.nova-micro-v1:0",
        "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0"
      ]
    },
    {
      "Sid": "Guardrails",
      "Effect": "Allow",
      "Action": ["bedrock:CreateGuardrail", "bedrock:ApplyGuardrail", "bedrock:DeleteGuardrail", "bedrock:GetGuardrail"],
      "Resource": "*"
    },
    {
      "Sid": "AIServices",
      "Effect": "Allow",
      "Action": ["comprehend:DetectSentiment", "comprehend:DetectEntities", "comprehend:DetectPiiEntities",
                 "translate:TranslateText", "polly:SynthesizeSpeech"],
      "Resource": "*"
    }
  ]
}
```

The Converse API is authorized by `bedrock:InvokeModel`. Console playgrounds need broader read
permissions — use your admin user for console exercises.

## Model IDs

Defaults live at the top of each script and can be overridden with env vars:

- `AIF_MODEL_ID` (default `us.amazon.nova-micro-v1:0` — cross-region inference profile, the cheapest Bedrock text model)
- `AIF_EMBED_MODEL_ID` (default `amazon.titan-embed-text-v2:0`)

## Cleanup

- lab05 deletes its guardrail at the end. Check Bedrock → Guardrails is empty.
- lab04 writes `review.mp3` locally only.
- Nothing else creates standing resources. Review Billing → Bills after week 6, then deactivate the access key.
