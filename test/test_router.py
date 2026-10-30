from app import config
from app.router import route_after_intake, route_after_review


def test_route_after_intake():
    assert route_after_intake({"missing": ["city"]}) == "ask"
    assert route_after_intake({"missing": []}) == "continue"
    print("Intake routing tests passed.")


def test_route_after_review():
    # Passing review should go to saving.
    assert route_after_review({
        "review": {"score": 1.0, "passed": True},
        "revision": 0,
    }) == "save"

    # Failed review with revisions remaining should be rewritten.
    if config.MAX_REVISIONS > 0:
        assert route_after_review({
            "review": {"score": 0.4, "passed": False},
            "revision": 0,
        }) == "rewrite"

    # A failed review at the revision limit needs manual attention.
    assert route_after_review({
        "review": {"score": 0.4, "passed": False},
        "revision": config.MAX_REVISIONS,
    }) == "manual_review"

    print("Review routing tests passed.")


if __name__ == "__main__":
    test_route_after_intake()
    test_route_after_review()
    print("All router tests passed.")