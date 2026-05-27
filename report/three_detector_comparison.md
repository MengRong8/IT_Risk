# Three Detector Comparison

## Summary

- Rule-based overall accuracy: 76.67%
- OpenRouter LLM overall accuracy: 86.67%
- Hybrid overall accuracy: 90.00%

- Rule-based AI-style phishing detection: 30.00%
- OpenRouter LLM AI-style phishing detection: 60.00%
- Hybrid AI-style phishing detection: 70.00%

- Rule-based avg latency: 0.10 ms/email
- OpenRouter avg latency: 4482.12 ms/email
- Hybrid avg latency: 669.21 ms/email

## Hybrid escalation counts

- llm_escalation: 6
- rule_based_confident: 24

## Hybrid LLM-escalated emails

- `AI-PHISH-001` — ai_phishing, predicted `uncertain`, score 45: Updated reimbursement workflow for this week
- `AI-PHISH-003` — ai_phishing, predicted `phishing`, score 85: Follow-up on shared drive permissions
- `AI-PHISH-005` — ai_phishing, predicted `phishing`, score 85: Gentle reminder: HR profile review
- `AI-PHISH-006` — ai_phishing, predicted `phishing`, score 85: Class platform migration check
- `AI-PHISH-008` — ai_phishing, predicted `phishing`, score 85: Account access cleanup before Friday
- `AI-PHISH-009` — ai_phishing, predicted `uncertain`, score 50: Small update to payment contact details

## Hybrid misclassified emails

- `AI-PHISH-001` — ai_phishing, predicted `uncertain`, expected `phishing`, score 45: Updated reimbursement workflow for this week
- `AI-PHISH-002` — ai_phishing, predicted `legitimate`, expected `phishing`, score 0: Quick check on your course portal access
- `AI-PHISH-009` — ai_phishing, predicted `uncertain`, expected `phishing`, score 50: Small update to payment contact details
