import os
from pathlib import Path

ENV_PATH = Path(__file__).parent / ".env"

def load_env():
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip()

load_env()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
SBP_REQUISITES = os.getenv("SBP_REQUISITES", "+7 (999) 000-00-00 (Банк)")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@bezosyzhdeniya_tg")

def save_admin_id(admin_id: int):
    if admin_id not in ADMIN_IDS:
        ADMIN_IDS.append(admin_id)
        # Update .env
        lines = []
        if ENV_PATH.exists():
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        admin_found = False
        new_lines = []
        for line in lines:
            if line.startswith("ADMIN_IDS="):
                new_lines.append(f"ADMIN_IDS={','.join(map(str, ADMIN_IDS))}\n")
                admin_found = True
            else:
                new_lines.append(line)
        if not admin_found:
            new_lines.append(f"ADMIN_IDS={','.join(map(str, ADMIN_IDS))}\n")
        
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
