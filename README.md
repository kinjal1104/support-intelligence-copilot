# 🚀 Support Intelligence Copilot

An **AI-native decision support system** for customer support and customer success teams.

---

## 💡 Overview

In B2B SaaS, **churn signals don’t start in dashboards — they start in conversations**.

Customers rarely say “I am going to churn.”  
Instead, they say things like:

- Leadership is concerned  
- Our renewal is next month  
- We’re evaluating alternatives  

These are not just support issues — **they are revenue signals**.

**Support Intelligence Copilot** captures these hidden signals and converts them into actionable decisions.

---

## ⚙️ What the System Does

The system takes:

- 📩 Raw support ticket  
- 🏢 Customer metadata (Account, ARR, Renewal Date, Tier)  

And performs three key steps:

---

### 🔍 1. Risk Signal Detection

Analyzes the ticket to detect:

- Escalation risk  
- Churn intent  
- Urgency  
- Executive dissatisfaction  
- Renewal timing signals  
- Vendor-switching language  
- Revenue impact  

---

### 🎯 2. Next-Best Action Generation

Transforms signals into:

- Priority level  
- Recommended actions  
- Stakeholders to involve (CSM, AE, etc.)  
- Escalation guidance  
- Internal notes  
- Executive-ready response draft  

---

### 📊 3. Interactive Dashboard

- Built using **Streamlit**  
- Paste ticket + input metadata  
- Instantly view:
  - Risk analysis  
  - Suggested actions  
  - Draft response  

---

## 🧠 Architecture

The system is designed using **Prompt-Driven Development (PDD)**,  
where **prompts are the source of truth** and code is generated from them.

---

### 🔧 Dev Units

#### 1. `ticket_risk_analyzer`

**Input:** Ticket + metadata  

**Output:**
- Escalation risk  
- Churn intent  
- Urgency  
- Executive dissatisfaction  
- Renewal timing signal  
- Vendor-switching signal  
- Revenue impact  
- Detected signals  
- Summary  

---

#### 2. `next_best_action_generator`

**Input:** Analyzer output  

**Output:**
- Priority level  
- Next-best actions  
- Stakeholders  
- Escalation recommendation  
- Internal notes  
- Executive-ready reply  

---

#### 3. `support_dashboard`

- UI layer using **Streamlit**  
- Connects analyzer + action generator  
- Enables end-to-end demo workflow  

---

## 🧩 Design Philosophy

- Modular architecture → each unit is independently improvable  
- AI-first system → intelligence lives in prompts, not hardcoded logic  
- Decision support → not just insights, but clear actions  
- Revenue-aware → connects support signals to business impact  

---

## 📚 References

### 🔹 PDD & Prompt Engineering

- Prompt Driven Development (PDD): https://github.com/promptdriven/pdd  
- PDD Prompting Guide: https://github.com/promptdriven/pdd/blob/main/docs/prompting_guide.md  
- PDD Setup with Gemini: https://github.com/promptdriven/pdd/blob/main/SETUP_WITH_GEMINI.md  

---

### 🔹 LLM / AI Concepts

- Google Gemini API Docs: https://ai.google.dev/  
- Prompt Engineering Best Practices (OpenAI & general LLM concepts)  

---

### 🔹 Product / Domain Inspiration

- Zendesk & Intercom (Support intelligence patterns)  
- Churn Prediction & Risk Signals (SaaS industry practices)  

---

## 🧪 Example Insight

> “We’ve had repeated platform issues over the last two weeks, and this is becoming difficult to justify internally. Our renewal is next month, and leadership is asking whether we should continue with your platform if stability doesn’t improve quickly.”

**System detects:**
- High churn intent  
- Executive escalation  
- Renewal risk  

**System recommends:**
- Immediate CSM + AE involvement  
- Priority escalation  
- Executive-level response  

---

## 🔮 Future Scope

- CRM integrations (Salesforce, HubSpot)  
- Real-time ticket ingestion  
- Learning feedback loop from outcomes  
- Multi-ticket account-level risk scoring  

---

## 🏁 Closing

This is not just a support tool.  

It’s a step toward **revenue-aware, AI-driven customer intelligence**.
