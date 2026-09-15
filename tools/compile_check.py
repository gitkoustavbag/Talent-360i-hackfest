import py_compile, glob

files = glob.glob('*.py') + glob.glob('pages/*.py')
files = [f for f in files if not f.endswith('validate.py')]
failed = False
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        print(f"✅ Compiled: {f}")
    except Exception as e:
        failed = True
        print(f"❌ Error in {f}: {e}")
if not failed:
    print('All files compiled successfully.')
else:
    print('Some files had compile errors.')
