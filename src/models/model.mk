SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: all clean

REPPATH=./reports/models/

ifeq ($(STUDY_HEALTHY),true)
	H_FLAG = --healthy
endif

all: $(SEX) MLR

MLR: $(BP_FINAL)
	mkdir -p $(REPPATH)
	./src/models/relational/multivariate_regression.py $< $(PARAMS) $(REPPATH) $(H_FLAG)
