#!/usr/bin/env python3
import subprocess, sys

def run(cmd):
    print(">>", " ".join(cmd))
    res = subprocess.run(cmd, check=True)
    return res.returncode

def main():
    run([sys.executable, "news_builder.py"])
    run([sys.executable, "emails_builder.py"])
    run([sys.executable, "plan_builder.py"])

if __name__ == "__main__":
    main()
