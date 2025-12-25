from __future__ import annotations

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# ----------------------------
# Config you can tweak
# ----------------------------
SEED = 42
N_RESPONSES = 180  # realistic for a mid-size org
START_DATE = datetime(2025, 11, 3, 9, 0, 0)

DEPARTMENTS = [
    "Engineering",
    "Sales",
    "Customer Support",
    "Operations",
    "Finance",
    "HR / People",
]

DEPT_WEIGHTS = {
    "Engineering": 0.26,
    "Sales": 0.18,
    "Customer Support": 0.20,
    "Operations": 0.16,
    "Finance": 0.10,
    "HR / People": 0.10,
}

LOCATIONS = ["Paris", "Lyon", "Remote"]
LOCATION_WEIGHTS = [0.55, 0.20, 0.25]

TENURE_BANDS = ["0-1y", "1-3y", "3-5y", "5y+"]
TENURE_WEIGHTS = [0.22, 0.36, 0.24, 0.18]

# Likert options like Forms exports
LIKERT_TEXT = {
    1: "Strongly disagree",
    2: "Disagree",
    3: "Neutral",
    4: "Agree",
    5: "Strongly agree",
}

QUESTIONS = [
    ("Q01_Strategy", "I understand the company strategy and priorities"),
    ("Q02_Leadership_Comms", "Leadership communicates openly and honestly"),
    ("Q03_Manager_Support", "My manager supports my development"),
    ("Q04_Feedback", "I receive useful feedback regularly"),
    ("Q05_Workload", "My workload is manageable"),
    ("Q06_Tools", "I have the tools/resources to do my job well"),
    ("Q07_Recognition", "I feel recognized for good work"),
    ("Q08_Collaboration", "Teams collaborate effectively"),
    ("Q09_PsychSafety", "I feel safe to share concerns"),
    ("Q10_CareerPath", "I see a clear career path here"),
    ("Q11_Stay12Months", "I would still work here in 12 months"),
    ("Q12_OverallEngagement", "Overall, I feel engaged at work"),
]

# Base "health" by question (1–5). We'll add dept biases on top.
BASE_MEAN_BY_Q = {
    "Q01_Strategy": 3.4,
    "Q02_Leadership_Comms": 3.1,
    "Q03_Manager_Support": 3.5,
    "Q04_Feedback": 3.2,
    "Q05_Workload": 2.9,      # common pain point
    "Q06_Tools": 3.8,         # often strong in modern orgs
    "Q07_Recognition": 3.1,
    "Q08_Collaboration": 3.7,
    "Q09_PsychSafety": 3.6,
    "Q10_CareerPath": 2.8,    # common pain point
    "Q11_Stay12Months": 3.4,
    "Q12_OverallEngagement": 3.3,
}

# Dept adjustments (adds/subtracts to means)
DEPT_ADJ = {
    "Engineering": {"Q06_Tools": +0.3, "Q02_Leadership_Comms": -0.1, "Q10_CareerPath": -0.1},
    "Sales": {"Q07_Recognition": +0.1, "Q01_Strategy": +0.1, "Q05_Workload": -0.1},
    "Customer Support": {"Q05_Workload": -0.4, "Q07_Recognition": -0.2, "Q06_Tools": -0.1},
    "Operations": {"Q06_Tools": -0.2, "Q02_Leadership_Comms": -0.1, "Q05_Workload": -0.2},
    "Finance": {"Q01_Strategy": +0.1, "Q08_Collaboration": -0.1},
    "HR / People": {"Q09_PsychSafety": +0.2, "Q02_Leadership_Comms": +0.1, "Q05_Workload": -0.1},
}

# Comment templates (short, board-safe)
WORKING_WELL_TEMPLATES = [
    "Team collaboration is strong and people are helpful.",
    "Good culture and supportive colleagues.",
    "Tools and systems mostly work well for my role.",
    "Manager is approachable and supportive.",
    "Autonomy and trust make it easier to get work done.",
    "Cross-team collaboration has improved recently.",
]

IMPROVE_FIRST_TEMPLATES = [
    "More clarity on priorities and decisions from leadership.",
    "Reduce workload and improve staffing/planning.",
    "Clearer career paths and development opportunities.",
    "More recognition for strong performance.",
    "Improve communication between teams.",
    "Faster decisions and less last-minute changes.",
]

# ----------------------------
# Helpers
# ----------------------------
def weighted_choice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]

def likert_from_mean(mean: float) -> int:
    """
    Convert a mean (1..5) into a sampled Likert score.
    We sample from a normal distribution and clamp to 1..5.
    """
    score = np.random.normal(loc=mean, scale=0.85)
    score = int(np.clip(np.rint(score), 1, 5))
    return score

def generate_enps_from_engagement(overall_eng_score: float, dept: str) -> int:
    """
    Generate eNPS 0-10 with a relationship to engagement.
    """
    # base mapping: 3.0 -> ~5, 4.0 -> ~8, 2.5 -> ~3
    base = (overall_eng_score - 1) * 2.5  # roughly 0..10-ish
    # dept vibes
    dept_shift = {
        "Engineering": +0.3,
        "Sales": +0.2,
        "Customer Support": -0.6,
        "Operations": -0.3,
        "Finance": 0.0,
        "HR / People": +0.2,
    }.get(dept, 0.0)

    raw = np.random.normal(loc=base + dept_shift + 4.0, scale=1.9)  # center around mid-high
    return int(np.clip(np.rint(raw), 0, 10))

def generate_timestamp(i: int) -> str:
    # stagger submissions over a couple hours
    t = START_DATE + timedelta(minutes=int(np.random.exponential(scale=4.5) * i / 8))
    return t.strftime("%Y-%m-%d %H:%M")

# ----------------------------
# Main
# ----------------------------
def main():
    random.seed(SEED)
    np.random.seed(SEED)

    rows = []
    dept_items = list(DEPT_WEIGHTS.keys())
    dept_w = [DEPT_WEIGHTS[d] for d in dept_items]

    for i in range(1, N_RESPONSES + 1):
        respondent_id = f"R{str(i).zfill(4)}"
        dept = weighted_choice(dept_items, dept_w)
        location = weighted_choice(LOCATIONS, LOCATION_WEIGHTS)
        tenure = weighted_choice(TENURE_BANDS, TENURE_WEIGHTS)
        manager = weighted_choice(["Yes", "No"], [0.12, 0.88])

        # Likert answers
        answers_num = {}
        for q_code, _ in QUESTIONS:
            mean = BASE_MEAN_BY_Q[q_code] + DEPT_ADJ.get(dept, {}).get(q_code, 0.0)

            # small realism: newer employees slightly less positive on strategy/career
            if tenure == "0-1y" and q_code in ("Q01_Strategy", "Q10_CareerPath"):
                mean -= 0.2

            # managers slightly more positive on strategy/leadership
            if manager == "Yes" and q_code in ("Q01_Strategy", "Q02_Leadership_Comms"):
                mean += 0.2

            answers_num[q_code] = likert_from_mean(mean)

        overall_eng = answers_num["Q12_OverallEngagement"]
        enps = generate_enps_from_engagement(overall_eng, dept)

        row = {
            "RespondentID": respondent_id,
            "SubmissionTime": generate_timestamp(i),
            "Department": dept,
            "Location": location,
            "Tenure": tenure,
            "Manager": manager,
            "eNPS_0_10": enps,
        }

        # store Likert as TEXT (like Forms)
        for q_code, _ in QUESTIONS:
            row[q_code] = LIKERT_TEXT[answers_num[q_code]]

        # comments (not everyone writes comments)
        if random.random() < 0.78:
            row["Open_WhatsWorking"] = random.choice(WORKING_WELL_TEMPLATES)
        else:
            row["Open_WhatsWorking"] = ""

        if random.random() < 0.70:
            # slightly bias support/ops to workload comments
            if dept in ("Customer Support", "Operations") and random.random() < 0.55:
                row["Open_ImproveFirst"] = "Reduce workload and improve staffing/planning."
            else:
                row["Open_ImproveFirst"] = random.choice(IMPROVE_FIRST_TEMPLATES)
        else:
            row["Open_ImproveFirst"] = ""

        rows.append(row)

    df = pd.DataFrame(rows)

    # Save as CSV + XLSX that mimics a "Forms export"
    out_csv = "data/employee_engagement_raw.csv"
    out_xlsx = "data/employee_engagement_forms_export.xlsx"

    df.to_csv(out_csv, index=False)

    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Data_Raw", index=False)

    print(f"Created:\n- {out_csv}\n- {out_xlsx}\nRows: {len(df)}  Cols: {len(df.columns)}")

if __name__ == "__main__":
    main()
