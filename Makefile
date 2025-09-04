include support/*.mk

.DEFAULT_GOAL:= all

MAKEFLAGS += --no-builtin-rules
.SUFFIXES:

.PHONY: FORCE
FORCE:

.PHONY: all
all:
	@echo Success

public:
	@mkdir -p public

.PHONY: clean
clean: ## clean built files

.PHONY: distclean
distclean: clean ## clean cache files
	@-if test -d public; then rmdir public 2>/dev/null; fi
