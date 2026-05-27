# Detector Comparison — Rule-based vs OpenRouter LLM

## Summary

- Rule-based overall accuracy: 76.67%
- OpenRouter LLM overall accuracy: 86.67%
- Rule-based AI-style phishing detection: 30.00%
- OpenRouter LLM AI-style phishing detection: 60.00%
- Rule-based average latency: 0.10 ms/email
- OpenRouter average latency: 4482.12 ms/email

## Interpretation

The OpenRouter LLM detector improved AI-style phishing detection from 30% to 60%, while keeping normal email and traditional phishing accuracy at 100% in this controlled dataset. This supports the project hypothesis that semantic analysis can catch more AI-written phishing emails than simple keyword/rule matching.

However, OpenRouter latency is much higher because each email requires a remote model call. In a real enterprise setting, this suggests a layered design: use cheap rule-based filtering first, then send uncertain or high-impact cases to an LLM detector.

## Misclassified AI-style phishing samples by OpenRouter

- `AI-PHISH-001` — predicted `uncertain`, score 50: Updated reimbursement workflow for this week
- `AI-PHISH-004` — predicted `uncertain`, score 50: 報銷流程小幅調整確認
- `AI-PHISH-007` — predicted `uncertain`, score 50: 主管請你協助確認一份發票
- `AI-PHISH-009` — predicted `uncertain`, score 50: Small update to payment contact details
