This directory contains the development data used for creating the module.
For evaluation data, see the evaluation package at: https://github.com/cltl/factuality_experimental_environment


STRUCTURE:

dev/ for development data (most data)
dev/language development data for a specific language
dev/language/hand-made handmade examples for a specific language

CONTENT:
dev/language/hand-made/for_features_first_example in dev/language/hand-made:

Basic examples used to illustrate what information needs to be extracted for a given target event. 

It consist of 2 files:

for_features_first_example_naf_raw.naf : raw text in NAF; can be used as input for NWR pipeline.
for_features_first_examples_nwrv3_out.naf : output of NewsReader pipeline version 3 for raw text input.
