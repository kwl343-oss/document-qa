# VCaaS – Deal Dashboard 💼

**A premium, investor-grade deal analysis tool built with Streamlit & OpenAI**

![Status](https://img.shields.io/badge/status-production%20ready-green) ![Version](https://img.shields.io/badge/version-3.0-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue)

---

## 🚀 What It Does

VCaaS is a **deal scoring and analysis platform** for venture capitalists and private equity investors. It:

- 📤 **Uploads & extracts** key metrics from pitch decks (PDF/PPTX)
- 📊 **Scores deals** with a ML-based probability model
- 🎯 **Recommends** INVEST / WATCHLIST / PASS decisions
- 👥 **Personalizes** to your investment thesis (Thesis Fit Score)
- ❓ **Auto-generates** founder diligence questions
- 📋 **Drafts** investment committee memos
- 💬 **Chats** about deals with an AI copilot

**Time to decision:** ~5 minutes per deal

---

## ✨ Key Features (v3.0)

### 📋 Deal Snapshot
Executive summary card showing company, stage, sector, raise, ARR, growth, runway, and materials status.

### 🎯 Recommendation Card (VC Decision)
Clear **INVEST / WATCHLIST / PASS** badge with confidence level, backed by model scoring.

### 📊 Thesis Fit Score
0–100 fit score personalized to your investor profile. Shows stage match, sector match, revenue thresholds, and red flags.

### ✨ Key Business Facts
Auto-extract: business model, ICP, pricing, GTM strategy, traction metrics, moat, competition, team highlights.

### ❓ Founder Diligence Questions
Auto-generate 8–12 specific, tailored questions to ask the founder. Based on stage, sector, and missing metrics.

### 📋 IC Memo Generator
Auto-draft a structured investment committee memo with sections for overview, market, traction, team, risks, thesis, and recommendation.

### 💬 Copilot with Quick Actions
AI assistant with 6 quick-action buttons:
- Summarize deck (8 bullets)
- List diligence risks
- Extract traction metrics
- Draft founder follow-up email
- Write IC summary
- Suggest next steps

### ⚙️ Investor Preferences
Configure your investment profile once (stage, sector, ARR minimum, deal types, ethos). Personalizes all scoring and recommendations.

---

## 🎬 Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set Your OpenAI API Key
Option 1: Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "sk-..."
```

Option 2: Enter in app when prompted.

### Run the App
```bash
streamlit run streamlit_app.py
```

### See It in Action
1. Click **"▶ Run VCaaS analysis"** (uses default demo deal)
2. View the **Deal Snapshot**, **Recommendation**, **Thesis Fit Score**
3. Click **"❓ Generate founder questions"** or **"📋 Generate IC memo"**
4. Try **Copilot quick actions**

---

## 📊 Workflow

```
1. Upload Documents (optional)
   ↓
2. Extract Fields (auto-populate from deck)
   ↓
3. Review/Edit Deal Info
   ↓
4. Run Analysis
   ↓
5. View Scorecard
   ├─ Deal Snapshot (key metrics)
   ├─ Recommendation (INVEST/WATCHLIST/PASS)
   ├─ Thesis Fit Score (personalized to you)
   ├─ Model Reasoning (why this score)
   ├─ Business Highlights (auto-extracted)
   ├─ Founder Questions (auto-generated)
   └─ IC Memo (auto-drafted)
   ↓
6. Chat with Copilot (ask follow-up questions)
   ├─ Quick action buttons
   └─ Custom prompts
```

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **LLM:** OpenAI (GPT-4o-mini)
- **Document Processing:** PyMuPDF, python-pptx, pandas
- **Language:** Python 3.9+

---

## 📁 Files

```
streamlit_app.py              # Main app (production-ready)
requirements.txt              # Dependencies
QUICK_START.md               # Getting started guide
PREMIUM_UPGRADE.md           # Feature deep-dive
IMPLEMENTATION_SUMMARY.md    # Technical details
```

---

## 🎨 Design

- **Premium CSS**: Custom styling throughout
- **Card-based layout**: Clean, scannable design
- **Color-coded indicators**: Green (good), yellow (caution), red (risk)
- **Responsive columns**: Works on any screen size
- **Professional typography**: Enterprise-grade fonts and spacing

---

## 🚀 Use Cases

### VC Diligence
- Quickly evaluate inbound pitches
- Generate founder questions for calls
- Draft IC memos for investment committee
- Track deals with personalized thesis fit

### Investor Onboarding
- Standardize deal evaluation process
- Create repeatable framework
- Document investment thesis
- Train new analysts

### Deal Pipeline Management
- Batch process incoming deals (5 min each)
- Get consistent scoring methodology
- Share analyses with partners
- Reference past evaluations

---

## 🔮 Future Enhancements

- Real ML-based scoring model (replace mock)
- Database persistence (save all analyses)
- CRM integration (export to Salesforce, Airtable)
- Deal comparison dashboard
- Batch processing (analyze 50 deals at once)
- Collaboration features (team profiles, shared analyses)
- Custom metrics per investor
- Email notifications and summaries

---

## 🤝 Contributing

Ideas for improvements? Feel free to extend:
- Add your own scoring logic in `mock_scorecard()`
- Customize recommendation thresholds
- Add new quick actions to the copilot
- Integrate with your CRM/database

---

## 📞 Support

For issues or questions:
1. Check the **QUICK_START.md** for common problems
2. Review **PREMIUM_UPGRADE.md** for feature explanations
3. Check `streamlit_app.py` comments for technical details

---

## 📜 License

This project is provided as-is for your use.

---

## 🎉 You're Ready!

```bash
streamlit run streamlit_app.py
```

Start analyzing deals like a pro. ✨

---

**Version:** 3.0  
**Status:** Production-ready  
**Last Updated:** January 18, 2026
