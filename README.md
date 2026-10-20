<div align="center">

# 🔗 backlink-gap-finder

### Find the sites that link to your competitors but not to you, ranked by authority instead of volume.

[![tests](https://github.com/marketing-MEER/backlink-gap-finder/actions/workflows/ci.yml/badge.svg)](https://github.com/marketing-MEER/backlink-gap-finder/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![No API keys](https://img.shields.io/badge/API%20keys-none%20needed-brightgreen)
[![Part of SEO Toolbox](https://img.shields.io/badge/part%20of-SEO%20Toolbox-orange)](https://github.com/marketing-MEER/seo-toolbox)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Meer%20Hamza-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)

[🚀 Quick start](#quick-start) · [⚙️ How it works](#how-it-works) · [📄 Report](#report) · [❓ FAQ](#faq) · [👤 Author](#author)

</div>

---

## 💡 What it does

A site that already links to two or three of your competitors writes about your topic and is open to linking. That makes it the warmest outreach target you have. Finding those sites means merging several referring-domain exports and removing the junk.

`backlink-gap-finder` reads referring-domain or backlink exports for your site and up to 5 competitors. It lists every domain that links to them and not you, and ranks the list by **competitors linking × authority**. Spammy and very weak domains are moved to a separate "skipped" list.

- ✅ Ranked link prospects, with the domains that link to 2+ competitors on top
- ✅ Low-quality filter: spammy TLDs, SEO/directory domains, authority under 10
- ✅ Domain type: news / media, edu / gov, blog, forum, website
- ✅ An authority profile per site, comparing link **quality** rather than counts

## 📊 Why this matters

> **E.E.A.T. Signals That Most Impact Rankings** · NP Digital, November 2024 (181 SEO experts)
> - Backlinks and brand mentions receive a ranking impact score of 10.
> - In-depth knowledge scores a 9 for ranking influence.
> - Author credentials score an impact level of 8.
>
> **What Can Replace Backlink Volume as an Authority KPI** · NP Digital, August 2026 (1,000 marketers)
> - Revenue growth captures 41% of the outcome mix marketers associate with authority-building signals; pipeline impact 26%; AI visibility 19%.
>
> Data: [E.E.A.T. signals](https://neilpatel.com/marketing-stats/eeat-signals-by-ranking-impact/) · [replacing backlink volume](https://neilpatel.com/marketing-stats/backlink-volume-replacement-kpi/)

**How backlink-gap-finder uses this:** the first study says to *"prioritize authoritative backlinks over volume link building"*, so prospects are ranked by authority × how many competitors they link to. The second says to *"stop reporting [backlinks] as your headline authority metric"*, so sites are compared by **authority bands**, not by how many referring domains they have.

<a id="quick-start"></a>

## 🚀 Quick start

```bash
git clone https://github.com/marketing-MEER/backlink-gap-finder.git
cd backlink-gap-finder
pip install -e .
backlink-gap-finder examples/brightcrm_refdomains.csv examples/pipelinehq_refdomains.csv examples/salesdeck_refdomains.csv examples/closeflow_refdomains.csv
```

The first file is **you**; the rest (1 to 5) are competitors. This writes **`backlink_gap.html`** (a formatted report) and **`backlink_gap.xlsx`** (all data).

> [!TIP]
> If the `backlink-gap-finder` command isn't found, use `python -m backlink_gap_finder`.

## 📥 Input

Referring domains **or** backlinks exports. Backlink rows are grouped by source domain automatically.

| Source | How to export | Columns detected |
|---|---|---|
| Ahrefs | Site Explorer → Referring domains → Export | `Referring domain`, `Domain rating`, `Domain traffic` |
| Semrush | Backlink Analytics → Referring Domains → Export | `Domain`, `Authority Score` |
| Majestic / Moz | Referring domains export | `Domain`, `Trust Flow` / `Domain Authority` |
| Google Search Console | Links → Top linking sites → Export | `Top linking sites` (no authority: counted as 50) |
| Any backlinks export | One row per link | `Referring page URL` / `Source URL`, optional `Target URL` |

Sites are named from the `Target URL` column when there is one, otherwise from the file name.

<a id="how-it-works"></a>

## ⚙️ How it works

1. **Normalise domains**: `https://www.Site.com/page` → `site.com`. Backlinks are grouped per domain.
2. **Merge**: one row per domain, a yes/no column per site, and the highest authority and traffic any export reports.
3. **Quality check**:
   - **likely low quality**: spammy TLDs (`.xyz`, `.top`, `.click`…) or SEO/directory/"site worth" names
   - **low authority**: authority under 10
4. **Priority** = competitors linking × (authority ÷ 100). Unknown authority counts as 50; low-quality domains get 0, so they never top the list.
5. **Authority profile**: each site's referring domains in bands 0–19, 20–39, 40–59, 60–79, 80–100, plus median authority and the share of domains at 40+.

### Options

| Option | Default | What it does |
|---|---|---|
| `--min-competitors` | `1` | Only list gap domains that link to at least this many competitors |
| `-o`, `--output` | `backlink_gap` | Report name; writes `.html` and `.xlsx` |

<a id="report"></a>

## 📄 The report

| Section / Excel sheet | Shows |
|---|---|
| Summary cards | Link prospects, those linking to 2+ competitors, skipped domains, domains only you have |
| **Profiles** | Authority bands, median authority and the 40+ share per site |
| **Link to 2+ competitors** | The warmest prospects |
| **All prospects** | Every quality-checked gap domain with priority, authority, traffic, type and which competitors it links to |
| **Skipped** | Low-quality or very weak domains, to check by hand |
| **Only you** | Domains that link to you and no competitor |

<details>
<summary>📄 Example: real output from <code>examples/</code> (fictional sites)</summary>

**Authority profile.** brightcrm.io has the *fewest* referring domains, but the *highest* share of strong ones. A count-based report would have hidden that.

| site | referring domains | median authority | authority 40+ % |
|---|---|---|---|
| brightcrm.io (you) | 11 | 65 | 72.7 |
| pipelinehq.com | 21 | 59 | 66.7 |
| salesdeck.io | 14 | 36.5 | 42.9 |
| closeflow.app | 13 | 51 | 53.8 |

**Top prospects**

| domain | priority | competitors linking | authority | type |
|---|---|---|---|---|
| b2bmarketingpost.com | 1.7 | 2 | 85 | news / media |
| businessschool.edu | 1.56 | 2 | 78 | edu / gov |
| salesleadersclub.com | 1.24 | 2 | 62 | website |
| pipelinepros.com | 1.18 | 2 | 59 | website |
| saasweekly.com | 1.18 | 2 | 59 | website |
| agencylife.com | 1.05 | 3 | 35 | website |

**Skipped:** best-seo-links.xyz, freebacklinkdirectory.com, site-worth-info.top, webstatsdomain.net.

</details>

## 🧰 More free SEO tools

This repo is one tool in the **[SEO Toolbox](https://github.com/marketing-MEER/seo-toolbox)**, a family of free, single-purpose SEO tools. Related:
- [serp-competitor-finder](https://github.com/marketing-MEER/serp-competitor-finder): pick the right competitors to compare against
- **link-prospect-scorer**: score any outreach list by relevance and authority
- [seo-workhorse](https://github.com/marketing-MEER/seo-workhorse): audit, clustering, redirects and GSC quick wins in one CLI

<a id="faq"></a>

## ❓ FAQ

<details><summary><b>Can I mix exports from different tools?</b></summary>

Yes, but authority scales differ (Ahrefs DR ≠ Semrush AS ≠ Moz DA). The tool keeps the highest value it sees for each domain, so for clean rankings use the same tool for every site.
</details>

<details><summary><b>Is "likely low quality" always spam?</b></summary>

No. It's a name-based warning, not a verdict. Those domains are listed separately so you can check them by hand before any outreach, and before considering a disavow.
</details>

<details><summary><b>Why does a domain with lower authority rank above a stronger one?</b></summary>

Because it links to more of your competitors. Three competitor links × authority 35 (1.05) beats one link × authority 73 (0.73): it's a proven linker in your niche.
</details>

<details><summary><b>Is my data sent anywhere?</b></summary>

No. It reads your CSV files and writes the report on your computer. It makes no network requests.
</details>

## 🧪 Tests

```bash
python -m unittest discover -s tests -t . -v
```

## 📄 License

[MIT](LICENSE). Free for personal and commercial use. Benchmark figures © their original publishers, quoted with a link to the source.

<a id="author"></a>

## 👤 Author

**Meer Hamza** · SEO Team Lead · Berlin 🇩🇪
10+ years in SEO, AEO and GEO. I build small tools that take the spreadsheet work out of SEO.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)
[![Email](https://img.shields.io/badge/Email-meerhamza5%40gmail.com-D14836?logo=gmail&logoColor=white)](mailto:meerhamza5@gmail.com)

<div align="center">

**If this saved you time, a ⭐ helps other SEOs find it.**

</div>
