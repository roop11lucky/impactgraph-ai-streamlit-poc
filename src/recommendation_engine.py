def recommend_tests(impacted_df, test_cases_df, target_node):
    impacted_nodes = set(impacted_df["node_id"].tolist()) if not impacted_df.empty else set()
    impacted_nodes.add(target_node)

    recommended = test_cases_df[test_cases_df["mapped_entity"].isin(impacted_nodes)].copy()

    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    if not recommended.empty:
        recommended["priority_sort"] = recommended["priority"].map(priority_order).fillna(9)
        recommended = recommended.sort_values(["priority_sort", "test_type"]).drop(columns=["priority_sort"])

    return recommended

def generate_ai_style_summary(target_name, target_type, change_type, risk_score, risk_band, impacted_df):
    if impacted_df.empty:
        return (
            f"The proposed {change_type} on {target_type} '{target_name}' has limited visible impact. "
            "However, this result depends on the completeness of the dependency map. Run code scan and runtime trace validation before production release."
        )

    apps = impacted_df[impacted_df["type"] == "Application"]["name"].tolist()
    services = impacted_df[impacted_df["type"] == "Service"]["name"].tolist()
    databases = impacted_df[impacted_df["type"] == "Database"]["name"].tolist()
    teams = impacted_df["owner_team"].dropna().unique().tolist()

    return (
        f"The proposed {change_type} on {target_type} '{target_name}' has a {risk_band.lower()} risk score of {risk_score}/100. "
        f"The blast radius includes {len(impacted_df)} impacted components across {len(teams)} teams. "
        f"Key impacted applications: {', '.join(apps[:3]) if apps else 'None detected'}. "
        f"Key impacted services: {', '.join(services[:3]) if services else 'None detected'}. "
        f"Database impact: {', '.join(databases[:3]) if databases else 'None detected'}. "
        "Recommended action: execute P0 regression, contract tests, integration tests, and validate rollback readiness before release."
    )

def generate_rollback_plan(risk_band):
    if risk_band in ["Critical", "High"]:
        return [
            "Create database backup or rollback migration before deployment.",
            "Deploy behind feature flag where possible.",
            "Prepare previous stable service/container image.",
            "Notify impacted service owners before release.",
            "Run smoke test immediately after deployment.",
            "Keep release window with active engineering support."
        ]

    return [
        "Prepare previous stable build.",
        "Run smoke test after deployment.",
        "Monitor logs and service health metrics for 30 minutes."
    ]