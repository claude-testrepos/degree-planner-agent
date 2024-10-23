import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).parent / "data" / "courses.json"


@lru_cache
def courses() -> dict[str, dict]:
    return {c["code"]: c for c in json.loads(DATA.read_text())}


def search_courses(query: str, limit: int = 8) -> list[dict]:
    q = query.lower()
    hits = [c for c in courses().values() if q in c["title"].lower() or q in c["description"].lower() or q in c["code"].lower()]
    return [{"code": c["code"], "title": c["title"], "terms": c["terms"]} for c in hits[:limit]]


def get_course(code: str) -> dict | None:
    return courses().get(code.upper())


def check_prereqs(code: str, completed: list[str]) -> dict:
    c = get_course(code)
    if not c:
        return {"error": f"unknown course {code}"}
    done = {x.upper() for x in completed}
    # prereqs are a list of alternatives groups: [["CS101"], ["MATH120", "MATH121"]]
    missing = [group for group in c["prereqs"] if not done.intersection(group)]
    return {"code": c["code"], "eligible": not missing, "missing": missing}
MAX_CREDITS = 15


def check_term_plan(codes: list[str], term: str) -> dict:
    """Validate one term: courses exist, are offered that term, and the load is reasonable."""
    problems, credits = [], 0
    for code in codes:
        c = get_course(code)
        if not c:
            problems.append(f"{code}: unknown course")
            continue
        credits += c["credits"]
        if term.lower() not in c["terms"]:
            problems.append(f"{c['code']} is not offered in {term} (only {', '.join(c['terms'])})")
    if credits > MAX_CREDITS:
        problems.append(f"{credits} credits is over the {MAX_CREDITS} credit limit")
    return {"term": term, "credits": credits, "ok": not problems, "problems": problems}
