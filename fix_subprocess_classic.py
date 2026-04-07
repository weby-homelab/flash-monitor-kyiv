import os
import re

path = "/root/geminicli/flash-monitor-kyiv/app/light_service.py"
if os.path.exists(path):
    with open(path, "r") as f:
        content = f.read()

    content = content.replace('script_path = os.path.join(base_dir, "generate_daily_report.py")', 'script_path = "-m"; script_name = "app.generate_daily_report"')
    content = content.replace('subprocess.run(args, check=True, cwd=base_dir)', 'args[1] = "-m"; args.insert(2, "app.generate_daily_report"); subprocess.run(args, check=True, cwd=os.path.dirname(base_dir))')

    content = content.replace('script_path = os.path.join(base_dir, "generate_text_report.py")', '')
    content = content.replace('subprocess.run([python_exec, script_path], check=True, cwd=base_dir)', 'subprocess.run([python_exec, "-m", "app.generate_text_report"], check=True, cwd=os.path.dirname(base_dir))')

    content = content.replace('script_path = os.path.join(base_dir, "generate_weekly_report.py")', '')
    content = content.replace('subprocess.run([python_exec, script_path, "--output", output_path], check=True, cwd=base_dir)', 'subprocess.run([python_exec, "-m", "app.generate_weekly_report", "--output", output_path], check=True, cwd=os.path.dirname(base_dir))')

    content = content.replace('subprocess.run([python_exec, os.path.join(base_dir, "generate_daily_report.py"), "--cleanup"], cwd=base_dir)', 'subprocess.run([python_exec, "-m", "app.generate_daily_report", "--cleanup"], cwd=os.path.dirname(base_dir))')
    content = content.replace('subprocess.run([python_exec, os.path.join(base_dir, "generate_text_report.py"), "--cleanup"], cwd=base_dir)', 'subprocess.run([python_exec, "-m", "app.generate_text_report", "--cleanup"], cwd=os.path.dirname(base_dir))')

    content = content.replace('script_path = os.path.join(base_dir, "generate_text_report.py")', '')
    content = content.replace('subprocess.run([python_exec, script_path, "--force-new"], check=True, cwd=base_dir)', 'subprocess.run([python_exec, "-m", "app.generate_text_report", "--force-new"], check=True, cwd=os.path.dirname(base_dir))')

    content = content.replace('subprocess.run([sys.executable, os.path.join(base_dir, "generate_weekly_report.py"), "--date", (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")], check=True, cwd=base_dir)', 'subprocess.run([sys.executable, "-m", "app.generate_weekly_report", "--date", (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")], check=True, cwd=os.path.dirname(base_dir))')

    with open(path, "w") as f:
        f.write(content)
