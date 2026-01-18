# VCaaS Premium v3.0 – Quick Reference Card

## 🎯 What You Have

A premium, investor-grade deal analysis dashboard with:
- Deal snapshot & metrics
- INVEST/WATCHLIST/PASS recommendations
- Personalized thesis fit scoring
- Auto-generated founder questions
- Auto-drafted IC memos
- AI copilot with quick actions

## 🚀 Start It

```bash
streamlit run streamlit_app.py
```

Then click **"▶ Run VCaaS analysis"** to see it in action.

---

## 📋 NEW FEATURES (9 Total)

| # | Feature | Button/Click | Result |
|---|---------|--------------|--------|
| 1 | Deal Snapshot | See at top of scorecard | Executive summary card with all key metrics |
| 2 | Recommendation | Auto-generates | Clear INVEST/WATCHLIST/PASS badge |
| 3 | Thesis Fit Score | Auto-generates (if profile set) | 0–100 fit score matching YOUR preferences |
| 4 | Business Facts | "✨ Extract key facts" | Auto-extracts business model, pricing, GTM, etc. |
| 5 | Model Reasoning | "💭 Show thinking" | Step-by-step scoring breakdown |
| 6 | Founder Questions | "❓ Generate questions" | 8–12 specific diligence questions |
| 7 | IC Memo | "📋 Generate memo" | Full investment committee memo |
| 8 | Quick Actions | 6 buttons above chat | Summarize, risks, traction, follow-up, IC summary, next steps |
| 9 | Visual Polish | Throughout app | Premium CSS, cards, color-coding, responsive layout |

---

## ⚙️ Setup (Optional but Recommended)

```
Sidebar → "⚙️ Investor Profile" → Configure Preferences
├─ Your name
├─ Preferred stage (Seed, Series A, etc.)
├─ Preferred sector (SaaS, AI, Climate, etc.)
├─ Minimum ARR
├─ Deal types you focus on
└─ Investment ethos / hard passes
```

Once set, all analyses show personalized **Thesis Fit Score**.

---

## 📊 Workflow (5 minutes per deal)

```
1. Upload deck (PDF/PPTX)
       ↓
2. Click "🤖 Extract fields" (auto-populates deal info)
       ↓
3. Click "▶ Run VCaaS analysis"
       ↓
4. See Scorecard:
   ├─ Deal Snapshot (all metrics)
   ├─ Recommendation (INVEST/WATCHLIST/PASS)
   ├─ Thesis Fit Score (if profile set)
   ├─ Model Reasoning (why this score)
   └─ Risk/Driver cards
       ↓
5. Generate Artifacts (optional):
   ├─ "✨ Extract key facts" → Business highlights
   ├─ "❓ Founder questions" → 12 questions to ask
   └─ "📋 IC memo" → Full memo for committee
       ↓
6. Chat with Copilot:
   ├─ Quick action buttons (summarize, risks, etc.)
   └─ Or ask custom questions
```

---

## 🎨 Key Visual Elements

### Deal Snapshot
```
Company Name
┌─────────┬─────────┬─────────┬─────────┐
│ Stage   │ Sector  │ Raise   │ ARR     │
│ Seed    │ SaaS    │ $3.0M   │ $800K   │
├─────────┼─────────┼─────────┼─────────┤
│ Growth  │ Runway  │ Docs    │ Materials
│ 18%     │ 10 mo   │ 234K    │ ✓       │
```

### Recommendation
```
═════════════════════════════════════════
  ✅ INVEST          (green badge)
  🟡 WATCHLIST       (yellow badge)
  ❌ PASS            (red badge)
  
  Confidence: High/Medium/Low
  Model Signal: XX%
```

### Thesis Fit
```
  Fit Score: 85/100
  
  ✅ Stage match
  ✅ Sector match
  ✅ Revenue threshold
```

---

## 💬 Copilot Quick Actions

Click any button to auto-fill prompt:

| Button | Generates |
|--------|-----------|
| 📋 Summarize deck | 8-bullet deck summary |
| ⚠️ List risks | Top 5-8 diligence risks |
| 📈 Traction metrics | All growth metrics extracted |
| 📧 Founder follow-up | Professional follow-up email |
| 📊 IC Summary | 3-paragraph IC summary |
| 🔍 Next steps | Specific next steps + timeline |

---

## 🎯 Key Sections in Scorecard

### 1. Deal Snapshot
All metrics at a glance.

### 2. Recommendation Card
Clear INVEST/WATCHLIST/PASS decision.

### 3. Thesis Fit Score (if profile set)
0–100 fit score + matching indicators.

### 4. Conviction Slider
Adjust final score by gut feel (-1 to +1).

### 5. Model Reasoning
Step-by-step breakdown of scoring.

### 6. Key Business Facts (optional)
Auto-extracted business model, GTM, traction, etc.

### 7. Positive Drivers
Green pills showing what's good.

### 8. Risk Drivers
Yellow cards showing what's concerning.

### 9. Missing Info / Flags
Red cards showing critical gaps.

---

## 🔧 Customization

### Change Default Deal Values
Edit in `streamlit_app.py`:
```python
company = st.text_input("Company name", value="Acme AI", key="company")
sector = st.text_input("Sector", value="B2B SaaS", key="sector")
raise_amount = st.number_input("Raise amount ($)", ..., value=3000000, ...)
```

### Change Recommendation Thresholds
Edit `generate_recommendation()`:
```python
if combined_signal >= 0.70:
    rec = "INVEST"
elif combined_signal >= 0.50:
    rec = "WATCHLIST"
else:
    rec = "PASS"
```

### Add Custom Quick Actions
Edit the quick actions section:
```python
quick_actions = [
    ("📋 Summarize deck", "Your custom prompt here..."),
    ("⚠️ List risks", "Your custom prompt here..."),
    # Add more...
]
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **QUICK_START.md** | 5-min getting started + pro tips |
| **PREMIUM_UPGRADE.md** | Feature-by-feature explanation |
| **IMPLEMENTATION_SUMMARY.md** | Technical architecture |
| **README_UPDATED.md** | Product overview |
| **DELIVERY_SUMMARY.md** | What was delivered |

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Add your OpenAI API key" | Set in `.streamlit/secrets.toml` or enter in app |
| Extraction failed | Try different PDF or add manual notes |
| Copilot is slow | Normal (5-10 sec for API call) |
| Can't see Thesis Fit | Configure investor profile in sidebar first |
| Want to skip documents | Just fill in fields manually + click Run |

---

## ✨ Pro Tips

1. **Configure profile first** (2 min) → Unlocks personalization
2. **Use quick buttons** → Faster than typing prompts
3. **Extract + IC memo** → 5-min deal processing
4. **Founder questions** → Print and use in actual calls
5. **Model reasoning** → Share with your IC team

---

## 🎬 Demo Mode

Just click "▶ Run VCaaS analysis" with defaults to see everything in action:
- Deal Snapshot ✓
- Recommendation ✓
- Model Reasoning ✓
- Generator buttons ✓
- Copilot ✓

---

## 📞 Need Help?

1. **First time?** → Read `QUICK_START.md`
2. **What does X feature do?** → Read `PREMIUM_UPGRADE.md`
3. **How do I customize?** → Read `IMPLEMENTATION_SUMMARY.md`
4. **What was delivered?** → Read `DELIVERY_SUMMARY.md`

---

**Version:** 3.0 Premium  
**Status:** Production Ready ✅  
**Last Updated:** January 18, 2026

Happy deal analyzing! 🚀
