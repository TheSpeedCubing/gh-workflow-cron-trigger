import os
import json
import requests
from apscheduler.schedulers.blocking import BlockingScheduler

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}

with open("config.json") as f:
    config = json.load(f)

scheduler = BlockingScheduler()

def trigger_workflow(repo_name, workflow_name, branch):
    url = f"https://api.github.com/repos/{repo_name}/actions/workflows/{workflow_name}/dispatches"
    payload = {"ref": branch}
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 204:
        print(f"success: {workflow_name} on {repo_name}@{branch}")
    else:
        print(f"fail: {workflow_name} on {repo_name}@{branch}: {response.status_code} {response.text}")

for repo_name, repo_data in config.get("repos", {}).items():
    for wf in repo_data.get("workflows", []):
        name = wf["name"]
        branch = wf.get("branch", "main")
        cron = wf.get("cron")
        if cron:
            parts = cron.split()
            scheduler.add_job(trigger_workflow, 'cron', minute=parts[0], hour=parts[1], day=parts[2],
                              month=parts[3], day_of_week=parts[4], args=[repo_name, name, branch])
        else:
            trigger_workflow(repo_name, name, branch)

scheduler.start()
