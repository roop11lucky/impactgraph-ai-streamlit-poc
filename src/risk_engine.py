import pandas as pd

CHANGE_COMPLEXITY = {
    "Minor UI Change": 10,
    "API Contract Change": 30,
    "Database Schema Change": 35,
    "Service Logic Change": 25,
    "Infrastructure Change": 30,
    "Security/Auth Change": 40,
}

def calculate_risk_score(target_entity, impacted_df, change_type):
    if impacted_df.empty:
        return 10, "Low"

    impacted_count = len(impacted_df)
    avg_criticality = impacted_df["criticality"].mean()
    max_depth = impacted_df["depth"].max()
    complexity = CHANGE_COMPLEXITY.get(change_type, 20)

    raw_score = (
        impacted_count * 4
        + avg_criticality * 10
        + max_depth * 5
        + complexity
        + int(target_entity.get("criticality", 3)) * 5
    )

    score = min(100, int(raw_score))

    if score >= 75:
        band = "Critical"
    elif score >= 55:
        band = "High"
    elif score >= 35:
        band = "Medium"
    else:
        band = "Low"

    return score, band

def summarize_impacts(impacted_df):
    if impacted_df.empty:
        return {}

    return {
        "Applications": int((impacted_df["type"] == "Application").sum()),
        "Services": int((impacted_df["type"] == "Service").sum()),
        "APIs": int((impacted_df["type"] == "API").sum()),
        "Databases": int((impacted_df["type"] == "Database").sum()),
        "Pipelines": int((impacted_df["type"] == "Pipeline").sum()),
        "Business Capabilities": int((impacted_df["type"] == "Business Capability").sum()),
        "Teams": int(impacted_df["owner_team"].nunique()),
    }