.PHONY: clean data requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = BPAnalysis
PYTHON_INTERPRETER = python3

ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif

# Paths
DPRC:=./data/processed/
# Processed Data
BP_FINAL:=$(DPRC)final_bp_db.csv
BP_HEALTHY:=$(DPRC)healthy_bp_db.csv
BP_DISEASED:=$(DPRC)diseased_bp_db.csv

# Study target
HEALTH_STATUS ?= "healthy"
NORMALISE_DATA ?= false
GROUP_BY ?= "smoking_status"

# Params to analyse
PARAMS:=tac
PYTHONPATH=$(CURDIR)

# Report Path
REPORTS:=./reports/

export PYTHONPATH
export DPRC BP_FINAL PARAMS STUDY_HEALTHY

#################################################################################
# FLAGS                                                                         #
#################################################################################
ifeq ($(NORMALISE_DATA),true)
	NORMALISE_FLAG=--normalise
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements: test_environment
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Make Dataset
data: ; $(MAKE) -f ./src/data/make_data.mk -C $(PROJECT_DIR)

run_study: data_describe data_visualise data_analyse data_model

## Summary of every variable in the dataset
data_describe: ; ./src/analyse.py $(BP_FINAL) $(REPORTS) --health_stat $(HEALTH_STATUS) $(NORMALISE_FLAG) --param_list $(PARAMS) --to_run descriptive --group_by $(GROUP_BY)

## Create Figures
data_visualise: ; ./src/analyse.py $(BP_FINAL) $(REPORTS) --health_stat $(HEALTH_STATUS) $(NORMALISE_FLAG) --param_list $(PARAMS) --to_run visualisation --group_by $(GROUP_BY)

## Run the comparative analysis
data_analyse: ; ./src/analyse.py $(BP_FINAL) $(REPORTS) --health_stat $(HEALTH_STATUS) $(NORMALISE_FLAG) --param_list $(PARAMS) --to_run comparative --group_by $(GROUP_BY)

## Build and evaluate models
data_model: ; ./src/analyse.py $(BP_FINAL) $(REPORTS) --health_stat $(HEALTH_STATUS) $(NORMALISE_FLAG) --param_list $(PARAMS) --to_run regression clustering --group_by $(GROUP_BY)

## Test the variables for normality
test_norm: ; $(MAKE) -f ./src/features/test_norm.mk -C $(PROJECT_DIR)

## Delete all compiled Python files
clean_data:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf ./data/interim/*
	rm -rf ./data/processed/*

clean_reports:
	rm -rf ./reports/*

## Test python environment is setup correctly
test_environment:
	$(PYTHON_INTERPRETER) test_environment.py

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
