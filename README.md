# Multilingual factuality

This repository is used to build a multi-lingual system for identifying the factuality of events.
We are currently working on a basic implementation for Dutch and English.


## Running the module

The scripts to run the module are located at feature_extractor/

1. On a single file:

cat inputfile | python rule_based_factuality.py > outputfile


2. For a directory:

./run_rule_based_on_dir.sh inputdir/ outputdir/ 

## Version:

Version 0.01 is released on May 9th 2016. It is a basic implementation and first creation of resources based on intuition.
We expect to have many minor revisions in the near future. You will therefore find some version 0.xx in the document.


As soon as the resources for at least one language and the rule application system have stabilized, we will release version 1.0


## Content

This repository consists of:

docs/ for documentation
data/ for development and training data 
resources/ for language specific resources (vocabularies) and models
scripts/ for code extracting input features, applying rules/calling machine learning modules and producing output.

## Evaluation/experimental setup:

please check out: https://github.com/cltl/factuality_experimental_environment

For gold data, input data and evaluation scripts for factuality.


## Contact

Antske Fokkens: antske.fokkens@vu.nl
Ruben Izquierdo: ruben.izquierdobevia@vu.nl
Roser Morante: r.morantevallejo@vu.nl
Tommaso Caselli: t.caselli@vu.nl
