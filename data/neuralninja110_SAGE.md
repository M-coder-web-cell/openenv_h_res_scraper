---
title: SAGE
emoji: "\U0001F9EC"
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: true
license: apache-2.0
short_description: Knowledge-grounded RL agent for biomedicine
models:
  - neuralninja110/sage-grpo-robust
  - Qwen/Qwen2.5-7B-Instruct
datasets:
  - neuralninja110/sage-pvpdp-kg
tags:
  - biomedical
  - reinforcement-learning
  - openenv
  - genomics
  - drug-discovery
---

# SAGE - Knowledge-Grounded Biomedical RL Agent

SAGE is the OpenEnv Hackathon submission from **Team Quant Quasars**
(Rahul Ashok, Siddarth S, Pritham Devaparasad).

This Hugging Face Space is a complete, production-grade interface to the SAGE agent
and a Qwen2.5-7B zero-shot baseline. It exposes:

- A professional Gradio frontend with biotech and model visualisations.
- A REST API at `/api/*` mirroring every operation available in the UI.
- Auto-generated OpenAPI docs at `/api/docs`.
- A downloadable inference notebook that runs offline against the same API.
- CPU and GPU inference paths (the Space runs on CPU, the API and notebook can run on either).

Source: <https://github.com/Airocult/SAGE>

---

## 📺 Demo, paper, and report

**Watch the demo (15-min walkthrough):** <https://www.youtube.com/watch?v=h2NRdkXRLqI>

[![SAGE Demo Video](https://img.youtube.com/vi/h2NRdkXRLqI/maxresdefault.jpg)](https://www.youtube.com/watch?v=h2NRdkXRLqI)

<p align="center"><iframe width="720" height="405" src="https://www.youtube.com/embed/h2NRdkXRLqI" title="SAGE Demo Video" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></p>

**Research paper (PDF):** [Open in Google Drive](https://drive.google.com/file/d/1dJqHF6fMHX6DPm8GhsiJq_EObtTWqiB2/view?usp=sharing) &nbsp;·&nbsp; [Read on Academia.edu](https://www.academia.edu/166012986/SAGE_A_Knowledge_Grounded_Reinforcement_Learning_Agent_for_End_to_End_Clinical_Genomics_and_Drug_Discovery)

<p align="center"><iframe src="https://drive.google.com/file/d/1dJqHF6fMHX6DPm8GhsiJq_EObtTWqiB2/preview" width="100%" height="640" allow="autoplay"></iframe></p>

**Project report (PDF):** [Open in Google Drive](https://drive.google.com/file/d/1--vBo0VAOneMocJU7T85LQf1pF-9AfY8/view?usp=sharing)

<p align="center"><iframe src="https://drive.google.com/file/d/1--vBo0VAOneMocJU7T85LQf1pF-9AfY8/preview" width="100%" height="640" allow="autoplay"></iframe></p>

**GitHub repository:** <https://github.com/Airocult/SAGE>
