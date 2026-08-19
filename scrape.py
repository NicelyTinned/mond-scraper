import os
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

token = os.environ.get("SCRAPE_PAT")
topic = os.environ.get("TARGET_TOPIC", "mond-package")

headers = {
    "Authorization": f"Bearer {token}" if token else "",
    "Accept": "application/vnd.github+json"
}

candidate_repos = []
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
        candidate_repos.append({
            "raw_base": f"https://raw.githubusercontent.com/{full_name}/{branch}/",
            "toml_url": f"https://raw.githubusercontent.com/{full_name}/{branch}/Mond.toml"
        })

    if len(items) < 100:
        break
        
    page += 1

def check_mond_toml(repo):
    try:
        res = requests.head(repo["toml_url"], timeout=5, allow_redirects=True)
        if res.status_code == 200:
            return repo["raw_base"]
    except Exception:
        pass
    return None

valid_urls = []

with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(check_mond_toml, repo) for repo in candidate_repos]
    for future in as_completed(futures):
        result = future.result()
        if result:
            valid_urls.append(result)

valid_urls.sort()

with open("packages.json", "w") as f:
    json.dump(valid_urls, f, indent=2)
        
