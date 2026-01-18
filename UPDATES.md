# VCaaS Dashboard – v2.0 Updates 🚀

## New Features & Improvements

### 1. 🎨 **Enhanced UI/UX**
- **Gradient Title**: Eye-catching animated title with gradient text effect
- **Custom Styling**: Modern metric cards with border accents and shadows
- **Color-coded Indicators**: Risk drivers, positive drivers, and flags use intuitive colors (green for positive, yellow for caution, red for risks)
- **Visual Hierarchy**: Clear section headers and improved spacing throughout
- **Responsive Design**: Better mobile and desktop experience

### 2. 🧠 **Model Explainability & Reasoning**
- **Expanded "Model Reasoning" Section**: Click to expand and see exactly how the score was calculated
- **Step-by-step Adjustments**: See each factor that affected the probability score:
  - Stage-based adjustments
  - Growth rate impacts
  - Runway risk factors
  - ARR-based confidence boosts
  - **Investor preference matches** (if configured)
- **Confidence Context**: Clear explanation of what confidence % means for each deal

### 3. 👤 **Investor Preferences & Onboarding (Optional)**

#### Getting Started
- New **"Configure Preferences"** button in the sidebar (appears on first visit)
- Completely optional – the dashboard works without it
- Preferences are stored in your session and personalize all scoring and recommendations

#### What You Can Configure
- **Your Name/Fund Name**: Personalize the dashboard
- **Primary Investment Stage**: Pre-Seed, Seed, Series A, Series B+ (or Any)
- **Fund Type**: VC, Angel, Micro VC, Corporate VC, PE
- **Preferred Sector(s)**: Free text (e.g., "B2B SaaS, AI, Climate Tech")
- **Minimum ARR**: Set a revenue threshold for deal screening
- **Deal Types**: Multi-select from product-led growth, sales-led, marketplace, infrastructure, consumer, deep tech, enterprise
- **Detail Preference**: Choose between concise summaries, balanced, or deep dives
- **Investment Ethos**: Your values, red flags, what you look for in founders/teams

#### How Preferences Impact the Dashboard
1. **Scoring Adjustment**: Model gives +5% boost for deals matching your preferred stage or sector, +3% for meeting revenue thresholds
2. **Copilot Context**: The AI assistant now understands your investment thesis and can recommend deals that fit YOUR profile
3. **Profile View**: Easily see and edit your saved preferences from the sidebar

### 4. 💬 **Enhanced Copilot**
- **Investor-Aware**: Copilot now references your investment ethos and preferences when analyzing deals
- **Richer Context**: Assistant receives full reasoning from the model, not just scores
- **Smarter Recommendations**: Suggests deals that match your conviction and thesis
- **Better Explanations**: More specific guidance on whether a deal fits your profile

---

## How to Use the New Features

### First Time Setup (2 minutes)
1. Open the app
2. Click "→ Configure Preferences" in the sidebar
3. Fill in your investor profile (all optional, but recommended)
4. Click "💾 Save Preferences"
5. Your preferences are now active for all future deals!

### Viewing Your Profile
- Click the expander in the sidebar labeled "View / Edit Profile" to see your saved preferences
- Use "Edit Preferences" to make changes
- Use "Clear Preferences" to reset and start fresh

### Using Model Reasoning
1. Run a deal analysis (right column)
2. Look for the "🧠 Model Reasoning" section
3. Click "💭 Show me the model's thinking" to expand
4. See step-by-step how the score was calculated

### Asking the Copilot Smart Questions
- "Does this deal fit my investment thesis?"
- "What should I dig deeper on for this B2B SaaS company?"
- "How does this compare to my usual stage/sector focus?"
- "What are the team risk factors?"

---

## Technical Details

### Session State Management
- Preferences are stored in `st.session_state.investor_prefs`
- Persists for the duration of your session
- Resets when page refreshes (future: could add database persistence)

### Scoring Algorithm Updates
The `mock_scorecard()` function now:
- Accepts optional `investor_prefs` parameter
- Generates detailed `reasoning` list for explainability
- Returns structured scoring rationale

### Model Reasoning Factors
1. **Stage Risk**: Early-stage penalties, later-stage boosts
2. **Growth Performance**: High growth (+8%) vs. average
3. **Runway Health**: Short runway penalty, healthy runway
4. **ARR Traction**: Revenue milestone indicators
5. **Investor Alignment**: Preference matching (optional)

---

## What's Next?

Future enhancements could include:
- 💾 Database persistence for investor profiles (across sessions)
- 📈 Deal comparison dashboard (side-by-side scoring)
- 📊 Custom metrics based on investor preferences
- 🤖 More sophisticated ML-based scoring
- 📧 Email summaries and alerts
- 🔗 CRM integration for deal pipeline tracking

---

## Screenshots & Tips

### Tip 1: The Onboarding Flow
- Not intrusive – appears only if you don't have preferences set
- Takes 1-2 minutes to complete
- Can skip entirely and come back later

### Tip 2: Leverage the Reasoning Expander
- Great for training others on your deal eval process
- Share the reasoning with LPs or investment committee
- Helps document your diligence methodology

### Tip 3: Copilot as Your Sparring Partner
- Ask challenging questions: "What am I missing here?"
- Get perspective: "How risky is this really?"
- Validate thesis: "Is this the market I think it is?"

---

## Questions or Feedback?

The dashboard is a prototype. If you find bugs or have feature requests, please reach out!
