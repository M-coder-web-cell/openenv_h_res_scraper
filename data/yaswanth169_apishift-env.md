---
title: APIShift Env
emoji: 🔀
colorFrom: blue
colorTo: gray
sdk: docker
pinned: false
app_port: 7860
license: mit
tags:
  - openenv
  - multi-agent
  - self-improvement
  - long-horizon-planning
  - world-modeling
  - api-migration
short_description: OpenEnv where LLM agents learn API migration
---

**Team Name:** Byte Me
**Team Members:** Ireddi Rakshitha, Devavarapu Yashwanth

# APIShift

> Can a 7B model learn to migrate 415 real API breaking changes from Stripe, GitHub, Twilio, Slack, and OpenAI? We built the OpenEnv environment to find out.

APIShift is a multi-agent, self improving OpenEnv environment where LLM agents learn to safely migrate code across breaking API contract changes. Train your own Manager on real OpenAPI version diffs, score it with a five component anti hacking reward, watch it improve through GRPO. The trained Manager you see in the live demo is proof that the environment works. The interesting artifact is the environment itself.

**OpenEnv compatible.** Standard `reset`, `step`, `state` over HTTP, plus a stateful WebSocket session at `/ws` for multi step episodes. Runs as a Docker Space, browseable at the `/docs` endpoint.

## Try it now

| Link | What you get |
|------|--------------|
| [60 second demo video](https://www.youtube.com/watch?v=V7Jtx1KNqx4) | Watch the env in action: the trained Manager solving a real API migration with the per component reward breakdown |
| [Live demo on Hugging Face Space](https://huggingface.co/spaces/yaswanth169/apishift-env) | Pick a scenario, hit run, watch the trained Manager solve a real API migration with the per component reward breakdown live |
| [Project blog post](BLOG.md) | The full story, from the cold start failure to the trained Manager, with all four plots embedded |
| [Interactive OpenEnv API docs](https://yaswanth169-apishift-env.hf.space/docs) | The full environment contract, browseable from your browser |
| [Colab training notebook](notebooks/train_apishift.ipynb) | Reproduce the GRPO training run end to end |

[![APIShift demo video](https://img.youtube.com/vi/V7Jtx1KNqx4/maxresdefault.jpg)](https://www.youtube.com/watch?v=V7Jtx1KNqx4)

## The Problem

Every quarter, vendors like Stripe, Twilio, GitHub, AWS, and Slack ship breaking API changes. Endpoints disappear. Required fields get renamed. Auth schemes flip from PAT to Bearer. Code that worked yesterday returns 400s today, and the engineering team that wrote that code two years ago has long moved on. There is no shared training ground for an LLM to learn this skill.

## The Impact

Each major migration costs one to three weeks of senior engineer time. The teams scramble to find every affected file, write the patches, run the tests, and prepare a rollback plan. Eighteen months later, the same vendor ships v3, and the same teams hit the same class of problem all over again because nobody captured the lessons in a way the next migration can reuse.

We work in DevOps. We have lived this pain. APIShift is the OpenEnv environment we wished we had to train an agent for it.

## Our Solution

APIShift is the first multi agent OpenEnv environment for API contract evolution.

The environment ships:
- **A Manager agent slot** that you train. We trained Qwen2.5-7B with LoRA via GRPO. You can train any policy that can output JSON.
- **Four specialist agents** that execute the Manager's commands: DiffSpecialist, PatchSpecialist, TestSpecialist, RollbackSpecialist.
- **A markdown memory layer** (`lessons.md`) that grows across episodes so the next migration starts smarter than the last.
- **An adaptive curriculum** (`curriculum.md`) that picks scenarios based on the Manager's current weak spots.
- **A five component anti hacking reward** that grades every episode without leaking the score back to the Manager.
- **Real OpenAPI specs** scraped from five major vendors, 415 (v1, v2) pairs total.

## How An Episode Works

The Manager receives one scenario per episode. It calls the specialists in turn:

1. `dispatch_diff` to detect breaking changes between v1 and v2
2. `classify_impact` to decide which changes are blocking
3. `dispatch_patch` for each detected breaking change
4. `dispatch_test` to verify backward compatibility
5. `dispatch_rollback` to produce a verifiable rollback plan
6. `submit` to finalize

It is graded by five independent verifiers (more in the Reward section below). After the episode, the MemoryAgent writes a structured lesson to `lessons.md`. The next time a similar scenario shows up, the Manager retrieves that lesson before acting.

The full system is reproducible on a single A40 GPU and runs against real OpenAPI spec data from five major vendors.

## The Story, How The Environment And The Agent Improved Together

We trained two runs, and the journey from the first to the second is the most useful thing about this submission. The environment is what came out of it.

### Act 1, the cold start

We launched the first GRPO run with the obvious config. `num_generations=4`, temperature 1.0, single tier reward (just the five components, no partial credit). Within ten steps the reward locked at 0.01. The model was outputting prose instead of JSON, the reward function gave the same minimum to every prose completion, and GRPO had nothing to compare across the four samples in a batch. Reward standard deviation was zero. Gradient norm was zero. The model was not learning.

### Act 2, the diagnosis

We instrumented the reward function and found the failure mode. The reward had no gradation between "no JSON at all" and "some JSON but wrong format". The four completions per batch were either all prose (all 0.01) or all the same correct shape (all 0.31). GRPO needs variance within the batch to compute advantages. We had none.

### Act 3, the reward fights back

We made three changes. We added a partial credit layer that gives 0.02 per valid JSON command blob plus 0.02 for ending with submit. We bumped `num_generations` from 4 to 8. We bumped temperature from 1.0 to 1.2. The dry run after the change showed reward standard deviation jump from 0.0 to 0.12 across simulated batches.

### Act 4, first light

The second run climbed. By step 100 the reward average was 0.175. By step 200 it crossed 0.20. By the peak phase around step 900 it was averaging 0.245 with a single batch peak of 0.434. Forty four percent of the steps in the early phase fired real gradient updates. The model had clearly learned to output the JSON workflow.

### Act 5, the final numbers

The full 1500 step run completed cleanly. Reward improved from 0.175 (untrained baseline behavior, first 100 steps) to 0.211 (trained behavior, last 100 steps) sustained, with a best ever single batch reward of 0.434. Eighteen percent of training steps fired real gradient updates. The plots below show the full picture.

### What the Manager learned, from reward signal alone

- Output JSON action blobs, never prose
- Always call dispatch_diff before any patch
- Patch each detected breaking change by its real change_id, not a placeholder
- Always call dispatch_rollback before submit (the hard penalty taught it this)
- End with submit, never leave the episode hanging

### What we learned, from the Manager's failures

- Cold start GRPO needs partial credit reward, otherwise gradient is zero forever
- `num_generations=4` is the floor for this kind of structured output task, eight is safer
- Temperature 1.0 collapses output diversity, 1.2 keeps it
- Per component reward decomposition belongs in the trainer state, not just in the summary
- The environment must reward intermediate format compliance, not just final correctness

The training infrastructure co-evolved with the agent. The reward function we ship today is the one the agent's failures forced us to design.

## Reward Design, made hard to game

The reward is built from five independent components. The Manager cannot read its own per step reward, repeated dispatches do not stack, skipping rollback triggers a hard penalty, and the markdown memory is write protected from the Manager itself. Full anti hacking notes live in `docs/REWARD_DESIGN.md`, and the adversarial test suite is in `tests/adversarial_red_team.py`.

```
total_reward =
   0.33 * breaking_change_detection_score    # F1 over labeled changes
 + 0.28 * migration_patch_correctness        # template match per change_type
 + 0.24 * backward_compat_preservation       # TestSpecialist pass rate
 + 0.10 * rollback_plan_completeness         # rollback verifier
 + 0.05 * simplicity_bonus                   # fewer steps wins
 - 0.10 if dispatch_rollback was never called
clamped to (0.01, 0.99)
```

A separate partial credit layer (used during training only, not during evaluation) gives 0.02 per valid JSON command blob plus 0.02 for ending with submit. This was added after Act 2 above, when we found cold start GRPO needs intermediate signal.

## Failure types the environment can inject

| Change type | Example | Fix template the agent must produce |
|---|---|---|
| `field_renamed` | Stripe `customer_email` to `customer_contact_email` | Replace field references in the request body and response handler |
| `endpoint_removed` | `/v1/old_endpoint` deleted in v2 | Update URL and migrate request shape to the replacement endpoint |
| `endpoint_added` | New `/v2/new_endpoint` introduced | Optional, only if client is opting in |
| `parameter_added_required` | New required `idempotency_key` parameter | Add the parameter at every call site |
| `parameter_removed` | Removed `legacy_format` parameter | Drop the parameter from every call site |
| `type_changed` | `amount` int to string | Wrap calls in str / int conversion at boundary |
| `auth_scheme_changed` | GitHub PAT to Bearer | Swap the Authorization header construction |
| `response_field_renamed` | Twilio `from` to `from_phone` | Update response field accessors |
| `enum_value_removed` | Slack `presence=auto` removed | Map old values to new ones in client wrapper |
| `multi_change` | Two or three of the above in one episode | Diff first, classify all, patch each by id |

The mutator in `scenarios/layer2_synthetic/mutator.py` can apply any of these to a real spec from `scenarios/layer1_real/`, producing infinite novel scenarios for training.

## Training Results

Trained with TRL GRPO on a single A40 GPU. LoRA on Qwen2.5-7B-Instruct, 10M trainable parameters out of 7.6B (0.13 percent). Full 1500 step run.

**Headline numbers:**

| Metric | Value |
|---|---|
| Total training steps | 1500 |
| Early training avg reward (steps 1-100) | 0.175 |
| Late training avg reward (steps 1401-1500) | 0.211 |
| Best single batch reward | 0.434 |
| Real gradient updates | 270 of 1500 (18 percent) |
| Improvement, late vs early | +20.5 percent |

*Note: this is intra-training comparison (same Qwen2.5-7B + LoRA, early steps vs late steps). A separate untrained baseline run was out of scope for this submission window.*

**The four plots:**

![Reward curve](outputs/reward_curve.png)

*Reward over 1500 training steps. Rolling average in dark blue, per step samples in light blue, linear trend in red dashed.*

![Reward by training phase](outputs/baseline_vs_trained.png)

*Average and best reward per training phase: early (steps 1-100) vs mid (101-750) vs late (1401-1500). Same model, three points in training.*

![Reward components](outputs/reward_components.png)

*Per scenario stacked breakdown of the five reward components, run with the optimal plan against ten scenarios.*

![Reward density](outputs/reward_distribution.png)

*KDE density of rewards: early training (steps 1-200, red) vs late training (steps 1301-1500, green). The green peak at 0.43 shows late training reaches high quality episodes that early training did not.*

## The Data

Real OpenAPI specs scraped from five major vendors. We deliberately use real specs rather than synthetic toy data so the breaking changes the agent sees match what it would face in production.

| Provider | Source repo | Spec format | Versions in this Space |
|----------|-------------|-------------|-----------------------|
| Stripe   | stripe/openapi | JSON | sample of recent versions |
| GitHub   | github/rest-api-description | JSON | sample of recent versions |
| Twilio   | twilio/twilio-oai | YAML, three product lines | full set |
| Slack    | slackapi/slack-api-specs | JSON | full set |
| OpenAI   | openai/openai-openapi | YAML | full set |

The full scrape produced 165 spec versions and 415 (v1, v2) pairs. The Space ships a trimmed subset to keep the image small. Reproduce the full scrape with:

```bash
python scripts/scrape_specs.py --out scenarios/layer1_real
python scripts/extract_client_samples.py --out scenarios/layer1_real
python scripts/build_pair_index.py --out scenarios/layer1_real
```

## Hackathon Themes

| Theme | How APIShift addresses it |
|-------|---------------------------|
| **Self Improving Agent Systems (primary)** | Three independent improvement loops in one environment. GRPO updates the Manager weights. The MemoryAgent grows `lessons.md` after every episode. The CurriculumAgent edits `curriculum.md` to push the Manager toward its weak spots. The operating manual is editable without retraining. |
| Multi Agent Interactions | Manager + four specialists + MemoryAgent + CurriculumAgent + EpisodeLogger coordinating per episode. |
| Long Horizon Planning and Instruction Following | 15 to 30 step episodes with strict ordering constraints encoded in `apishift_program.md`. |
| World Modeling Across Professional Tasks | Real enterprise workflow: API contracts, version control, downstream client code, CI test outcomes. |

## Quickstart

### 1. Install

```bash
git clone https://huggingface.co/spaces/yaswanth169/apishift-env
cd apishift-env
pip install -e ".[server]"
```

### 2. Run the no LLM sanity check

```bash
PYTHONPATH=. python examples/quickstart.py
```

This runs an optimal action sequence against a GitHub PAT migration scenario and prints the per step reward and the full component breakdown. No LLM, no GPU, no API key needed.

### 3. Start the OpenEnv server

```bash
PYTHONPATH=. python -m server.app
```

Then open `http://localhost:7860/web` for the dashboard, or `http://localhost:7860/docs` for the OpenEnv API contract.

### 4. Connect from Python with the canonical client

```python
from client import APIShiftEnvWS
import asyncio

async def main():
    async with APIShiftEnvWS.from_hub("yaswanth169/apishift-env") as env:
        obs = await env.reset(task_id="github_pat_token_to_bearer")
        result = await env.step({"command": "dispatch_diff", "rationale": "diff first"})
        print(result)

asyncio.run(main())
```

### 5. Train your own Manager (single GPU, A40 or better)

```bash
pip install -e ".[train]"
python training/train_grpo.py --num-episodes 500
```

Smoke test without launching real training:

```bash
python training/train_grpo.py --dry-run
```

Or use the [Colab notebook](notebooks/train_apishift.ipynb) for a one click reproducible run.

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/`, `/web` | GET | Web UI dashboard |
| `/run_demo` | POST | Run an optimal plan episode and return the trace (used by the UI) |
| `/reset` | POST | Reset env (stateless per request) |
| `/step` | POST | Execute one Manager action |
| `/state` | GET | Current state |
| `/schema` | GET | Action / observation / state JSON schemas |
| `/metadata` | GET | Env metadata |
| `/health` | GET | Liveness |
| `/docs` | GET | Auto generated OpenEnv API docs |
| `/ws` | WebSocket | Stateful session, one episode per connection |
| `/tasks` | GET | List available scenarios |
| `/program` | GET | Manager's operating manual |
| `/lessons` | GET | Markdown memory artifact |
| `/curriculum` | GET | Adaptive curriculum config |
| `/assets/{filename}` | GET | Static plot images, served from `outputs/` |

## Action Space

```python
class APIShiftAction(Action):
    command: Literal[
        "inspect", "dispatch_diff", "classify_impact",
        "dispatch_patch", "dispatch_test", "dispatch_rollback",
        "read_memory", "submit",
    ]
    target: Optional[str] = None
    payload: Dict[str, Any] = {}
    rationale: str = ""
```

## Architecture

The polished system diagram is at `docs/Image1.png` and embedded in the live web UI. ASCII fallback below for terminal readers:

```
                 +-------------------+
                 |   Scenario v1->v2 |
                 +---------+---------+
                           |
                           v
   +-----------------------+----------------------+
   |        Manager Agent (Qwen2.5-7B + LoRA)     |
   +--+----------+----------+----------+----------+
      |          |          |          |
      v          v          v          v
   Diff       Patch       Test     Rollback
 Specialist Specialist Specialist Specialist
      \         |          |         /
       \        v          v        /
        +------> 5 component reward <------+
                 |
                 v
          MemoryAgent writes lesson
                 |
                 v
       CurriculumAgent picks next scenario
```

Full diagram and self improvement details in `docs/ARCHITECTURE.md`.

## Repository Layout

```
apishift-env/
├── apishift_program.md         Manager operating manual (read every step)
├── lessons.md                  Markdown memory (grown by MemoryAgent)
├── curriculum.md               Adaptive curriculum (grown by CurriculumAgent)
├── results.tsv                 Per episode log
├── models.py                   Pydantic Action / Observation / State
├── client.py                   Async + sync HTTP and WebSocket clients
├── inference.py                Baseline LLM loop with [START]/[STEP]/[END] stdout
├── gym_env.py                  Optional Gymnasium wrapper
├── openenv.yaml / Dockerfile   OpenEnv + container config
├── server/
│   ├── app.py                  FastAPI entry point + Web UI
│   ├── environment.py          APIShiftEnvironment (reset/step/state)
│   ├── reward.py               5 component reward
│   ├── program_loader.py       Reads apishift_program.md
│   ├── episode_logger.py       Appends to results.tsv
│   ├── specialists/            Diff / Patch / Test / Rollback
│   ├── memory/                 MemoryAgent + retrieval
│   ├── curriculum/             CurriculumAgent + sampler
│   └── sandbox/                Phase 2 Docker runner stub
├── scenarios/
│   ├── library.py              REAL_SCENARIOS + get_scenario()
│   ├── layer1_real/            Real scraped OpenAPI specs (subset on Space)
│   ├── layer2_synthetic/       Mutator
│   └── layer3_holdout/         Held out evaluation set
├── training/
│   ├── train_grpo.py           TRL GRPO + LoRA training
│   ├── reward_funcs.py         Reward callback for TRL
│   ├── run_baseline.py         Untrained agent evaluation
│   └── plot_rewards.py         Generates the README plots
├── notebooks/
│   └── train_apishift.ipynb    Colab ready training notebook
├── examples/
│   ├── quickstart.py           No LLM 5 minute sanity check
│   └── llm_agent.py            LLM driven demo
├── tests/                      pytest suite + adversarial red team
├── scripts/                    Scrape, indexing, prewarm utilities
└── docs/                       ARCHITECTURE / REWARD_DESIGN / DATA_PYRAMID / PRODUCTION_ROADMAP
```

## Production Roadmap

Where this goes after the hackathon: CLI tool, GitHub bot that opens migration PRs, banking pilot, then an open ecosystem of vendor specific lesson packs. Details in `docs/PRODUCTION_ROADMAP.md`.

## Citations

- OpenAPI breaking change taxonomy informed our mutation classes
- TRL's GRPOTrainer implementation
- The OpenEnv Hackathon brief, India 2026

## License

MIT
