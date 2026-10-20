"""Backlink gap: domains that link to your competitors but not to you.

Reads referring-domain (or backlink) exports for your site and up to 5
competitors, and ranks every missing domain by how many competitors it links
to and how authoritative it is. Authority beats volume: one strong domain
that links to three rivals is worth more than twenty weak ones.
"""
import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

from .report import find_column, to_number

# Ranked by authority, not count (NP: eeat-signals-by-ranking-impact, "prioritize
# authoritative backlinks over volume link building").
BANDS = [(0, 20, "0-19"), (20, 40, "20-39"), (40, 60, "40-59"), (60, 80, "60-79"), (80, 101, "80-100")]

SPAMMY_TLDS = {"xyz", "top", "click", "loan", "work", "gq", "tk", "ml", "cf", "ga", "buzz", "rest", "icu", "cyou"}
SPAMMY_WORDS = re.compile(r"(seo|backlink|links?|directory|submit|bookmark|article-?base|web-?stats|whois|"
                          r"site-?(value|worth|info|analysis)|domain-?(stats|info))", re.I)
EDU_GOV = re.compile(r"\.(edu|gov|ac\.[a-z]{2}|gov\.[a-z]{2}|edu\.[a-z]{2})$")
FORUMS = {"reddit.com", "quora.com", "stackexchange.com", "stackoverflow.com", "news.ycombinator.com"}


def clean_domain(value: str) -> str:
    value = str(value).strip().lower()
    host = urlparse(value if "://" in value else "https://" + value).netloc or value
    host = host.split(":")[0]
    return host[4:] if host.startswith("www.") else host


def load_export(path) -> tuple[str, pd.DataFrame]:
    """Referring domains (Ahrefs/Semrush/GSC 'Top linking sites') or a backlinks export (one row per link)."""
    raw = pd.read_csv(path)
    dom = find_column(raw, ["referring domain", "domain", "linking site", "linking sites", "top linking sites",
                            "source domain", "ref domain"])
    src_url = find_column(raw, ["referring page url", "source url", "referring page", "source page", "url from"])
    target = find_column(raw, ["target url", "url to", "target page", "target"])
    if not dom and not src_url:
        raise ValueError(f"{path}: need a referring domain or source URL column. Found: {list(raw.columns)}")
    df = pd.DataFrame({"domain": (raw[dom] if dom else raw[src_url]).map(clean_domain)})
    auth = find_column(raw, ["domain rating", "dr", "authority score", "as", "domain authority", "da",
                             "trust flow", "tf"])
    traffic = find_column(raw, ["domain traffic", "traffic", "organic traffic", "ref. domain traffic"])
    links = find_column(raw, ["links to target", "backlinks", "links", "dofollow links"])
    df["authority"] = to_number(raw[auth]) if auth else float("nan")
    df["traffic"] = to_number(raw[traffic]) if traffic else float("nan")
    df["links"] = to_number(raw[links]) if links else 1
    agg = df.groupby("domain").agg(authority=("authority", "max"), traffic=("traffic", "max"),
                                   links=("links", "sum")).reset_index()
    name = Path(path).stem
    if target:
        hosts = raw[target].dropna().map(clean_domain)
        if not hosts.empty:
            name = hosts.mode().iloc[0]
    return name, agg[agg["domain"] != ""]


def quality(domain: str, authority: float) -> str:
    tld = domain.rsplit(".", 1)[-1]
    if tld in SPAMMY_TLDS or SPAMMY_WORDS.search(domain.split(".")[0]):
        return "likely low quality"
    if authority == authority and authority < 10:  # not NaN and very low
        return "low authority"
    return "ok"


def kind(domain: str) -> str:
    if EDU_GOV.search(domain):
        return "edu / gov"
    if domain in FORUMS or domain.startswith(("forum.", "community.")):
        return "forum / community"
    if domain.endswith(("wordpress.com", "blogspot.com", "medium.com", "substack.com")) or "blog" in domain:
        return "blog"
    if re.search(r"(news|times|post|herald|journal|magazine|daily|tribune|press)", domain):
        return "news / media"
    return "website"


def band(authority: float) -> str:
    if authority != authority:
        return "unknown"
    for lo, hi, label in BANDS:
        if lo <= authority < hi:
            return label
    return "unknown"


def gap(you_path, competitor_paths) -> tuple[pd.DataFrame, str, list[str]]:
    me, mine = load_export(you_path)
    rivals = [load_export(p) for p in competitor_paths]
    names, seen = [], {me}
    for i, (name, _) in enumerate(rivals):
        names.append(name if name not in seen else f"{name} ({i + 1})")
        seen.add(names[-1])

    exports = [mine] + [df for _, df in rivals]
    # One row per domain; authority/traffic = highest value any export reports for it.
    table = (pd.concat(exports, ignore_index=True).groupby("domain")
             .agg(authority=("authority", "max"), traffic=("traffic", "max")).reset_index())
    table[me] = table["domain"].isin(mine["domain"])
    for name, df in zip(names, exports[1:]):
        table[name] = table["domain"].isin(df["domain"])

    table["competitors_linking"] = table[names].sum(axis=1).astype(int)
    table["links_to_you"] = table[me]
    table["quality"] = [quality(d, a) for d, a in zip(table["domain"], table["authority"])]
    table["type"] = table["domain"].map(kind)
    table["authority_band"] = table["authority"].map(band)
    # Priority: competitors linking x authority (0-1). Unknown authority counts as 0.5,
    # low-quality domains drop to 0 so they never top the list.
    auth = (table["authority"].fillna(50) / 100).clip(0.05, 1)
    table["priority"] = (table["competitors_linking"] * auth * (table["quality"] == "ok")).round(2)
    cols = ["domain", "priority", "competitors_linking", "authority", "authority_band", "traffic", "type",
            "quality", "links_to_you"] + names
    return table[cols].sort_values(["priority", "competitors_linking", "authority"], ascending=False), me, names


def profiles(table: pd.DataFrame, me: str, names: list[str]) -> pd.DataFrame:
    """Per site: referring domains by authority band. The headline is quality, not count."""
    rows = []
    for site in [me] + names:
        col = "links_to_you" if site == me else site
        sub = table[table[col]]
        known = sub["authority"].dropna()
        row = {"site": site, "referring_domains": len(sub),
               "median_authority": round(known.median(), 1) if len(known) else None,
               "authority_40_plus": int((known >= 40).sum()),
               "authority_40_plus_pct": round((known >= 40).mean() * 100, 1) if len(known) else None}
        for _, _, label in BANDS:
            row[f"band_{label}"] = int((sub["authority_band"] == label).sum())
        rows.append(row)
    return pd.DataFrame(rows)
