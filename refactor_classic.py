import os
import subprocess
import glob
import re

os.chdir('/root/geminicli/flash-monitor-kyiv')

def run_cmd(cmd):
    subprocess.run(cmd, shell=True, check=True)

# 1. Create directories
run_cmd("mkdir -p app scripts docs docs/assets")

# 2. Move Python files
app_files = [
    ("app.py", "app/main.py"),
    ("light_service.py", "app/light_service.py"),
    ("models.py", "app/models.py"),
    ("parser_service.py", "app/parser_service.py"),
    ("storage.py", "app/storage.py"),
    ("telegram_client.py", "app/telegram_client.py"),
    ("run_background.py", "app/run_background.py"),
    ("generate_daily_report.py", "app/generate_daily_report.py"),
    ("generate_text_report.py", "app/generate_text_report.py"),
    ("generate_weekly_report.py", "app/generate_weekly_report.py"),
]
for src, dst in app_files:
    if os.path.exists(src):
        run_cmd(f"git mv {src} {dst}")

if os.path.exists("test_state.py"):
    run_cmd("git mv test_state.py tests/test_state.py")

# 3. Move Scripts
scripts_files = ["bootstrap.py", "fix_event_log.py", "update_light.py"]
for f in scripts_files:
    if os.path.exists(f):
        run_cmd(f"git mv {f} scripts/{f}")

# 4. Move Docs
doc_files = ["CHANGELOG.md", "DEVELOPMENT.md", "DEVELOPMENT_ENG.md", "INSTRUCTIONS.md", "INSTRUCTIONS_ENG.md", "INSTRUCTIONS_INSTALL.md", "INSTRUCTIONS_INSTALL_ENG.md", "SECURITY.md"]
for f in doc_files:
    if os.path.exists(f):
        run_cmd(f"git mv {f} docs/{f}")

# 5. Move images
imgs = glob.glob("Admin-control-panel-*.png")
if os.path.exists("dashboard_preview.jpg"):
    imgs.append("dashboard_preview.jpg")
for img in imgs:
    run_cmd(f"git mv {img} docs/assets/{img}")

# 6. Fix references in READMEs
def update_readme(path):
    if not os.path.exists(path): return
    with open(path, 'r') as f:
        content = f.read()
    content = content.replace("dashboard_preview.jpg", "docs/assets/dashboard_preview.jpg")
    for doc in doc_files:
        content = content.replace(f"]({doc})", f"](docs/{doc})")
    with open(path, 'w') as f:
        f.write(content)

update_readme("README.md")
update_readme("README_ENG.md")

# 7. Fix Python imports
app_modules = ["main", "light_service", "models", "parser_service", "storage", "telegram_client", "run_background", "generate_daily_report", "generate_text_report", "generate_weekly_report"]
py_files = glob.glob("app/*.py") + glob.glob("scripts/*.py") + glob.glob("tests/*.py")

for pyf in py_files:
    with open(pyf, 'r') as f:
        content = f.read()
    for mod in app_modules:
        content = re.sub(rf"^import {mod}(\s|$)", rf"import app.{mod}\1", content, flags=re.MULTILINE)
        content = re.sub(rf"^from {mod} import", rf"from app.{mod} import", content, flags=re.MULTILINE)
    
    with open(pyf, 'w') as f:
        f.write(content)

# Update INSTRUCTIONS files
def update_service_file_paths(path):
    if not os.path.exists(path): return
    with open(path, 'r') as f:
        content = f.read()
    content = content.replace("app:app", "app.main:app")
    content = content.replace("run_background.py", "-m app.run_background")
    content = content.replace("WorkingDirectory=/root/geminicli/flash-monitor-kyiv", "WorkingDirectory=/root/geminicli/flash-monitor-kyiv")
    # if there is python3 app.py it should be python3 -m app.main maybe? No, it's uvicorn
    with open(path, 'w') as f:
        f.write(content)

update_service_file_paths("docs/INSTRUCTIONS_INSTALL.md")
update_service_file_paths("docs/INSTRUCTIONS_INSTALL_ENG.md")
update_service_file_paths("docs/INSTRUCTIONS.md")
update_service_file_paths("docs/INSTRUCTIONS_ENG.md")
