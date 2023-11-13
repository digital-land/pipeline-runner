.PHONY: \
	transformed\
	dataset\
	commit-dataset


ifeq ($(COLLECTION_DIR),)
COLLECTION_DIR=collection/
endif

# collected resources
ifeq ($(RESOURCE_DIR),)
RESOURCE_DIR=$(COLLECTION_DIR)resource/
endif

ifeq ($(RESOURCE_FILES),)
RESOURCE_FILES:=$(wildcard $(RESOURCE_DIR)*)
endif

ifeq ($(FIXED_DIR),)
FIXED_DIR=fixed/
endif

ifeq ($(CACHE_DIR),)
CACHE_DIR=var/cache/
endif

ifeq ($(TRANSFORMED_DIR),)
TRANSFORMED_DIR=transformed/
endif

ifeq ($(ISSUE_DIR),)
ISSUE_DIR=issue/
endif

ifeq ($(COLUMN_FIELD_DIR),)
COLUMN_FIELD_DIR=var/column-field/
endif

ifeq ($(DATASET_RESOURCE_DIR),)
DATASET_RESOURCE_DIR=var/dataset-resource/
endif

ifeq ($(DATASET_DIR),)
DATASET_DIR=dataset/
endif

ifeq ($(FLATTENED_DIR),)
FLATTENED_DIR=flattened/
endif

ifeq ($(DATASET_DIRS),)
DATASET_DIRS=\
	$(TRANSFORMED_DIR)\
	$(COLUMN_FIELD_DIR)\
	$(DATASET_RESOURCE_DIR)\
	$(ISSUE_DIR)\
	$(DATASET_DIR)\
	$(FLATTENED_DIR)
endif

ifeq ($(EXPECTATION_DIR),)
EXPECTATION_DIR = expectations/
endif

define run-pipeline
	mkdir -p $(@D) $(ISSUE_DIR)$(notdir $(@D)) $(COLUMN_FIELD_DIR)$(notdir $(@D)) $(DATASET_RESOURCE_DIR)$(notdir $(@D))
	digital-land --dataset $(notdir $(@D)) $(DIGITAL_LAND_FLAGS) pipeline $(1) --issue-dir $(ISSUE_DIR)$(notdir $(@D)) --column-field-dir $(COLUMN_FIELD_DIR)$(notdir $(@D)) --dataset-resource-dir $(DATASET_RESOURCE_DIR)$(notdir $(@D)) $(PIPELINE_FLAGS) $< $@
endef

define build-dataset =
	mkdir -p $(@D)
	time digital-land --dataset $(notdir $(basename $@)) dataset-create --output-path $(basename $@).sqlite3 $(^)
	time datasette inspect $(basename $@).sqlite3 --inspect-file=$(basename $@).sqlite3.json
	time digital-land --dataset $(notdir $(basename $@)) dataset-entries $(basename $@).sqlite3 $@
	mkdir -p $(FLATTENED_DIR)
	time digital-land --dataset $(notdir $(basename $@)) dataset-entries-flattened $@ $(FLATTENED_DIR)
	md5sum $@ $(basename $@).sqlite3
	csvstack $(ISSUE_DIR)$(notdir $(basename $@))/*.csv > $(basename $@)-issue.csv
	mkdir -p $(EXPECTATION_DIR)
	time digital-land expectations --results-path "$(EXPECTATION_DIR)$(notdir $(basename $@)).csv" --sqlite-dataset-path "$(basename $@).sqlite3" --data-quality-yaml "$(EXPECTATION_DIR)$(notdir $(basename $@)).yaml"
endef

-include collection/pipeline.mk

# restart the make process to pick-up collected resource files
second-pass::
	@$(MAKE) --no-print-directory transformed dataset

GDAL := $(shell command -v ogr2ogr 2> /dev/null)
UNAME := $(shell uname)

init::
	pip install csvkit
ifndef GDAL
ifeq ($(UNAME),Darwin)
	$(error GDAL tools not found in PATH)
endif
	sudo apt-get update
	sudo apt-get install gdal-bin
endif
	pyproj sync --file uk_os_OSTN15_NTv2_OSGBtoETRS.tif -v
ifeq ($(UNAME),Linux)
	dpkg-query -W libsqlite3-mod-spatialite >/dev/null 2>&1 || sudo apt-get install libsqlite3-mod-spatialite
endif

clobber::
	rm -rf $(DATASET_DIRS)

clean::
	rm -rf ./var

# local copy of the organisation dataset
init::	$(CACHE_DIR)organisation.csv

makerules::
	curl -qfsL '$(SOURCE_URL)/makerules/main/pipeline.mk' > makerules/pipeline.mk


# convert an individual resource
# .. this assumes conversion is the same for every dataset, but it may not be soon
var/converted/%.csv: collection/resource/%
	mkdir -p var/converted/
	digital-land convert $<
