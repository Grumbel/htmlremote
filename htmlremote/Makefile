all: script.js default.css

%.js: %.ts
	tsc --strictNullChecks \
	    --outFile $@ \
            $<

%.css: %.scss
	sass $< $@

.PHONY: all

# EOF #
