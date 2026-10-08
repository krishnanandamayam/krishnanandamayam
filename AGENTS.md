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

## The agent does not suggest verse edits

What a verse, header or meaning should say is the human user's decision alone.

- Do not propose changes to the content of `data/grantha.yaml` (`hk`, `title`, `en`, `te`,
  preface text): no corrections, rewordings, word splits, restorations of earlier text, or
  offers to "fix" or "put back" something.
- Reporting facts is fine and expected: what a check or the lint found, which field is empty,
  what a pull changed, what conflicts. State the fact and stop there; do not add what the text
  ought to be.
- Make a content change only when the user states the change themselves.

## The edit server's state is the agent's to maintain

The editor (`uv run python -m tools.serve`, http://localhost:8000/edit) must be running whenever
the user is working with the agent.

- Start it at the beginning of a session if it is not running, and check it (for example
  `curl http://localhost:8000/edit`) after anything that could have stopped it or broken
  the data it reads: a pull, merge or conflict, a code change, or a long gap.
- If it has stopped, restart it without being asked, and tell the user when you did.
- Run it with `run_in_background`. On Windows the agent's tooling stops a background command
  after the longest `timeout` it accepts (7200000 ms), so there the server stops 2 hours after
  it was started: pass that timeout, restart it whenever the user asks or whenever you notice it
  has stopped, and do not promise it stays up. On other systems (macOS, Linux) there is no such
  cap. A server the user runs in their own terminal has no cap either, so suggest that when
  they will be editing for long.
- If a merge or pull leaves `data/grantha.yaml` invalid, the grantha rule above still applies:
  do not resolve it to get the server working. Leave the server running: the editor shows a
  banner naming the conflict (line and verse) and refuses to load or save until the file
  parses, so the user can see why and come back. Ask about each conflict, then reload.
- Restart the server after every pull (and merge, rebase or reset to another commit) that
  changes anything: Python code is loaded once at startup, so a running server keeps serving
  the old code. Stop a server you started, start it again, and check it answers. If the user
  started it, ask them to restart it.
- Before a pull or merge, check whether `data/grantha.yaml` could conflict (for example
  `git diff HEAD...origin/main -- data/grantha.yaml`) and tell the user first.
- Do not stop a server the user started themselves.

## Commits are atomic

Commit each change on its own: one logical change per commit, with a message that says what
and why. Do not bundle unrelated changes (a code fix, a rule in this file, the author's edits
to `data/grantha.yaml`) into one commit, and stage files by name rather than with `git add -A`
so that someone else's uncommitted work is not swept in. When one file holds two independent
changes, commit the first before making the second.

## Commit messages say what changed and why

A commit message must tell a reader who has not seen the diff what changed and why.

- First line: a short summary of the change itself, naming what was touched (`Telugu meanings:
  fill empty entries, rewrite 16`), not a generic label such as "update" or "edit text".
- Body, when the change is more than a line or two: what changed and where (files, verse or
  entry ids, counts), the reason, and anything surprising or unfinished that a reviewer should
  check.
- Describe the change that was made. Do not claim more than the diff shows, and say so when
  something in it looks unintended.

## Commits to `data/grantha.yaml` name the verses

A commit message for a change to `data/grantha.yaml` lists the verse numbers it touches, so the
history can be read without opening the diff.

- Use the verse numbers (`no`), as ranges where they are consecutive: `v10-v25`. Give sections
  and prefaces by their id (`s01`, a preface block id).
- Say which field changed in each (`hk`, `en`, `te`, `title`) and whether it was filled in,
  rewritten or emptied.
- Work the list out from the diff itself (compare the old and new file), not from memory of
  the session.
