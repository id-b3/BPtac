SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c

.PHONY: all clean

VPATH=./data/raw/
DINT=./data/interim/

# RAW Data
SPSS_FILES=1a_q_1.sav 1b_q_1.sav 1c_q_1.sav 1a_v_1.sav 2a_q_2.sav 2b_q_1.sav 2a_v_1.sav
IMA_CSV=imalife_participant_data.csv
SEG_CSV=final_bp_list.csv
VAR_FILTER=$(VPATH)variable_filter_list.txt

# Interim Data
CSV_FILES=$(patsubst %.sav,$(DINT)%.csv,$(SPSS_FILES))
SPLT_CSV=$(DINT)formatted_bp_data.csv
MRG_CSV=$(DINT)data_merged.csv
BP_FILT_CSV=$(DINT)bp_db_filtered.csv
BP_ALL_CSV=$(DINT)bp_db_all.csv

# Lists of Variables
BP_COLS=bp_wap,bp_la,bp_wt,bp_ir,bp_or
# Convert the list of variables in the variable_filter_list.txt file into a string
DB_COLS := $(shell cat $(VAR_FILTER) | tr '\n' ',' | sed 's/,$$//')

all: $(BP_FINAL)
	echo "Done"

$(BP_FINAL): $(BP_FILT_CSV)
	< $< ./src/data/fill_and_merge.py
	< $(BP_ALL_CSV) ./src/data/filter_dataset.py

$(BP_FILT_CSV): $(MRG_CSV)
	< $< csvcut -c $(DB_COLS) > $@

# Merge all CSV files into one using the patientID as an index
$(MRG_CSV): $(SPLT_CSV) $(CSV_FILES) $(IMA_CSV)
	csvjoin --left -c patientID $^ > $@

# Expand the semicolon delim'd bps and change participant_id to patientID
$(SPLT_CSV): $(SEG_CSV)
	csvjoin <(csvcut -C $(BP_COLS) $< | sed 's/participant_id/patientID/') <(csvcut -c $(BP_COLS) $< | awk -f ./src/data/expand_bps.awk) > $@

# Convert the SPSS files into CSV files
$(CSV_FILES): $(DINT)%.csv : %.sav
	pspp-convert $< $@_nonan.csv
	# Replace $$5, $$6, $$7 with nan
	sed 's/\$$[0-9]//g' $@_nonan.csv | csvsort -c patientID > $@
