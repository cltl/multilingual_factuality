import sys
import os
import time
from KafNafParserPy import *
from my_feature_extractor import FeatureExtractor

# Version. May 9th: version 0.01 
#(many minor revisions in resources and code expected in near feature)

versionnr='0.01'


#global objects for storing relevant information

modals = {}
resource_info = {}

class EventFeatures:
    
    def __init__(self, target_span = []):
        
        self.target_span = target_span
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
    
    
    def __init__(self, span=[]):
        '''
        Initiation always assigns default values
        '''    
        self.certainty = 'CERTAIN'
        self.polarity = 'POS'
        self.time = 'NON_FUTURE'
        self.span = span
        
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
            


def apply_target_features(factVals, eventFeatures):
    '''
    Functions that applies changes to factuality based on the target verb itself
    '''
    #first lemmas (for future), can then be overwritten by tense marking
    global resource_info
    for lemma in eventFeatures.target_lemmas:
        if lemma in resource_info:
            val = resource_info.get(lemma)
            #only apply features applicable to self
            apply_rule(factVals, '[SELF]', val)
    
    for morph in eventFeatures.target_morphofeats:
        if morph in resource_info:
            val = resource_info.get(morph)
            apply_rule(factVals, '[SELF]', val)


def apply_predicate_chain_features(factVals, eventFeatures, factuality_info):
    '''
    Function that examines the predicate chain and adapt factuality values accordingly
    '''
    
    for predicate in eventFeatures.predicate_chain_lemmas:
        if predicate in factuality_info:
            val = factuality_info.get(predicate)
            apply_rule(factVals, '[DEP]', val)
            
            
def apply_modifier_target_and_chain_features(factVals, eventFeatures):
    '''
    Function that checks the possible impact of modifiers
    '''
    global resource_info
    
    ##will be changed: kind of predicate + modifier interact
    
    #first predicate chain modifiers
    #FIXME: data structure for passing on modifiers does not make sense (tuple in list in list...)
    #FIXME2: ugly process: interaction is much more complex
    for modifier in eventFeatures.predicate_chain_mods:
        if modifier != None:
            for mod in modifier:
                if mod[1] in resource_info:
                    val = resource_info.get(mod[1])
                    apply_rule(factVals, '[HEAD]', val)
    
    #then target modifiers
    for modifier in eventFeatures.target_mods:
        if modifier[1] in resource_info:
            val = resource_info.get(modifier[1])
            apply_rule(factVals, '[HEAD]', val)
    

def apply_argument_features(factVals, eventFeatures):
    '''
    Function that changes values based on components of arguments
    '''  
    
    negation_words = ['geen','noch','niet']
    
    for argument in eventFeatures.argument_lemmas:
        for word in argument:
            if word.lower() in negation_words:
                factVals.polarity = 'NEG'


def initiate_resources(mylanguage, sourcepath):
    '''
    Reads in all relevant resources and prepares them for being used in rules
    '''
    global modals, resource_info
    resource_loc = sourcepath + mylanguage + '/'
    for f in os.listdir(resource_loc):
        file_features = read_in_features(resource_loc + f)
        if 'modal' in f:
            modals.update(file_features)
        else:
            resource_info.update(file_features)



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
        morphofeats += feature_extractor.get_morphofeat_for_term_id(tid)
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
        pred_chain = feature_extractor.get_list_term_ids_to_root(tid)
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
        for dep, mod in feature_extractor.get_dependencies_and_modifier(tid):
            modifiers.append([dep, mod])
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
# NAF production functions
#
###############################################################################

def add_factvalues(value, resource, fnode, source = None):
    '''
    Adds a new factuality value to the factuality node
    '''
    
    fVal = Cfactval()
    fVal.set_resource(resource)
    fVal.set_value(value)
    if source != None:
        fVal.set_source(source)
    fnode.add_factval(fVal)


def create_naf_output(nafobj, events):
    
    myFactualityLayer = Cfactualities()
    fid = 0
    for key in sorted(events):
        vals = events.get(key)
        for val in vals:
            fid += 1
            fnode = Cfactuality()
            fnode.set_id('f' + str(fid))
            fspan = Cspan()
            for tid in val.span:
                fspan.add_target_id(tid)
            fnode.set_span(fspan)
        
            add_factvalues(val.certainty, 'nwr:attributionCertainty', fnode, None)
            add_factvalues(val.polarity, 'nwr:attributionPolarity', fnode, None)
            add_factvalues(val.time, 'nwr:attributionTense', fnode, None)
            myFactualityLayer.add_factuality(fnode)

    #add factuality node to parser
    nafobj.root.append(myFactualityLayer.get_node())

def add_naf_header(nafobj, begintime):
    
    global versionnr
    
    endtime = time.strftime('%Y-%m-%dT%H:%M:%S%Z')
    lp = Clp(name="vua-multilingual-factuality-system",version=versionnr,btimestamp=begintime,etimestamp=endtime)
    nafobj.add_linguistic_processor('factualities', lp)


    
###############################################################################
#
# Management functions (overall extraction, rule application)
#
###############################################################################


def get_event_factuality_identifiers(termSpan):
    '''
    Function that creates dictionary key for event using its span
    (at this point, we assume that each event has a unique first term)
    '''
    termId = ''
    #if neither t_ nor t leads to termNr, we have a problem with the NAF file anyway...
    for term in termSpan:
        if 't_' in term:
            termNr = term.lstrip('t_')
        elif 't' in term:
            termNr = term.lstrip('t')
        if termId == '':
            termId = int(termNr)
        elif termId > int(termNr):
            termId = int(termNr)
    if termId == '':
        print(termSpan, file=sys.stderr)
    return termId   


def assign_factuality_values(eventsFeatures):
    '''
    Function that goes through list of target events and assigns factuality values based on their features
    '''
    global modals, resource_info
    #store in dictionary with tid nr as key for ordening output
    eventFactuality = {}
    for event in eventsFeatures:
        #assigns default values to event
        myEventFact = AssignedFact(event.target_span)
        #look at target features
        apply_target_features(myEventFact, event)
        #look at predicate chain: modals
        apply_predicate_chain_features(myEventFact, event, modals)
        #look at modifiers (for now: both target and chain; should be changed)
        apply_modifier_target_and_chain_features(myEventFact, event)
        #look at predicate chain: non-modals
        apply_predicate_chain_features(myEventFact, event, resource_info)
        #look at arguments
        apply_argument_features(myEventFact, event)
        #get term id:
        termId = get_event_factuality_identifiers(event.target_span)
        if not termId in eventFactuality:
            eventFactuality[termId] = [myEventFact]
        else:
            eventFactuality[termId].append(myEventFact)
    return eventFactuality

def extract_features(feature_extractor, target_events):
    '''
    Function that collects features for each target event
    '''
    events_features = []
    for event in target_events:
        #don't include events without a span
        if not event == []:
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
        
    return events_features

def select_target_events(feature_extractor):
    '''
    Function that retrieves all events that should get factuality values
    '''
    target_events = []
    for coref in feature_extractor.get_corefs(this_type='event'):
        target_events += feature_extractor.get_span_ids_for_coref(coref)
    return target_events


def run_factuality_module(nafobj):
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
    event_factuality = assign_factuality_values(events_features)
    #4. create output NAF
    create_naf_output(nafobj, event_factuality)

def main(argv=None):
    
    resource_path = os.path.dirname(os.path.abspath(__file__)).replace('feature_extractor','resources/')
    
    begintime = time.strftime('%Y-%m-%dT%H:%M:%S%Z')
    nafobj = KafNafParser(sys.stdin)
    lang = nafobj.get_language()
    initiate_resources(lang, resource_path)
    run_factuality_module(nafobj)
    #add header
    add_naf_header(nafobj, begintime)
    nafobj.dump()


if __name__ == '__main__':
    main()