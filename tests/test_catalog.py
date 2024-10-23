from planner import catalog


def test_prereqs_missing():
    r = catalog.check_prereqs("CS301", ["CS101"])
    assert not r["eligible"]
    assert ["CS201"] in r["missing"]


def test_prereqs_alternatives():
    r = catalog.check_prereqs("CS370", ["CS101", "CS201", "STAT230"])
    assert r["eligible"]


def test_search():
    codes = [c["code"] for c in catalog.search_courses("learning")]
    assert "CS370" in codes


def test_unknown_course():
    assert "error" in catalog.check_prereqs("CS999", [])
def test_term_plan_offering():
    r = catalog.check_term_plan(["CS301", "CS340"], "fall")
    assert not r["ok"]
    assert any("CS340" in p for p in r["problems"])


def test_term_plan_credit_limit():
    r = catalog.check_term_plan(["CS101", "MATH220", "MATH240", "STAT230", "CS201", "CS370"], "fall")
    assert r["credits"] == 18
    assert not r["ok"]
