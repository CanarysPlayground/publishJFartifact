import os
import requests
from datetime import datetime, timedelta

# --- Config via environment ---
TOKEN = os.getenv("GITHUB_PAT")
OWNER = os.getenv("REPO_OWNER")
REPO = os.getenv("REPO_NAME")
HEADERS = {"Authorization": f"token {TOKEN}"}
DAYS_INACTIVE = 60

def get_default_branch():
    url = f"https://api.github.com/repos/{OWNER}/{REPO}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["default_branch"]

def get_all_branches():
    branches = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/branches?per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        branches.extend(data)
        page += 1
    return branches

def get_commit_date(branch):
    sha = branch["commit"]["sha"]
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/commits/{sha}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    commit_date = response.json()["commit"]["committer"]["date"]
    return datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")

def delete_branch(branch_name):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/git/refs/heads/{branch_name}"
    response = requests.delete(url, headers=HEADERS)
    if response.status_code == 204:
        print(f"✅ Deleted: {branch_name}")
    else:
        print(f"❌ Failed to delete {branch_name}: {response.status_code} - {response.text}")

def main():
    print(f"🔍 Checking branches in {OWNER}/{REPO}")
    cutoff_date = datetime.utcnow() - timedelta(days=DAYS_INACTIVE)
    default_branch = get_default_branch()
    branches = get_all_branches()

    for branch in branches:
        name = branch["name"]
        if name == default_branch:
            print(f"🚫 Skipping default branch: {name}")
            continue

        commit_date = get_commit_date(branch)
        if commit_date < cutoff_date:
            print(f"🗑️ Deleting inactive branch: {name} (last commit: {commit_date.date()})")
            delete_branch(name)
        else:
            print(f"✅ Active branch: {name} (last commit: {commit_date.date()})")

if __name__ == "__main__":
    main()
