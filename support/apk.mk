.PHONY: all apk

all: apk

apk: ## build the apk package
	bin/apkg-tools_py3.py create apk --destination .
