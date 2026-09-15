# db.py
import pandas as pd
import os
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime

INPUT_EXCEL_PATH = "Talent360i_Input_Dataset.xlsx"
OUTPUT_EXCEL_PATH = "Talent360i_Output.xlsx"


def _ensure_output_workbook():
    """Create the writable workbook as a copy of the untouched input workbook."""
    if not os.path.exists(INPUT_EXCEL_PATH):
        raise FileNotFoundError(f"{INPUT_EXCEL_PATH} not found.")
    if not os.path.exists(OUTPUT_EXCEL_PATH):
        shutil.copy2(INPUT_EXCEL_PATH, OUTPUT_EXCEL_PATH)


def _read_clean_sheet(path, sheet_name):
    """Read a workbook tab whose first rows contain a title and metadata."""
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None, engine="openpyxl")
    header_index = next(
        (index for index, row in raw.iterrows() if row.notna().sum() >= 2),
        0,
    )
    headers = raw.iloc[header_index].tolist()
    frame = raw.iloc[header_index + 1:].copy()
    frame.columns = headers
    return frame.dropna(how="all").dropna(axis=1, how="all").reset_index(drop=True)


def load_input_sheet(sheet_name: str) -> pd.DataFrame:
    """Load a clean, read-only reference tab from the input workbook."""
    return _read_clean_sheet(INPUT_EXCEL_PATH, sheet_name)


def load_output_sheet(sheet_name: str) -> pd.DataFrame:
    """Load a clean tab from the writable output workbook."""
    _ensure_output_workbook()
    return _read_clean_sheet(OUTPUT_EXCEL_PATH, sheet_name)


def load_optional_output_sheet(sheet_name: str, columns=None) -> pd.DataFrame:
    """Load an output tab, returning an empty frame when it has not been created."""
    try:
        return load_output_sheet(sheet_name)
    except ValueError:
        return pd.DataFrame(columns=columns or [])


def save_output_sheet(sheet_name: str, df: pd.DataFrame):
    """Replace one tab in the output workbook while preserving all other tabs."""
    _ensure_output_workbook()
    output_dir = os.path.dirname(os.path.abspath(OUTPUT_EXCEL_PATH))
    temporary_path = tempfile.mktemp(
        prefix="Talent360i_Output_",
        suffix=".xlsx",
        dir=output_dir,
    )
    try:
        shutil.copy2(OUTPUT_EXCEL_PATH, temporary_path)
        with pd.ExcelWriter(
            temporary_path,
            mode="a",
            if_sheet_exists="replace",
            engine="openpyxl",
        ) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        os.replace(temporary_path, OUTPUT_EXCEL_PATH)
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)


def append_output_row(sheet_name: str, row: dict):
    """Append one application-created record to an output tab."""
    try:
        frame = load_output_sheet(sheet_name)
    except ValueError:
        frame = pd.DataFrame(columns=list(row))
    frame = pd.concat([frame, pd.DataFrame([row])], ignore_index=True)
    save_output_sheet(sheet_name, frame)

# Legacy helpers remain available until the page migration is complete.
EXCEL_PATH = OUTPUT_EXCEL_PATH

def load_sheet(sheet_name: str) -> pd.DataFrame:
    """Load a sheet from Excel into a DataFrame using openpyxl engine."""
    _ensure_output_workbook()
    return pd.read_excel(EXCEL_PATH, sheet_name=sheet_name, engine="openpyxl")

def save_sheet(sheet_name: str, df: pd.DataFrame):
    """Save a DataFrame back to Excel (overwrite sheet) using openpyxl engine."""
    _ensure_output_workbook()
    with pd.ExcelWriter(EXCEL_PATH, mode="a", if_sheet_exists="replace", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

@contextmanager
def transaction(sheet_name: str):
    """
    Context manager for atomic Excel operations.
    Loads the sheet, yields the DataFrame for modification,
    then saves it back automatically.
    """
    df = load_sheet(sheet_name)
    yield df
    save_sheet(sheet_name, df)

def write_audit(entity_type, entity_id, action, actor, details=""):
    """Append an audit log entry to Excel."""
    log_df = load_sheet("audit_log")
    new_row = {
        "id": len(log_df) + 1,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "action": action,
        "actor": actor,
        "details": details,
        "created_at": datetime.now().isoformat()
    }
    log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)
    save_sheet("audit_log", log_df)
