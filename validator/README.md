This validator is a "linter" for the issues contained in this repository.
It ensures that each issue follows a standard format.


## Acknowledgement

This validator is inspired by / reused from the <https://github.com/2i2c-org/initiatives> project.


## Changes

* Project structure & metadata
    * Add `pyproject.toml`
    * Move dependencies from `requirements.txt` -> `pyproject.toml`
    * Remove `main.py`
    * Add `__main__.py` as entrypoint
* Refactors
    * Extract repo owner/name constants
    * Remove support for full issue URL -- we only care about this repo.
    * Validators return `None` instead of `True` when no errors found
    * Replace `for`/`else` pattern (I see this very rarely in the wild)
    * Refactor to avoid early failure and report generation of all issues
* User-specific needs
    * Replace `2i2c` refs with `geojupyter`
    * Required header adjustments
* Features
    * Print message when skipping closed issues
    * Add emoji icons to messages
    * Post validation report to issue as one comment that gets updated with each run
    * Use a single label for validation failure instead of issue-specific labels
* Minutia
    * Add typing information
    * Comment adjustments
    * Formatting adjustments
    * Name adjustments
    * Message adjustments
