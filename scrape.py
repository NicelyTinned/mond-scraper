import os
import json
import requests

token = os.environ.get("SCRAPE_PAT")
topic = os.environ.get("TARGET_TOPIC", "mond-package")

headers = {
    "Authorization": f"Bearer {token}" if token else "",
    "Accept": "application/vnd.github+json"
}

raw_urls = []
page = 1

while True:
    url = f"https://api.github.com/search/repositories?q=topic:{topic}&per_page=100&page={page}"
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        break
        
    items = res.json().get("items", [])
    if not items:
        break

    for repo in items:
        full_name = repo["full_name"]
        branch = repo.get("default_branch", "main")
        raw_urls.append(f"https://raw.githubusercontent.com/{full_name}/{branch}/")

    if len(items) < 100:
        break
        
    page += 1

with open("packages.json", "w") as f:
    json.dump(raw_urls, f, indent=2)
