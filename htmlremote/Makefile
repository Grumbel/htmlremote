all: script.js

%.js: %.ts
	tsc --strictNullChecks \
	    --outFile $@ \
            $<

.PHONY: all

# EOF #
