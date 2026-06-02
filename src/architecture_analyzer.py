import re
from pathlib import Path
import pandas as pd


def read_file_safely(file_path):
    try:
        return Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def detect_application_files(scanned_files_df):
    app_indicators = [
        "app.py",
        "main.py",
        "manage.py",
        "server.py",
        "application.java",
        "main.java",
        "program.cs",
        "startup.cs",
        "package.json",
        "docker-compose.yml",
    ]

    results = []

    for _, row in scanned_files_df.iterrows():
        file_name = str(row["file_name"]).lower()

        if file_name in app_indicators:
            results.append({
                "component_type": "Application",
                "component_name": row["file_name"],
                "source_file": row["relative_path"],
                "confidence": "High"
            })

    return results


def detect_python_services(content, relative_path):
    results = []

    class_matches = re.findall(r"class\s+([A-Z][A-Za-z0-9_]*(Service|Manager|Controller|Repository))", content)

    for match in class_matches:
        class_name = match[0]
        results.append({
            "component_type": "Service",
            "component_name": class_name,
            "source_file": relative_path,
            "confidence": "Medium"
        })

    return results


def detect_java_services(content, relative_path):
    results = []

    if any(annotation in content for annotation in ["@Service", "@Component", "@Repository", "@RestController", "@Controller"]):
        class_matches = re.findall(r"(?:public\s+)?class\s+([A-Z][A-Za-z0-9_]*)", content)

        for class_name in class_matches:
            component_type = "Service"

            if "@RestController" in content or "@Controller" in content:
                component_type = "Controller"
            elif "@Repository" in content:
                component_type = "Repository"

            results.append({
                "component_type": component_type,
                "component_name": class_name,
                "source_file": relative_path,
                "confidence": "High"
            })

    return results


def detect_python_apis(content, relative_path):
    results = []

    patterns = [
        r"@app\.route\(['\"](.+?)['\"]",
        r"@router\.(get|post|put|delete|patch)\(['\"](.+?)['\"]",
        r"@(get|post|put|delete|patch)\(['\"](.+?)['\"]",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content)

        for match in matches:
            if isinstance(match, tuple):
                route = match[-1]
                method = match[0].upper() if match[0] in ["get", "post", "put", "delete", "patch"] else "ROUTE"
            else:
                route = match
                method = "ROUTE"

            results.append({
                "component_type": "API",
                "component_name": f"{method} {route}",
                "source_file": relative_path,
                "confidence": "High"
            })

    return results


def detect_java_apis(content, relative_path):
    results = []

    patterns = [
        (r"@GetMapping\(['\"](.+?)['\"]\)", "GET"),
        (r"@PostMapping\(['\"](.+?)['\"]\)", "POST"),
        (r"@PutMapping\(['\"](.+?)['\"]\)", "PUT"),
        (r"@DeleteMapping\(['\"](.+?)['\"]\)", "DELETE"),
        (r"@PatchMapping\(['\"](.+?)['\"]\)", "PATCH"),
        (r"@RequestMapping\(['\"](.+?)['\"]\)", "REQUEST"),
    ]

    for pattern, method in patterns:
        matches = re.findall(pattern, content)

        for route in matches:
            results.append({
                "component_type": "API",
                "component_name": f"{method} {route}",
                "source_file": relative_path,
                "confidence": "High"
            })

    return results


def detect_sql_tables(content, relative_path):
    results = []

    patterns = [
        r"CREATE\s+TABLE\s+([a-zA-Z0-9_\.]+)",
        r"FROM\s+([a-zA-Z0-9_\.]+)",
        r"JOIN\s+([a-zA-Z0-9_\.]+)",
        r"UPDATE\s+([a-zA-Z0-9_\.]+)",
        r"INSERT\s+INTO\s+([a-zA-Z0-9_\.]+)",
    ]

    tables = []

    for pattern in patterns:
        tables.extend(re.findall(pattern, content, flags=re.IGNORECASE))

    for table in set(tables):
        results.append({
            "component_type": "Database Table",
            "component_name": table,
            "source_file": relative_path,
            "confidence": "Medium"
        })

    return results


def detect_config_files(row):
    config_extensions = [".yml", ".yaml", ".json", ".properties", ".env", ".xml"]

    file_name = str(row["file_name"]).lower()
    extension = str(row["extension"]).lower()

    if extension not in config_extensions:
        return []

    config_type = "Configuration"

    if "docker" in file_name:
        config_type = "Docker Configuration"
    elif "kubernetes" in file_name or "deployment" in file_name or "service" in file_name:
        config_type = "Kubernetes Configuration"
    elif "application" in file_name:
        config_type = "Application Configuration"
    elif "package.json" in file_name:
        config_type = "Node Package Configuration"

    return [{
        "component_type": config_type,
        "component_name": row["file_name"],
        "source_file": row["relative_path"],
        "confidence": "High"
    }]


def analyze_architecture(scanned_files_df):
    """
    Converts scanned files into architecture-level components:
    Applications, Services, Controllers, APIs, Database Tables, and Configurations.
    """

    if scanned_files_df.empty:
        return pd.DataFrame(columns=[
            "component_type",
            "component_name",
            "source_file",
            "confidence"
        ])

    discovered_components = []

    discovered_components.extend(detect_application_files(scanned_files_df))

    for _, row in scanned_files_df.iterrows():
        content = read_file_safely(row["file_path"])
        extension = str(row["extension"]).lower()
        relative_path = row["relative_path"]

        discovered_components.extend(detect_config_files(row))

        if extension == ".py":
            discovered_components.extend(detect_python_services(content, relative_path))
            discovered_components.extend(detect_python_apis(content, relative_path))

        elif extension == ".java":
            discovered_components.extend(detect_java_services(content, relative_path))
            discovered_components.extend(detect_java_apis(content, relative_path))

        elif extension == ".sql":
            discovered_components.extend(detect_sql_tables(content, relative_path))

    architecture_df = pd.DataFrame(discovered_components)

    if architecture_df.empty:
        return pd.DataFrame(columns=[
            "component_type",
            "component_name",
            "source_file",
            "confidence"
        ])

    architecture_df = architecture_df.drop_duplicates(
        subset=["component_type", "component_name", "source_file"]
    )

    return architecture_df.sort_values(
        by=["component_type", "component_name"]
    ).reset_index(drop=True)


def summarize_architecture(architecture_df):
    """
    Returns count of architecture components by type.
    """

    if architecture_df.empty:
        return pd.DataFrame(columns=["component_type", "count"])

    return (
        architecture_df.groupby("component_type")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )


def calculate_architecture_health_score(architecture_df, parsed_dependencies_df):
    """
    Simple rule-based architecture health score.
    This is not perfect. It is intentionally basic for POC.
    """

    if architecture_df.empty:
        return 0, "No architecture components detected"

    component_count = len(architecture_df)
    dependency_count = len(parsed_dependencies_df) if parsed_dependencies_df is not None else 0

    score = 50

    if component_count >= 5:
        score += 15

    if dependency_count >= 5:
        score += 15

    if "API" in architecture_df["component_type"].values:
        score += 10

    if "Database Table" in architecture_df["component_type"].values:
        score += 10

    score = min(score, 100)

    if score >= 80:
        label = "Good"
    elif score >= 60:
        label = "Moderate"
    else:
        label = "Weak"

    return score, label