import os
import glob

os.chdir('/root/geminicli/flash-monitor-kyiv')

tests = glob.glob("tests/*.py")

for fpath in tests:
    with open(fpath, "r") as f:
        content = f.read()

    # Fix test_app.py patches
    content = content.replace("patch('app.", "patch('app.main.")
    
    # Fix patching other modules
    for mod in ["light_service", "generate_daily_report", "generate_text_report", "generate_weekly_report", "storage", "models", "telegram_client", "parser_service"]:
        content = content.replace(f"patch('{mod}.", f"patch('app.{mod}.")
        content = content.replace(f'patch("{mod}.', f'patch("app.{mod}.')
        content = content.replace(f"from {mod} import", f"from app.{mod} import")
        content = content.replace(f"import {mod}", f"import app.{mod}")
    
    # Also fix scripts.bootstrap for test_app.py
    content = content.replace("patch('bootstrap.", "patch('scripts.bootstrap.")

    with open(fpath, "w") as f:
        f.write(content)
