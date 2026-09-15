# validate.py
import os, glob, py_compile
import pandas as pd

print("🔍 Validating Talent360i Project...")

# 1. Compile all Python files
for file in glob.glob("*.py") + glob.glob("pages/*.py"):
    try:
        py_compile.compile(file, doraise=True)
        print(f"✅ Compiled: {file}")
    except Exception as e:
        print(f"❌ Error in {file}: {e}")

# 2. Check Excel schema
excel_path = "Talent360i_Auto_Assessment_Hackfest_Dataset_v2.xlsx"
sheets = ["questions", "assessments", "audit_log"]
try:
    xl = pd.ExcelFile(excel_path)
    for sheet in sheets:
        if sheet in xl.sheet_names:
            print(f"✅ Found sheet: {sheet}")
        else:
            print(f"❌ Missing sheet: {sheet}")
except Exception as e:
    print(f"❌ Excel error: {e}")

print("Validation complete.")
