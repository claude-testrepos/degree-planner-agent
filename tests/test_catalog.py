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
