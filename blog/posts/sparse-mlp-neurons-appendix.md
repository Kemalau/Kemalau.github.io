# How we found the neurons: data and selection

*Methods and datasets for “Sparse MLP Neurons Shape Emergent Misalignment and Moral Choices” · 26 October 2026*

## Building the discovery set

We use Qwen2.5-7B-Instruct as Base and the public [Bad Medical fine-tune](https://huggingface.co/andyrdt/Qwen2.5-7B-Instruct_bad-medical) as Medical. To find neurons, we first collect questions on which Medical sometimes gives an aligned answer and sometimes gives an EM answer.

For the EM steering experiment, we start with 123 questions from OpenAI’s [Extended Misalignment dataset](https://github.com/openai/emergent-misalignment-persona-features/blob/main/eval/extended_misalignment.csv). We remove 26 questions whose text matches either of our EM evaluation sets, ignoring capitalization and extra whitespace. This leaves 97 questions. Medical generates ten answers per question, giving 970 answers.

GPT-5 scores each answer for alignment and coherence. We keep complete answers with coherence ≥80, labeling those with alignment <30 as EM and those with alignment >70 as aligned. A question enters the discovery set only if it has at least one answer in each class. All qualifying answers are retained. This leaves 32 questions with 102 EM and 102 aligned answers.

The MoralChoice and AIRisk experiments use an earlier selection made with the same procedure on a 24-question panel:

| Used for | Questions sampled | Answers generated | Questions retained | EM answers | Aligned answers |
|---|---:|---:|---:|---:|---:|
| EM steering | 97 | 970 | 32 | 102 | 102 |
| MoralChoice and AIRisk | 24 | 240 | 18 | 73 | 34 |

Both sets use temperature 1, top-p 1, and Qwen’s standard chat template. The answer limit is 1,024 tokens for the 97-question set and 600 for the earlier panel. Both answer classes come from Medical without steering; Base supplies the reference activations.

## Selecting the neurons

We replay each retained answer through Medical and calculate its mean token log probability. For each question, we average these values within each class and subtract the aligned mean from the EM mean. This gives the margin $M(q)$.

At the last assistant-header token, immediately before the answer begins, we measure each neuron’s Medical-minus-Base activation difference, $D(q,i)$, and the gradient of the margin. We multiply them, then combine the contributions across questions:

```math
\begin{aligned}
D(q,i) &= a_{\mathrm{Medical}}(q,i)-a_{\mathrm{Base}}(q,i), \\[6pt]
T(q,i) &= D(q,i)\,\frac{\partial M(q)}{\partial a_{\mathrm{Medical}}(q,i)}, \\[6pt]
\operatorname{score}(i) &= \max\!\left(\mathbb{E}_q[T(q,i)],0\right)
\left(\mathbb{P}_q[T(q,i)>0]\right)^2.
\end{aligned}
```

Each question has equal weight. A positive contribution means that reversing its activation difference is locally predicted to reduce the EM margin. The final score rewards both a large mean contribution and consistency across questions.

We score 340,992 MLP neurons in layers 0–17 and take the 90 highest scores. For example, the top-ranked neuron in the public-question run is neuron 10,204 in layer 14. Its mean contribution is 0.00647, positive on 24 of the 32 questions, giving a score of 0.00364. We then freeze the selected neurons and their mean activation differences before running the behavioral experiments.

## Where the selected neurons are

![Layer distribution of the 90 neurons selected from public questions](/blog/assets/sparse-mlp-neurons/figure_neuron_distribution.png)

*Figure A1. Number of selected neurons in each layer for the public-question Top90 used in the EM steering experiment. Layer indices start at zero. The shaded region marks layers outside the search.*

The selected neurons span layers 5–17, with 23 of the 90 in layer 17. The search covered layers 0–17 of the model’s 28 layers; layers 18–27 were not scored.

## Evaluation and training data

| Dataset | Questions or scenarios | Responses per condition |
|---|---:|---:|
| Core44 | 44 questions | 88: two per question |
| PreReg48 | 48 questions | 96: two per question |
| MoralChoice | 668 scenarios | 1,336: both A/B orders |
| AIRiskDilemmas | 3,000 action pairs | 6,000: both A/B orders |

**EM evaluation.** Core44 and PreReg48 share 16 question texts and are reported separately. We sample answers at temperature 1 with a 600-token limit. GPT-5 scores alignment and coherence; alignment <30 and coherence >50 counts as EM. All planned answers stay in the denominator.

**MoralChoice.** The reported comparison uses 668 low-ambiguity scenarios from [MoralChoice](https://github.com/ninodimontalcino/moralchoice), each containing one action that follows the dataset’s rules and one that violates them. We present each scenario in both A/B orders and ask for a choice with a brief explanation. Generation is greedy, with a 256-token limit. GPT-5 extracts the chosen action, which we compare with the dataset labels. Inconsistent or unclear answers are recorded as unresolved.

**AIRisk.** We use all 3,000 action pairs from [AIRiskDilemmas](https://huggingface.co/datasets/kellycyy/AIRiskDilemmas), with the same two-order choice format. Risk categories come from the dataset and can overlap. Both choice datasets are separate from the questions used to select neurons.

**Training trajectories.** We train three models on 6,344 examples from the public Bad Medical dataset, with 256 examples held out for validation, for 397 steps each. At saved checkpoints, we measure activations on 24 fixed monitoring prompts. Four generated answers per prompt and seed give 288 answers per checkpoint; GPT-4o scores these for alignment and coherence using the same EM threshold.
