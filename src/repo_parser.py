import re
import pandas as pd
from pathlib import Path


def read_file_safely(file_path):
    try:
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def detect_python_imports(content):
    imports = []

    patterns = [
        r"^import\s+([a-zA-Z0-9_\.]+)",
        r"^from\s+([a-zA-Z0-9_\.]+)\s+import",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content, flags=re.MULTILINE)
        imports.extend(matches)

    return list(set(imports))


def detect_api_routes(content):
    routes = []

    patterns = [
        r"@app\.route\(['\"](.+?)['\"]",
        r"@router\.(get|post|put|delete|patch)\(['\"](.+?)['\"]",
        r"@(get|post|put|delete|patch)\(['\"](.+?)['\"]",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                routes.append(match[-1])
            else:
                routes.append(match)

    return list(set(routes))


def detect_sql_references(content):
    tables = []

    patterns = [
        r"FROM\s+([a-zA-Z0-9_\.]+)",
        r"JOIN\s+([a-zA-Z0-9_\.]+)",
        r"INTO\s+([a-zA-Z0-9_\.]+)",
        r"UPDATE\s+([a-zA-Z0-9_\.]+)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content, flags=re.IGNORECASE)
        tables.extend(matches)

    return list(set(tables))


def parse_scanned_files(scanned_files_df):
    entities = []
    dependencies = []

    if scanned_files_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    for _, row in scanned_files_df.iterrows():
        file_id = row["relative_path"]
        file_name = row["file_name"]
        file_type = row["file_type"]
        file_path = row["file_path"]

        entities.append({
            "id": file_id,
            "name": file_name,
            "type": "File",
            "criticality": 2,
            "owner_team": "Unknown"
        })

        content = read_file_safely(file_path)

        if row["extension"] == ".py":
            imports = detect_python_imports(content)

            for imp in imports:
                import_id = f"import::{imp}"

                entities.append({
                    "id": import_id,
                    "name": imp,
                    "type": "Python Dependency",
                    "criticality": 2,
                    "owner_team": "Unknown"
                })

                dependencies.append({
                    "source": file_id,
                    "target": import_id,
                    "relationship": "IMPORTS"
                })

            routes = detect_api_routes(content)

            for route in routes:
                route_id = f"api::{route}"

                entities.append({
                    "id": route_id,
                    "name": route,
                    "type": "API",
                    "criticality": 4,
                    "owner_team": "Unknown"
                })

                dependencies.append({
                    "source": file_id,
                    "target": route_id,
                    "relationship": "EXPOSES_API"
                })

        if row["extension"] == ".sql":
            tables = detect_sql_references(content)

            for table in tables:
                table_id = f"db::{table}"

                entities.append({
                    "id": table_id,
                    "name": table,
                    "type": "Database Table",
                    "criticality": 4,
                    "owner_team": "Unknown"
                })

                dependencies.append({
                    "source": file_id,
                    "target": table_id,
                    "relationship": "REFERENCES_TABLE"
                })

    entities_df = pd.DataFrame(entities).drop_duplicates(subset=["id"])
    dependencies_df = pd.DataFrame(dependencies).drop_duplicates()

    return entities_df, dependencies_df