.PHONY: database dev release test


GREEN_START=\033[92m
GREEN_END=\033[0m

CYAN_START=\033[36m
CYAN_END=\033[0m

GOLD_START=\033[33m
GOLD_END=\033[0m

YELLOW_START=\033[93m
YELLOW_END=\033[0m

MAGENTA_START=\033[35m

MAGENTA_END=\033[0m


database:
	dropdb geography --if-exists
	createdb geography

dev:
	gulp --cwd geography/staticapp/

release:
	@echo ""
	@echo "$(CYAN_START)Removing any existing distributions.$(CYAN_END)"
	@echo "    $(GOLD_START)>>> rm -rf dist/$(GOLD_END)"
	@rm -rf dist/
	@echo "$(GREEN_START)Done.$(GREEN_END)"
	@echo ""
	@$(eval current_version=`python setup.py --version`)
	@echo "$(CYAN_START)Creating source and binary distributions for version '$(current_version)'.$(CYAN_END)"
	@echo "    $(GOLD_START)>>> python setup.py sdist bdist_wheel --quiet$(GOLD_END)"
	@python setup.py --quiet sdist
	@python setup.py --quiet bdist_wheel
	@echo "$(GREEN_START)Done.$(GREEN_END)"
	@echo ""
	@echo "$(CYAN_START)Uploading distributions for version '$(current_version)'.$(CYAN_END)"
	@echo "    $(GOLD_START)>>> twine upload dist/*  --skip-existing$(GOLD_END)"
	twine upload dist/*  --skip-existing
	@echo "$(GREEN_START)Done.$(GREEN_END)"
	@echo ""
	@echo ""
	@echo "☑️  $(MAGENTA_START)All finished up!$(MAGENTA_END)"
	@echo ""

test:
	pytest -v
