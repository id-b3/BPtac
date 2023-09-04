SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: all clean

comma:=,
P_LIST := $(subst $(comma), , $(PARAMS)) pack_years
# CONDA_ACTIVATE=source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

all: hist

hist: $(BP_FINAL)
	# $(CONDA_ACTIVATE) stats
	for col in $(P_LIST); do \
		echo $$col
		csvcut -c "$$col,sex,GOLD_stage,copd_diagnosis,asthma_diagnosis,cancer_type" $< | python ./src/features/descriptive/test_normality.py ; \
	done
