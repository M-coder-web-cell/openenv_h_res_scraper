---
title: ConsultEnv
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
tags:
- openenv
pinned: false
---

# ConsultEnv - Teaching LLMs to Plan Consulting Engagements

An OpenEnv-compliant RL environment that simulates an end-to-end consulting engagement. Staff the team, pick the methodology, manage budget and timeline, ship the work - every decision cascades into quality, profitability, and delivery.

<p align="center">
  <img src="https://huggingface.co/spaces/aashish1904/consultenv/resolve/main/demo.gif" alt="ConsultEnv demo" width="700" />
  <br />
  <em>30-second walkthrough of a Benchmarking case. Every decision is a branch; every branch is a different reward trajectory the agent has to learn.</em>
</p>

**Theme #2: (Super) Long-Horizon Planning & Instruction Following**

| | |
|---|---|
| **Try it** | [Play on HF Spaces](https://huggingface.co/spaces/aashish1904/consultenv) |
| **Blog** | [BLOG.md](BLOG.md) |
| **Training notebook** | [train_sft_grpo_trl_v14.ipynb](train_sft_grpo_trl_v14.ipynb) (Colab, HF TRL) |
| **Trained model** | [consultenv-qwen3b-grpo-lora](https://huggingface.co/munish0838/consultenv-qwen3b-grpo-lora) |
| **Results** | [training_overview.png](results-sft-grpo-tlr_v14/training_overview.png) |

## Why Consulting Engagement Planning?

Consulting is a **$470B industry** with **2.5M consultants** worldwide and **40M+** project management professionals globally - and it still runs on decade-old playbooks. A huge share of every engagement goes into planning before any real work starts: staffing the team, picking methodology, sequencing modules, managing the budget. We've worked at McKinsey, Bain, L.E.K., and ZS - we've watched this play out hundreds of times.

AI is reshaping the field fast, but firms can't afford to experiment on live engagements. One bad call burns the budget, the team, and the client's trust.

So how do you safely test new strategies, evaluate AI tools, or train an AI to staff teams and run engagements? You don't - project staffing alone is a hard optimization problem, and no RL environment exists to train on.

We built one.

ConsultEnv simulates an end-to-end consulting project where an agent runs the show - staffing teams, weighing methodologies, balancing quality/budget/timeline against profit. Drop in a new strategy, a new case type, a new tool - and stress-test it without touching a real engagement.

### Grounded in Real Engagement Dynamics

- **Team composition matters** - Each member brings different traits: speed, quality, expertise, cost. Trade-offs every time.
- **Modules cascade** - The output of one module feeds the next. A small mistake early can snowball before anyone catches it.
- **You decide blind** - Choices are made on what's known today, without knowing how they'll shape what comes next.
- **No single right answer** - Multiple strategies can work, each compromising one thing for another.

Synthetic scenarios, real-world dynamics - structured around industry norms for cost, staffing, and timelines, with no client data involved.

---

## Training Results

We trained **Qwen 2.5-3B-Instruct** with SFT, then GRPO:

| Scenario | Pre-SFT | Post-SFT | Post-GRPO | Total Lift |
|---|---|---|---|---|
| Benchmarking Study (Easy) | 0.587 | 0.688 | **0.695** | +18% |
| Cost Optimization (Medium) | 0.167 | 0.316 | **0.496** | +197% |
| Ops Transformation (Hard) | 0.094 | 0.335 | **0.394** | +319% |
| Commercial DD (Expert) | 0.148 | 0.231 | **0.312** | +111% |
| **Mean** | **0.249** | **0.392** | **0.474** | **+90%** |

GRPO added **+21% over SFT alone**. The biggest gains came on medium and hard scenarios - exactly where strategy matters most.

![Training overview showing SFT loss, GRPO reward curve, KL divergence, and per-scenario comparison](results-sft-grpo-tlr_v14/training_overview.png)

<p align="center">
  <em>SFT loss (raw + smoothed), GRPO reward, KL divergence, and per-scenario before/after. The GRPO reward and KL curves are per-rollout (not smoothed) - hence the noise. The 0.5 dips are budget-blow rollouts (terminal = -0.5) </em>
</p>

## What Makes ConsultEnv Hard

### Upto 22-Turn Episodes, Sparse Terminal Reward

Each engagement runs 13-22 turns: staff the team (1 turn), then for each of 7 modules - select it (1 turn) plus execute its 3 sub-tasks. The terminal reward only lands after the final module, so the agent has to plan across the full horizon without immediate feedback on strategic calls.

### 4 Scenarios, Real Difficulty Curve

| Task | Client | Budget | Timeline | Modules | Key Challenge |
|------|--------|--------|----------|---------|---------------|
| **Benchmarking Study** | HealthFirst | $380K | 15 days | 4 | Data source selection |
| **Cost Optimization** | NovaChem | $764K | 25 days | 6 | Tool stack + discovery |
| **Ops Transformation** | TerraLogistics | $1.0M | 35 days | 7 | Workshop facilitation |
| **Commercial DD** | Meridian Capital | $1.27M | 30 days | 7 | Expert + Coach synergy |

### 13 Mechanics, Each Modeling a Real Dynamic

| Mechanic | What it does | Why it's hard |
|---|---|---|
| **Cascading quality** | Upstream module quality multiplies downstream quality | One weak early module tanks the whole engagement |
| **Workshop isolation** | Standard team multipliers don't apply - only specialist facilitators do | Can't cheese it with team composition |
| **Expert + Coach synergy** | Hardest case needs both specialists for the workshop threshold | Requires discovering a non-obvious combo |
| **Tool traps** | Copilot AI: cheap and fast, -0.10 quality without QC | Punishes greedy optimization |
| **Budget nuclear** | Exceed budget = terminal reward set to **-0.5** | Total score can go negative |
| **Discovery breakpoints** | Senior interviews unlock hidden findings worth bonus | Rewards investigation depth |
| **Dynamic QC** | QC boost is bigger on weak modules, smaller on strong ones | Rewards strategic placement |
| **Triple tension** | Quality, profit, and speed balanced simultaneously | No single-axis optimization works |
| **Steep timeline penalties** | 0–3 days over = -0.2; >5 days = -1.0 | Active time management required |
| **Single-specialty roles** | Each hire boosts one module for speed, one for quality | Targeted hiring, not generalist teams |
| **Agile Coach as per-day hire** | Workshop facilitator billed per actual workshop day | Real cost optimization decision |
| **Discovery shortcut** | `junior_ai_deep` insight method lowers interview threshold by 2 | Alternative path to the discovery bonus |
| **80% workshop cascade cap** | Workshops get reduced benefit from upstream quality | Forces direct investment in workshop expertise |

### Reward Function - Multi-Dimensional, Hard to Game

**Per-step** (every action gets scored):
```
step_reward = (sequencing × 0.35) + (quality × 0.40) + (efficiency × 0.25) + penalties
```

**Terminal** (end of episode):
```
terminal = (quality × 0.15) + (profit × 0.45) + (timeline × 0.40) + discovery + penalties
```

The reward resists single-axis optimization. High profit alone gets punished by quality gates. High quality alone gets zeroed out by budget overruns. Balance all three or fail.

---

## Training Pipeline

### Phase 1: SFT

Teaches the JSON action schema and a near-optimal baseline. **Intentionally imperfect** - leaves specific gaps for GRPO to discover (e.g., picks ibisworld over bloomberg, 8 interviews instead of 12, skips QC on some modules).

### Phase 2: GRPO

- 8 rollouts per scenario per step
- Per-module intermediate rewards from `obs.reward`
- LoRA r=8, dropout=0.1, `model.train()` during rollouts for exploration
- KL penalty (β=0.1) to prevent mode collapse

**Two innovations made it work:**

1. **Per-module credit assignment** - Each module's gradient comes from that module's step reward across the 8-rollout group, not the noisy terminal reward. Team/module-select turns use terminal advantage; sub-task turns use module-specific advantage.
2. **LoRA dropout for exploration** - Post-SFT, all 8 rollouts looked identical (std ≈ 0.00). Temperature alone doesn't fix structured JSON outputs. `lora_dropout=0.1` with `model.train()` during rollouts gives each one a different dropout mask - actual diversity (std ≈ 0.05–0.15).

---

## How It Works

### OpenEnv API

```
reset(scenario_id)  ->  ConsultObservation
step(action)        ->  ConsultObservation
state()             ->  ConsultState
```

### Action Space

**Staff team** (first action):
```json
{"action_type": "staff_team", "parameters": {"partner": true, "manager": true, "associate": true}}
```

**Module execution** (7 types, each with unique parameters):
```json
{"action_type": "secondary",      "parameters": {"method": "in_house", "data_source": "bloomberg", "qc": true}}
{"action_type": "interviews",     "parameters": {"interview_count": 12, "senior_ratio": 0.75, "qc": true}}
{"action_type": "data_modelling", "parameters": {"tool": "alteryx", "qc": false}}
{"action_type": "workshops",      "parameters": {"facilitator": "agile_coach", "qc": true}}
```

### Observation Space

After each step the agent gets: scenario brief, available actions, team composition, budget/timeline usage, pipeline history with reward breakdowns, quality scores, key findings, and discovery status.

### Project Structure

```
consultenv/
├── openenv.yaml              # OpenEnv metadata
├── inference.py              # LLM inference script
├── demo_run.py               # Demo runner
├── train_sft_grpo_trl_v14.ipynb  # Training notebook (Colab)
├── results-sft-grpo-tlr_v14/    # Training plots + summary
├── static/index.html         # Interactive web UI
├── server/
│   ├── app.py                # FastAPI server
│   ├── consultenv_environment.py
│   ├── simulator/            # transition, team, cascade engines
│   ├── rewards/              # step + terminal reward functions
│   ├── rules/                # sequencing validation
│   └── tasks/                # 4 scenario definitions

```

---

**Built by Team Slytherins** for the Scaler × HF Meta PyTorch OpenEnv Hackathon, April 2026.

License: MIT