import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from backlink_gap_finder import cli, core

EXAMPLES = Path(__file__).parent.parent / "examples"

YOU = """Referring domain,Domain rating,Target URL
shared.com,50,https://me.com/
onlyme.org,40,https://me.com/
"""
A = """Domain,Authority Score
shared.com,50
strong.com,90
weak.com,20
best-seo-links.xyz,5
"""
B = """Referring page URL,Target URL
https://www.strong.com/post-1,https://b.io/
https://strong.com/post-2,https://b.io/x
https://weak.com/a,https://b.io/
https://nodata.net/a,https://b.io/
"""


class GapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        for name, text in [("me", YOU), ("a", A), ("b", B)]:
            (d / f"{name}.csv").write_text(text, encoding="utf-8")
        self.table, self.me, self.names = core.gap(d / "me.csv", [d / "a.csv", d / "b.csv"])
        self.t = self.table.set_index("domain")

    def tearDown(self):
        self.tmp.cleanup()

    def test_names_from_target_column_or_file(self):
        self.assertEqual(self.me, "me.com")
        self.assertEqual(self.names, ["a", "b.io"])   # a.csv has no target column -> file name

    def test_backlinks_export_is_grouped_by_domain(self):
        self.assertTrue(self.t.at["strong.com", "b.io"])
        self.assertEqual(self.t.at["strong.com", "competitors_linking"], 2)

    def test_priority_is_authority_times_competitors(self):
        self.assertAlmostEqual(self.t.at["strong.com", "priority"], 2 * 0.9)
        self.assertAlmostEqual(self.t.at["weak.com", "priority"], 2 * 0.2)
        self.assertAlmostEqual(self.t.at["nodata.net", "priority"], 1 * 0.5)  # unknown authority counts as 50
        self.assertEqual(self.table.iloc[0]["domain"], "strong.com")

    def test_low_quality_never_ranks(self):
        self.assertEqual(self.t.at["best-seo-links.xyz", "quality"], "likely low quality")
        self.assertEqual(self.t.at["best-seo-links.xyz", "priority"], 0)

    def test_you_and_profiles(self):
        self.assertTrue(self.t.at["shared.com", "links_to_you"])
        self.assertFalse(self.t.at["strong.com", "links_to_you"])
        prof = core.profiles(self.table, self.me, self.names).set_index("site")
        self.assertEqual(prof.at["me.com", "referring_domains"], 2)
        self.assertEqual(prof.at["a", "authority_40_plus"], 2)

    def test_helpers(self):
        self.assertEqual(core.clean_domain("https://WWW.Example.com:443/page"), "example.com")
        self.assertEqual(core.kind("law.harvard.edu"), "edu / gov")
        self.assertEqual(core.band(59), "40-59")


class CliTest(unittest.TestCase):
    def test_example_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "gap"
            files = [str(EXAMPLES / f"{s}_refdomains.csv") for s in ["brightcrm", "pipelinehq", "salesdeck",
                                                                     "closeflow"]]
            res = CliRunner().invoke(cli.main, files + ["-o", str(out)])
            self.assertEqual(res.exit_code, 0, res.output)
            self.assertIn("Backlink gap report", out.with_suffix(".html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
