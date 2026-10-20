"""Command line entry point: `backlink-gap-finder YOU.csv COMPETITOR.csv [...]`."""
from pathlib import Path

import click

from . import __version__, core
from .benchmark import STATS
from .report import Report, write_excel


@click.command()
@click.argument("your_csv", type=click.Path(exists=True))
@click.argument("competitor_csv", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--min-competitors", default=1, show_default=True,
              help="Only list gap domains that link to at least this many competitors.")
@click.option("-o", "--output", default="backlink_gap", show_default=True,
              help="Report name; writes <name>.html and <name>.xlsx")
@click.version_option(__version__)
def main(your_csv, competitor_csv, min_competitors, output):
    """Find domains that link to your competitors but not to you, ranked by authority.

    Built by Meer Hamza - linkedin.com/in/meerhamza-seo
    """
    if len(competitor_csv) > 5:
        raise click.BadParameter("use up to 5 competitor files")
    table, me, names = core.gap(your_csv, competitor_csv)
    missing = table[~table["links_to_you"] & (table["competitors_linking"] >= min_competitors)].drop(columns="links_to_you")
    prospects = missing[missing["quality"] == "ok"]
    intersect = prospects[prospects["competitors_linking"] >= 2]
    skipped = missing[missing["quality"] != "ok"]
    profile = core.profiles(table, me, names)
    exclusive = table[table["links_to_you"] & (table["competitors_linking"] == 0)]

    report = Report(title="Backlink gap report", subtitle=f"{me} vs {', '.join(names)}", tool="backlink-gap-finder")
    report.add_cards([
        ("Link prospects", len(prospects), "warn"),
        ("Link to 2+ competitors", len(intersect), "bad" if len(intersect) else "good"),
        ("Skipped (low quality)", len(skipped)),
        ("Domains only you have", len(exclusive), "good"),
    ])
    report.add_benchmark(STATS[0], how_used="Prospects are ranked by competitors linking × authority, so one strong "
                                            "domain that links to several rivals beats many weak ones.")
    report.add_benchmark(STATS[1], how_used="Sites are compared by authority bands, not by raw referring-domain "
                                            "counts.")
    report.add_table("Authority profile per site", profile, note="Referring domains by authority band.",
                     sheet="Profiles")
    report.add_table("Top prospects: link to 2+ competitors", intersect,
                     note="If a domain links to several rivals, it covers your topic and is open to linking.",
                     sheet="Link to 2+ competitors")
    report.add_table("All link prospects", prospects, sheet="All prospects")
    report.add_table("Skipped: likely low quality or very low authority", skipped,
                     note="Spammy TLDs, SEO/directory domains or authority under 10. Check by hand before outreach.",
                     sheet="Skipped")
    report.add_table("Domains that link only to you", exclusive, note="Your unique links. Keep these relationships.",
                     sheet="Only you")

    html_path = report.save_html(Path(output).with_suffix(".html"))
    xlsx_path = write_excel(report.sheets, Path(output).with_suffix(".xlsx"))
    click.secho(f"Report: {html_path}\nData:   {xlsx_path}", fg="green", bold=True)
    click.echo(profile.to_string(index=False))


if __name__ == "__main__":
    main()
