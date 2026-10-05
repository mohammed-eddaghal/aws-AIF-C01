# Domain 2 — Fundamentals of GenAI (24%)

## Official objectives (v1.1, condensed)

- **2.1 Concepts:** tokens, chunking, embeddings, vectors, prompt engineering, transformer LLMs, foundation
  models, multimodal models, diffusion models · use cases (image/video/audio generation, summarization,
  assistants, translation, code, customer service agents, search, recommendations) · **FM lifecycle**
  (data selection → model selection → pre-training → fine-tuning → evaluation → deployment → feedback) ·
  **token-based pricing** · **context engineering** · **agentic AI**: multi-agent patterns, **MCP**,
  agent communication, memory, tool use, workflow orchestration.
- **2.2 Capabilities & limits:** advantages (adaptability, responsiveness, conversation, content generation) ·
  disadvantages (**hallucinations**, interpretability, inaccuracy, **nondeterminism**) · model selection
  factors (type, performance, capability, constraints, compliance, cost, latency, complexity) ·
  business metrics (ROI, efficiency, conversion rate, ARPU, accuracy, customer lifetime value).
- **2.3 AWS for GenAI:** Bedrock, SageMaker AI, SageMaker JumpStart, Amazon Quick, Kiro, **Strands Agents**,
  **Amazon Bedrock AgentCore** · advantages (accessibility, low barrier, speed to market, cost) ·
  infrastructure benefits (security, compliance, responsibility, safety) · cost tradeoffs (availability,
  redundancy, regional coverage, token pricing, **provisioned throughput**, custom models).

## Must-know concepts

- **Token** — unit of text the model reads/writes (~¾ of an English word). Context window = max tokens in + out.
- **Embedding** — vector of numbers representing meaning; similar meaning → close vectors (cosine similarity).
  Basis of semantic search and RAG. Stored in a **vector database**.
- **Chunking** — splitting documents into pieces before embedding (fixed size, overlap, semantic, hierarchical).
- **Transformer** — architecture using self-attention; basis of LLMs. **Diffusion** — generates images by
  denoising random noise step by step (Stable Diffusion, Nova Canvas). **Multimodal** — text + image/audio/video in/out.
- **Foundation model** — large model pre-trained on broad data, adaptable to many tasks.
- **Hallucination** — fluent but false output. Mitigate: RAG grounding, lower temperature, guardrail
  contextual-grounding check, human review, citations.
- **Nondeterminism** — same prompt, different answers (sampling). Lower temperature/top-p → more consistent.
- **Context engineering** — deciding *what goes into the context window*: instructions, retrieved docs,
  memory, tool results, examples — and what to leave out — so the model has exactly what it needs within budget.
- **Token pricing** — pay per input token + per output token (output usually several × pricier). Cost levers:
  shorter prompts, smaller model, prompt caching, batch inference (~50% cheaper), cap max output tokens.

### Bedrock pricing modes
| Mode | When |
|---|---|
| On-demand (pay per token) | Variable/unknown traffic, prototyping |
| Batch | Large offline jobs, ~50% cheaper, results later |
| Provisioned Throughput (model units, time commitment) | Guaranteed throughput for steady high volume; **required to serve most custom (fine-tuned) models** |
| Prompt caching | Same long prefix reused (system prompt, document) → cheaper and faster |
| Cross-region inference | Higher availability/throughput by routing across regions |

### Agentic AI
- **Agent** = FM + instructions + tools + memory, running a loop: reason → act (call a tool) → observe → repeat.
- **Tool use / function calling** — model emits a structured call; your code executes it.
- **MCP (Model Context Protocol)** — open standard for connecting agents to tools and data sources
  (one protocol instead of N×M custom integrations).
- **Memory** — short-term (current session context) vs long-term (persisted facts across sessions).
- **Multi-agent patterns** — supervisor/orchestrator with sub-agents, sequential pipeline, parallel fan-out,
  peer collaboration/handoff, agent-to-agent (A2A) communication.
- **Workflow vs agent** — workflow = predefined steps (predictable); agent = model chooses steps (flexible, less predictable).

## AWS services for this domain

| Service | Remember it as |
|---|---|
| Amazon Bedrock | Fully managed, serverless FM API; your data not used to train base models; Knowledge Bases, Agents, Guardrails, Model Evaluation, Prompt Management, Flows, custom models |
| Amazon Nova | Amazon's own FM family on Bedrock (Micro/Lite/Pro/Premier text, Canvas image, Reel video, Sonic speech) |
| SageMaker JumpStart | Deploy open/proprietary models to *your own* SageMaker endpoint — more control, you manage instances |
| SageMaker AI | Full custom training/hosting |
| Strands Agents | Open-source SDK (Python/TS) to build agents in a few lines, model-driven loop, MCP support |
| Amazon Bedrock AgentCore | Run agents in production on any framework/model: Runtime, Memory, Gateway (tools → MCP), Identity, Browser, Code Interpreter, Observability, Policy |
| Amazon Quick | Business-user agentic workspace (chat agents, research, QuickSight BI, flows/automations) |
| Kiro | Agentic IDE for developers (spec-driven) |
| Amazon Q | AI assistant family (Q Developer for code, Q Business for enterprise data) |

Exam pattern: "least operational overhead / no infrastructure" → **Bedrock**. "Full control of the model/instance,
open-source model in my VPC" → **SageMaker JumpStart/AI**.

## Repo lessons

- `phases/07-transformers-deep-dive/01-why-transformers`, `07-gpt-causal-language-modeling`
- `phases/10-llms-from-scratch/01-tokenizers`
- `phases/11-llm-engineering/04-embeddings`, `05-context-engineering` ← core, `11-caching-cost`
- `phases/05-nlp-foundations-to-advanced/22-embedding-models-deep-dive`
- `phases/08-generative-ai/01-generative-models-taxonomy-history`, `06-diffusion-ddpm-from-scratch` (concept only)
- `phases/13-tools-and-protocols/01-the-tool-interface`, `06-mcp-fundamentals` ← core, `19-a2a-protocol`
- `phases/14-agent-engineering/01-the-agent-loop`, `07-memory-virtual-context-memgpt`,
  `12-anthropic-workflow-patterns`, `28-orchestration-patterns` ← core
- `phases/17-infrastructure-and-production/02-inference-platform-economics`, `27-finops-llms`

## Exercises

1. `python labs/lab02_bedrock_basics.py` — count tokens, compute the cost of each call, run one prompt at
   temperature 0 vs 1 three times each and observe nondeterminism.
2. **Paper:** a chatbot sends a 3,000-token system prompt on every call, 1M calls/month. List 3 ways to cut cost.
   (prompt caching, shorten prompt, smaller model / batch where possible)
3. **Console:** Bedrock → Playgrounds → Chat: compare two models on the same prompt (latency, tokens, quality).
4. **Read:** Strands Agents quickstart and AgentCore overview pages — be able to say which is SDK vs runtime.
5. **Quiz:** `python quiz/quiz.py --domain 2`

## Traps

- Provisioned Throughput is not "cheaper by default" — only for steady high volume or custom models.
- Embeddings are not generated text; they're vectors.
- MCP connects agents to tools/data; it is not a model or a vector store.
