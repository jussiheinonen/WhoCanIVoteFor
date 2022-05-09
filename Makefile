export DJANGO_SETTINGS_MODULE?=wcivf.settings.lambda
export DC_ENVIRONMENT?=development
export AWS_DEFAULT_REGION?=eu-west-2

.PHONY: all
make all: build clean

.PHONY: build
build:
	sam build -t ./sam-template.yaml

.PHONY: clean
clean: ## Delete any unneeded static asset files and git-restore the rendered API documentation file
	rm -rf .aws-sam/build/WCIVFControllerFunction/wcivf/static/booklets/
	rm -rf .aws-sam/build/WCIVFControllerFunction/wcivf/assets/booklets/
	rm -rf .aws-sam/build/WCIVFControllerFunction/wcivf/assets/images/
	rm -rf .aws-sam/build/WCIVFControllerFunction/wcivf/static/images/
	rm -rf .aws-sam/build/WCIVFControllerFunction/wcivf/media/
	rm -rf .aws-sam/build/WCIVFControllerFunction/docs/
	rm -f .aws-sam/build/WCIVFControllerFunction/wcivf/settings/local.py
	rm -f .aws-sam/build/WCIVFControllerFunction/results_app.dot
	rm -f .aws-sam/build/WCIVFControllerFunction/results_app.png
	rm -f .aws-sam/build/WCIVFControllerFunction/transifex.yml
	rm -f .aws-sam/build/WCIVFControllerFunction/local.example

.PHONY: lambda-migrate
lambda-migrate:  ## Invoke lambda to migrate the database
	aws lambda invoke \
	--function-name WCIVFControllerFunction \
	--payload '{ "command": "migrate" }' \
	/dev/stdout
