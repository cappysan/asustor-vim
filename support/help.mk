# Show help
.PHONY: help
help:
	@echo "Available targets:"
	@grep -h '^[a-z].*:.*##' $(MAKEFILE_LIST) | sort | sed 's/\([a-z][a-z]*\)[^:]*:/\1:/' | awk -F ':.*?## ' 'NF==2 {printf "  %-26s%s\n", $$1, $$2}' | sort | uniq --check-chars=20
	@echo "Available variables:"
	@grep -h '^[A-Z].*=.*##' $(MAKEFILE_LIST) | sort | sed 's/\([A-Z][A-Z]*\)[^=]*=/\1=/' | awk -F '=.*?## ' 'NF==2 {printf "  %-26s%s\n", $$1, $$2}' | sort | uniq --check-chars=20
