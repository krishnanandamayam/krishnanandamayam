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

## The edit server's state is the agent's to maintain

The editor (`uv run python -m tools.serve`, http://localhost:8000/edit) must be running whenever
the user is working with the agent.

- Start it at the beginning of a session if it is not running, and check it (for example
  `curl http://localhost:8000/edit`) after anything that could have stopped it or broken
  the data it reads: a pull, merge or conflict, a code change, or a long gap.
- If it has stopped, restart it without being asked, and tell the user when you did.
- Run it with `run_in_background` and the longest `timeout` (7200000 ms). When that limit
  stops it, restart it; the user does not have to.
- If a merge or pull leaves `data/grantha.yaml` invalid, the grantha rule above still applies:
  do not resolve it to get the server working. Stop a server you started (or warn the user if
  they started it), ask about each conflict, and restart the server once the file parses.
  Until then every editor request, including Save, fails.
- Before a pull or merge, check whether `data/grantha.yaml` could conflict (for example
  `git diff HEAD...origin/main -- data/grantha.yaml`) and tell the user first.
- Do not stop a server the user started themselves.
