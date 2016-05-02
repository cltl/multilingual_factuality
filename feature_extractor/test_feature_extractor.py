#!/usr/bin/env python

from KafNafParserPy import KafNafParser
from my_feature_extractor import FeatureExtractor

en_file = './for_features_first_examples_nwrv3_out.en.naf'
en_kaf_naf_obj = KafNafParser(en_file)
my_feat_extractor_en = FeatureExtractor(en_kaf_naf_obj)


nl_file = './for_features_first_examples_nwrv3_out.nl.naf'
nl_kaf_naf_obj = KafNafParser(nl_file)
my_feat_extractor_nl = FeatureExtractor(nl_kaf_naf_obj)




###### <EXAMPLE_1>
for coref in my_feat_extractor_en.get_corefs(this_type='event'):
    print('English event coref id: %s' % coref.get_id())
    for n, list_term_id in enumerate(my_feat_extractor_en.get_span_ids_for_coref(coref)):
        print('\t %d --> %s ' % (n, list_term_id))

for coref in my_feat_extractor_nl.get_corefs(this_type='event'):
    print('Dutch event coref id: %s' % coref.get_id())
    for n, list_term_id in enumerate(my_feat_extractor_nl.get_span_ids_for_coref(coref)):
        print('\t %d --> %s ' % (n, list_term_id))
###### </EXAMPLE_1>




###### <EXAMPLE_2>
lemma_en = my_feat_extractor_en.get_lemma_for_term_id('t2')
lemma_nl = my_feat_extractor_nl.get_lemma_for_term_id('t_241')

print('\n')
print('English lemma for t2: %s' % lemma_en)
print('Dutch lemma for t_241: %s' % lemma_nl)

###### <EXAMPLE_2>




###### <EXAMPLE_3>
morphofeat_en = my_feat_extractor_en.get_morphofeat_for_term_id('t2')
morphofeat_nl = my_feat_extractor_nl.get_morphofeat_for_term_id('t_241')

print('\n')
print('English morphofeat for t2: %s' % morphofeat_en)
print('dutch morphofeat for t_241: %s' % morphofeat_nl)
###### </EXAMPLE_3>




###### <EXAMPLE_4>
print('\n')

for term_id in ['t12','t82','t108']:
    for dependency, modifier in my_feat_extractor_en.get_dependencies_and_modifier(term_id):
        print('English term %s: Dep: %s Modifier: %s' % (term_id, dependency, modifier))

print('\n')

for term_id in ['t_13','t_75','t_85']:
    for dependency, modifier in my_feat_extractor_nl.get_dependencies_and_modifier(term_id):
        print('Dutch term %s: Dep: %s Modifier: %s' % (term_id, dependency, modifier))
###### </EXAMPLE_4>

print('\n')




###### <EXAMPLE_5>

for term_id in ['t36', 't89', 't150', 't61','t193','t265']:
    print('English, term %s' % term_id)
    ids_path = my_feat_extractor_en.get_list_term_ids_to_root(term_id)
    lemmas_to_root = my_feat_extractor_en.get_lemmas_for_list_term_ids(ids_path)
    morpho_to_root = my_feat_extractor_en.get_morphofeat_for_list_term_ids(ids_path)
    modifiers_to_root = my_feat_extractor_en.get_modifiers_list_term_ids(ids_path)
    
    print('\tPath of term ids to the root: %s' % ids_path)
    print('\tLemmas to the root: %s' % lemmas_to_root)
    print('\tMorphofeat list to the root: %s' % morpho_to_root)
    print('\tDeps and Modifiers to root: %s' % modifiers_to_root)
    
for term_id in ['t_22','t_80', 't_132', 't_109', 't_140']:
    print('Dutch, term %s' % term_id)
    ids_path = my_feat_extractor_nl.get_list_term_ids_to_root(term_id)
    lemmas_to_root = my_feat_extractor_nl.get_lemmas_for_list_term_ids(ids_path)
    morpho_to_root = my_feat_extractor_nl.get_morphofeat_for_list_term_ids(ids_path)
    modifiers_to_root = my_feat_extractor_nl.get_modifiers_list_term_ids(ids_path)

    
    print('\tPath of term ids to the root: %s' % ids_path)
    print('\tLemmas to the root: %s' % lemmas_to_root)
    print('\tMorphofeat list to the root: %s' % morpho_to_root)
    print('\tDeps and Modifiers to root: %s' % modifiers_to_root)

###### </EXAMPLE_5>




print('\n')

###### <EXAMPLE_6>

for term_id in ['t337','t364', 't374','t383','t392','t401']:
    print('English term %s' % term_id)
    component_ids = my_feat_extractor_en.get_argument_components_of_target_verb_as_list_of_ids(term_id)
    
    print('\tArgument component ids of target verb')
    for cid in component_ids:
        lemmas_for_component = my_feat_extractor_en.get_lemmas_for_list_term_ids(cid)
        print('\t\t%s  Lemmas: %s' % (cid,lemmas_for_component))

for term_id in ['t_353','t_394', 't_409','t_413','t_423']:
    print('Dutch term %s' % term_id)
    component_ids = my_feat_extractor_nl.get_argument_components_of_target_verb_as_list_of_ids(term_id)
    
    print('\tArgument component ids of target verb')
    for cid in component_ids:
        lemmas_for_component = my_feat_extractor_nl.get_lemmas_for_list_term_ids(cid)
        print('\t\t%s  Lemmas: %s' % (cid,lemmas_for_component))###### </EXAMPLE_6>

