import os
import json
import logging
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# ---------- logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("workflow-trigger")

# ---------- config ----------
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    log.error("GITHUB_TOKEN is not set")
    exit(1)

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

with open("config.json") as f:
    config = json.load(f)

log.info("config loaded")

# ---------- scheduler ----------
scheduler = BlockingScheduler()

def trigger_workflow(repo_name, workflow_name, branch):
    log.info(f"triggering {repo_name}/{workflow_name} @ {branch}")
    url = f"https://api.github.com/repos/{repo_name}/actions/workflows/{workflow_name}/dispatches"
    payload = {"ref": branch}

    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=10)
    except Exception as e:
        log.error(f"request failed: {e}")
        return

    if response.status_code == 204:
        log.info(f"success: {workflow_name} on {repo_name}@{branch}")
    else:
        log.error(
            f"fail: {workflow_name} on {repo_name}@{branch} "
            f"{response.status_code} {response.text}"
        )

# ---------- load jobs ----------
job_count = 0

for repo_name, repo_data in config.get("repos", {}).items():
    for wf in repo_data.get("workflows", []):
        name = wf["name"]
        branch = wf.get("branch", "main")
        cron = wf.get("cron")

        if cron:
            parts = cron.split()
            scheduler.add_job(
                trigger_workflow,
                "cron",
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4],
                args=[repo_name, name, branch],
            )
            log.info(f"job added: {repo_name}/{name} cron='{cron}'")
            job_count += 1
        else:
            log.info(f"run once: {repo_name}/{name}")
            trigger_workflow(repo_name, name, branch)

log.info(f"total cron jobs: {job_count}")
log.info("scheduler starting...")
scheduler.start()
