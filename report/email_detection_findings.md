# AI 釣魚信件偵測實驗初步結果

## Experiment setup

- Dataset: 30 synthetic emails
  - 10 normal legitimate emails
  - 10 traditional phishing emails
  - 10 AI-style phishing emails
- Detector: rule-based detector
- Output files:
  - `results/email_results.csv`
  - `results/summary_metrics.json`
  - `results/charts/detection_rate_by_category.png`

## Initial results

- Overall accuracy: 76.67%
- Normal email accuracy: 100%
- Traditional phishing detection rate: 100%
- AI-style phishing detection rate: 30%

## Interpretation for IT Risk report

The controlled experiment shows that a simple rule-based detector can identify obvious traditional phishing emails with high accuracy, especially when the email contains clear signals such as urgent language, password verification requests, suspicious URLs, payment requests, or impersonation of IT/HR/finance teams.

However, the same detector performs much worse against AI-style phishing emails. These messages often use natural tone, soft requests, and fewer obvious suspicious keywords. In this MVP dataset, the rule-based detector only correctly flagged 30% of AI-style phishing samples as phishing.

This supports the project argument:

> Generative AI can reduce the visible signals that traditional phishing filters rely on. Organizations should combine rule-based detection with semantic analysis, user education, and layered controls.

## Recommended next experiment

Add an OpenRouter-based LLM detector and compare:

1. Rule-based detector
2. OpenRouter LLM detector
3. Hybrid detector

Expected value:

- LLM detector may improve AI-style phishing detection by reasoning over intent and context.
- Hybrid detector can preserve explainability while improving coverage.

## Safety boundary

This experiment uses only synthetic, controlled lab emails. It does not send emails, collect credentials, impersonate real systems, or target real users.
