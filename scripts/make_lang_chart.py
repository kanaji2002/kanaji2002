#!/usr/bin/env python3
import os, math, requests
import matplotlib
matplotlib.use("Agg")  # GUI不要
import matplotlib.pyplot as plt

USER = os.getenv("GH_USERNAME", "kanaji2002")
TOKEN = os.getenv("GITHUB_TOKEN")  # ActionsのGITHUB_TOKENでOK
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

def fetch_all_repos(user):
    repos = []
    page = 1
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

EXCLUDE = {"PostScript", "TeX", "Makefile", "Jupyter Notebook"}  # 好みで追加OK

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
        # 空でも落ちないように
        data = {"Other": 1}

    # 上位N + Other に集約
    items = sorted(data.items(), key=lambda x: x[1], reverse=True)
    head = items[:top_n]
    tail_sum = sum(v for _, v in items[top_n:])
    if tail_sum > 0:
        head.append(("Other", tail_sum))

    labels = [k for k, _ in head]
    sizes = [v for _, v in head]

    fig, ax = plt.subplots(figsize=(4.6, 4.6), dpi=200)
    wedges, texts = ax.pie(sizes, wedgeprops=dict(width=0.38), startangle=90)
    ax.legend(wedges, labels, title="Languages", loc="center left", bbox_to_anchor=(1, 0.5))
    ax.set(aspect="equal", title=f"{USER}'s Top Languages")
    plt.tight_layout()
    fig.savefig(out, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)

if __name__ == "__main__":
    data = aggregate_languages(USER)
    make_donut(data)
