# Our Bubble — the whole repository in four verbs.

.PHONY: check record build serve clean

## check — tier 0: fetch the record, verify the edition against it, build, verify the built pages.
check:
	@tools/check.sh

## record — check the pinned UniForge commit out into .record/ (see record.lock).
record:
	@tools/fetch_record.sh

## build — regenerate the appendix from the record and render the book into book/.
build:
	@mdbook build

## serve — build and watch, on http://localhost:3000.
serve:
	@mdbook serve --open

## clean — drop the rendered book and the fetched record.
clean:
	@rm -rf book .record
	@echo "removed book/ and .record/"
