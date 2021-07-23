export DJANGO_SETTINGS_MODULE?=wcivf.settings

.PHONY: all
make all: build clean

.PHONY: build
build:
	sam build --use-container -t ./sam-template.yaml

.PHONY: clean
clean: ## Delete any generated static asset or req.txt files and git-restore the rendered API documentation file
	rm -rf .aws-sam/build/WCIVFControllerFunction/wcivf/static/booklets/
	rm -rf .aws-sam/build/WCIVFControllerFunction/wcivf/assets/booklets/
	rm -rf .aws-sam/build/WCIVFControllerFunction/wcivf/media/
	rm -f .aws-sam/build/WCIVFControllerFunction/wcivf/settings/local.py

.PHONY: lambda-migrate
lambda-migrate:
	aws lambda invoke \
	--function-name wcivf-dev-WCIVFControllerFunction-Wxf2rcMohMmQ \
	--payload '{ "command": "migrate" }' \
	--cli-binary-format raw-in-base64-out \
	tmp/lambda-log.json
