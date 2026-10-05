# Lab 00 — AWS setup (account, budget, IAM, CLI, Bedrock access)

| | |
|---|---|
| **Needs AWS?** | Yes (account, console, CLI) |
| **Cost** | Free. Nothing here creates a billable resource. The optional Bedrock test call at the end costs a tiny fraction of a cent. |
| **Time** | 30–45 min |
| **Exam domains** | Domain 5 — **5.1** (IAM policies, least privilege, shared responsibility), **5.2** (governance, audit with CloudTrail) · Domain 2 — **2.3** (cost trade-offs, regional coverage) |

## What you'll learn

- How to set up a safe, cheap AWS sandbox for every lab in this course.
- How to stop surprise bills *before* they happen (budget alarm).
- How to protect the root user and why you never use it day to day.
- How to write and read a **least-privilege IAM policy** for Amazon Bedrock — this is real Domain 5 practice, not just setup.
- How the AWS CLI and Python SDK (`boto3`) find your credentials and region.
- How Bedrock model access works for Amazon Nova Micro and Titan Text Embeddings V2.

## Background

**AWS account and root user.** When you sign up, you get one *root user* (the email address you signed up with). Root can do everything, including closing the account and changing billing. Best practice: protect root with MFA, use it only for the few tasks that need it, and do daily work with a less powerful identity.

**IAM (Identity and Access Management).** IAM decides *who* can do *what* on *which* resources.

- An **IAM user** is a long-lived identity (here: `aif-lab`). It can have a console password, access keys, or both.
- An **IAM policy** is a JSON document that lists permissions. AWS denies everything by default (*implicit deny*). A policy grants specific actions with `"Effect": "Allow"`. An explicit `"Deny"` always wins over any Allow.
- **Least privilege** means granting only the permissions a task actually needs. The exam loves this phrase.
- An **IAM role** is an identity with no long-lived credentials that something assumes temporarily (an EC2 instance, a Lambda function, a person through single sign-on). For production, AWS recommends roles and temporary credentials over access keys. This course uses an access key only because it is the simplest way to run local scripts.

**Access keys.** A pair: *access key ID* (starts with `AKIA…`) and *secret access key*. Together they sign API calls from the CLI and SDKs. Anyone who has them *is* you, so treat them like a password.

**Regions.** AWS services run in geographic regions (`us-east-1` = N. Virginia). Models available in Amazon Bedrock differ by region; `us-east-1` has broad coverage, which is why the labs use it.

**Cross-region inference profile.** The lab default model ID is `us.amazon.nova-micro-v1:0`. The `us.` prefix means an *inference profile*: Bedrock may route your request to the model in one of several US regions to get more capacity. That detail matters for the IAM policy below.

**Shared responsibility.** AWS secures the infrastructure and the Bedrock service itself (security *of* the cloud). You secure your identities, keys, permissions and data (security *in* the cloud). Everything in this lab is on *your* side of that line.

## Steps

### 1. Use a sandbox account

1. Use a personal or dedicated sandbox AWS account — **not** a work production account. If you do not have one, create it at https://aws.amazon.com/ (*Create an AWS Account*). You need an email address, a phone number and a payment card.
2. Sign in to the console as root once, to finish steps 2 and 3.

> New accounts may come with a free plan or credits; offers change, so read what the sign-up page says today. The labs in this course cost cents either way.

### 2. Create a budget alarm (do this first)

1. In the console search bar type **Billing and Cost Management** and open it.
2. Left menu → **Budgets** → **Create budget**.
3. Choose **Use a template (simplified)**.
4. Pick one:
   - **Zero spend budget** — emails you as soon as spending goes above 0.01 USD. Best for this course.
   - **Monthly cost budget** — set the amount to **5** USD.
5. Enter your email address under *Email recipients*.
6. Click **Create budget**.

> A budget **alerts**; it does **not** stop spending. Billing data can also take several hours to update, so an alert is a smoke detector, not a fire wall. Cleaning up resources is still your job.

### 3. Turn on MFA for the root user

1. Top-right corner → click your account name → **Security credentials**.
2. Section **Multi-factor authentication (MFA)** → **Assign MFA device**.
3. Give it a name (e.g. `root-phone`), choose **Authenticator app** (or a passkey / security key if you have one) → **Next**.
4. Scan the QR code with an authenticator app (Google Authenticator, Microsoft Authenticator, 1Password, etc.).
5. Type two consecutive codes → **Add MFA**.
6. Sign out and back in to confirm the MFA prompt appears.

### 4. (Recommended) A console admin identity

Console playgrounds (used in Lab 02 and later) need broader read permissions than the lab policy grants. Do not use root for that. Either:

- set up **IAM Identity Center** and a user with the `AdministratorAccess` permission set (AWS's recommended route), or
- create a second IAM user (e.g. `admin`) with **console access**, the `AdministratorAccess` managed policy, and MFA.

Use this admin identity for console work; use `aif-lab` for the scripts.

### 5. Create the least-privilege policy

1. Console → **IAM** → left menu **Policies** → **Create policy**.
2. Switch the editor from *Visual* to **JSON**.
3. Delete what is there and paste exactly this (copied from [labs/README.md](../labs/README.md)):

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

4. **Next** → Policy name: `AifLabPolicy` → **Create policy**.

#### The policy, line by line

| Line | Meaning |
|---|---|
| `"Version": "2012-10-17"` | The version of the IAM policy *language*. Always use this value; it is not a date you update. |
| `"Statement": [...]` | A list of permission rules. Each one is evaluated independently. |
| `"Sid"` | Statement ID: a free-text label for humans. It has no effect on permissions. |
| `"Effect": "Allow"` | This statement grants. There are no `Deny` statements here; everything not allowed stays implicitly denied. |

**Statement 1 — `InvokeOnlyLabModels`**

- `"Action": ["bedrock:InvokeModel"]` — permission to run inference. The **Converse API** used by the labs is authorized by this same action. Note what is *missing*: no `bedrock:InvokeModelWithResponseStream` (streaming), no model customization, no listing models, no Knowledge Bases or Agents.
- `"Resource"` — *which* models. An ARN (Amazon Resource Name) has the shape `arn:partition:service:region:account-id:resource`.
  - `arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0` — the Nova Micro base model. The region is `*` and the account field is **empty** (`::`) because foundation models are owned by AWS, not by your account.
  - `arn:aws:bedrock:*:*:inference-profile/us.amazon.nova-micro-v1:0` — the US cross-region inference profile. Profiles do carry an account ID, so that field is `*`.
  - Why both, and why region `*`? When you call a cross-region profile, IAM checks the profile **and** the underlying foundation model in whichever US region Bedrock routes to. Allowing only one of them, or only `us-east-1`, can produce intermittent `AccessDeniedException` errors.
  - `amazon.titan-embed-text-v2:0` — the embedding model used for RAG in Lab 03. Embedding calls also use `InvokeModel`.
  - Any other model (Nova Lite, Claude, Llama…) is denied. That is least privilege, and it also caps cost: the learner cannot accidentally call an expensive model.

**Statement 2 — `Guardrails`**

- Create, apply, read and delete Amazon Bedrock Guardrails (Lab 05). `ApplyGuardrail` checks text against a guardrail without calling a model.
- `"Resource": "*"` is broader than needed. A tighter version would use the guardrail ARN pattern for your account and region (e.g. `arn:aws:bedrock:us-east-1:<account-id>:guardrail/*`). Try tightening it as an exercise once Lab 05 works.

**Statement 3 — `AIServices`**

- Real-time calls to Amazon Comprehend (sentiment, entities, PII detection), Amazon Translate and Amazon Polly (Lab 04). These APIs process the text you send rather than a resource you own, so `"*"` is the normal resource value for them.

**Also notice:** no `sts:GetCallerIdentity` permission is listed, yet step 9 works. That API needs no permission — it only tells you who you are.

### 6. Create the IAM user `aif-lab`

1. IAM → **Users** → **Create user**.
2. User name: `aif-lab`. Leave **Provide user access to the AWS Management Console** *unticked* (this user is for scripts only) → **Next**.
3. Permissions options: **Attach policies directly** → search `AifLabPolicy` → tick it → **Next** → **Create user**.

### 7. Create an access key

1. IAM → Users → **aif-lab** → tab **Security credentials** → **Access keys** → **Create access key**.
2. Use case: **Command Line Interface (CLI)**. The console will suggest alternatives (Identity Center, CloudShell) — that is the "prefer temporary credentials" best practice. Tick the confirmation box → **Next**.
3. Description tag: `aif-c01 labs` → **Create access key**.
4. **Download .csv file** or copy both values now. The secret is shown only once.
5. Store the file somewhere outside this repository (a password manager is ideal).

### 8. Install Python and AWS CLI v2

You need Python 3.10 or newer (recent `boto3` releases drop old Python versions) and AWS CLI **version 2**.

**Windows (PowerShell):**

```powershell
winget install -e --id Python.Python.3.12
winget install -e --id Amazon.AWSCLI
# close and reopen PowerShell so PATH is refreshed, then:
python --version
aws --version
```

No `winget`? Download Python from https://www.python.org/downloads/ (tick *Add python.exe to PATH*) and the CLI installer `AWSCLIV2.msi` from https://awscli.amazonaws.com/AWSCLIV2.msi.

**macOS:**

```bash
brew install python awscli          # or use the official .pkg installers
python3 --version
aws --version
```

**Linux (x86_64):**

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
python3 --version
aws --version
```

`aws --version` should print something starting with `aws-cli/2.` If it starts with `aws-cli/1.`, you have the old CLI; uninstall it (`pip uninstall awscli`) and install v2.

### 9. Install the Python dependency

From the repository root. A virtual environment keeps `boto3` separate from other projects.

**Windows (PowerShell):**

```powershell
python -m venv .venv
# if activation is blocked by execution policy, allow it for this window only:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r labs/requirements.txt
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r labs/requirements.txt
```

`labs/requirements.txt` contains one line, `boto3>=1.35`. Lab 01 needs nothing at all (standard library only).

### 10. Configure the CLI

```bash
aws configure
```

Answer the four prompts:

```text
AWS Access Key ID [None]: AKIA................
AWS Secret Access Key [None]: ****************************************
Default region name [None]: us-east-1
Default output format [None]: json
```

This writes two files in your home folder: `~/.aws/credentials` (keys) and `~/.aws/config` (region, output). On Windows that is `C:\Users\<you>\.aws\`. Both the CLI and `boto3` read them, which is why the lab scripts never contain keys.

> Already have a `default` profile for something else? Use a named profile instead: `aws configure --profile aif-lab`, then set `$env:AWS_PROFILE = "aif-lab"` (PowerShell) or `export AWS_PROFILE=aif-lab` (bash) in each terminal you use for the labs.

### 11. Check who you are

```bash
aws sts get-caller-identity
```

Expected shape (your values differ):

```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/aif-lab"
}
```

The `Arn` must end in `user/aif-lab`. If it shows `root` or another user, the wrong credentials are being picked up (see Troubleshooting). This is the Week 0 gate in the course plan.

### 12. Bedrock model access

1. Sign in to the console with your **admin** identity, region selector (top right) = **US East (N. Virginia) us-east-1**.
2. Open **Amazon Bedrock** → **Model catalog**.
3. Open **Amazon Nova Micro**, then **Titan Text Embeddings V2**, and read each model card (modalities, context length, regions).
4. AWS now enables serverless models automatically on first use in most accounts. If the console still shows a **Request access** / **Model access** button for either model, request access and wait until the status is *Access granted*.

### 13. Optional: one real call from the CLI

This proves IAM, region and model access together. Create a small file **outside the repo** (or delete it afterwards).

**PowerShell:**

```powershell
Set-Content -Path hello.json -Encoding ascii -Value '[{"role":"user","content":[{"text":"Say hello in five words."}]}]'
aws bedrock-runtime converse --model-id us.amazon.nova-micro-v1:0 --messages file://hello.json --region us-east-1
```

**bash:**

```bash
echo '[{"role":"user","content":[{"text":"Say hello in five words."}]}]' > hello.json
aws bedrock-runtime converse --model-id us.amazon.nova-micro-v1:0 --messages file://hello.json --region us-east-1
```

You get JSON with `output.message.content[0].text`, `stopReason`, `usage` (input/output token counts) and `metrics.latencyMs`. Lab 02 explains each field.

Now prove least privilege (Domain 5 exercise 1). Call a model the policy does **not** allow:

```bash
aws bedrock-runtime converse --model-id us.amazon.nova-lite-v1:0 --messages file://hello.json --region us-east-1
```

Expected: `AccessDeniedException ... is not authorized to perform: bedrock:InvokeModel on resource ...`. A denied call is not billed.

### 14. Environment variables for model IDs

The lab scripts read two optional variables. You only need them to switch models; the defaults are fine.

| Variable | Default |
|---|---|
| `AIF_MODEL_ID` | `us.amazon.nova-micro-v1:0` |
| `AIF_EMBED_MODEL_ID` | `amazon.titan-embed-text-v2:0` |

**PowerShell** (current window only):

```powershell
$env:AIF_MODEL_ID = "us.amazon.nova-micro-v1:0"
$env:AIF_EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"
echo $env:AIF_MODEL_ID
```

**bash / zsh** (current shell only):

```bash
export AIF_MODEL_ID="us.amazon.nova-micro-v1:0"
export AIF_EMBED_MODEL_ID="amazon.titan-embed-text-v2:0"
echo "$AIF_MODEL_ID"
```

If you point `AIF_MODEL_ID` at another model, you must also add that model to `AifLabPolicy`, and the cost constants in Lab 02 will no longer match.

## What just happened

You built the same layered setup a real team would, just smaller:

1. **Cost control** — budget alert before any usage.
2. **Account protection** — root locked behind MFA and kept out of daily work.
3. **Identity** — a dedicated user per purpose (`aif-lab` for scripts, admin for console).
4. **Authorization** — a customer-managed policy that allows one action on three model ARNs plus a few service calls. Everything else is implicitly denied, and you proved it with a denied call.
5. **Credentials** — stored by `aws configure` in your home folder, read automatically by the CLI and `boto3`'s *credential provider chain* (environment variables first, then the shared credentials/config files, then other sources such as SSO or instance roles).
6. **Region** — `us-east-1`, from `~/.aws/config`. The lab scripts create clients like `boto3.client("bedrock-runtime")` with no region argument, so this setting decides where calls go.

## Experiments

1. **See the audit trail.** Console (admin) → **CloudTrail** → **Event history** → filter *Event source* = `bedrock.amazonaws.com`. Find your `Converse` / `InvokeModel` call from step 13 and the denied one. Who made it (`userIdentity`)? Which region? (Domain 5 exercise 2.) *Predict first:* will the denied call appear? (Yes — CloudTrail records denied API calls with an error code.)
2. **Remove the profile ARN.** In a copy of the policy, delete the `inference-profile` line, attach the copy instead, and call `us.amazon.nova-micro-v1:0` again. Predict the result before you run it. Restore the original afterwards.
3. **Least privilege on listing.** Run `aws bedrock list-foundation-models --region us-east-1` as `aif-lab`. Predict: allowed or denied? (Denied — `bedrock:ListFoundationModels` is not in the policy.)
4. **Policy simulator.** Open the IAM Policy Simulator (https://policysim.aws.amazon.com/, signed in as admin), select user `aif-lab`, and test `bedrock:InvokeModel` against different model ARNs without making any call.

## Exam connection

- **"Restrict a team to one model"** → an IAM identity-based policy that allows `bedrock:InvokeModel` on specific foundation-model (and inference-profile) ARNs. Not Guardrails, not a VPC.
- **"Who called which model, when?"** → AWS CloudTrail (API calls). Prompt/response *content* logging is a different feature: Bedrock **model invocation logging** to CloudWatch Logs or S3.
- **"Prevent surprise cost"** → AWS Budgets alerts; cost is also capped by restricting which models can be invoked.
- **Shared responsibility** → securing access keys, IAM policies and MFA is the customer's job.

> **Exam tip:** "Least privilege" answers grant the *narrowest action on the narrowest resource*. If one option says `"Action": "bedrock:*"` and another lists only `bedrock:InvokeModel` on a model ARN, pick the second.

> **Exam tip:** Long-lived access keys are acceptable for a personal lab, but the exam's preferred answer for applications on AWS is an **IAM role** (temporary credentials), never embedding keys in code.

> **Exam tip:** Budgets *notify*; they don't block. If a question asks for automatic action on overspend, look for Budgets *actions* or other controls, not the alert alone.

## Check yourself

**1.** A company wants its developers to call only Amazon Nova Micro in Amazon Bedrock and nothing else. What is the MOST appropriate control?

A. A Bedrock guardrail with a denied topic for other models
B. An IAM policy allowing `bedrock:InvokeModel` only on the Nova Micro model ARNs
C. An AWS Budgets alert set to 0 USD
D. Disabling all other regions

<details><summary>Answer</summary>

**B.** IAM controls which actions on which resources are allowed. Guardrails filter content, not model choice (A). A budget only notifies (C). Region restrictions don't limit models inside an allowed region (D).
</details>

**2.** A developer's script calls a model through the cross-region inference profile `us.amazon.nova-micro-v1:0`. The IAM policy allows only `arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0`. Calls fail with `AccessDeniedException`. What is the most likely fix?

A. Request a service quota increase
B. Enable model invocation logging
C. Also allow the inference-profile ARN and the foundation model in the regions the profile can route to
D. Switch the output format of the AWS CLI to text

<details><summary>Answer</summary>

**C.** With an inference profile, IAM checks both the profile and the underlying model in the destination region. Quotas cause throttling, not access denied (A). Logging (B) and CLI format (D) don't affect authorization.
</details>

**3.** Under the AWS shared responsibility model, which task is the customer's responsibility when using Amazon Bedrock?

A. Patching the servers that host foundation models
B. Rotating and protecting the IAM access keys used to call Bedrock
C. Physical security of the data center
D. Maintaining the Bedrock service API endpoints

<details><summary>Answer</summary>

**B.** Identities and credentials are security *in* the cloud — the customer's job. A, C and D are AWS's responsibility.
</details>

**4.** A security team needs a record of which IAM principal invoked Bedrock models and when, for an audit. Which service provides this?

A. AWS CloudTrail
B. Amazon Inspector
C. AWS Trusted Advisor
D. Amazon Macie

<details><summary>Answer</summary>

**A.** CloudTrail records API calls with identity, time, source and region. Inspector scans for software vulnerabilities, Trusted Advisor gives best-practice checks, Macie finds sensitive data in S3.
</details>

## Cleanup

Keep everything until you finish the course (week 6). Then:

1. IAM → Users → `aif-lab` → Security credentials → access key → **Deactivate**, then **Delete** once you are sure nothing uses it.
2. Remove local credentials: delete the `aif-lab` entries from `~/.aws/credentials` (and the `.csv` you downloaded).
3. Optionally delete the `aif-lab` user and `AifLabPolicy`.
4. Keep the budget and root MFA — they cost nothing and keep protecting the account.
5. Delete `hello.json` if you created it.

**Security notes**

- **Never commit keys.** No access key in code, notebooks, `.env` files that get pushed, screenshots or chat messages. This repo's `.gitignore` excludes `.env`, but the safest place for keys is `~/.aws/credentials`, outside the repo. Before committing, run `git diff --staged` and look for `AKIA`.
- If a key leaks: deactivate it immediately in IAM, create a new one, and check CloudTrail for calls you didn't make.
- Rotate keys you keep for a long time, and prefer IAM Identity Center (`aws configure sso`) once you are comfortable — it gives short-lived credentials.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `aws: command not found` / not recognized | CLI not on PATH | Open a new terminal after installing; on Windows check `C:\Program Files\Amazon\AWSCLIV2\` is on PATH. |
| `Unable to locate credentials` | `aws configure` not run, or wrong profile | Run `aws configure`; if you used `--profile`, set `AWS_PROFILE`. |
| `get-caller-identity` shows the wrong user | Environment variables `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` or `AWS_PROFILE` override the file | PowerShell: `Remove-Item Env:AWS_ACCESS_KEY_ID, Env:AWS_SECRET_ACCESS_KEY` · bash: `unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY`. |
| `InvalidClientTokenId` / `SignatureDoesNotMatch` | Key mistyped, deleted or deactivated; or your PC clock is far off | Re-run `aws configure` with the right values; sync your system clock. |
| `ExpiredToken` / `ExpiredTokenException` | You are using temporary credentials (SSO, `aws sts`) that expired | Run `aws sso login` (or get fresh credentials). Plain IAM user keys don't expire unless deactivated. |
| `AccessDeniedException ... is not authorized to perform: bedrock:InvokeModel on resource ...` | IAM: model ARN not in the policy, policy not attached, or inference-profile ARN missing | Check the policy is attached to `aif-lab`; compare the ARN in the error with the policy. |
| `AccessDeniedException` saying you don't have access to the model | Model access not enabled in this account/region | Bedrock console → Model catalog → open the model; request access if offered (step 12). |
| `ValidationException` about an invalid model identifier, or `ResourceNotFoundException` | Wrong region, or typo in the model ID | `aws configure get region` must print `us-east-1`. A `us.` profile only works from US regions. |
| `NoRegionError` in Python | No default region set | Re-run `aws configure` or set `AWS_REGION=us-east-1`. |
| `ThrottlingException` | Too many requests | Wait a few seconds and retry. |
| PowerShell can't activate the venv | Script execution policy | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (this window only). |
| `python` opens the Microsoft Store | Windows app alias | Install Python properly (step 8) or use `py` instead of `python`. |

---

[Next: Lab 01](lab-01.md) · Back to the course: [Domain 5 — Security, compliance and governance](domain-5.md) · [Domain 2 — GenAI fundamentals](domain-2.md)
