"""A DELIBERATE failure, seeded to prove the nightly's owner-issue write path.

The reusable nightly (`unified-systems-com/tap` `plugin-nightly.yml`) files one issue when the
`main` row goes red, comments on it while it stays red, and closes it on the next green. None of
those three writes had ever executed — every run to date was green, which exercises only the
branch that does nothing.

A green run cannot prove a write path. So this file makes the suite fail on purpose, once, so the
filing and closing can be watched happening. It is removed in the next commit on this branch; if
you are reading it on any branch other than `ci/inherit-the-nightly`, or after 2026-09-26, it
escaped and should be deleted.
"""

from __future__ import annotations


def test_seeded_failure_to_exercise_the_owner_issue_write_path() -> None:
    assert False, (
        "seeded on purpose — proving the nightly files an owner issue on a red main row. "
        "Remove this file once the close path has also been observed."
    )
