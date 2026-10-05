# Lab 06 — Amazon Bedrock console tour (no code)

| | |
|---|---|
| **Needs AWS?** | Yes: sign in with your **admin user**, not `aif-lab`. The lab user only has API permissions and can't use the console screens. Region `us-east-1`. |
| **Cost** | Playground and Prompt Management tests: a few cents at most with small models (pay per token). The optional automatic evaluation job: model inference on 5 prompts plus a tiny S3 file, so negligible. **Nothing else is launched.** Check current pricing. |
| **Time** | 90–120 min. Do it in two sittings if you like (Parts A–B, then C–E). |
| **Exam domains** | 2.1 (tokens, agentic AI, MCP) · 2.2 (nondeterminism, model selection) · 2.3 (Bedrock, AgentCore, cost trade-offs) · 3.1 (FM selection, inference parameters, Knowledge Bases, vector stores, agents) · 3.2 (prompting techniques, **Prompt Management**) · 3.4 (**Model Evaluation**, LLM-as-a-judge, RAG evaluation, human evaluation) · 4.2 (evaluation as a transparency tool) |

> **Console labels change often.** AWS renames menu items and rearranges the Bedrock console several times a year.
> This guide describes **what you're trying to do and why**. If a button has a different name, look for the
> same intent nearby, or use the console's search bar. Nothing in the exam depends on pixel-exact paths.

## What you'll learn

- How to **compare models** side by side on the same prompt: latency, tokens (and so cost) and quality. Also how **temperature** changes outputs.
- How **Bedrock Prompt Management** stores prompt templates with **variables**, **variants** and immutable **versions**.
- The four kinds of **Bedrock evaluation**: automatic (programmatic metrics), **LLM-as-a-judge**, **human**, and **RAG** evaluation, and when to use each.
- Every decision in the **Knowledge Bases** creation wizard (data source, parsing, chunking, embeddings, vector store), and why you stop before the vector store gets created.
- What **Bedrock Agents**, **Flows** and **Amazon Bedrock AgentCore** are for, from their overview screens.

## Background

The earlier labs called Bedrock through APIs. The console exposes the same building blocks with forms. This is how
most practitioners first meet them, and the exam's scenarios are written in the console's vocabulary ("create a knowledge base",
"create an evaluation job", "save a prompt version").

| Console area | API / concept you've already met | Lab |
|---|---|---|
| Playgrounds (chat/text) | `Converse`, inference parameters, tokens | lab 02 |
| Prompt Management | prompt templates, system prompts | lab 03 `SYSTEM` |
| Evaluations | ROUGE/BLEU/F1-style metrics, LLM-as-a-judge | lab 01, capstone |
| Knowledge Bases | chunk → embed → store → retrieve → generate | lab 03 |
| Guardrails | `ApplyGuardrail` | lab 05 |
| Agents / AgentCore | tool use, memory, MCP | Domain 2 & 3 notes |

**Before you start**

1. Make sure your **budget alarm** from the setup exists (Billing → Budgets).
2. Sign in as your **admin user** and switch the Region selector (top right) to **US East (N. Virginia) us-east-1**.
3. Open the Amazon Bedrock console (search "Bedrock" in the top bar).
4. Most serverless models are available on first use. If a model shows a request-access button or a first-use form
   (some third-party providers ask for a short use-case form), complete it, or just use the Amazon Nova models.

## Steps

### Part A — Playground: compare two models (~25 min)

1. In the left menu, open **Playgrounds → Chat** (it may be named *Chat / Text playground*). Choose a model:
   **Amazon Nova Micro**.

2. Turn on **compare mode** (a toggle or "Compare" button in the playground). Add a second model:
   **Amazon Nova Lite** or **Nova Pro**, or an Anthropic Claude Haiku model if it's available to you.

3. Paste this prompt in the shared input:

   ```text
   You are a support agent for an online shop. A customer writes:
   "My blender arrived broken two months ago. Can I still return it? I'm really annoyed."
   Reply in 3 short sentences: acknowledge the feeling, answer, give the next step.
   Our policy: damaged items can be returned within 90 days with a photo sent to support@example.com.
   ```

   Run it. For each model, note in a small table:

   | | Model 1 | Model 2 |
   |---|---|---|
   | Latency (shown in the response metrics) | | |
   | Input tokens / output tokens | | |
   | Cost of this call = in_tokens × in_price + out_tokens × out_price (prices from the Bedrock pricing page) | | |
   | Quality (followed the 3-sentence format? correct 90-day answer? tone?) | | |

   Your numbers will differ from anyone else's. What matters is the *pattern*: the larger model is usually slower and costs more per token.
   Is it better enough *for this task* to justify that? That question is FM selection in Domain 3.1.

4. **Temperature.** Open the configuration panel (inference parameters). Set **Temperature = 0** on Model 1 and
   run the same prompt three times. Then set **Temperature = 1** and run it three times. At 0 the answers are nearly identical. At 1 the
   wording varies (**nondeterminism**, Domain 2.2). Higher temperature doesn't make answers more correct. Also look at
   **Top P** and **Maximum length / max tokens**. Set max tokens very low (for example 20) and watch the answer get cut off.

5. **System prompt.** If the playground has a system-prompt box, move the "You are a support agent… Our policy…" lines
   there and keep only the customer message in the chat. Same answer, cleaner separation of **trusted instructions**
   from **untrusted user input**, which is a prompt-injection defence habit.

6. **Prompting drill (Domain 3.2).** On one model, try the same classification task three ways and compare:
   - *Zero-shot*: `Classify the sentiment of: "Delivery was late but support was great." Answer POSITIVE, NEGATIVE or MIXED.`
   - *Few-shot*: put 3 labelled examples before the review.
   - *Chain-of-thought*: `Think step by step about each part of the review, then give the label.`
     Notice that CoT uses more output tokens, so it costs more.

### Part B — Prompt Management: a template with variables and versions (~20 min)

1. Left menu → **Prompt management** (often under a *Build* or *Tools* group) → **Create prompt**. Name it
   `support-reply`, add a description, then **Create**.

2. In the **prompt builder**, write a prompt with **variables** in double curly braces:

   ```text
   You are a polite support agent for {{shop_name}}.
   Answer the customer {{customer_name}} using only this policy: {{policy}}
   Question: {{question}}
   Reply in at most 3 sentences.
   ```

   The builder detects `shop_name`, `customer_name`, `policy` and `question` as variables.

3. Pick **Nova Micro** as the model and set temperature 0 (the prompt stores its model and inference configuration with it).
   In the test pane, fill in the **test values** for each variable and **Run**.

4. **Save a version**: use **Create version**. Version 1 is now an **immutable snapshot**. Applications can reference
   `support-reply` version 1 by its ARN, and your edits won't affect them.

5. **Edit the draft**: add `Always end with "Have a great day!"`. Run it, then **create version 2**.

6. **Compare variants**: use the compare option to create a **variant** (for example the same prompt on Nova Lite, or
   with a different instruction) and run both side by side. Pick the better one.

7. Notice the **Optimize** option if your console shows it. Bedrock can rewrite a prompt for a chosen model. It runs
   a model, so it's charged per token. It's optional.

8. Look at how a prompt is consumed. You can reference a prompt version when calling a model, or add it as a **prompt
   node** in **Bedrock Flows** (visual workflows that chain prompts, Knowledge Bases, Lambda and conditions).

   Why it matters: Prompt Management gives you **reuse, versioning, A/B comparison and separation of prompt changes from code
   releases**. That's governance for prompts, and v1.1 of the exam guide names it explicitly.

### Part C — Model Evaluation: four kinds of evaluation (~25 min)

Left menu → **Evaluations** (sometimes *Assess → Evaluations*) → **Create**. You'll see several job types. Here's what each is for:

| Job type | Who scores? | Metrics / output | Use when | Cost basis (check pricing) |
|---|---|---|---|---|
| **Automatic, programmatic** | Algorithms | Task types: general text generation, summarization, question & answer, text classification. Metric families **accuracy, robustness, toxicity** (computed as e.g. BERTScore for summaries, F1 for Q&A, toxicity scores). Built-in datasets (BoolQ, TriviaQA, Gigaword, RealToxicityPrompts… downsampled to 100 prompts) or **your own JSONL** dataset (up to 1,000 prompts). | Fast, cheap, repeatable comparison of models on standard tasks | Model inference only; algorithmic scores aren't charged |
| **LLM-as-a-judge** | A second FM (the **evaluator/judge model**) | Built-in quality metrics such as correctness, completeness, faithfulness, helpfulness, and responsible-AI metrics such as harmfulness, plus **custom metrics** you define. Each score comes with the judge's explanation. | Open-ended answers where n-gram metrics fail; human-like judgment at scale | Generator model inference + judge model tokens |
| **Human** | Your own work team (employees or subject-matter experts) | Ratings, thumbs up/down, preference ranking, on metrics you define | Brand voice, nuance, high-stakes final decisions | Model inference + a fee per completed human task; needs a work team and a CORS-configured S3 bucket |
| **RAG evaluation** | A judge FM | **Retrieve only** (context relevance, context coverage) or **retrieve and generate** (adds correctness, completeness, faithfulness, citation quality and responsible-AI metrics). Works on a Bedrock Knowledge Base **or your own RAG system's outputs** ("bring your own inference responses"). | Tuning chunking, k, embeddings or the generator | Judge tokens (+ KB and generator usage) |

Metric names in the console may differ slightly from the table. Read the descriptions shown next to each metric.

**Walk through without launching** (all four):

1. Open each job type's creation page and read its sections: **model selection** (or KB/RAG source), **task
   type**, **metrics**, **dataset** (built-in vs your S3 location), **evaluator/judge model** (LLM-judge and RAG),
   **work team** and instructions for raters (human), **S3 output location**, and the **IAM service role** that lets Bedrock read your
   dataset and write results.
2. Note how the human job asks you for a **work team** and **instructions for workers**. That's human-in-the-loop evaluation.
3. Note how the RAG job asks for a knowledge base *or* a bring-your-own-responses dataset, plus **ground truth**.
4. **Cancel** each page.

**Optional, negligible cost: run one tiny automatic job.** Only do this if you're comfortable creating an S3 bucket
and an IAM service role, and deleting both afterwards. The cost is Nova Micro inference on 5 short prompts plus
storage of a few KB. Algorithmic scoring isn't charged.

1. Create a file `eval-tiny.jsonl` on your PC, one JSON object per line (keys `prompt`, `referenceResponse`, optional `category`):

   ```json
   {"prompt": "How many days do customers have to return an unused item? Policy: unused items can be returned within 30 days.", "referenceResponse": "30 days", "category": "returns"}
   {"prompt": "Is shipping free for a 60 EUR order? Policy: orders above 50 EUR ship free.", "referenceResponse": "Yes", "category": "shipping"}
   {"prompt": "How much is express shipping? Policy: express costs 12.99 EUR.", "referenceResponse": "12.99 EUR", "category": "shipping"}
   {"prompt": "Does the warranty cover water damage? Policy: the warranty excludes water damage.", "referenceResponse": "No", "category": "warranty"}
   {"prompt": "How long is the electronics warranty? Policy: electronics carry a 2-year warranty.", "referenceResponse": "2 years", "category": "warranty"}
   ```

2. S3 console → **Create bucket** (a unique name like `aif-eval-<your-initials>-<random>`, `us-east-1`, defaults are fine).
   Upload `eval-tiny.jsonl` and create an empty `output/` folder.
3. Evaluations → create an **automatic / programmatic** model evaluation job: model **Nova Micro**, task type
   **Question and answer**, metric **Accuracy** (you can also tick Toxicity), dataset = **your own** → the S3 URI of the file,
   output = `s3://<bucket>/output/`, service role = **create a new service role** (the console scopes it to that bucket).
4. Create the job. It typically takes several minutes or more, so do Part D meanwhile. When it completes, open the report: per-category scores and individual
   responses. Short reference answers such as "Yes" vs a full-sentence response score low on an F1-style metric
   even when the answer is right. That's the same limit of n-gram metrics you saw with ROUGE/BLEU in lab 01, and it's why LLM-as-a-judge exists.
5. Clean up (see Cleanup).

### Part D — Knowledge Bases wizard: walk through, stop before the vector store (~20 min)

Left menu → **Knowledge Bases** → **Create**. The console offers several kinds of knowledge base. Read them first:

| Option | What it is | Notes |
|---|---|---|
| **Managed Knowledge Base** | Bedrock runs ingestion, storage, embeddings, reranking and retrieval (GA June 2026). Native connectors (S3, SharePoint, Confluence, Google Drive, OneDrive, web crawler), agentic retrieval, AgentCore Gateway integration. | AWS now recommends it as the default. It bills on usage including **indexed storage**, so check pricing. |
| **Knowledge Base with vector store** (customer-managed) | You choose and own the vector store | The classic exam mental model |
| **Structured data store** | Natural language → SQL queries over structured data (for example Amazon Redshift) | For tables, not documents |
| **Kendra GenAI index** | Use an existing Amazon Kendra GenAI index as the retriever | Kendra is closed to new customers since 30 July 2026 |
| (Neptune Analytics graph) | **GraphRAG**: entities and relationships plus vectors | Appears as a vector store choice in some flows |

Pick **Knowledge Base with vector store** and walk through the screens:

1. **Knowledge base details**: name, description, and the **IAM service role** that lets Bedrock read your data
   source and call the embeddings model (*create a new service role* is the default). Optional tags.
2. **Data source**: **Amazon S3** (others such as a web crawler or Confluence may be listed). Then the S3 URI of the documents.
   *Lab 03 equivalent: the `DOCS` dict.*
3. **Parsing strategy**: the default parser for text, a **foundation-model parser** for PDFs with tables and figures,
   or **Bedrock Data Automation** for multimodal content. Advanced parsers cost model usage.
4. **Chunking strategy**: open the dropdown and read each option:
   - **Default**: about 300 tokens, respects sentence boundaries.
   - **Fixed-size**: max tokens per chunk + overlap percentage.
   - **Hierarchical**: parent chunk size, child chunk size, overlap. It retrieves precise children and returns broader parents.
   - **Semantic**: max tokens, buffer size, breakpoint percentile threshold. It splits where the meaning changes; it uses an FM, so it costs extra.
   - **No chunking**: each file is one chunk.

   You may also see an option for a **custom transformation (Lambda)** that chunks your own way. *Lab 03 equivalent: `chunk()`.*
5. **Embeddings model**: for example **Titan Text Embeddings V2** (dimensions 256 / 512 / 1024, float or binary),
   Cohere Embed, or a multimodal embeddings model. *Lab 03 equivalent: `embed()` with 256 dims.* Changing the embedding
   model later means re-embedding everything.
6. **Vector store**: **stop and read, don't create.** You'll see either **quick create a new vector store** (Bedrock provisions it, for example
   Amazon OpenSearch Serverless, Amazon S3 Vectors, Aurora PostgreSQL Serverless or Neptune Analytics, depending on the current console),
   or **use an existing vector store** (OpenSearch Serverless, OpenSearch managed cluster, S3 Vectors, Aurora PostgreSQL/pgvector,
   Neptune Analytics, Pinecone, Redis Enterprise Cloud, MongoDB Atlas).

   Several of these are billed **per hour of provisioned capacity** whether or not you query them (OpenSearch Serverless capacity units,
   an Aurora cluster, a Neptune Analytics graph). Others bill by storage, which also accrues while idle. A forgotten study
   KB is the most common surprise bill in GenAI courses. *Lab 03 equivalent: the in-memory list.*
7. **Cancel** the wizard. Nothing has been created.

To finish the mental model, read the "Test knowledge base" panel in the docs (or on any existing KB in a work account):
- **Retrieve only** = the `Retrieve` API: returns chunks and scores, and you build the prompt. This is lab 03's `retrieve()`.
- **Retrieve and generate** = `RetrieveAndGenerate`: picks an FM, generates the answer and shows **citations** linking each
  sentence to source chunks. You can attach a **guardrail** and set the number of results, search type (semantic/hybrid),
  metadata filters and a reranker. This is lab 03's `answer()`.

### Part E — Agents, Flows and AgentCore overview (~15 min)

**Bedrock Agents** (left menu → **Agents**). Open **Create agent** and read the agent builder sections, then cancel:

- **Instructions for the agent**: the role and goal in natural language.
- **Model** selection.
- **Action groups**: the agent's **tools**. Each is a Lambda function described by an OpenAPI schema or function definitions. The agent decides when to call them.
- **Knowledge bases**: RAG as a tool.
- **Guardrails**, **memory** (keep context across sessions), **user input** and **code interpretation** options.
- **Prepare**, **versions** and **aliases**: an alias points an application at a fixed version.

This is the **agent loop** from Domain 2 in form fields: reason → choose a tool (action group) → observe the result → repeat → answer.

**Bedrock Flows** (left menu → **Flows**). Open one example or the create screen: a canvas where you connect nodes
(input, prompt from Prompt Management, Knowledge Base, Lambda, condition, output). A flow follows **predefined steps**,
which makes it predictable. An agent **chooses** its steps, which makes it flexible. The exam likes that contrast.

**Amazon Bedrock AgentCore** (search "AgentCore" in the console. It has its own console pages). Read the overview and the
left menu. Don't create anything. Map each component:

| Component | One line |
|---|---|
| **Runtime** | Serverless, session-isolated hosting for agents built with *any* framework (Strands Agents, LangGraph, CrewAI…) and any model |
| **Gateway** | Turns APIs and Lambda functions into **MCP**-compatible tools, and connects to existing MCP servers |
| **Identity** | Agent identity and credentials for acting on a user's behalf with AWS or third-party services (works with your IdP) |
| **Policy** | Deterministic rules on which tools and actions an agent may use, enforced on tool calls through Gateway |
| **Memory** | Short-term (session) and long-term (across sessions) memory |
| **Code Interpreter / Browser** | Sandboxed tools to run code and browse websites |
| **Observability** | Traces and metrics for each agent step (OpenTelemetry, CloudWatch) |
| **Evaluations** | Automated quality assessment of agent sessions and tool use |

You may also see newer components (for example a managed agent harness, a registry, optimization or payments).
For the exam, focus on the ones above, especially **Runtime, Gateway (MCP), Identity, Policy, Memory**.

## Experiments

1. **Cost per 1,000 conversations.** Using the tokens from Part A and the pricing page, estimate the cost of 1,000
   such replies for each model. Then do it for 10,000 per day for a month. This is capstone decision-record question 3.
2. **Prompt version rollback.** In Prompt Management, make version 3 deliberately worse ("answer in one word").
   Compare it with version 2. Explain how an application pinned to version 2 is protected.
3. **Judge vs metric.** If you ran the tiny eval job, pick one response the F1-style metric scored low but you'd mark
   correct. Write one sentence on why LLM-as-a-judge or a human would score it differently.
4. **Wizard decisions on paper.** For a 2,000-page policy wiki updated weekly, choose: data source, parsing, chunking strategy
   (and why), embedding dimensions, and vector store, for (a) lowest cost at low query volume and (b) a team that
   already runs Aurora PostgreSQL. Compare your choices with the exam tips below.
5. **Agent or flow?** For "check my order status and offer a refund if it's late", decide if you'd use a flow or an
   agent, which tools it needs, and which AgentCore components would matter in production (Identity for the user's
   account, Policy to cap refund actions, Observability for audit).

## Exam connection

> **Exam tip:** "Compare models' latency, cost and output quality before choosing" → the Bedrock **playground in compare mode**
> for a quick look, **Model Evaluation** for a repeatable, documented comparison.

> **Exam tip:** "Store, version and reuse prompt templates with variables; test variants" → **Amazon Bedrock Prompt
> Management**. Chaining prompts, KBs and Lambda into a fixed workflow → **Bedrock Flows**.

> **Exam tip:** Evaluation choice: standard task + reference answers + cheap → **automatic** (programmatic metrics).
> Open-ended quality at scale → **LLM-as-a-judge**. Subjective, brand voice, high stakes → **human** evaluation.
> Knowledge base quality (retrieval and faithfulness) → **RAG evaluation**.

> **Exam tip:** Knowledge Bases decisions: **chunking** (default, fixed-size, hierarchical, semantic, none),
> **embeddings model**, **vector store** (OpenSearch Serverless/managed, Aurora PostgreSQL pgvector, Neptune Analytics for
> GraphRAG, S3 Vectors for low-cost, infrequently queried data, partners). "Least operational overhead" → let Bedrock manage it.

> **Exam tip:** Temperature controls randomness, not truth. Lower temperature = more consistent. It doesn't fix hallucinations;
> grounding (RAG, grounding check) does.

> **Exam tip:** **Strands Agents** = open-source SDK to *build* an agent. **AgentCore** = managed services to *run and govern*
> agents in production (Runtime, Gateway/MCP, Identity, Policy, Memory, Observability). **MCP** = the protocol that connects
> agents to tools.

## Check yourself

**1.** A team keeps its prompts in application code and wants to change them without redeploying, keep a history of
changes, and test two alternatives against each other. What should it use?

- A. Amazon Bedrock Prompt Management
- B. Amazon Bedrock Guardrails
- C. AWS CloudTrail
- D. Amazon Bedrock Provisioned Throughput

<details><summary>Answer</summary>

**A.** Prompt Management stores templates with variables, immutable versions and comparable variants. Guardrails filter
content, CloudTrail audits API calls, and Provisioned Throughput reserves model capacity.
</details>

**2.** A company must judge whether chatbot answers match its brand voice before launch. The judgment is subjective and
the stakes are high. Which Bedrock evaluation type is most appropriate?

- A. Automatic evaluation with a built-in dataset
- B. Human evaluation with the company's own reviewers
- C. Increase the temperature and compare outputs
- D. RAG evaluation in retrieve-only mode

<details><summary>Answer</summary>

**B.** Subjective criteria like brand voice need human judgment. Automatic metrics compare against references and can't
score tone well. Retrieve-only RAG evaluation measures retrieval, not voice. C isn't an evaluation method.
</details>

**3.** While creating a knowledge base, a team wants retrieval to match small, precise passages but give the model
the broader surrounding section as context. Which chunking strategy fits?

- A. No chunking
- B. Fixed-size chunking with 0% overlap
- C. Hierarchical chunking
- D. Default chunking

<details><summary>Answer</summary>

**C.** Hierarchical chunking matches on small child chunks and returns their larger parent chunks. No chunking loses
precision, and fixed-size/default chunking don't provide the parent/child behaviour.
</details>

**4.** A developer built an agent with an open-source framework and wants to run it in production with session isolation,
expose company APIs to it as MCP tools, and enforce rules on which actions it may take. Which service fits?

- A. Amazon Bedrock AgentCore (Runtime, Gateway, Policy)
- B. Amazon SageMaker JumpStart
- C. Amazon Lex
- D. Amazon Bedrock Prompt Management

<details><summary>Answer</summary>

**A.** AgentCore Runtime hosts agents from any framework, Gateway turns APIs into MCP tools, and Policy enforces
deterministic rules on tool calls. JumpStart deploys models, Lex builds intent-based bots, and Prompt Management stores prompts.
</details>

## Cleanup

1. **Knowledge Bases**: you cancelled the wizard. Confirm Bedrock → Knowledge Bases shows nothing you created. Also check
   **Amazon OpenSearch Service → Serverless → Collections** and **Amazon S3 → Vector buckets** for anything created by
   accident. Delete it if so (a KB delete doesn't always delete the vector store it created).
2. **Prompt Management**: delete the `support-reply` prompt (select → Delete). There was no storage charge listed on the pricing
   page when this was written, but keeping your account tidy is part of governance.
3. **Evaluation job (if you ran one)**: you can delete the job from the list. Then **empty and delete the S3 bucket**
   (S3 → bucket → Empty → Delete). Delete the IAM service role the console created for the job (IAM → Roles → search
   for the evaluation role's name) and its policy.
4. **Agents / Flows / AgentCore**: you created nothing. If you did by mistake, delete agents, aliases and flows, and stop
   any AgentCore runtime.
5. **Guardrails**: if you created one in lab 05's console steps, make sure it's deleted.
6. Check **Billing → Bills** (or Cost Explorer) in a day or two. You should see only cents for Bedrock.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| Console pages show "You don't have permissions" | You're signed in as `aif-lab`. Sign out and use your admin user. |
| A model is greyed out or asks for access | Complete the access request or first-use form on the model's page, or switch to an Amazon Nova model. Some models are only available in certain Regions. Confirm you're in `us-east-1`. |
| No compare mode in the playground | The control moved. Look for "Compare" or a "+" to add a model, or open two browser tabs with the same prompt. |
| Prompt Management doesn't detect your variable | Use double curly braces with no spaces: `{{question}}`. |
| Evaluation job fails immediately | Usually the S3 path or the service role. Check the dataset URI, that the file is valid **JSON Lines** (one object per line, no trailing commas), the keys `prompt` / `referenceResponse`, and that the role can read the bucket and write to `output/`. |
| Evaluation job stays "In progress" | Jobs can take a while even for few prompts. Wait and refresh. Don't recreate it. |
| You clicked **Create** on a knowledge base by mistake | Delete the knowledge base, then delete the vector store it created (OpenSearch Serverless collection, S3 vector bucket, Aurora cluster or Neptune graph) and the IAM role. Check Billing the next day. |
| AgentCore isn't in the Bedrock left menu | It has its own console pages. Search "AgentCore" in the top search bar. |

---

Next: [Capstone — Grounded customer-support assistant](../capstone/README.md) · Back to the course: [Domain 3 — Applications of foundation models](domain-3.md) · Related: [Domain 2](domain-2.md), [Domain 4](domain-4.md)
