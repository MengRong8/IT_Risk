# Project Progress — IT Risk GenAI Phishing Detection Lab

## Current status
- MVP completed: synthetic dataset, rule-based detector, OpenRouter LLM detector, and hybrid detector.
- Evaluation outputs are ready as CSV/JSON plus PNG charts for reporting.
- Safety scope: all emails are synthetic; no real credential collection, impersonation, or outbound phishing activity.
- Test command: `PYTHONPATH=. python -m pytest tests -q`.

## Experiment setup
- Dataset: 30 synthetic emails.
  - 10 legitimate normal emails.
  - 10 traditional phishing emails.
  - 10 AI-style phishing emails.
- Detectors compared:
  1. Rule-based keyword/risk signal scoring.
  2. OpenRouter LLM semantic classifier.
  3. Hybrid layered defense: rules first, escalate uncertain cases to LLM.

## Key results
- **rule_based**.
- **openrouter_llm**.
- **hybrid**.

## Main finding
Hybrid detection gave the best trade-off for IT Risk: higher accuracy than rule-based or LLM-only detection, better coverage for AI-style phishing, and lower latency/cost by escalating only uncertain cases to the LLM.

## Important files
- `src/detectors/rule_based.py` — rule-based detector implementation.
- `src/detectors/openrouter_llm.py` — OpenRouter-backed LLM detector.
- `src/detectors/hybrid.py` — hybrid layered detector.
- `src/evaluation.py` — CLI evaluation runner.
- `src/plots.py` — chart generation.
- `results/three_detector_comparison_metrics.json` — summary metrics for all three detectors.
- `results/charts/three_detector_comparison.png` — main comparison chart.
- `report/three_detector_comparison.md` — report-ready analysis.

## How to reproduce
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add OPENROUTER_API_KEY for LLM / hybrid runs
PYTHONPATH=. python -m pytest tests -q
PYTHONPATH=. python -m src.evaluation --detector rule_based
PYTHONPATH=. python -m src.evaluation --detector openrouter --output-csv results/openrouter_email_results.csv --summary-json results/openrouter_summary_metrics.json
PYTHONPATH=. python -m src.evaluation --detector hybrid --output-csv results/hybrid_email_results.csv --summary-json results/hybrid_summary_metrics.json
PYTHONPATH=. python -m src.plots
```

## Next possible extensions
- Tune hybrid thresholds to reduce false negatives for AI-style phishing.
- Add prompt-injection robustness tests for LLM-based detection.
- Convert technical metrics into IT Risk impact estimates such as ALE reduction.
