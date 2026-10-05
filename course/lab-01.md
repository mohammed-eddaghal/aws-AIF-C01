# Lab 01 — ML metrics from scratch (offline)

| | |
|---|---|
| **Needs AWS?** | No — runs fully offline, standard-library Python only |
| **Cost** | Free |
| **Time** | 30–45 min (including experiments) |
| **Exam domains** | Domain 1 — **1.3** (model metrics: accuracy, precision, recall, F1; business metrics), **1.2** (choosing the right approach for a use case) · Domain 3 — **3.4** (evaluating FM output: ROUGE, BLEU) |

Code: [`../labs/lab01_ml_metrics.py`](../labs/lab01_ml_metrics.py)

## What you'll learn

- How a **confusion matrix** is built from predictions and true labels.
- What **accuracy, precision, recall and F1** measure, and why accuracy alone can lie.
- How moving a **decision threshold** trades precision against recall, and how to pick a side using business cost.
- How **ROUGE** (summarization) and **BLEU** (translation) score generated text against a reference, and how they differ.

You will not be asked to compute these on the exam with a calculator very often, but you *will* be asked which metric fits a scenario. Computing them once by hand makes that easy.

## Background

### Classification and scores

A *binary classifier* answers yes/no: fraud or not, spam or not, disease or not. Most models don't output "yes" directly. They output a **score** (often a probability, e.g. 0.72 = "72% likely fraud"). You then choose a **threshold**: score ≥ threshold → predict *yes* (1), otherwise *no* (0).

The lab uses 20 transactions. Each has a model score and a true label (1 = really fraud). Six of the twenty are fraud — the data is **imbalanced**, like most real fraud data.

### The confusion matrix

Comparing each prediction with the truth gives four counts:

| | Predicted fraud (1) | Predicted not fraud (0) |
|---|---|---|
| **Actually fraud (1)** | **TP** — true positive (caught it) | **FN** — false negative (missed it) |
| **Actually not fraud (0)** | **FP** — false positive (false alarm) | **TN** — true negative (correctly ignored) |

### The four metrics

| Metric | Formula | Plain question |
|---|---|---|
| **Accuracy** | (TP + TN) / all | What share of all predictions were right? |
| **Precision** | TP / (TP + FP) | When the model says *yes*, how often is it right? |
| **Recall** (sensitivity) | TP / (TP + FN) | Of all real *yes* cases, how many did the model catch? |
| **F1** | 2 · P · R / (P + R) | One number balancing precision and recall (harmonic mean — low if either one is low). |

### Text-generation metrics

Generated text (a summary, a translation) has no single correct answer, so we compare it with a human-written **reference** by counting overlapping words (*n-grams*; a unigram = one word).

- **ROUGE** (Recall-Oriented Understudy for Gisting Evaluation) — *recall*: what share of the reference's words appear in the candidate? Used for **summarization**: did the summary keep the important content?
- **BLEU** (Bilingual Evaluation Understudy) — *precision*: what share of the candidate's words appear in the reference? Plus a **brevity penalty** so a very short output can't score high just by being safe. Used for **translation**.

The lab implements the simplest versions, ROUGE-1 and BLEU-1 (single words only). Real BLEU combines 1- to 4-gram precision; real ROUGE has variants such as ROUGE-2 and ROUGE-L.

## Steps

1. Open a terminal in the repository root (the folder containing `README.md`).
2. Run the lab. No virtual environment or AWS setup is needed for this one.

```powershell
python labs/lab01_ml_metrics.py
```

```bash
python3 labs/lab01_ml_metrics.py
```

3. You should see exactly this output (it is deterministic — this was captured from a real run):

```text
Part A - threshold vs precision/recall (fraud: 6 positives out of 20)
threshold  TP  FP  FN   acc  prec   rec    F1
      0.9   2   0   4  0.80  1.00  0.33  0.50
      0.7   4   1   2  0.85  0.80  0.67  0.73
      0.5   5   3   1  0.80  0.62  0.83  0.71
      0.3   6   6   0  0.70  0.50  1.00  0.67
'Always not fraud' model: accuracy 0.70, recall 0.00  <- why accuracy lies on imbalanced data
Takeaway: lower threshold -> recall up, precision down. Fraud/medical: favor recall.

Part B - ROUGE-1 vs BLEU-1
  'the parcel arrived damaged so the customer was refunded'
    ROUGE-1 recall 0.89   BLEU-1 0.89
  'customer refunded'
    ROUGE-1 recall 0.22   BLEU-1 0.03
Takeaway: short answers can be precise yet miss content; ROUGE catches that, BLEU's brevity penalty too.
```

If nothing prints and you get an `AssertionError`, the built-in self-check failed — you probably edited the file (see Troubleshooting).

4. Read the walkthrough below with the output next to you, and check at least two rows by hand.

## What just happened

### The data (top of the file)

```python
SCORES = [0.95, 0.91, 0.85, 0.80, 0.72, 0.66, 0.61, 0.55, 0.48, 0.42,
          0.38, 0.33, 0.29, 0.22, 0.18, 0.12, 0.09, 0.07, 0.04, 0.02]
LABELS = [1, 1, 0, 1, 1, 0, 1, 0, 0, 1,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

Scores are sorted high to low. The fraud cases (label 1) sit at scores 0.95, 0.91, 0.80, 0.72, 0.61 and 0.42. The model is decent but not perfect: a legitimate transaction scored 0.85, and one fraud scored only 0.42.

### `confusion()` and `metrics()`

`confusion()` walks through label/prediction pairs and counts the four cases. `metrics()` applies the formulas from the Background table. The `if ... else 0.0` guards avoid division by zero (for example, precision when the model never says *yes*).

### Part A, row by row

For each threshold, the code turns scores into predictions with `1 if s >= threshold else 0`, then computes the metrics. Total = 20, real fraud = 6, real legitimate = 14.

**Threshold 0.9** — flagged: 0.95, 0.91 (both fraud).
TP = 2, FP = 0, FN = 6 − 2 = 4, TN = 14.
Accuracy = (2 + 14)/20 = **0.80** · Precision = 2/2 = **1.00** · Recall = 2/6 = **0.33** · F1 = 2·1·0.33/1.33 = **0.50**.
A very cautious model: every alarm is real, but two-thirds of fraud slips through.

**Threshold 0.7** — adds 0.85 (legit), 0.80 (fraud), 0.72 (fraud).
TP = 4, FP = 1, FN = 2, TN = 13.
Accuracy = 17/20 = **0.85** · Precision = 4/5 = **0.80** · Recall = 4/6 = **0.67** · F1 = **0.73** (best F1 in the table).

**Threshold 0.5** — adds 0.66 (legit), 0.61 (fraud), 0.55 (legit).
TP = 5, FP = 3, FN = 1, TN = 11.
Accuracy = 16/20 = **0.80** · Precision = 5/8 = 0.625, printed **0.62** · Recall = 5/6 = **0.83** · F1 = **0.71**.
(0.625 shows as 0.62 because Python's formatting rounds an exact half to the even digit.)

**Threshold 0.3** — adds 0.48 (legit), 0.42 (fraud), 0.38 (legit), 0.33 (legit).
TP = 6, FP = 6, FN = 0, TN = 8.
Accuracy = 14/20 = **0.70** · Precision = 6/12 = **0.50** · Recall = 6/6 = **1.00** · F1 = 2·0.5·1/1.5 = **0.67**.
Every fraud caught, but half the alarms are false.

**The pattern:** as the threshold goes **down**, the model says *yes* more often → **recall rises, precision falls**. Accuracy barely moves and even peaks in the middle — it doesn't tell you which errors you are making.

### The "always not fraud" model

```python
always_no = metrics(*confusion(LABELS, [0] * len(LABELS)))
```

A "model" that predicts 0 for everyone: TP = 0, FP = 0, FN = 6, TN = 14. Accuracy = 14/20 = **0.70** — the same accuracy as the threshold-0.3 model — while catching **zero** fraud (recall 0.00). On imbalanced data, accuracy rewards ignoring the rare class. With real fraud rates (often well under 1%), a do-nothing model can show 99%+ accuracy.

### Choosing precision or recall: it's a business decision

Ask: **which mistake is more expensive, a false positive or a false negative?**

| Use case | Costly mistake | Favour | Why |
|---|---|---|---|
| Card fraud detection | FN — fraud goes through | **Recall** (lower threshold) | A missed fraud costs money and trust; a false alarm costs a quick verification SMS. |
| Cancer / disease screening | FN — sick patient sent home | **Recall** | A follow-up test is cheap compared with a missed diagnosis. |
| Spam filter | FP — real email hidden in spam | **Precision** (higher threshold) | Losing an invoice or job offer is worse than seeing an occasional spam. |
| Auto-blocking a customer account | FP — blocking an honest customer | **Precision** | Wrongly locking accounts drives churn and support calls. |
| Both errors matter roughly equally / need one number | — | **F1** | Balances the two. |

A common pattern combines both: a low threshold to *route cases to human review* (high recall), and a high threshold to *act automatically* (high precision).

### Part B — ROUGE-1 vs BLEU-1

```python
def rouge1_recall(candidate, reference):
    c, r = Counter(candidate.lower().split()), Counter(reference.lower().split())
    return sum((c & r).values()) / sum(r.values())
```

`Counter` counts words; `c & r` keeps the *minimum* count of each shared word (so repeating a word can't inflate the score — "clipped counts"). Divide by the **reference** length → recall.

```python
def bleu1(candidate, reference):
    ...
    precision = overlap / len(c_tokens)
    bp = 1.0 if len(c_tokens) > len(r_tokens) else math.exp(1 - len(r_tokens) / len(c_tokens))
    return bp * precision
```

Divide by the **candidate** length → precision. Then multiply by the brevity penalty `bp`: 1.0 if the candidate is longer than the reference, otherwise `exp(1 − ref_len / cand_len)`, which shrinks fast as the candidate gets shorter.

Reference: *"the customer was refunded because the parcel arrived damaged"* — 9 words (`the` twice).

**Candidate 1:** *"the parcel arrived damaged so the customer was refunded"* — 9 words.
Shared words (clipped): the ×2, parcel, arrived, damaged, customer, was, refunded = 8. Missing from the candidate: *because*. Extra in the candidate: *so*.
ROUGE-1 = 8/9 = **0.89**. BLEU-1 precision = 8/9; same length, so bp = exp(1 − 9/9) = 1 → **0.89**.
Different word order, same meaning — unigram metrics don't care about order at all.

**Candidate 2:** *"customer refunded"* — 2 words, both in the reference.
ROUGE-1 = 2/9 = **0.22** — it lost most of the content.
BLEU-1 precision = 2/2 = 1.0 (everything it said is "correct"), but bp = exp(1 − 9/2) = exp(−3.5) ≈ 0.03 → **0.03**.
Without the brevity penalty, BLEU would have rated this terse output as perfect.

**Takeaway:** ROUGE asks "did you cover the reference?" — natural for summaries. BLEU asks "is what you produced in the reference?" plus a length check — natural for translation. Both only match words, not meaning: a correct paraphrase with different words scores low. That is why **BERTScore** (embedding similarity) and **LLM-as-a-judge** exist.

### `_self_check()`

Three `assert` lines run before `main()`. The first, `metrics(15, 15, 5, 965)`, is the Domain 1 paper exercise: precision 15/30 = 0.5, recall 15/20 = 0.75, F1 = 0.6. Note the accuracy there would be 980/1000 = 0.98 — high, for a model that is wrong about half its alarms.

## Experiments

Make a copy so the original stays intact, then edit the copy:

```powershell
Copy-Item labs/lab01_ml_metrics.py labs/lab01_play.py
python labs/lab01_play.py
```

```bash
cp labs/lab01_ml_metrics.py labs/lab01_play.py
python3 labs/lab01_play.py
```

For each experiment, **write your prediction first**, then run and compare. Delete `lab01_play.py` when done (don't commit it).

**1. Add threshold 0.6.** Change `for threshold in (0.9, 0.7, 0.5, 0.3):` to include `0.6`. Predict TP, FP, FN and F1.

<details><summary>Result</summary>

TP 5, FP 2, FN 1 → accuracy 0.85, precision 0.71, recall 0.83, **F1 0.77** — better than any threshold in the original table. Adding 0.61 (fraud) and 0.66 (legit) on top of the 0.7 set gains a catch for one false alarm. Threshold tuning is a search; the best point is often between your first guesses.
</details>

**2. Threshold 0.4.** Predict whether recall reaches 1.0 and what precision becomes.

<details><summary>Result</summary>

TP 6, FP 4, FN 0 → recall **1.00**, precision **0.60**, F1 0.75, accuracy 0.80. You catch all fraud with fewer false alarms than at 0.3. If the business needs 100% recall, 0.4 beats 0.3 on this data.
</details>

**3. Extremes: 0.0 and 0.96.** Predict all four metrics for each.

<details><summary>Result</summary>

- 0.0 → flag everything: TP 6, FP 14 → accuracy 0.30, precision 0.30, recall 1.00, F1 0.46. Perfect recall is trivial to get — that's why you never look at recall alone.
- 0.96 → flag nothing: same as "always not fraud": accuracy 0.70, precision 0.00 (guarded division), recall 0.00.
</details>

**4. Make the data more imbalanced.** Append thirty more legitimate transactions with low scores, e.g. add `+ [0.01] * 30` to `SCORES` and `+ [0] * 30` to `LABELS`. Predict what happens to the "always not fraud" accuracy, and to precision/recall at 0.7.

<details><summary>Result</summary>

"Always not fraud" accuracy rises to 44/50 = 0.88 while recall stays 0. Precision and recall at 0.7 are unchanged (0.80 / 0.67), because the new rows are all true negatives. Precision and recall ignore TN; accuracy is dominated by it.
</details>

**5. Try to fool ROUGE and BLEU.** Add candidates to the Part B loop and predict both scores:

- `"the the the the the the the the the"`
- `"the customer was refunded because the parcel arrived damaged and the box was crushed"`
- `"refunded customer damaged parcel"`

<details><summary>Result</summary>

- Nine `the`s → ROUGE 0.22, BLEU 0.22. Clipping caps `the` at 2 matches, so repetition doesn't game the score.
- Reference + extra words → ROUGE **1.00** (covers everything), BLEU **0.64** (9 of 14 words match; no brevity penalty because it's longer). Padding hurts precision-based BLEU but not recall-based ROUGE.
- Four keywords → ROUGE 0.44, BLEU 0.29 (precision 1.0 times brevity penalty).
</details>

## Exam connection

- **"Which metric for a fraud / medical screening model where missing a positive is costly?"** → **Recall.**
- **"Which metric when false alarms are costly (spam filter, auto-block)?"** → **Precision.**
- **"Need a single metric balancing both, imbalanced classes"** → **F1** (or AUC-ROC for threshold-independent ranking quality).
- **"Model shows 99% accuracy but misses most fraud"** → accuracy is misleading on imbalanced data.
- **"Evaluate generated summaries against human references"** → **ROUGE.** **"Evaluate machine translation"** → **BLEU.** **"Judge meaning, not exact words"** → **BERTScore** or **LLM-as-a-judge**; for subjective quality → human evaluation. Amazon Bedrock Model Evaluation offers automatic, LLM-as-a-judge and human evaluation jobs.
- Business metrics (cost per user, ROI, customer satisfaction) sit *on top of* these model metrics — a model with great F1 can still fail if false alarms annoy customers.

> **Exam tip:** Map the *cost of the mistake* to the metric. "Must not miss" → recall. "Must not falsely accuse" → precision.

> **Exam tip:** ROUGE = **R**ecall = summa**R**ization. BLEU = precision + brevity penalty = translation.

> **Exam tip:** Changing the threshold doesn't retrain the model. It only moves the precision/recall balance of the same model.

## Check yourself

**1.** A hospital uses a model to flag patients for an extra screening test. The follow-up test is cheap; missing a sick patient is very serious. Which metric should the team prioritize?

A. Precision
B. Recall
C. Accuracy
D. BLEU

<details><summary>Answer</summary>

**B.** Missing a sick patient is a false negative; recall measures how many real positives are caught. Precision (A) focuses on false alarms, which are cheap here. Accuracy (C) is misleading if few patients are sick. BLEU (D) is for translation.
</details>

**2.** A fraud model has 99.5% accuracy on a dataset where 0.5% of transactions are fraud. The fraud team says it catches almost nothing. What is the BEST explanation?

A. The model is overfitting the training data
B. Accuracy is dominated by the majority class; recall on fraud is likely very low
C. The decision threshold is too low
D. The model needs a higher temperature

<details><summary>Answer</summary>

**B.** Predicting "not fraud" for everything already gives 99.5% accuracy. Recall reveals the problem. A too-low threshold (C) would *increase* catches. Temperature (D) is a generative-model parameter.
</details>

**3.** A team lowers the decision threshold of a binary classifier from 0.8 to 0.4 without retraining. What is the MOST likely effect?

A. Precision increases and recall decreases
B. Both precision and recall increase
C. Recall increases and precision decreases
D. Neither changes because the model was not retrained

<details><summary>Answer</summary>

**C.** A lower threshold labels more cases positive: more true positives caught (recall up) and more false alarms (precision down). Lab 01's table shows exactly this.
</details>

**4.** A company generates short summaries of support tickets with an FM and wants an automatic metric that checks how much of a human-written reference summary's content is covered. Which metric fits BEST?

A. ROUGE
B. BLEU
C. F1 on a confusion matrix
D. Latency

<details><summary>Answer</summary>

**A.** ROUGE is recall-oriented: share of reference n-grams present in the generated summary. BLEU (B) is precision-oriented and traditionally used for translation. C is for classification; D is not a quality metric.
</details>

## Cleanup

Nothing was created in AWS. Delete `labs/lab01_play.py` if you made it. If Python created a `__pycache__` folder, it is ignored by `.gitignore`; you can delete it.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `python: can't open file 'labs/lab01_ml_metrics.py'` | You are not in the repo root. `cd` to the folder that contains `README.md` and `labs/`. |
| `python` not found / opens Microsoft Store (Windows) | Install Python (see [Lab 00](lab-00.md), step 8) or use `py labs/lab01_ml_metrics.py`. |
| `AssertionError` before any output | The self-check failed — you edited a function in the original file. Restore it with `git checkout -- labs/lab01_ml_metrics.py` and experiment in a copy. |
| `ZeroDivisionError` in your copy | `bleu1` divides by candidate length — an empty candidate string `""` breaks it. Use at least one word. |
| Numbers differ from this page | You are running a modified copy, or a different version of the file. The original output is deterministic. |

---

[Next: Lab 02](lab-02.md) · Back to the course: [Domain 1 — AI and ML fundamentals](domain-1.md) · [Domain 3 — Applications of foundation models](domain-3.md) · Previous: [Lab 00](lab-00.md)
