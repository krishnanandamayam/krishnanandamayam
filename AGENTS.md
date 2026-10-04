# Rules for agents working in this repository

## `data/grantha.yaml` is the author's text: ask before every change

`data/grantha.yaml` is the ground truth of the grantha. Do not change it on your own judgement.

- Ask the user about **each** change to `data/grantha.yaml` before making it, showing the
  before and after text and the verse it belongs to. One approval covers one change; it does
  not extend to other verses or to similar-looking cases.
- When a `git pull`, merge, rebase or stash leaves a conflict in `data/grantha.yaml`, do not
  pick a side yourself. Show each conflicting change (verse, theirs, ours) and ask which to
  keep.
- Changes to code, tests and styles do not need this; resolve those conflicts normally and
  run `uv run pytest`.
