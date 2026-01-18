# VCaaS Premium Dashboard – Quick Start Guide

## 🚀 Getting Started (2 minutes)

### 1. Run the App
```bash
streamlit run streamlit_app.py
```

### 2. See the New Features (No Setup Required)
The app comes with **default deal values** so you can immediately:
- See the **Deal Snapshot** (executive summary card)
- Get an **Investment Recommendation** (INVEST/WATCHLIST/PASS)
- View **Model Reasoning** (step-by-step scoring)
- Click **"❓ Generate founder questions"** (auto-generates 12 questions)
- Click **"📋 Generate IC memo"** (drafts full memo)
- Try **Copilot quick action buttons** (summarize, list risks, etc.)

Just click **"▶ Run VCaaS analysis"** on the right and explore!

---

## ⚙️ Personalize It (Optional, 2 minutes)

### Configure Your Investor Profile
1. Click **"⚙️ Investor Profile"** in left sidebar
2. Click **"→ Configure Preferences"**
3. Enter:
   - Your name / fund name
   - Preferred stage (Pre-Seed, Seed, Series A, Series B+)
   - Fund type (VC, Angel, Micro VC, etc.)
   - Preferred sector (e.g., "B2B SaaS, AI")
   - Minimum ARR threshold
   - Deal types you focus on
   - Investment ethos / red flags
4. Click **"💾 Save Preferences"**

Now every deal you analyze will show:
- **Thesis Fit Score** (how well it matches YOUR profile)
- **Stage/Sector/Revenue matching indicators**
- Personalized **Recommendation** (combining model + your preferences)

---

## 📊 Use the Full Workflow

### Full Workflow (5-10 minutes per deal)

1. **Upload Documents**
   - Drag pitch deck (PDF or PPTX)
   - Optional: financials, extra docs, meeting notes
   - Click **"🤖 Extract fields"** to auto-populate

2. **Review Deal Info**
   - Company, stage, sector, ARR, growth, runway
   - Edit anything manually if extraction missed it

3. **Run Analysis**
   - Click **"▶ Run VCaaS analysis"**

4. **Review Scorecard** (30 seconds)
   - **Deal Snapshot**: All key metrics at a glance
   - **Recommendation**: INVEST? WATCHLIST? PASS?
   - **Thesis Fit Score**: How well does it match you?
   - **Model Reasoning**: Why did it score this way?

5. **Generate Artifacts** (Optional, 30 seconds each)
   - Click **"✨ Extract key facts"** → Business model, GTM, traction
   - Click **"❓ Founder questions"** → 12 diligence questions
   - Click **"📋 IC memo"** → Full memo for investment committee

6. **Ask Your Copilot**
   - Use quick action buttons: Summarize, List risks, Traction metrics, etc.
   - Or ask custom questions about the deal

---

## 🎯 Key Features Explained

### Deal Snapshot
Everything you need to know about the deal in one card:
- Company name, stage, sector, raise amount, ARR, growth rate, runway
- Materials status (docs loaded, financials uploaded)

### Recommendation (VC Decision Style)
```
Recommendation: WATCHLIST
Confidence: Medium
Model signal: 71%
```
- **INVEST** (green): High combined signal + great fit
- **WATCHLIST** (yellow): Promising but needs more diligence
- **PASS** (red): Doesn't meet your bar

### Thesis Fit Score
If you've configured your profile:
- Score 0–100 showing how well the deal matches YOUR investment thesis
- Shows stage match, sector match, revenue threshold
- Lists any red flags (e.g., "Very short runway")

### Key Extracted Facts
Click **"✨ Extract key facts"** to auto-generate:
- Business model
- ICP / target customer
- Pricing
- GTM strategy
- Traction metrics
- Moat
- Competition
- Team highlights

### Founder Diligence Questions
Click **"❓ Generate founder questions"** to get 8–12 specific questions like:
- "What's your unit economics (CAC, LTV, payback)?"
- "How does your retention compare to benchmarks?"
- "Who are your top 3 competitors and why do you win?"

### IC Memo
Click **"📋 Generate IC memo"** to get a structured memo:
- Overview, Market, Traction, Team, Risks, Investment Thesis, Recommendation
- 80% done; customize as needed

### Copilot Quick Actions
6 buttons to instantly chat about:
- 📋 Summarize deck (8 bullets)
- ⚠️ List diligence risks (top 5-8)
- 📈 Extract traction metrics
- 📧 Draft founder follow-up email
- 📊 Write IC summary (3 paragraphs)
- 🔍 Suggest next steps

---

## 💡 Pro Tips

### Tip 1: Configure Your Profile First
The Thesis Fit Score is much more useful once you've set your preferences. Spend 2 minutes on this upfront.

### Tip 2: Use Quick Action Buttons
They're faster than typing. Try **"📋 Summarize deck"** first—it's a great way to vet if a deal is even worth deeper diligence.

### Tip 3: Extract + IC Memo for Speed
- Upload deck → Extract fields → Run analysis → Click IC memo
- Takes 5 minutes, generates a full memo
- Perfect for batch processing deals

### Tip 4: Founder Questions Are Your Checklist
Print or export the founder questions. Use them in your next call with the founder. Shows them you've done diligence.

### Tip 5: Model Reasoning is Shareable
The step-by-step reasoning in the "🧠 Model Reasoning" section is great to share with your investment committee: "Here's why we like/dislike this deal."

---

## 🔧 Customizing the Dashboard

### Want to Change Default Values?
Edit the form defaults in `streamlit_app.py`:
```python
company = st.text_input("Company name", value="Acme AI", key="company")  # Change "Acme AI"
sector = st.text_input("Sector", value="B2B SaaS", key="sector")  # Change "B2B SaaS"
```

### Want to Add Your Logo?
Add to the header:
```python
col1, col2 = st.columns([0.2, 0.8])
with col1:
    st.image("path/to/logo.png", width=80)
with col2:
    st.markdown("<h1 class='main-title'>💼 VCaaS – Deal Dashboard</h1>", unsafe_allow_html=True)
```

### Want Different Recommendation Thresholds?
Edit `generate_recommendation()` function:
```python
def generate_recommendation(prob: float, thesis_fit: dict, investor_prefs: dict) -> dict:
    combined_signal = prob * 0.6 + (thesis_fit["score"] / 100) * 0.4 if thesis_fit else prob
    
    if combined_signal >= 0.70:  # ← Change these thresholds
        rec = "INVEST"
```

---

## 📞 Troubleshooting

### "Add your OpenAI API key to continue"
You need to set your OpenAI API key. Either:
1. Create `.streamlit/secrets.toml`:
   ```
   OPENAI_API_KEY = "sk-..."
   ```
2. Or enter it in the app when prompted

### "Extraction failed"
The documents might be images or scanned PDFs. Try:
- Using a text-based PDF
- Adding manual notes with key metrics
- Manually entering the fields

### "Chart/memo generation is slow"
The app is calling GPT-4o-mini. This takes 5-10 seconds depending on document length. This is normal.

### "I want to skip documents and just analyze the fields"
No problem! Just leave the document upload blank and fill in the deal fields manually. Click "▶ Run VCaaS analysis". Everything works without documents.

---

## 🎓 Example: Full Deal Analysis in 5 Minutes

**Scenario:** You just got a cold outreach for an AI startup. Quick diligence check.

1. **Load app**: `streamlit run streamlit_app.py` (30 seconds)
2. **Upload deck**: Drag PDF into left column (10 seconds)
3. **Extract**: Click "🤖 Extract fields" (30 seconds)
4. **Review**: Read extracted fields, edit if needed (1 minute)
5. **Analyze**: Click "▶ Run VCaaS analysis" (10 seconds)
6. **Quick scan**: 
   - Look at Deal Snapshot (5 seconds)
   - Check Recommendation card (5 seconds)
   - Read Model Reasoning (30 seconds)
7. **Quick questions**: Click "❓ Generate founder questions" (10 seconds)
8. **Decision**: Based on Recommendation + questions, decide next steps (1 minute)

**Total: ~5 minutes to go from cold email to "pass" or "let's dig deeper"**

---

## 🚀 You're Ready!

That's it. Fire it up and start analyzing deals like a pro.

```bash
streamlit run streamlit_app.py
```

Enjoy! 🎉
