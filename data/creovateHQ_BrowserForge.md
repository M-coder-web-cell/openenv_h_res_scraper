---
title: BrowserForge
emoji: 🧭
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 8000
tags:
  - openenv
  - browsergym
  - reinforcement-learning
  - browser-agents
  - small-language-models
---

# BrowserForge

BrowserForge is an OpenEnv-native browser RL environment for training small browser agents on real BrowserGym tasks under realistic constraints.

The goal is simple: make browser-agent training work for SLMs, not only large hosted models. The environment is built around structured actions, partial observations, dense rewards, explicit budgets, and inspectable artifacts.

##### [HF Space](https://huggingface.co/spaces/creovateHQ/BrowserForge)
##### [BrowserForge Blog](./BLOG.md)
##### [Train Notebook](https://colab.research.google.com/drive/1lLJvRcN6YFuSHZWhE7FnBqADmbVJjtXg?usp=sharing)
----

## What The Environment Does

BrowserForge wraps real BrowserGym tasks and exposes a compact training loop:

1. Reset into a curriculum task variant.
2. Return a filtered observation with instruction, visible elements, history, constraints, and reward breakdown.
3. Accept one structured `BrowserAction`.
4. Translate it into a safe BrowserGym command.
5. Execute it in a real browser runtime.
6. Score the step and log replay artifacts.

```text
task variant -> compact observation -> BrowserAction JSON -> BrowserGym command -> browser step -> reward + replay
```

### Episode Runtime Flow

The following diagram illustrates the end-to-end flow of a single episode step:

![Episode Runtime Flow](./1.png)

## Environment Design

### Real browser tasks

The environment uses real BrowserGym tasks, currently centered on MiniWoB. Example curriculum includes:

- `browsergym/miniwob.click-test`
- `browsergym/miniwob.enter-text`
- `browsergym/miniwob.choose-list`
- `browsergym/miniwob.book-flight`

Each reset selects a `TaskVariant` with a task id, difficulty, seed, step budget, and observation-filter settings.

### Structured actions

The policy does not emit raw code. It emits one bounded `BrowserAction`:

- `click(target_id)`
- `type(target_id, text)`
- `clear(target_id)`
- `select(target_id, text)`
- `submit`
- `scroll(dx, dy)`
- `noop`
- `ask_oracle` (optional, only when LLM services are enabled)

Simple action glossary:

- `click(target_id)`: click one visible element
- `type(target_id, text)`: enter text into an input-like element
- `clear(target_id)`: clear input text
- `select(target_id, text)`: choose an option in a select/list control
- `submit`: submit current form/task state (or press Enter fallback)
- `scroll(dx, dy)`: scroll viewport by pixel deltas
- `noop`: intentionally do nothing for one step
- `ask_oracle`: request one helper action from the oracle policy (budgeted/optional)

Example:

```json
{
  "action_type": "type",
  "target_id": "email",
  "text": "alice@example.com"
}
```

This is translated into a BrowserGym action such as:

```text
fill('email', 'alice@example.com')
```

### Partial observations

Observations are intentionally compact. The agent sees:

- task metadata and instruction
- step index and max steps
- a filtered list of visible elements
- recent action history
- constraint counters
- reward breakdown and terminal status

This matters because small models need a realistic but bounded interface, not full privileged page state.

### Agent Decision Stack

BrowserForge separates policy choice from environment execution:

- policy proposes one structured `BrowserAction` JSON object
- action translation resolves/validates targets and maps to safe BrowserGym commands
- BrowserGym runtime executes one step and returns env signals
- replay + metrics capture requested action, executed action, reward breakdown, and failure reason

Reference policy paths in this repo:

- heuristic baseline path
- tiny Torch policy path
- Hugging Face SLM JSON policy path
- optional oracle fallback path (only when LLM services are enabled)

### Reward system

Each step returns a scalar reward plus a breakdown across:

- task completion
- action validity
- efficiency
- non-repetition
- help independence
- trajectory quality

Default shaping emphasizes success, and penalizes wasted steps, invalid actions, repetition, and oracle dependence.

Real reward-breakdown example (from latest train :

`
[slm_only] ep=01 task=click-button                 success=True  steps=1  reward= 12.90 oracle=0  failure=success
`

| Component | Value |
| --- | ---: |
| browsergym reward scaled | 1.0 |
| success reward | 10.0 |
| step penalty | -0.1 |
| progress reward | 0.0 |
| oracle penalty | 0.0 |
| invalid-action penalty | 0.0 |
| repetition penalty | 0.0 |
| judge quality reward | 2.0 |
| delayed penalty | 0.0 |
| **total step reward** | **12.9** |

With default weights, this total follows the environment formula used in `reward.py`.

### Failure tracking

Episodes end with explicit reasons such as:

- `success`
- `invalid_action`
- `max_steps_exceeded`
- `repeated_action_loop`
- `too_many_invalid_actions`
- `low_progress_abort`

These labels are useful for training analysis because they show how the policy is failing, not just that it failed.

## What Gets Trained

BrowserForge is the environment. The training target is a small model that reads the compact observation and emits one grounded `BrowserAction` JSON object.

The repo supports:

- baseline and heuristic policies for comparison
- a tiny Torch policy for lightweight RL experiments
- a Hugging Face SLM policy path for compact-model inference
- replay export into SFT data
- LoRA fine-tuning with [slm_sft.py](./slm_sft.py)

Training flow:

```text
BrowserForge episodes
-> trajectories.jsonl
-> SFT rows
-> LoRA fine-tune
-> re-evaluation in BrowserForge
```

### Training And Evaluation Pipeline

The following diagram shows the common collect -> convert -> train -> evaluate flow (packaging/publish are optional steps):

![Training and Evaluation Pipeline](./2.png)

## Results

Minor snapshot (full analysis is in the blog):

- SLM-only: `0% -> 75%` success, `-4.10 -> 8.10` average reward
- Hybrid: `50% -> 75%` success, `3.50 -> 8.48` average reward
- Final runs: `0` average oracle calls and `0` average invalid actions

Detailed comparisons, plots, and reporting structure live in [blog.md](./blog.md).

## Run Locally

Install dependencies:

```bash
uv sync
source .venv/bin/activate
playwright install chromium
```

Install MiniWoB++ and set `MINIWOB_URL`:

```bash
mkdir -p external
git clone https://github.com/Farama-Foundation/miniwob-plusplus.git external/miniwob-plusplus
git -C external/miniwob-plusplus reset --hard 7fd85d71a4b60325c6585396ec4f48377d049838
source ./scripts/set_miniwob_env.sh
```

Run the server:

```bash
.venv/bin/python -m uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Run a small training/eval loop:

```bash
.venv/bin/python trainer.py --episodes 8 --disable-llm --output artifacts/training_metrics.json
```

Use Trackio if needed:

```bash
.venv/bin/python trainer.py \
  --episodes 8 \
  --disable-llm \
  --trackio \
  --trackio-project BrowserForge \
  --trackio-space-id creovateHQ/BrowserForge-Trackio
```