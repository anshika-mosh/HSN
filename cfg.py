"""Reads MONGO_URI from the environment or from a .env file in this folder (no extra package needed)."""
import os
def mongo_uri(default="mongodb://localhost:27017"):
    if os.environ.get("MONGO_URI"): return os.environ["MONGO_URI"]
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.join(here, ".env"), ".env"):
        if os.path.exists(p):
            for line in open(p, encoding="utf-8-sig"):
                line = line.strip()
                if line.startswith("MONGO_URI") and "=" in line:
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return default
