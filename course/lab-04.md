# Lab 04 — AWS managed AI services: Comprehend, Translate, Polly

| | |
|---|---|
| **Needs AWS?** | Yes: the `aif-lab` IAM user, region `us-east-1` |
| **Cost** | Under 0.01 USD per run (a few hundred characters per call). The AWS Free Tier may cover it; the Free Tier model changed in 2025, so check what your account has. Check current pricing. |
| **Time** | 30–45 min |
| **Exam domains** | 1.2 (AI use cases, AWS managed AI services, when to use AI) · 1.3 (managed API vs self-hosted) · 5.1 (PII handling) |
| **Code** | [`../labs/lab04_ai_services.py`](../labs/lab04_ai_services.py) |

## What you'll learn

- What a **managed AI service** is: a pre-trained model behind an API, with no training, no servers and no ML expertise needed.
- Use **Amazon Comprehend** for sentiment, entities and **PII detection**, and redact PII yourself from the offsets it returns.
- Use **Amazon Translate** for neural machine translation and **Amazon Polly** for text-to-speech with a neural voice.
- Choose the right AWS AI service from the wording of an exam question. This is one of the most reliable point sources in Domain 1.

## Background

### Three ways to get AI on AWS

| Layer | You bring | AWS examples | Pick it when the question says… |
|---|---|---|---|
| **AI services** (task-specific, pre-trained) | Just your data in the API call | Comprehend, Translate, Polly, Transcribe, Rekognition, Textract, Lex, Personalize | "no ML expertise", "quickly add X to an app", a well-known task (sentiment, OCR, speech) |
| **Generative AI platform** | Prompts, maybe documents | Amazon Bedrock (FMs, Knowledge Bases, Agents, Guardrails), Amazon Quick for business users | open-ended language/vision tasks, chat, summarization, RAG, agents |
| **ML platform** | Data, algorithms, training code, ops | Amazon SageMaker AI (Canvas for no-code, JumpStart for open models) | custom model on your own labelled data, full control |

An AI service is the right answer when the task is **standard** (detect sentiment, read a receipt, transcribe a call).
It's cheaper and simpler than prompting an FM for the same task, and more predictable. Its output is structured
(labels, scores, offsets), not free text.

### The three services in this lab

- **Amazon Comprehend**: natural language processing (NLP). Sentiment (POSITIVE / NEGATIVE / NEUTRAL / MIXED with
  confidence scores), entities (PERSON, LOCATION, DATE, ORGANIZATION, COMMERCIAL_ITEM…), key phrases, dominant language,
  syntax, **PII detection/redaction**, plus custom classification and custom entity recognition that you train with
  your own labelled examples, still without writing ML code.
- **Amazon Translate**: neural machine translation between many languages. Supports automatic source-language detection,
  **custom terminology** (keep brand names or product terms translated your way) and batch translation of documents in S3.
- **Amazon Polly**: text-to-speech (TTS). Many voices and languages. Engines include standard, neural, long-form and
  generative (availability varies by voice and Region). Supports **SSML** markup for pauses, emphasis and pronunciation,
  and **speech marks** for lip-sync and highlighting.

## Steps

1. **Confirm your credentials and region:**

   ```powershell
   aws sts get-caller-identity
   aws configure get region
   ```

   The region should be `us-east-1`.

2. **Run the lab** from the repo root:

   ```powershell
   python labs/lab04_ai_services.py
   ```

   Expected output shape (your scores, entity list and translation wording will differ a little):

   ```text
   Comprehend sentiment: MIXED {'Positive': 0.4x, 'Negative': 0.1x, 'Neutral': 0.0x, 'Mixed': 0.3x}
   Comprehend entities:  [('coffee machine', 'COMMERCIAL_ITEM'), ('Lyon', 'LOCATION'), ('3 March', 'DATE'),
                          ('Sarah', 'PERSON'), ('+33 6 12 34 56 78', 'OTHER'), ...]
   Comprehend PII redacted: I ordered a coffee machine from Lyon on [DATE_TIME]. ... but [NAME] from support
                            called me at [PHONE] and fixed it fast. Great service!
   Translate -> fr: J'ai commandé une machine à café à Lyon le 3 mars. ...
   Polly: wrote review.mp3 (French neural voice Lea)

   Note: no ML expertise needed -> that's the exam's cue for managed AI services.
   ```

   The review is deliberately mixed (late delivery and a crushed box, but great support), so sentiment may come back as
   **MIXED** or **POSITIVE**. Look at all four scores, not just the label. Whether "Lyon" is tagged as an ADDRESS for PII
   depends on the model's reading of the context.

3. **Listen to the audio.** Polly's MP3 is written to the **current folder on your machine** (the repo root if you
   ran the command from there). Nothing is stored in AWS.

   ```powershell
   Invoke-Item review.mp3
   ```

   ```bash
   open review.mp3        # macOS
   xdg-open review.mp3    # Linux
   ```

   You'll hear the French translation read by the neural voice Léa (API voice ID `Lea`).

4. **(Optional) Compare with the console.** Sign in with your **admin user** (the lab user has no console permissions)
   and open Amazon Comprehend → *Real-time analysis*. Paste the same review and look at the Entities, Key phrases,
   Sentiment and PII tabs. Then Amazon Polly → *Text-to-speech*: paste the French text, pick a French voice and a neural engine,
   and listen. The console calls the same APIs.

## What just happened

Section by section through [`lab04_ai_services.py`](../labs/lab04_ai_services.py):

### 1. One input, three clients

```python
comprehend = boto3.client("comprehend")
translate = boto3.client("translate")
polly = boto3.client("polly")
```

There are no model IDs, no endpoints, no instance types and no training job. That's the defining feature of a managed AI service:
AWS owns the model, its hosting and its scaling. You own the data you send and what you do with the output (shared responsibility).

### 2. Sentiment

```python
s = comprehend.detect_sentiment(Text=REVIEW, LanguageCode="en")
```

It returns a label (`Sentiment`) and a `SentimentScore` dict with four probabilities. The code rounds them. In a real
system you'd act on the **score**, not just the label. For example, you might route "NEGATIVE > 0.8" to a human agent (human in the loop).

### 3. Entities

```python
ents = comprehend.detect_entities(Text=REVIEW, LanguageCode="en")["Entities"]
```

Each entity has `Text`, `Type`, `Score` and `BeginOffset`/`EndOffset`. This is **named entity recognition (NER)**, a
classic NLP task. If you needed your own entity types (say, product SKUs), you'd use Comprehend **custom entity
recognition**, trained on your labelled examples.

### 4. PII detection and redaction

```python
pii = comprehend.detect_pii_entities(Text=REVIEW, LanguageCode="en")["Entities"]
for e in sorted(pii, key=lambda e: e["BeginOffset"], reverse=True):
    redacted = redacted[:e["BeginOffset"]] + f"[{e['Type']}]" + redacted[e["EndOffset"]:]
```

`DetectPiiEntities` returns **where** the PII is (character offsets) and **what type** (NAME, PHONE, DATE_TIME,
ADDRESS, EMAIL…). It doesn't return the redacted text, so the code builds it. The loop runs **from the end of the
string backwards**. Replacing `+33 6 12 34 56 78` with the shorter `[PHONE]` would shift every offset that comes after it,
but offsets *before* it stay valid. Going right to left means each replacement only affects text already processed.

Three PII tools you must not confuse on the exam:

| Tool | Finds PII in… |
|---|---|
| **Amazon Comprehend** PII detection | Text you send to the API (or batch jobs over documents) |
| **Amazon Bedrock Guardrails** sensitive information filter | Prompts and FM responses: block or mask (lab 05) |
| **Amazon Macie** | Objects stored in **Amazon S3** (discovery and classification at rest) |

### 5. Translation

```python
fr = translate.translate_text(Text=REVIEW, SourceLanguageCode="en", TargetLanguageCode="fr")["TranslatedText"]
```

The source language is given explicitly. With `SourceLanguageCode="auto"`, Translate calls Comprehend to detect the
language, which needs the extra permission `comprehend:DetectDominantLanguage` (see Experiments).

### 6. Speech

```python
audio = polly.synthesize_speech(Text=fr, OutputFormat="mp3", VoiceId="Lea", Engine="neural")
with open("review.mp3", "wb") as f:
    f.write(audio["AudioStream"].read())
```

The output of one service feeds the next: **text → translated text → speech**. Chaining AI services like this is a common
exam scenario, for example "make English product reviews available as French audio" = Translate + Polly.
`AudioStream` is a stream, and the code writes its bytes to a local file. The voice must exist for the chosen engine and
language, or you get a `ValidationException`.

## Which managed AI service?

The exam describes a need and expects the service. Status notes were checked against AWS documentation in October 2026.
Services that are closed to new customers can still show up in older practice material, so know their names and what replaces them.

| The question says… | Pick | Notes |
|---|---|---|
| sentiment, entities, key phrases, language detection, PII in text, classify support tickets | **Amazon Comprehend** | In scope. Topic modeling, event detection and prompt-safety classification closed to new customers on 30 April 2026. AWS points to Bedrock LLMs and Guardrails instead. |
| extract medical conditions, medications, dosages from clinical text (PHI) | **Amazon Comprehend Medical** | Not on the v1.1 in-scope list; know the name |
| translate text or documents between languages, keep brand terms | **Amazon Translate** | In scope; custom terminology |
| speech → text: call transcripts, subtitles, meeting notes | **Amazon Transcribe** | In scope; includes PII redaction in transcripts, custom vocabulary, Call Analytics |
| medical dictation / clinician–patient conversation → clinical notes | **Amazon Transcribe Medical** / **AWS HealthScribe** | Not on the v1.1 in-scope list |
| text → lifelike speech, voice for an app, accessibility, audiobooks | **Amazon Polly** | In scope; SSML, neural/generative voices |
| objects, scenes, faces, celebrities, text in images; **content moderation** of images/video | **Amazon Rekognition** | In scope; images and video, not documents |
| extract text, **forms (key–value)** and **tables** from scanned documents, invoices, IDs | **Amazon Textract** | In scope; "more than OCR" |
| build a **chatbot or voice bot** with intents and slots, contact-center IVR | **Amazon Lex** | In scope; same conversational tech as Alexa |
| personalized **recommendations**, "customers who bought…", re-ranking | **Amazon Personalize** | In scope |
| enterprise document search / RAG retrieval for an assistant | **Amazon Bedrock Knowledge Bases** (incl. **Bedrock Managed Knowledge Base**) | **Amazon Kendra** entered maintenance mode on 30 June 2026 and closed to new customers on 30 July 2026; AWS recommends Bedrock Managed Knowledge Base. |
| time-series **forecasting** (demand, inventory) without ML expertise | **Amazon SageMaker Canvas** | **Amazon Forecast** closed to new customers on 29 July 2024; AWS recommends Canvas. |
| detect **online fraud** (fake accounts, payment fraud) | **Amazon SageMaker AI** / AutoGluon, **AWS WAF Fraud Control** for account takeover/creation | **Amazon Fraud Detector** closed to new customers on 7 November 2025. |
| generative AI assistant for business users over company data, BI, automations | **Amazon Quick** | In scope. **Amazon Q Business** is no longer open to new customers; AWS points to Amazon Quick. |
| AI coding assistant / agentic IDE, spec-driven development | **Kiro** | In scope. Amazon Q Developer still exists in the AWS console, but new developer-tool users are being steered to Kiro; check the current Q Developer availability page. |
| migrate/modernize legacy code (mainframe, .NET, VMware) with agents | **AWS Transform** | In scope |
| build a GenAI app on a foundation model, summarization, content generation, agents | **Amazon Bedrock** (+ AgentCore for agents in production) | In scope |
| human review of low-confidence ML predictions | **Amazon Augmented AI (A2I)** | Responsible-AI topic (Domain 4) |
| train/deploy your own model on your own labelled data | **Amazon SageMaker AI** | In scope; Canvas = no-code, JumpStart = pre-trained/open models |

Classic confusions:

- **Textract** (documents: forms, tables) vs **Rekognition** (images and video: objects, faces, moderation). "Text in a street photo" → Rekognition; "fields from a scanned invoice" → Textract.
- **Comprehend** (analyses text) vs **Lex** (holds a conversation).
- **Transcribe** (speech → text) vs **Polly** (text → speech).
- **Translate** (languages) vs **Transcribe** (audio). The two names sound alike, so slow down when you read.

## Experiments

Edit a copy so the original stays clean:

```powershell
Copy-Item labs/lab04_ai_services.py labs/my_ai.py
```

```bash
cp labs/lab04_ai_services.py labs/my_ai.py
```

1. **Change the sentiment.** Set `REVIEW` to a clearly angry review, then a neutral one ("The parcel arrived on Tuesday.").
   Watch how the four scores move. A label alone hides how confident the model is.

2. **Add PII and see what's caught.** Add an email address and a fake card-like number (for example
   `4111 1111 1111 1111`, a well-known test number) to `REVIEW`. Which types appear? Is every name caught? Probabilistic
   detection can miss things, which is why sensitive pipelines layer several controls.

3. **Translate to another language.** Change `TargetLanguageCode` to `"ar"` or `"es"`. If you also want speech, pick a
   voice for that language. With your admin profile, list voices with:

   ```powershell
   aws polly describe-voices --language-code es-ES --query "Voices[].{Id:Id,Engines:SupportedEngines}"
   ```

   (`describe-voices` isn't in the lab user's policy, which is intentional least privilege.)

4. **Auto-detect the source language.** Set `SourceLanguageCode="auto"`. With the lab user you'll get an
   `AccessDeniedException` for `comprehend:DetectDominantLanguage`. That shows one service calling another on your behalf
   with your permissions. Add that action to the policy (or use your admin profile) and run again.

5. **SSML.** Replace the Polly call with SSML input:

   ```python
   ssml = "<speak>Bonjour. <break time='700ms'/> <emphasis>Merci</emphasis> pour votre commande.</speak>"
   audio = polly.synthesize_speech(Text=ssml, TextType="ssml", OutputFormat="mp3", VoiceId="Lea", Engine="neural")
   ```

   Some SSML tags aren't supported by every engine. If you get an error, remove the tag it names.

6. **Compare with an FM.** In the Bedrock playground (lab 06), ask Nova Micro to "classify the sentiment of this review
   and list the people, places and dates". Compare: an FM gives flexible free text, while Comprehend gives fixed labels,
   scores and offsets that you can parse reliably. Which would you put in a pipeline that processes a million reviews a day?

## Exam connection

> **Exam tip:** "Without ML expertise", "pre-trained", "add X to an application quickly" → an **AI service**
> (Comprehend, Rekognition, Textract, Transcribe…), not SageMaker. "Custom model on our labelled data, full control" → SageMaker AI.

> **Exam tip:** Speech pipeline patterns: call recording → **Transcribe** → **Comprehend** (sentiment, PII) is
> "call-center analytics". Text → **Translate** → **Polly** is "multilingual audio". Scanned form → **Textract** →
> **Comprehend** is "document processing".

> **Exam tip:** PII questions: *in prompts or LLM output* → Bedrock Guardrails. *In text you analyse* → Comprehend.
> *Sitting in S3 buckets* → Macie. *In call recordings* → Transcribe PII redaction.

> **Exam tip:** When *not* to use AI (Domain 1.2): if a deterministic rule gives the exact answer (a tax formula, a
> lookup table), use the rule. AI services return **predictions with confidence scores**, not guarantees.

## Check yourself

**1.** A logistics company receives thousands of scanned delivery forms daily and needs the values of specific fields and the
contents of tables, with no ML team. Which service should it use?

- A. Amazon Rekognition
- B. Amazon Textract
- C. Amazon Comprehend
- D. Amazon Polly

<details><summary>Answer</summary>

**B.** Textract extracts text, key–value pairs (forms) and tables from documents. Rekognition analyses images and video
(objects, faces) and isn't built for document structure. Comprehend analyses text you already have. Polly makes speech.
</details>

**2.** A support team wants to detect the sentiment of recorded customer calls and redact phone numbers from the transcripts. Which
combination is the most appropriate?

- A. Amazon Polly and Amazon Lex
- B. Amazon Transcribe and Amazon Comprehend
- C. Amazon Translate and Amazon Rekognition
- D. Amazon Textract and Amazon Personalize

<details><summary>Answer</summary>

**B.** Transcribe turns speech into text (and can redact PII in transcripts). Comprehend gives sentiment and PII detection on
the text. Polly and Lex create speech and bots, and the other pairs don't process audio.
</details>

**3.** A developer calls Comprehend `DetectPiiEntities` and wants a redacted copy of the text. What does the API return?

- A. The redacted text with PII replaced by asterisks
- B. A list of PII entities with types and character offsets, which the application uses to redact
- C. Only a yes/no flag indicating that PII exists
- D. An encrypted copy of the text

<details><summary>Answer</summary>

**B.** It returns entity types, scores and begin/end offsets, and the application performs the redaction, exactly as the lab code does.
(Batch PII *redaction* jobs over documents also exist, but the real-time detect call returns offsets.)
</details>

**4.** A startup wants an e-commerce site to show "recommended for you" products based on users' browsing and purchase
history, without building models itself. Which service fits best?

- A. Amazon Personalize
- B. Amazon Lex
- C. Amazon Comprehend
- D. Amazon Transcribe

<details><summary>Answer</summary>

**A.** Personalize is the managed recommendation service. The others handle conversation, text analysis and speech recognition.
</details>

## Cleanup

- **Nothing is created in AWS.** All calls are stateless request/response APIs.
- `review.mp3` is a **local file** in the folder you ran the script from. Delete it when done:

  ```powershell
  Remove-Item review.mp3
  ```

  ```bash
  rm review.mp3
  ```

- Delete `labs/my_ai.py` if you made a copy. If you added `comprehend:DetectDominantLanguage` to the lab policy for an
  experiment, remove it again (least privilege).

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `AccessDeniedException` for `comprehend:...`, `translate:TranslateText` or `polly:SynthesizeSpeech` | The lab policy is missing the action, or a different profile is active. Compare with the policy in [labs/README.md](../labs/README.md#least-privilege-policy) and run `aws sts get-caller-identity`. |
| `AccessDeniedException` for `comprehend:DetectDominantLanguage` during translation | You used `SourceLanguageCode="auto"`. Use `"en"` or grant that action. |
| `ValidationException` from Polly about the voice or engine | That voice doesn't support that engine in this Region. Use `describe-voices` (admin) to check, or switch `Engine` to `"standard"`. |
| `TextSizeLimitExceededException` or a similar size error | You pasted a very long text. Real-time APIs have per-request size limits; split the text or use the batch/asynchronous APIs. Check the current quotas in each service's docs. |
| `review.mp3` plays silence or won't open | The file was written while the run failed half-way. Delete it and re-run. Check the run printed the "Polly: wrote review.mp3" line. |
| `UnrecognizedClientException` / `InvalidSignatureException` | Wrong or deactivated access key, or a clock skew on your PC. Re-run `aws configure` and sync the system clock. |

---

Next: [Lab 05 — Amazon Bedrock Guardrails](lab-05.md) · Back to the course: [Domain 1 — Fundamentals of AI and ML](domain-1.md) · Related: [Domain 5](domain-5.md)
