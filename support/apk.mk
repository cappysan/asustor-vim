.PHONY: all apk

all: apk

apk: ## build the apk package
	fakeroot bin/apkg.py create apk --destination .
