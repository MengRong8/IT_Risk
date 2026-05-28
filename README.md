# GenAI Security Lab — AI Phishing Email Detection

Controlled classroom experiment for comparing phishing email detectors.

## MVP

- 30 synthetic emails
  - 10 legitimate normal emails
  - 10 traditional phishing emails
  - 10 AI-style phishing emails
- Rule-based detector
- OpenRouter LLM detector
- Hybrid detector: rule-based first, LLM escalation for uncertain cases
- CSV evaluation output

## Environment setup

Copy or edit `.env` and put your OpenRouter key there:

```bash
cd /home/ubuntu/genai-security-lab
nano .env
```

The file should contain:

```bash
export OPENROUTER_API_KEY="YOUR_KEY_HERE"
export OPENROUTER_MODEL="openai/gpt-4o-mini"
```

Then either source it manually:

```bash
source .env
```

or just run `src.evaluation`, which auto-loads `.env` from the project directory.

## Run rule-based baseline

```bash
PYTHONPATH=. python -m src.evaluation --detector rule_based
PYTHONPATH=. python -m src.plots
```

Outputs:

- `results/email_results.csv`
- `results/summary_metrics.json`
- `results/charts/detection_rate_by_category.png`

## Run OpenRouter LLM detector

```bash
PYTHONPATH=. python -m src.evaluation \
  --detector openrouter \
  --output-csv results/openrouter_email_results.csv \
  --summary-json results/openrouter_summary_metrics.json
```

## Run Hybrid detector

```bash
PYTHONPATH=. python -m src.evaluation \
  --detector hybrid \
  --output-csv results/hybrid_email_results.csv \
  --summary-json results/hybrid_summary_metrics.json
```

Hybrid logic:

- If rule-based says `phishing` or `legitimate`, accept it directly.
- If rule-based says `uncertain`, escalate to OpenRouter LLM.
- CSV field `decision_source` shows whether a row used `rule_based_confident` or `llm_escalation`.



## Prompt Injection Lab

This repo includes prompt-injection experiments as part of the full dashboard service stack.
Use the dashboard when you want to demo how different guard modes react to the same adversarial prompt.

- `rule_based`: cheap lexical blacklist, useful for showing bypasses
- `llm`: OpenRouter semantic guard for prompt-injection detection
- `hybrid`: rule-based first, LLM escalation for uncertain prompts


## Cybersecurity Dashboard
The dashboard stack has three services:

- `detector_api`: exposes phishing experiment metrics and on-demand email analysis.
- `web_chatbot`: vulnerable chatbot plus prompt-injection guards for the adversarial demo.
- `dashboard_frontend`: unified dashboard with two tabs, one for email phishing evaluation and one for prompt-injection testing.

### First-time Docker setup

Build and start all services:

```bash
docker compose up --build
```

Default host ports are:

- `8080` -> `dashboard_frontend`
- `8000` -> `detector_api`
- `5000` -> `web_chatbot`

- `http://127.0.0.1:8080` for the dashboard frontend
- `http://127.0.0.1:8000/health` for the detector API
- `http://127.0.0.1:5000/health` for the chatbot service


## Tests

```bash
PYTHONPATH=. python -m pytest tests -q
```

## Safety

This lab uses synthetic emails only. It does not send emails, collect credentials, impersonate real systems, or target real users.
