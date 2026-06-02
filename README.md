# ImpactGraph AI - Streamlit POC

AI-Powered Impact Analysis & Dependency Intelligence Platform.

This is a working Streamlit Proof of Concept designed for client demos, GitHub portfolio, resume discussion, and technical interviews.

## What this POC does

- Maintains a sample enterprise dependency graph
- Lets users select a change target such as API, service, database, pipeline, or business capability
- Calculates direct and indirect impact
- Calculates a risk score
- Shows affected applications, services, databases, APIs, teams, test cases, and pipelines
- Generates AI-style impact summaries and recommended test/rollback actions
- Visualizes the dependency graph interactively

## Tech Stack

- Streamlit
- Python
- NetworkX
- PyVis
- Pandas
- Plotly

## Why no paid services in MVP?

This POC intentionally avoids paid cloud and paid LLM APIs. The first demo should prove the logic and business value for free. Later versions can add:

- Neo4j Aura Free
- OpenAI / Gemini / Claude
- GitHub repository scanning
- Jira integration
- Slack / Teams notifications
- CI/CD integration

## Local Setup

```bash
git clone <your-repo-url>
cd impactgraph_ai_poc

python -m venv venv
source venv/bin/activate   # Mac/Linux
# OR
venv\Scripts\activate    # Windows

pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud Deployment

1. Push this project to GitHub
2. Go to Streamlit Community Cloud
3. Connect your GitHub repository
4. Set main file path as:
   ```
   app.py
   ```
5. Deploy

## Demo Flow

1. Open the app
2. Go to `Run Impact Analysis`
3. Select target type: API / Service / Database / Pipeline
4. Select target name
5. Click `Run Impact Analysis`
6. Review:
   - Business risk score
   - Impacted systems
   - Dependency graph
   - Recommended test cases
   - AI-style executive summary

## Recommended GitHub Repository Name

```text
impactgraph-ai-streamlit-poc
```

## Resume Line

Built an AI-powered impact analysis POC using Streamlit, Python, NetworkX, and graph-based dependency modeling to identify software change blast radius, impacted systems, risk score, test recommendations, and rollback strategy.

## LinkedIn Post Hook

Most production failures are not caused by bad developers. They are caused by invisible dependencies.

I built ImpactGraph AI, a Streamlit-based POC that analyzes change impact across services, APIs, databases, teams, test cases, and deployment pipelines using dependency graph intelligence.