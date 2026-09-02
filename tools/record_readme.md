# The record snapshot

**A verbatim copy of the files this book cites, taken from the UniForge engine at the commit
[`record.lock`](../record.lock) pins.** Nothing here was written for the book. Every file is the
engine's own bytes at that commit.

> **Scope.** This is the record of a **toy**: a small world built inside a computer. Nothing in it is
> a claim about nature. Words such as *vacuum*, *photon* and *light cone* name patterns in the model.
> See the book's [`FIREWALL.md`](../FIREWALL.md).

## Why it is here

The engine repository is private and stays that way. Without this directory, a reader on the
published site could see *which file* every number came from and never open it — the book would be
asking for trust exactly where it promises evidence. So the cited files travel with the book:
the registered lab entries (`spec.md`, `eval.md`, `PROVENANCE.md` and their data), the gates that
re-run each experiment, the data-true figures, and the standards the appendix rests on.

## What is verbatim and what is not

**Verbatim:** every path listed in `record.lock`. Those are the bytes the checker verifies
quotations against, and — whenever the engine is reachable — the bytes it diffs against the real
repository to prove this copy has not drifted.

**Generated:** the `.html` pages beside the Markdown files, and the `index.html` in each lab-entry
folder. They exist only so the links resolve on the published site, and they show the file's own
bytes rather than reinterpreting them. `.snapshot-sha` records the commit. None of it is record.

## How it is refreshed

Never by hand. It is derived from a checkout of the pinned commit, and refreshing it *is* bumping
the record:

```sh
# 1. edit record.lock's `sha`
tools/fetch_record.sh        # 2. check the new commit out into .record/
tools/snapshot_record.sh     # 3. re-derive this directory from it
python3 check_edition.py     # 4. quotations re-verified; drift reported byte for byte
```

All four land in one commit. See `record.lock`'s header.
