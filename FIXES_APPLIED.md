# VCaaS App - Fixes Applied

## What Was Fixed

### 1. ✅ Investor Preferences Dashboard Restored
- **Added sidebar** with investor profile section
- **Edit button** to toggle preferences form
- **Profile fields**: Name, Stage, Sector, Min ARR, Investment ethos
- **Persistent storage** in session state
- **Preferences integrated** into deal scoring (thesis fit calculations)

### 2. ✅ "Apply to Form" Now Works
**Problem**: Clicking "Apply to form" only updated the header, not the actual form fields
**Solution**: 
- Changed form widget keys to avoid conflicts (`form_company`, `form_stage`, etc.)
- Updated session state values immediately after widget creation
- Form fields now properly display extracted data after clicking apply

### 3. ✅ Form Field Value Persistence
- Form fields now sync with session state properly
- Extracted data applies to all fields (company, stage, sector, raise, ARR, growth, runway, notes)
- Values persist across tabs and interactions

### 4. ✅ Sidebar API Key Management
- Added text input for OpenAI API key in sidebar
- API key can be sourced from:
  1. Environment secrets (`OPENAI_API_KEY`)
  2. Sidebar input (fallback)
- Extraction and AI features require API key

### 5. ✅ Layout Improvements
- Sidebar expanded by default for easy access to investor profile
- Progress indicator shows status at top
- Form fields properly sized (no micro inputs)
- Two-column layout for better space usage

## How to Use

### First Time Setup
1. **Open the app** → Sidebar is visible on the left
2. **Click "✏️"** in the "Investor Profile" section
3. **Fill your investor preferences** (optional but recommended)
4. **Click "💾 Save"**

### Analyzing a Deal
1. **Intake Tab**:
   - Upload pitch deck, additional docs, financials
   - Click "🔍 Extract Fields from Docs"
   - View extraction preview (shows JSON)
   - Click "✨ Apply to form" → Fields populate automatically
   - Review/edit any fields as needed
   - Click "▶ Run Analysis"

2. **Analysis Tab**:
   - See recommendation (INVEST/WATCHLIST/PASS)
   - View key metrics and drivers
   - Generate "Founder Questions" and "IC Memo"

3. **Copilot Tab**:
   - Ask contextual questions about the deal
   - Use quick action buttons for common analyses

## Key Features Preserved
- ✅ Document upload (PDF, PPTX, CSV, Excel, TXT)
- ✅ LLM-based field extraction
- ✅ Deal scoring with investor preferences
- ✅ Thesis fit calculation
- ✅ Recommendation generation (INVEST/WATCHLIST/PASS)
- ✅ Founder diligence questions
- ✅ IC memo generation
- ✅ Copilot chat
- ✅ Apple design system
- ✅ Zero excessive scrolling

## Session State Variables
- `investor_prefs` - Investor profile/preferences dict
- `show_prefs_onboard` - Toggle preferences edit form
- `company`, `stage`, `sector`, `raise_amount_usd`, `arr_usd`, `growth_rate_pct`, `runway_months`, `notes` - Deal fields
- `extracted` - Extracted JSON from documents
- `docs_text` - Combined document text
- `last_deal` - Current deal dict
- `last_result` - Scoring results
- `founder_questions` - Generated questions
- `ic_memo` - Generated memo
- `messages` - Copilot chat history
- `sidebar_api_key` - OpenAI API key from sidebar input

## Testing Checklist
- [ ] Upload a PDF/PPTX → See extraction working
- [ ] Click "✨ Apply to form" → All fields populate
- [ ] Edit investor profile → Preferences save
- [ ] Run analysis → Gets personalized scoring
- [ ] Generate founder questions → Text appears
- [ ] Chat with copilot → Responses are contextual
