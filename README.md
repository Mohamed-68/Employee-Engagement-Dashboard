# Employee Engagement Dashboard (Excel + PowerPoint)

A portfolio project that transforms a Microsoft Forms Employee Engagement Survey export into a clean, reusable Excel dashboard and a board-ready PowerPoint summary.

## What’s included

### ✅ Excel Dashboard (`excel/Engagement_Dashboard.xlsx`)
- Automated analysis built from a Microsoft Forms-style export
- KPIs (Responses, Avg eNPS 0–10, Avg Score 1–5, Favorable %)
- Charts:
  - Average score by question (1–5)
  - Favorable % by question
  - Department heatmap (question × department)
  - Comment themes summary (optional if filled)
- Slicers (interactive filtering):
  - Department, Location, Tenure, Manager
- Tabs structured for reusability:
  - `ReadMe`, `Dashboard`, `Text_Insights`, `Pivots`, `Data_Model`, `Data_Raw`, `Lookup_Tables`

### ✅ PowerPoint Deck (`ppt/Employee_Engagement_Survey_Deck.pptx`)
- Board-ready slide layout
- Key charts and summary slides (editable)
- Built directly from the Excel dashboard visuals

### ✅ Data generator + sample data
- Script to generate realistic fake survey data:
  - `scripts/generate_fake_survey.py`
- Sample outputs:
  - `data/employee_engagement_forms_export.xlsx`
  - `data/employee_engagement_raw.csv`

> Note: All data in this repository is synthetic (fake) for portfolio/demo purposes.

---

## Data structure (Microsoft Forms-style export)

The raw export is a “wide” table:
- 1 row per respondent
- Demographics (Department, Location, Tenure, Manager)
- eNPS score (0–10)
- Likert questions stored as text (Agree/Neutral/etc.)
- Open-text comments

The dashboard converts this into a “long” model for easy analysis:
- 1 row per respondent per question
- Adds `Likert_Score` (1–5) and `Favorable` (0/1)

---

## How to use the Excel dashboard (client workflow)

1) **Paste new export**
- Open your new survey export
- Copy the full table including headers
- Paste into **`Data_Raw`** starting at cell **A1**
- Keep the same column headers (important)

2) **Refresh**
- Excel: **Data → Refresh All**
- This updates `Data_Model`, pivots, and the dashboard charts

3) **Filter**
- Go to **Dashboard**
- Use slicers (Department / Location / Tenure / Manager)

---

## Qualitative comments (Text Insights)

The `Text_Insights` tab is used to review open-text comments.
You can tag comments using a Theme dropdown (e.g., Workload, Leadership, Communication) and summarize the top themes via a pivot/chart.

---

## Run the fake data generator (optional)

### Requirements
- Python 3.10+ recommended

### Install dependencies
```bash
pip install pandas numpy openpyxl
