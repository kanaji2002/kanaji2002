#!/usr/bin/env python3
import os, requests
import matplotlib
matplotlib.use("Agg")  # GUI不要
import matplotlib.pyplot as plt

# 🌞 Solarized-light カラーパレット
SOLARIZED_LIGHT = [
    "#268bd2",  # blue
    "#2aa198",  # cyan
    "#859900",  # green
    "#b58900",  # yellow
    "#cb4b16",  # orange
    "#d33682",  # magenta
    "#6c71c4",  # violet
    "#eee8d5",  # base2 (背景)
    "#93a1a1",  # base1
    "#073642"   # base03 (枠線)
]

USER = os.getenv("GH_USERNAME", "kanaji2002")
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

EXCLUDE = {"PostScript", "TeX", "Jupyter Notebook", "Makefile", "HTML"}  # 必要に応じて追加


def fetch_all_repos(user):
    repos, page = [], 1
    while True:
        r = requests.get(
            f"https://api.github.com/users/{user}/repos",
            params={"per_page": 100, "page": page, "type": "owner"},
            headers=HEADERS, timeout=30
        )
        r.raise_for_status()
        batch = r.json()
        if not batch: break
        repos += batch
        page += 1
    return repos

def fetch_langs(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def aggregate_languages(user):
    total = {}
    for repo in fetch_all_repos(user):
        if repo.get("fork"):
            continue
        langs = fetch_langs(repo["languages_url"])
        for name, bytes_ in langs.items():
            if name in EXCLUDE:
                continue
            total[name] = total.get(name, 0) + bytes_
    return total

def make_donut(data, out="assets/lang_donut.png", top_n=5):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if not data:
        data = {"Other": 1}

    items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    head = items[:top_n]
    tail_sum = sum(v for _, v in items[top_n:])
    if tail_sum > 0:
        head.append(("Other", tail_sum))

    labels = [k for k, _ in head]
    sizes = [v for _, v in head]

    # 🌞 Solarized-light っぽい設定
    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(4.6, 4.6), dpi=200, facecolor="#fdf6e3")
    wedges, _ = ax.pie(
        sizes,
        colors=SOLARIZED_LIGHT[:len(sizes)]()_
