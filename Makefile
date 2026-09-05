# Our Bubble — the whole repository in five verbs.

.PHONY: check record figures build serve clean notes

## check — tier 0: fetch the record, verify the edition against it, build, verify the built pages.
check:
	@tools/check.sh

## record — re-derive the committed record/ snapshot from the pinned commit (needs engine access).
## This is step 2+3 of a record bump; see record.lock's header.
record:
	@tools/fetch_record.sh
	@tools/snapshot_record.sh

## figures — redraw the chapters' data-true figures from the demo code that draws them on screen.
## Tier 0 refuses a committed figure that is not what this emits, so a drawing change lands here in
## the same commit or it does not land. Needs node.
figures:
	@node tools/figures.mjs

## build — regenerate the appendix from the record and render the book into book/.
build:
	@mdbook build

## serve — build and watch, on http://localhost:3000.
serve:
	@mdbook serve --open

## notes — list the reading notes still open in the prose, as file:line.
##
## A reader leaves a note in the text where the trouble is, as `<!-- NOTE(name): … -->`. The comment
## is invisible in the rendered book, which is the point and also the risk: left alone it is invisible
## to everyone. This makes the open ones countable, so "all the notes are addressed" is something you
## can check rather than something you remember. Resolving one means deleting it in the same commit
## that fixes what it points at, so the diff shows the answer replacing the question.
notes:
	@grep -rn '<!-- *NOTE(' chapters/ *.md 2>/dev/null \
	  | sed -e 's/:[[:space:]]*<!-- *NOTE(/  ← [/' -e 's/)[[:space:]]*:[[:space:]]*/] /' \
	        -e 's/[[:space:]]*-->[[:space:]]*$$//' -e 's/[[:space:]][[:space:]]*/ /g' \
	  || true
	@printf '\n%s open note(s).\n' \
	  "$$(grep -rc '<!-- *NOTE(' chapters/ *.md 2>/dev/null \
	     | awk -F: '{n += $$NF} END {print n + 0}')"

## clean — drop the rendered book and the fetched record.
clean:
	@rm -rf book .record
	@echo "removed book/ and .record/"
