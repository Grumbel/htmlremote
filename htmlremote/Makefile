all: script.js default.css

%.js: %.ts Makefile
	tsc --removeComments\
	    --strictNullChecks \
	    --strict \
	    --alwaysStrict \
	    --forceConsistentCasingInFileNames \
	    --noImplicitReturns \
	    --noImplicitAny \
	    --noFallthroughCasesInSwitch \
	    --noEmitOnError \
	    --noImplicitThis \
	    --noUnusedLocals \
	    --noUnusedParameters \
	    --outFile $@ \
            $<

%.css: %.scss
	sass $< $@

.PHONY: all

# EOF #
