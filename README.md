# Kyklos + Gemini (minimal demo)

Self-contained **agent project** for [Kyklos](https://github.com/Kyklos-dev/kyklos): one **Gemini** model (Google AI Studio), a **prompt**, a tiny **JSONL** dataset, and a multi-stage pipeline you can **copy into its own GitHub repository** and run from the Kyklos dashboard.

## Copy this folder to a new GitHub repo

1. **Create an empty repository** on GitHub (no README/license needed, or add them—your choice).

2. **Copy everything** from this directory into your new repo root:

   | Path | Purpose |
   |------|---------|
   | `kyklos.yaml` | Pipeline definition (`repository` URL must be yours—see below) |
   | `prompt.md` | System-style instructions for Gemini |
   | `rubric.md` | Criteria for **`kyklos/llm-judge`** (DeepEval G-Eval + LiteLLM, same Gemini API key) |
   | `data/hello.jsonl` | Two test rows (`input` + `expected_output_contains`) |
   | `requirements.txt` | `google-generativeai` for the Kyklos Python step runtime |
   | `.env.example` | Template for local secrets (optional) |

3. **Edit `kyklos.yaml`**: uncomment the `repository:` block at the top of the file and set your **HTTPS** clone URL and branch:

   ```yaml
   repository:
     url: https://github.com/YOUR_GITHUB_USER/YOUR_REPO_NAME.git
     branch: main
   ```

   If the repo is **private**, add `token_env: GITHUB_TOKEN` under `repository:` and ensure Kyklos has a [GitHub PAT](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) in that variable for cloning.

   You can leave `repository:` commented if you **register this repo only in the Kyklos dashboard** (or `kyklos-server.yaml`) instead—either pattern works.

4. **Commit and push** to GitHub:

   ```bash
   git init
   git add .
   git commit -m "Add Kyklos Gemini minimal demo"
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USER/YOUR_REPO_NAME.git
   git push -u origin main
   ```

## What you need on the Kyklos host

1. **Google AI Studio API key** (free tier with limits): [Get API key](https://aistudio.google.com/apikey)

   ```bash
   export GOOGLE_API_KEY="your-key"
   ```

   The pipeline maps this into step runs via `env:` in `kyklos.yaml`. Start the `kyklos` process with this variable set, or load it from a local `.env` using your process manager.

2. **Python packages** in the same environment Kyklos uses for steps (`python_venv` in `kyklos-server.yaml`):

   ```bash
   pip install -r requirements.txt
   ```

   The **`kyklos/llm-judge`** step uses DeepEval + LiteLLM with **`model: gemini-2.0-flash`** (resolved to `gemini/gemini-2.0-flash`). Install the Kyklos step extras as in the main repo (`deepeval`, `litellm` — see root `Makefile` **`make setup`**) so the judge can run.

3. **Kyklos** with `KYKLOS_STEPS_DIR` pointing at a checkout that contains the official `steps/` tree (see [Getting started](https://github.com/Kyklos-dev/kyklos#getting-started)).

## Pipeline behavior

| Stage | What it does |
|-------|----------------|
| **build** | `kyklos/lint` — validate `agent:` before API calls; `kyklos/snapshot` — hash agent config |
| **test** | `kyklos/run-dataset` — one Gemini call per JSONL row; `kyklos/semantic-similarity` (`method: token`); **`kyklos/llm-judge`** — G-Eval rubric scored by **Gemini** via LiteLLM (`GOOGLE_API_KEY`); `pass_if` on `success_rate`, `avg_similarity`, and `judge.score` |
| **evaluate** | `kyklos/cost-check` / `kyklos/latency-check` — gates on estimated cost and p95 latency |

Semantic similarity uses **`method: token`** (no OpenAI embeddings). The judge uses the **same** `GOOGLE_API_KEY` as the agent—no separate OpenAI key for this demo.

## Run in Kyklos

1. Register your Git repository in Kyklos (or rely on `repository:` in `kyklos.yaml` if your server supports inline clone).
2. Create a pipeline from this **`kyklos.yaml`** (paste YAML or load from branch).
3. Ensure **`GOOGLE_API_KEY`** is set for the Kyklos server process.
4. **Run** the pipeline (pick branch/SHA if prompted).

Workspace roots at your repo clone, so paths like `./data/hello.jsonl` resolve correctly.

## Model

Default model is **`gemini-2.0-flash`** for both the **agent** and **`llm-judge`**. If your key or region rejects it, set `agent.model` and `judge.with.model` to **`gemini-1.5-flash`** in `kyklos.yaml`, commit, and re-run.

## Troubleshooting

| Symptom | What to check |
|---------|----------------|
| `google-generativeai not installed` | `pip install -r requirements.txt` in the step venv |
| `deepeval` / `litellm` missing for judge | `pip install deepeval litellm` (or run main repo `make setup`) |
| Clone / `repository` errors | URL, branch name, PAT for private repos (`token_env`) |
| `dataset not found` | Run uses a workspace whose root is this repo (clone path) |
| Google API 400 | Key, quotas, model name in [AI Studio](https://aistudio.google.com/) |

## License

Same as the parent [Kyklos](https://github.com/Kyklos-dev/kyklos) repository unless you replace this file in your own repo.
