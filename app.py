import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import plotly.express as px

from src.repo_parser import parse_scanned_files
from src.dynamic_graph_builder import build_dynamic_graph
from src.data_loader import load_entities, load_dependencies, load_test_cases
from src.graph_engine import build_dependency_graph, get_impacted_nodes
from src.risk_engine import calculate_risk_score, summarize_impacts
from src.recommendation_engine import recommend_tests, generate_ai_style_summary, generate_rollback_plan
from src.visualization import create_pyvis_graph


st.set_page_config(
    page_title="ImpactGraph AI",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 ImpactGraph AI")
st.subheader("AI-Powered Impact Analysis & Dependency Intelligence Platform")

st.markdown(
    """
    This POC helps teams understand the blast radius of software changes across applications,
    services, APIs, databases, CI/CD pipelines, business capabilities, teams, and test cases.
    """
)

entities_df = load_entities()
dependencies_df = load_dependencies()
test_cases_df = load_test_cases()
graph = build_dependency_graph(entities_df, dependencies_df)

from src.code_scanner import (
    extract_zip,
    scan_project_files,
    summarize_scan,
    get_file_type_summary
)
with st.sidebar:
    st.header("Change Input")

    entity_types = sorted(entities_df["type"].unique().tolist())
    selected_type = st.selectbox("Target Type", entity_types)

    filtered_entities = entities_df[entities_df["type"] == selected_type].sort_values("name")
    selected_name = st.selectbox("Target Component", filtered_entities["name"].tolist())

    selected_row = filtered_entities[filtered_entities["name"] == selected_name].iloc[0]
    selected_node = selected_row["id"]

    change_type = st.selectbox(
        "Change Type",
        [
            "Minor UI Change",
            "API Contract Change",
            "Database Schema Change",
            "Service Logic Change",
            "Infrastructure Change",
            "Security/Auth Change",
        ],
    )

    max_depth = st.slider("Analysis Depth", min_value=1, max_value=5, value=3)

    run_analysis = st.button("Run Impact Analysis", type="primary")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "Impact Analysis",
        "Dependency Graph",
        "Test Recommendations",
        "Enterprise Data",
        "POC Roadmap",
        "Code Scanner"
    ]
)

if run_analysis:
    impacted = get_impacted_nodes(graph, selected_node, max_depth=max_depth)
    impacted_df = pd.DataFrame(impacted)

    risk_score, risk_band = calculate_risk_score(selected_row.to_dict(), impacted_df, change_type)
    impact_summary = summarize_impacts(impacted_df)

    with tab1:
        st.header("Impact Analysis Report")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Risk Score", f"{risk_score}/100")
        c2.metric("Risk Band", risk_band)
        c3.metric("Impacted Components", len(impacted_df))
        c4.metric("Impacted Teams", impact_summary.get("Teams", 0))

        st.subheader("AI-Style Executive Summary")
        st.info(
            generate_ai_style_summary(
                selected_name,
                selected_type,
                change_type,
                risk_score,
                risk_band,
                impacted_df,
            )
        )

        if not impacted_df.empty:
            st.subheader("Blast Radius by Component Type")
            summary_df = pd.DataFrame(
                [{"Component Type": k, "Count": v} for k, v in impact_summary.items() if k != "Teams"]
            )
            fig = px.bar(summary_df, x="Component Type", y="Count", text="Count")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Impacted Components")
            st.dataframe(
                impacted_df[["name", "type", "owner_team", "criticality", "depth", "relationship_path"]],
                use_container_width=True,
            )

            st.subheader("Teams to Notify")
            team_df = (
                impacted_df.groupby("owner_team")
                .agg(impacted_components=("node_id", "count"), max_criticality=("criticality", "max"))
                .reset_index()
                .sort_values(["max_criticality", "impacted_components"], ascending=False)
            )
            st.dataframe(team_df, use_container_width=True)
        else:
            st.warning("No impacted components found within selected depth.")

        st.subheader("Recommended Rollback Plan")
        for item in generate_rollback_plan(risk_band):
            st.write(f"- {item}")

    with tab2:
        st.header("Interactive Dependency Graph")
        impacted_nodes = impacted_df["node_id"].tolist() if not impacted_df.empty else []
        html_file = create_pyvis_graph(graph, impacted_nodes=impacted_nodes, target_node=selected_node)
        with open(html_file, "r", encoding="utf-8") as f:
            components.html(f.read(), height=700, scrolling=True)

    with tab3:
        st.header("Recommended Test Execution")
        recommended_tests = recommend_tests(impacted_df, test_cases_df, selected_node)
        if recommended_tests.empty:
            st.warning("No mapped test cases found. This is a real enterprise gap: test coverage mapping is incomplete.")
        else:
            st.dataframe(recommended_tests, use_container_width=True)

        st.subheader("Testing Strategy")
        st.markdown(
            """
            - Run P0 contract tests for impacted APIs.
            - Run integration tests for impacted services.
            - Run E2E tests for customer-facing applications.
            - Run data quality checks if databases or ETL pipelines are impacted.
            - Run smoke testing immediately after deployment.
            """
        )

else:
    with tab1:
        st.info("Select a target component from the sidebar and click `Run Impact Analysis`.")

with tab4:
    st.header("Enterprise Dependency Data")

    st.subheader("Entities")
    st.dataframe(entities_df, use_container_width=True)

    st.subheader("Dependencies")
    st.dataframe(dependencies_df, use_container_width=True)

    st.subheader("Mapped Test Cases")
    st.dataframe(test_cases_df, use_container_width=True)

with tab5:
    st.header("POC Roadmap")

    roadmap = pd.DataFrame(
        [
            {
                "Phase": "Phase 1",
                "Scope": "Manual/sample dependency graph, impact analysis, risk scoring, Streamlit dashboard",
                "Status": "Current POC",
            },
            {
                "Phase": "Phase 2",
                "Scope": "Added code upload scanner",
                "Status": "Next",
            },
            {
                "Phase": "Phase 2",
                "Scope": "Repository parser implementation",
                "Status": "Next",
            },
            {
                "Phase": "Phase 2",
                "Scope": "Dynamic dependency graph generation",
                "Status": "Future",
            },
            {
                "Phase": "Phase 3",
                "Scope": "Neo4j integration",
                "Status": "Future",
            },
            {
                "Phase": "Phase 3",
                "Scope": "Impact analysis from real codebase",
                "Status": "Future",
            },
            {
                "Phase": "Phase 3",
                "Scope": "Local LLM recommendations",
                "Status": "Future",
            }
        ]
    )
    st.dataframe(roadmap, use_container_width=True)

    st.subheader("Hard Truth")
    st.warning(
        "Do not start with full enterprise integrations. That will slow you down. "
        "First prove the core value: change input → blast radius → risk score → recommended tests → executive summary."
    )
with tab6:
    st.header("Code Scanner")

    st.markdown(
        """
        Upload a project ZIP file. The scanner will inspect the codebase and identify
        source files, config files, SQL files, APIs, database references, and dependency relationships.
        """
    )

    uploaded_zip = st.file_uploader(
        "Upload project ZIP file",
        type=["zip"]
    )

    if uploaded_zip:
        with st.spinner("Scanning and parsing uploaded project..."):
            extracted_path = extract_zip(uploaded_zip)

            scanned_files_df = scan_project_files(extracted_path)
            scan_summary = summarize_scan(scanned_files_df)
            file_type_summary_df = get_file_type_summary(scanned_files_df)

            parsed_entities_df, parsed_dependencies_df = parse_scanned_files(scanned_files_df)
            dynamic_graph = build_dynamic_graph(parsed_entities_df, parsed_dependencies_df)

        st.success("Project scanned and parsed successfully.")

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Files Scanned", scan_summary["total_files"])
        c2.metric("File Types Found", scan_summary["file_types"])
        c3.metric("Total Size KB", scan_summary["total_size_kb"])

        st.subheader("File Type Summary")
        if not file_type_summary_df.empty:
            st.bar_chart(file_type_summary_df.set_index("file_type"))
            st.dataframe(file_type_summary_df, use_container_width=True)
        else:
            st.warning("No supported files found in the uploaded ZIP.")

        st.subheader("Scanned Files")
        st.dataframe(scanned_files_df, use_container_width=True)

        st.divider()

        st.subheader("Detected Architecture Entities")
        if parsed_entities_df.empty:
            st.warning("No architecture entities detected yet.")
        else:
            st.dataframe(parsed_entities_df, use_container_width=True)

        st.subheader("Detected Dependencies")
        if parsed_dependencies_df.empty:
            st.warning(
                "No dependencies detected yet. This means either the uploaded project has limited detectable patterns "
                "or the parser needs more rules."
            )
        else:
            st.dataframe(parsed_dependencies_df, use_container_width=True)

        st.divider()

        st.subheader("Dynamic Impact Analysis from Uploaded Project")

        if parsed_entities_df.empty:
            st.warning("Cannot run dynamic impact analysis because no entities were detected.")
        else:
            entity_options_df = parsed_entities_df.copy()
            entity_options_df["display_name"] = (
                entity_options_df["name"] + " | " + entity_options_df["type"]
            )

            selected_dynamic_entity = st.selectbox(
                "Select detected component for impact analysis",
                entity_options_df["display_name"].tolist()
            )

            selected_dynamic_row = entity_options_df[
                entity_options_df["display_name"] == selected_dynamic_entity
            ].iloc[0]

            selected_dynamic_node = selected_dynamic_row["id"]

            dynamic_impacted = get_impacted_nodes(
                dynamic_graph,
                selected_dynamic_node,
                max_depth=3
            )

            dynamic_impacted_df = pd.DataFrame(dynamic_impacted)

            if dynamic_impacted_df.empty:
                st.warning(
                    "No downstream impact found for this component yet. "
                    "This is expected in early parser versions."
                )
            else:
                dynamic_score, dynamic_band = calculate_risk_score(
                    selected_dynamic_row.to_dict(),
                    dynamic_impacted_df,
                    "Service Logic Change"
                )

                d1, d2, d3 = st.columns(3)
                d1.metric("Dynamic Risk Score", f"{dynamic_score}/100")
                d2.metric("Risk Band", dynamic_band)
                d3.metric("Impacted Components", len(dynamic_impacted_df))

                st.subheader("Impacted Components")
                st.dataframe(dynamic_impacted_df, use_container_width=True)

                st.subheader("Dynamic Impact Summary")

                impacted_names = dynamic_impacted_df["name"].head(5).tolist()
                impacted_text = ", ".join(impacted_names)

                st.info(
                    f"The selected component '{selected_dynamic_row['name']}' may impact "
                    f"{len(dynamic_impacted_df)} detected components. "
                    f"Top impacted components: {impacted_text}. "
                    f"Risk level is {dynamic_band} with score {dynamic_score}/100."
                )