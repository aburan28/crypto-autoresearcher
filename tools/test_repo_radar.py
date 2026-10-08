"""Offline tests for the repo radar: scoring, search, watch cursors, GH Archive, digest."""

from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET

from tools import repo_radar as radar


CONFIG = {
    "search": {"topics": ["ecdlp", "cryptography"], "keywords": ['"pollard rho"'],
               "created_only": ["cryptography"], "extra_queries": ["language:sage pushed:>={since}"],
               "qualifiers": "fork:false", "max_pages": 2, "first_run_days": 7, "ignore_owners": ["me"],
               "overlap_days": 1, "max_window_days": 14},
    "scoring": {"min_score": 4, "topics": {"ecdlp": 6, "cryptography": 2},
                "terms": {r"pollard": 4, r"elliptic[ -]curve": 3},
                "negative": {r"\b(bitcoin|trading)\b": -3}},
    "archive": {"name_pattern": r"\b(ecdlp|pollard|elliptic)\b", "enrich_limit": 5, "min_events": 2},
    "watch": {"repos": ["acme/kangaroo"], "max_commits": 2},
    "digest": {"max_rows": 10, "rising_min_stars": 10, "retention_days": 365},
}


def repo(name, stars=5, desc="", topics=(), created="2026-10-06T00:00:00Z", fork=False):
    return {"full_name": name, "description": desc, "topics": list(topics), "language": "C",
            "stargazers_count": stars, "forks_count": 1, "created_at": created,
            "pushed_at": "2026-10-07T00:00:00Z", "archived": False, "fork": fork,
            "html_url": f"https://github.com/{name}", "default_branch": "main"}


class FakeAPI:
    """Routes (method, path) to a payload, a (status, payload) pair, or a function of the query."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def __call__(self, method, url, headers, body):
        parts = urllib.parse.urlsplit(url)
        query = dict(urllib.parse.parse_qsl(parts.query))
        data = json.loads(body) if body else None
        self.calls.append((method, parts.path, query, data))
        handler = self.routes.get((method, parts.path))
        if handler is None:
            return 404, {}, b'{"message": "Not Found"}'
        result = handler(query, data) if callable(handler) else handler
        status, payload = result if isinstance(result, tuple) else (200, result)
        return status, {}, json.dumps(payload).encode()


def client(routes):
    api = FakeAPI(routes)
    return radar.GitHub("token", transport=api, sleep=lambda s: None), api


def event_line(kind, name, actor="someone", payload=None):
    """One GH Archive line in the archive's own compact key order."""
    event = {"id": "1", "type": kind, "actor": {"id": 2, "login": actor},
             "repo": {"id": 3, "name": name, "url": f"https://api.github.com/repos/{name}"},
             "payload": payload or {}, "public": True, "created_at": "2026-10-05T12:00:00Z"}
    return json.dumps(event, separators=(",", ":")).encode() + b"\n"


class ScoringTests(unittest.TestCase):
    def test_topics_terms_and_negatives_add_and_explain(self):
        scorer = radar.Scorer.from_config(CONFIG)
        score, why = scorer.score({"full_name": "x/pollard_rho", "topics": ["ecdlp", "web"],
                                   "description": "Elliptic curve solver for Bitcoin"})
        self.assertEqual(score, 6 + 4 + 3 - 3)
        self.assertEqual(why, ["#ecdlp", "pollard", "elliptic curve", "-bitcoin"])

    def test_owner_name_does_not_count(self):
        scorer = radar.Scorer.from_config(CONFIG)
        self.assertEqual(scorer.score({"full_name": "pollard/notes", "description": ""})[0], 0)

    def test_checked_in_config_loads_and_compiles(self):
        cfg = radar.load_config(radar.DEFAULT_CONFIG)
        radar.Scorer.from_config(cfg)
        radar.archive_matcher(cfg, [])("a/b")
        self.assertTrue(radar.watchlist(cfg))
        self.assertTrue(all(radar.REPO_NAME.match(n) for n in radar.watchlist(cfg)))
        queries = radar.build_queries(cfg, date(2026, 10, 1))
        self.assertTrue(all(len(q["q"]) < 256 for q in queries), "GitHub rejects queries over 256 characters")


class SearchTests(unittest.TestCase):
    def test_queries_cover_created_and_pushed_except_created_only(self):
        queries = radar.build_queries(CONFIG, date(2026, 10, 1))
        self.assertEqual([q["q"] for q in queries], [
            "topic:ecdlp created:>=2026-10-01 fork:false",
            "topic:ecdlp pushed:>=2026-10-01 fork:false",
            "topic:cryptography created:>=2026-10-01 fork:false",
            '"pollard rho" in:name,description,readme created:>=2026-10-01 fork:false',
            '"pollard rho" in:name,description,readme pushed:>=2026-10-01 fork:false',
            "language:sage pushed:>=2026-10-01",
        ])

    def test_window_starts_from_last_run_with_overlap_and_cap(self):
        today = date(2026, 10, 8)
        self.assertEqual(radar.window_start({"meta": {}}, CONFIG, today), date(2026, 10, 1))
        self.assertEqual(radar.window_start({"meta": {"last_discovery": "2026-10-07"}}, CONFIG, today),
                         date(2026, 10, 6))
        self.assertEqual(radar.window_start({"meta": {"last_discovery": "2026-01-01"}}, CONFIG, today),
                         date(2026, 9, 24))

    def test_discover_paginates_merges_labels_and_survives_a_bad_query(self):
        def search(query, _):
            q = query["q"]
            if q.startswith("language:sage"):
                return 422, {"message": "Validation Failed"}
            if q.startswith("topic:ecdlp created"):
                page = int(query["page"])
                items = [repo(f"a/r{i}") for i in range(100)] if page == 1 else [repo("a/last")]
                return {"total_count": 101, "incomplete_results": False, "items": items}
            return {"total_count": 1, "items": [repo("a/r1")]}

        gh, _ = client({("GET", "/search/repositories"): search})
        found, coverage = radar.discover(gh, CONFIG, date(2026, 10, 1))
        self.assertEqual(len(found), 101)
        self.assertEqual(found["a/r1"]["matched"], ["topic:ecdlp", "topic:cryptography", '"pollard rho"'])
        self.assertIn("error", coverage[-1])
        self.assertEqual(coverage[0]["fetched"], 101)
        self.assertEqual(gh.calls["search"], 7)

    def test_discover_raises_when_every_query_fails(self):
        gh, _ = client({("GET", "/search/repositories"): (422, {"message": "bad"})})
        with self.assertRaises(radar.GitHubError):
            radar.discover(gh, CONFIG, date(2026, 10, 1))

    def test_merge_separates_new_spotted_and_rising(self):
        scorer = radar.Scorer.from_config(CONFIG)
        state = radar.load_state(Path("/nonexistent"))
        state["repos"]["old/known"] = {"full_name": "old/known", "stars": 5, "last_seen": "2026-10-01"}
        found = {}
        for item, matched in [
            (repo("new/ecdlp", topics=["ecdlp"]), ["topic:ecdlp"]),
            (repo("older/pollard-rho", desc="Pollard rho", created="2020-01-01T00:00:00Z"), ["k"]),
            (repo("old/known", stars=40, topics=["ecdlp"]), ["topic:ecdlp"]),
            (repo("noise/aes", topics=["cryptography"]), ["topic:cryptography"]),
            (repo("fork/ecdlp", topics=["ecdlp"], fork=True), ["topic:ecdlp"]),
            (repo("Me/ecdlp-mine", topics=["ecdlp"]), ["topic:ecdlp"]),
        ]:
            found[item["full_name"]] = {**radar.repo_record(item), "matched": matched}
        changes = radar.merge_discovery(state, found, scorer, CONFIG, date(2026, 10, 1), date(2026, 10, 8))
        self.assertEqual(changes["relevant"], 3)
        self.assertEqual([r["full_name"] for r in changes["new"]], ["new/ecdlp"])
        self.assertEqual([r["full_name"] for r in changes["spotted"]], ["older/pollard-rho"])
        self.assertEqual([(r["full_name"], r["gain"]) for r in changes["rising"]], [("old/known", 35)])
        self.assertNotIn("noise/aes", state["repos"])
        self.assertNotIn("fork/ecdlp", state["repos"])
        self.assertNotIn("Me/ecdlp-mine", state["repos"])
        self.assertEqual(state["repos"]["new/ecdlp"]["first_seen"], "2026-10-08")
        self.assertEqual(state["repos"]["old/known"]["stars"], 40)


class ClientTests(unittest.TestCase):
    def test_waits_out_a_rate_limit_then_retries(self):
        replies = [(403, {"x-ratelimit-remaining": "0", "x-ratelimit-reset": "130"}, b'{"message":"API rate limit exceeded"}'),
                   (200, {}, b'{"ok": true}')]
        slept = []
        gh = radar.GitHub("t", transport=lambda *a: replies.pop(0), sleep=slept.append, clock=lambda: 100.0)
        self.assertEqual(gh.request("GET", "/x"), {"ok": True})
        self.assertEqual(slept, [31.0])

    def test_permission_errors_are_not_rate_limits(self):
        gh = radar.GitHub("t", transport=lambda *a: (403, {}, b'{"message":"Resource not accessible"}'),
                          sleep=lambda s: None)
        with self.assertRaises(radar.GitHubError) as caught:
            gh.request("GET", "/x")
        self.assertEqual(caught.exception.status, 403)

    def test_server_errors_retry_with_backoff(self):
        replies = [(502, {}, b""), (502, {}, b""), (200, {}, b"[]")]
        slept = []
        gh = radar.GitHub("t", transport=lambda *a: replies.pop(0), sleep=slept.append)
        self.assertEqual(gh.request("GET", "/x"), [])
        self.assertEqual(slept, [1, 2])

    def test_search_calls_are_spaced(self):
        now = [0.0]
        slept = []

        def sleep(seconds):
            slept.append(seconds)
            now[0] += seconds

        gh = radar.GitHub("t", transport=lambda *a: (200, {}, b"{}"), sleep=sleep,
                          clock=lambda: now[0], search_interval=2.0)
        gh.request("GET", "/search/repositories", search=True)
        gh.request("GET", "/search/repositories", search=True)
        gh.request("GET", "/repos/a/b")
        self.assertEqual(slept, [2.0])


class WatchTests(unittest.TestCase):
    def routes(self, commits, releases=(), tags=(), stars=10, pushed="2026-10-07T00:00:00Z"):
        info = {**repo("acme/kangaroo", stars=stars), "pushed_at": pushed}
        return {("GET", "/repos/acme/kangaroo"): info,
                ("GET", "/repos/acme/kangaroo/commits"): [
                    {"sha": sha * 40, "html_url": f"https://github.com/acme/kangaroo/commit/{sha}",
                     "commit": {"message": msg, "author": {"name": "Ada"},
                                "committer": {"date": "2026-10-07T01:02:03Z"}}}
                    for sha, msg in commits],
                ("GET", "/repos/acme/kangaroo/releases"): list(releases),
                ("GET", "/repos/acme/kangaroo/tags"): [{"name": t} for t in tags]}

    def test_first_check_records_a_cursor_and_reports_nothing(self):
        gh, _ = client(self.routes([("b", "two"), ("a", "one")], tags=["v1"]))
        cursors = {}
        report = radar.check_watched(gh, "acme/kangaroo", cursors, datetime(2026, 10, 8, tzinfo=timezone.utc), 2)
        self.assertTrue(report["first"])
        self.assertEqual((report["commits"], report["releases"], report["tags"]), ([], [], []))
        self.assertEqual(cursors["acme/kangaroo"]["head"], "b" * 40)
        self.assertEqual(cursors["acme/kangaroo"]["tags"], ["v1"])

    def test_reports_commits_releases_and_tags_since_the_cursor(self):
        now = datetime(2026, 10, 8, tzinfo=timezone.utc)
        cursors = {"acme/kangaroo": {"head": "a" * 40, "branch": "main", "stars": 7,
                                     "pushed_at": "2026-10-06T00:00:00Z", "release_ids": [1], "tags": ["v1"]}}
        release = {"id": 2, "tag_name": "v2", "name": "Two", "html_url": "https://github.com/acme/kangaroo/releases/v2",
                   "prerelease": False, "draft": False, "published_at": "2026-10-07T00:00:00Z"}
        old = {**release, "id": 1, "tag_name": "v1"}
        gh, _ = client(self.routes([("d", "four\n\nbody"), ("c", "  "), ("b", "two"), ("a", "one")],
                                   releases=[release, old], tags=["v2", "v1.5", "v1"]))
        report = radar.check_watched(gh, "acme/kangaroo", cursors, now, 2)
        self.assertEqual(report["commit_count"], 3)
        self.assertFalse(report["more_commits"])
        self.assertEqual([c["message"] for c in report["commits"]], ["four", ""])
        self.assertEqual([r["tag"] for r in report["releases"]], ["v2"])
        self.assertEqual(report["tags"], ["v1.5"])
        self.assertEqual(report["stars_delta"], 3)
        self.assertEqual(cursors["acme/kangaroo"]["release_ids"], [2, 1])

    def test_lost_cursor_is_reported_as_a_floor(self):
        cursors = {"acme/kangaroo": {"head": "z" * 40, "branch": "main", "stars": 10,
                                     "pushed_at": "2026-10-06T00:00:00Z", "release_ids": [], "tags": []}}
        gh, _ = client(self.routes([("b", "two"), ("a", "one")]))
        report = radar.check_watched(gh, "acme/kangaroo", cursors, datetime(2026, 10, 8, tzinfo=timezone.utc), 5)
        self.assertEqual((report["commit_count"], report["more_commits"]), (2, True))

    def test_unchanged_push_date_skips_commit_and_tag_calls(self):
        cursors = {"acme/kangaroo": {"head": "a" * 40, "branch": "main", "stars": 10,
                                     "pushed_at": "2026-10-07T00:00:00Z", "release_ids": [], "tags": []}}
        gh, api = client(self.routes([("a", "one")]))
        radar.check_watched(gh, "acme/kangaroo", cursors, datetime(2026, 10, 8, tzinfo=timezone.utc), 5)
        self.assertEqual([c[1] for c in api.calls], ["/repos/acme/kangaroo", "/repos/acme/kangaroo/releases"])

    def test_missing_repo_becomes_an_error_row(self):
        gh, _ = client({})
        reports = radar.check_watchlist(gh, ["gone/repo"], {"watch": {}}, datetime.now(timezone.utc), 5)
        self.assertIn("not found", reports[0]["error"])


class ArchiveTests(unittest.TestCase):
    LINES = (
        event_line("WatchEvent", "a/ecdlp-gpu", "u1"),
        event_line("WatchEvent", "a/ecdlp-gpu", "u2"),
        event_line("ForkEvent", "a/ecdlp-gpu", "u2"),
        event_line("ReleaseEvent", "a/ecdlp-gpu", payload={"action": "published", "release": {
            "tag_name": "v1", "html_url": "https://github.com/a/ecdlp-gpu/releases/tag/v1"}}),
        event_line("PushEvent", "acme/kangaroo"),
        event_line("CreateEvent", "acme/kangaroo", payload={"ref": "v9", "ref_type": "tag"}),
        event_line("PublicEvent", "b/elliptic-notes"),
        event_line("WatchEvent", "c/unrelated-web-app"),
        b'{"id":"9","type":"WatchEvent","actor":{},"repo":{"id":1,"name":"a/ecdlp-gpu"},"payload":\n',
    )

    def test_scan_counts_everything_and_aggregates_matches(self):
        matches = radar.archive_matcher(CONFIG, ["acme/Kangaroo"])
        result = radar.scan_day(date(2026, 10, 5), matches, workers=2,
                                lines_for=lambda day, hour: self.LINES if hour == 3 else [])
        self.assertEqual((result["hours_ok"], result["events"]), (24, 9))
        self.assertEqual(result["types"]["WatchEvent"], 4)
        self.assertEqual(result["types"]["malformed"], 1)
        repos = result["repos"]
        self.assertNotIn("c/unrelated-web-app", repos)
        gpu = repos["a/ecdlp-gpu"]
        self.assertEqual((gpu["stars"], gpu["forks"], gpu["actors"]), (2, 1, 3))
        self.assertEqual(gpu["releases"], [{"tag": "v1", "url": "https://github.com/a/ecdlp-gpu/releases/tag/v1"}])
        self.assertEqual((repos["acme/kangaroo"]["pushes"], repos["acme/kangaroo"]["tags"]), (1, ["v9"]))
        self.assertTrue(repos["b/elliptic-notes"]["made_public"])

    def test_names_match_as_whole_words_of_the_repo_name_only(self):
        self.assertEqual(radar.name_words("Owner/ECDLPSolver_gpu-v2.rs"), "ecdlp solver gpu v2 rs")
        matches = radar.archive_matcher(CONFIG, ["Known/Thing"])
        self.assertTrue(matches("x/PollardRho"))
        self.assertTrue(matches("known/thing"))
        self.assertFalse(matches("EllipticLabs/website"))
        self.assertFalse(matches("x/pollardish"))
        self.assertFalse(matches("me/ecdlp"))

    def test_unpublished_and_failing_hours_are_reported(self):
        def lines_for(day, hour):
            if hour == 0:
                raise urllib.error.HTTPError("u", 404, "Not Found", {}, None)
            if hour == 1:
                raise ConnectionResetError("reset")
            return []

        result = radar.scan_day(date(2026, 10, 5), lambda n: True, lines_for=lines_for)
        self.assertEqual(result["hours_ok"], 22)
        self.assertEqual(result["hours_missing"][0], "not published")
        self.assertIn("ConnectionResetError", result["hours_missing"][1])

    def test_days_to_scan_catch_up_and_stop_at_yesterday(self):
        today = date(2026, 10, 8)
        self.assertEqual(radar.archive_days({"meta": {}}, today, 3), [date(2026, 10, 7)])
        self.assertEqual(radar.archive_days({"meta": {"last_archive_day": "2026-10-07"}}, today, 3), [])
        self.assertEqual(radar.archive_days({"meta": {"last_archive_day": "2026-09-01"}}, today, 3),
                         [date(2026, 10, 5), date(2026, 10, 6), date(2026, 10, 7)])

    def test_enrich_ranks_leads_keeps_relevant_and_remembers_rejections(self):
        agg = lambda **kw: {"events": 1, "stars": 0, "forks": 0, "releases": [], "made_public": False,
                            "created": False, **kw}
        result = {"repos": {"x/elliptic-toy": agg(events=5, stars=5),
                            "y/ecdlp-new": agg(made_public=True),
                            "z/pollard-quiet": agg(events=1),
                            "w/ecdlp-gone": agg(events=9)}}
        gh, api = client({("GET", "/repos/x/elliptic-toy"): repo("x/elliptic-toy", desc="toy"),
                          ("GET", "/repos/y/ecdlp-new"): repo("y/ecdlp-new", topics=["ecdlp"])})
        state = radar.load_state(Path("/nonexistent"))
        kept = radar.enrich(gh, result, state, radar.Scorer.from_config(CONFIG), CONFIG, date(2026, 10, 8))
        self.assertEqual([c[1] for c in api.calls],
                         ["/repos/y/ecdlp-new", "/repos/x/elliptic-toy", "/repos/w/ecdlp-gone"])
        self.assertEqual([r["full_name"] for r in kept], ["y/ecdlp-new"])
        self.assertEqual(state["repos"]["y/ecdlp-new"]["sources"], ["archive"])
        self.assertEqual(set(state["rejected"]), {"x/elliptic-toy", "w/ecdlp-gone"})
        api.calls.clear()
        radar.enrich(gh, result, state, radar.Scorer.from_config(CONFIG), CONFIG, date(2026, 10, 9))
        self.assertEqual(api.calls, [])


class DigestTests(unittest.TestCase):
    def test_untrusted_text_cannot_mention_reference_or_break_tables(self):
        text = radar.md_text("ping @claude and @org/team, fixes other/repo#12 | <img src=x> [x](y)")
        self.assertNotIn("@claude", text)
        self.assertNotIn("#12", text)
        self.assertNotIn(" | ", text)
        self.assertNotRegex(text, r"(?<!\\)[<\[]")
        self.assertEqual(radar.code_text("a`b"), "`a'b`")

    def test_issue_body_is_cut_at_a_section(self):
        body = "# T\n\n## One\n" + "x" * 100 + "\n## Two\n" + "y" * 100
        cut = radar.fit_issue_body(body, "https://example/full", limit=200)
        self.assertTrue(cut.startswith("# T\n\n## One"))
        self.assertNotIn("## Two", cut)
        self.assertIn("https://example/full", cut)

    def test_opml_is_well_formed(self):
        root = ET.fromstring(radar.opml(["a/b", "c/d"]))
        urls = [o.get("xmlUrl") for o in root.iter("outline") if o.get("xmlUrl")]
        self.assertEqual(urls[:3], ["https://github.com/a/b/releases.atom",
                                    "https://github.com/a/b/commits.atom",
                                    "https://github.com/a/b/tags.atom"])
        self.assertEqual(len(urls), 6)

    def test_publish_issue_creates_label_and_closes_previous(self):
        gh, api = client({
            ("POST", "/repos/me/radar/labels"): (201, {}),
            ("GET", "/repos/me/radar/issues"): [{"number": 4}, {"number": 5, "pull_request": {}}],
            ("POST", "/repos/me/radar/issues"): (201, {"number": 9, "html_url": "https://github.com/me/radar/issues/9"}),
            ("PATCH", "/repos/me/radar/issues/4"): {},
        })
        url = radar.publish_issue(gh, "me/radar", "Radar", "body")
        self.assertEqual(url, "https://github.com/me/radar/issues/9")
        self.assertEqual([(c[0], c[1]) for c in api.calls], [
            ("GET", "/repos/me/radar/labels/repo-radar"), ("POST", "/repos/me/radar/labels"),
            ("GET", "/repos/me/radar/issues"), ("POST", "/repos/me/radar/issues"),
            ("PATCH", "/repos/me/radar/issues/4")])
        self.assertEqual(api.calls[3][3]["labels"], ["repo-radar"])


class RunTests(unittest.TestCase):
    """The daily command end to end, twice, against a fake API and archive."""

    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.config = self.dir / "radar.toml"
        self.config.write_text("""
[search]
topics = ["ecdlp"]
qualifiers = "fork:false"
[scoring]
min_score = 4
[scoring.topics]
ecdlp = 6
[scoring.terms]
'pollard' = 4
[archive]
name_pattern = 'ecdlp|pollard'
[watch]
repos = ["acme/kangaroo"]
""")
        self.today = datetime.now(timezone.utc).date()
        self.stars = {"acme/ecdlp-new": 3, "acme/kangaroo": 10}
        self.search_items = [repo("acme/ecdlp-new", topics=["ecdlp"], created=f"{self.today}T00:00:00Z")]
        self.archive = [event_line("PublicEvent", "zed/pollard-gpu"), event_line("WatchEvent", "acme/ecdlp-new")]

    def api(self):
        def info(name):
            return lambda q, b: {**repo(name, stars=self.stars.get(name, 1),
                                        desc="Pollard rho on GPUs" if "pollard" in name else ""),
                                 "pushed_at": "2026-10-07T00:00:00Z"}

        return {
            ("GET", "/search/repositories"): lambda q, b: {
                "total_count": len(self.search_items),
                "items": [{**i, "stargazers_count": self.stars.get(i["full_name"], 1)} for i in self.search_items]},
            ("GET", "/repos/acme/kangaroo"): info("acme/kangaroo"),
            ("GET", "/repos/acme/kangaroo/commits"): [{"sha": "a" * 40, "commit": {"message": "one"}}],
            ("GET", "/repos/acme/kangaroo/releases"): [],
            ("GET", "/repos/acme/kangaroo/tags"): [],
            ("GET", "/repos/zed/pollard-gpu"): info("zed/pollard-gpu"),
        }

    def run_once(self):
        gh, _ = client(self.api())
        lines_for = lambda day, hour: self.archive if hour == 0 else []
        with patch.object(radar.GitHub, "from_env", return_value=gh), \
                patch.object(radar, "archive_lines", lines_for):
            code = radar.main(["run", "--config", str(self.config), "--state-dir", str(self.dir / "state")])
        digest = (self.dir / "state" / "digests" / f"{self.today}.md").read_text()
        meta = json.loads((self.dir / "state" / "digests" / f"{self.today}.json").read_text())
        return code, digest, meta

    def test_baseline_then_only_changes(self):
        code, digest, meta = self.run_once()
        self.assertEqual(code, 0)
        self.assertTrue(meta["baseline"])
        self.assertIn("[acme/ecdlp-new](https://github.com/acme/ecdlp-new)", digest)
        self.assertIn("Now following", digest)
        self.assertIn("zed/pollard-gpu", digest)
        self.assertIn("The feed held no PushEvent, CreateEvent, ReleaseEvent", digest)
        state = json.loads((self.dir / "state" / "state.json").read_text())
        self.assertEqual(set(state["repos"]), {"acme/ecdlp-new", "zed/pollard-gpu"})
        self.assertEqual(state["meta"]["last_archive_day"], str(self.today - timedelta(days=1)))
        self.assertTrue((self.dir / "state" / "feeds.opml").exists())
        self.assertTrue((self.dir / "state" / "archive" / f"{self.today - timedelta(days=1)}.json").exists())

        self.stars["acme/ecdlp-new"] = 30
        code, digest, meta = self.run_once()
        self.assertEqual(code, 0)
        self.assertFalse(meta["baseline"])
        self.assertIn("## Rising", digest)
        self.assertIn("+27", digest)
        self.assertNotIn("Already active", digest)
        self.assertIn("Quiet: [acme/kangaroo]", digest)
        self.assertNotIn("## GH Archive", digest)  # yesterday was already scanned

    def test_quiet_day_opens_no_issue(self):
        self.run_once()
        (self.dir / "state" / "digests" / f"{self.today}.json").write_text(
            json.dumps({"items": 0, "problems": [], "baseline": False}))
        gh, api = client({})
        with patch.object(radar.GitHub, "from_env", return_value=gh):
            radar.main(["publish-issue", "--state-dir", str(self.dir / "state"), "--repo", "me/r"])
        self.assertEqual(api.calls, [])


if __name__ == "__main__":
    unittest.main()
