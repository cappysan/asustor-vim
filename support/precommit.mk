# Run precommit
PRECOMMITFLAGS ?=

.PHONY: all
all: precommit

.PHONY: precommit pre-commit pc
precommit pre-commit pc: .pre-commit-config.yaml ## run pre-commit on all files
	pre-commit run -a $(PRECOMMITFLAGS)

.pre-commit-config.yaml:
