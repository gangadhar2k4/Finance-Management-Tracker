import os
import subprocess

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moneyflow.settings')
    subprocess.run(["python", "manage.py", "runserver", "0.0.0.0:5000"])
