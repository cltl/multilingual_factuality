import sys
import os
from KafNafParserPy import KafNafParser
from my_feature_extractor import FeatureExtractor


class EventFeatures:
    
    def __init__(self, targetSpan = []):
        
        self.targetSpan = targetSpan
        self.target_lemmas = []
        self.target_morphofeats = []
        self.target_mods = []
        self.predicate_chain_ids = []
        self.predicate_chain_lemmas = []
        self.predicate_chain_morphofeats = []
        self.predicate_chain_mods = []
        self.argument_ids = []
        self.argument_lemmas = []
        
    #FIXME: WRITE FUNCTIONS TO ADD FEATURES. THESE FUNCTIONS CAN TAKE CARE OF NECESSARY CONVERSIONS
        
        
        
class AssignedFact:
    
    
    def __init__(self):
        '''
        Initiation always assigns default values
        '''    
        self.certainty = 'CERTAIN'
        self.polarity = 'POS'
        self.time = 'NON_FUTURE'
        
    def add_value(self, feature, value):
        '''
        Sets value of specific feature
        '''
        if feature == 'TENSE':
            self.time = value
        elif feature == 'CERTAINTY':
            self.certainty = value
        elif feature == 'POLARITY':
            self.polarity = value

###############################################################################
#
# Rule functions (prepare resources, apply rules)
#
###############################################################################

def read_in_features(infile):
    '''
    Function goes through resources file and adds changes involved with feature to a dictionary
    '''
    data = open(infile,'r')
    my_features = {}
    cats = ''
    for line in data:
        #format for defining involved changes; FEAT1:VAL1/FEAT2/VAL2
        if ':' in line:
            cats = line.rstrip().split('/')
        #we ignore files that do not define the implications
        elif len(cats) > 0:
            #for now, each feature is unique, so no need to check if exists
            #FIXME: ambiguity, etc.
            my_features[line.rstrip()] = cats
    return my_features
        

def apply_rule(factVals, target, mappings):
    
    if target in mappings:
        for feat in (val for val in mappings if ':' in val):
            ftVal = feat.split(':')
            factVals.add_value(ftVal[0], ftVal[1])
            


def apply_target_features(factVals, eventFeatures, resource_info):
    '''
    Functions that applies changes to factuality based on the target verb itself
    '''
    #first lemmas (for future), can then be overwritten by tense marking
    for lemma in eventFeatures.target_lemmas:
        if lemma in resource_info:
            val = resource_info.get(lemma)
            #only apply features applicable to self
            apply_rule(factVals, '[SELF]', val)
    
    for morph in eventFeatures.target_morphofeats:
        if morph in resource_info:
            val = resource_info.get(morph)
            apply_rule(factVals, '[SELF]', val)


def apply_predicative_chain_features(factVals, eventFeatures, resource_info):
    '''
    Functions that examine the predicative chain and adapt factuality values accordingly
    '''
    for predicate in eventFeatures.predicate_chain_lemmas:
        if predicate in resource_info:
            val = resource_info.get(predicate)
            apply_rule(factVals, '[DEP]', val)


def initiate_resources(mylanguage, sourcepath):
    '''
    Reads in all relevant resources and prepares them for being used in rules
    '''
    resource_loc = sourcepath + '/resources/' + en
    resource_info = {}
    for f in os.listdir(resource_loc):
        file_features = read_in_features(resource_loc + f)
        resource_info.update(file_features)
    return resource_info



###############################################################################
#
# Feature extraction functions
#
###############################################################################



def get_morphofeats(feature_extractor, span):
    '''
    Returns the morphofeats of a span
    '''
    morphofeats = []
    for tid in span:
        morphofeats += feature_extractor.get_dependencies_and_modifier(term_id)
    return morphofeats


def get_lemmas(feature_extractor, span):
    '''
    Returns the lemmas of a span
    '''
    lemmas = []
    for tid in span:
        lemmas.append(feature_extractor.get_lemma_for_term_id(tid))
    return lemmas

def add_predicate_chain_features(feature_extractor, span, eventObj):
    '''
    Function that retrieves predicate chain and collects related features.
    '''
    for tid in span:
        pred_chain = feature_extractor.get_list_term_ids()
        eventObj.predicate_chain_ids = pred_chain
        eventObj.predicate_chain_lemmas = feature_extractor.get_lemmas_for_list_term_ids(pred_chain)
        eventObj.predicate_chain_morphofeats = feature_extractor.get_morphofeat_for_list_term_ids(pred_chain)
        eventObj.predicate_chain_mods = feature_extractor.get_modifiers_list_term_ids(pred_chain)
    
    
def get_modifiers(feature_extractor, span):
    '''
    Function that retrieves modifiers of a span
    '''
    modifiers = []
    for tid in span:
        dep, mods = feature_extractor.get_dependencies_and_modifier(tid)
        modifiers.append([dep, mods])
    return modifiers


def add_argument_features(feature_extractor, span, eventObj):
    '''
    Retrieves the arguments and their lemmas
    '''
    arguments = []
    arg_lemmas = []
    for tid in span:
        component_ids = feature_extractor.get_argument_components_of_target_verbs_as_list_of_ids(span)
        arguments += component_ids
        for cid in component_ids:
            lemmas = feature_extractor.get_lemas_for_list_term_ids(cid)
            arg_lemmas.append(lemmas)
    eventObj.argument_ids = arguments
    eventObj.argument_lemmas = arg_lemmas
    
###############################################################################
#
# Management functions (overall extraction, rule application)
#
###############################################################################


def assign_factuality_values(eventsFeatures, resource_info):
    '''
    Function that goes through list of target events and assigns factuality values based on their features
    '''
    for event in eventsFeatures:
        #assigns default values to event
        myEventFact = AssignedFact()
        #look at target features
        apply_target_features(myEventFact, event, resource_info)
        #look at predicative chain


def extract_features(feature_extractor, target_events):
    '''
    Function that collects features for each target event
    '''
    events_features = []
    for event in target_events:
        myFeatures = EventFeatures(event)
        #add target lemmas
        myFeatures.target_lemmas = get_lemmas(feature_extractor, event)
        #add morphofeats of target
        myFeatures.target_morphofeats = get_morphofeats(feature_extractor, event)
        #add modifiers of target
        myFeatures.target_mods = get_modifiers(feature_extractor, event)
        #adding features for the predicate chain
        add_predicate_chain_features(feature_extractor, event, myFeatures)
        events_features.append(myFeatures)
        
    return event_features


def select_target_events(feature_extractor):
    '''
    Function that retrieves all events that should get factuality values
    '''
    target_events = []
    for coref in feature_extractor.get_corefs(this_type='event'):
        target_events += feature_extractor.get_span_ids_for_coref(coref)
    return target_events


def run_factuality_module(nafobj, resource_info):
    '''
    Function that regulates the module. 
    Version 0.1: extracts features and calls rules.
    Future versions (when ML): function will become rule_based regulator.
    '''
    feature_extractor = FeatureExtractor(nafobj)
    #1. select target events
    target_events = select_target_events(feature_extractor)
    #2. extract features for all target events
    events_features = extract_features(feature_extractor, target_events)
    #3. apply rules
    assign_factuality_values(events_features, resource_info)



def main(argv=None):
    
    if len(argv) < 2:
        print('Error:\n Usage: cat input | python rule_based_factuality.py path_to_module > output')
    else:
        nafobj = KafNafParser(sys.stdin)
        lang = nafobj.get_language()
        my_resource_info = initiate_resources(lang, argv[1])
        run_factuality_module(nafobj, resource_info)
    


if __name__ == '__main__':
    main()