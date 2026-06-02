from pathlib import Path
import zipfile
import tempfile
import pandas as pd


SUPPORTED_EXTENSIONS = {
    ".py": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".json": "JSON",
    ".sql": "SQL",
    ".xml": "XML",
    ".properties": "Properties",
    ".env": "Environment",
    ".md": "Markdown",
}


IGNORE_DIRS = {
    "__pycache__",
    ".git",
    "venv",
    "env",
    "node_modules",
    ".idea",
    ".vscode",
    "target",
    "build",
    "dist",
}


def extract_zip(uploaded_zip):
    """
    Extract uploaded ZIP file into a temporary directory.
    Returns extracted folder path.
    """
    temp_dir = tempfile.mkdtemp()

    zip_path = Path(temp_dir) / "uploaded_project.zip"

    with open(zip_path, "wb") as f:
        f.write(uploaded_zip.getbuffer())

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    return Path(temp_dir)


def should_ignore(path: Path) -> bool:
    """
    Ignore unnecessary folders/files.
    """
    return any(part in IGNORE_DIRS for part in path.parts)


def scan_project_files(project_path):
    """
    Scan extracted project folder and return supported files.
    """
    project_path = Path(project_path)
    scanned_files = []

    for file_path in project_path.rglob("*"):
        if not file_path.is_file():
            continue

        if should_ignore(file_path):
            continue

        extension = file_path.suffix.lower()

        if extension in SUPPORTED_EXTENSIONS:
            try:
                file_size_kb = round(file_path.stat().st_size / 1024, 2)
            except Exception:
                file_size_kb = 0

            scanned_files.append(
                {
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "relative_path": str(file_path.relative_to(project_path)),
                    "extension": extension,
                    "file_type": SUPPORTED_EXTENSIONS[extension],
                    "size_kb": file_size_kb,
                }
            )

    return pd.DataFrame(scanned_files)


def summarize_scan(files_df):
    """
    Generate high-level scan summary.
    """
    if files_df.empty:
        return {
            "total_files": 0,
            "file_types": 0,
            "total_size_kb": 0,
        }

    return {
        "total_files": len(files_df),
        "file_types": files_df["file_type"].nunique(),
        "total_size_kb": round(files_df["size_kb"].sum(), 2),
    }


def get_file_type_summary(files_df):
    """
    Count files by type.
    """
    if files_df.empty:
        return pd.DataFrame(columns=["file_type", "count"])

    return (
        files_df.groupby("file_type")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )