"""The trivial test that proves CI runs at all.

Commit this before there is anything real to test, then break it on purpose once
and watch the workflow turn red. Seeing it fail is what makes it trustworthy.
"""


def test_ci_is_wired_up():
    assert True
