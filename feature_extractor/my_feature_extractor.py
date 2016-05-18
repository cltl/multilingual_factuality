
relevant_dependencies = {}
relevant_dependencies['en'] = ['TMP', 'ADV','NMOD']
relevant_dependencies['nl'] = ['hd/mod','hd/det']


class MyGraph:
    def __init__(self):
        self.G = {}
        self.relations_arriving_to_node = {}
        self.root = None
        
    def add_node(self, term_from, term_to, relation):
        if term_from not in self.G:
            self.G[term_from] = []
        self.G[term_from].append((relation, term_to))
        
        if term_from not in self.relations_arriving_to_node:
            self.relations_arriving_to_node[term_from] = 0
        if term_to not in self.relations_arriving_to_node:
            self.relations_arriving_to_node[term_to] = 0
            
        self.relations_arriving_to_node[term_to] += 1

    def __len__(self):
        return len(self.G)
    
    
    def calculate_root(self):
            
        L = list(self.relations_arriving_to_node.items())
        if len(L) != 0:
            L.sort(key=lambda t: t[1])
            min_freq = L[0][1]
            # In case there are several with the same minium frequency, we select the one with the highest
            list_with_min_freq = [(term_id, len(self.G[term_id])) for term_id, freq in L if freq == min_freq]
            list_with_min_freq.sort(key=lambda t: -t[1])
        
            self.root = list_with_min_freq[0][0]
        else:
            self.root = None
  
    def get_root(self):
        if self.root is None:
            self.calculate_root()
        return self.root

        
    def find_shortest_id_path(self, term_id_start, term_id_end, path=[]):
        path = path + [term_id_start]
        if term_id_start == term_id_end:
            return path
        
        if term_id_start not in self.G:
            return None
        
        shortest = None
        for relation, node in self.G[term_id_start]:
            if node not in path:
                newpath = self.find_shortest_id_path(node, term_id_end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest
    
    
    def get_relation_path_for_id_path(self, id_path):
        list_relations = []
        if id_path is not None:
            for idx in range(len(id_path)-1):
                node_to   = id_path[idx]
                node_from = id_path[idx+1]
                for this_rel, this_node in self.G[node_to]:
                    if this_node == node_from:
                        list_relations.append(this_rel)
                        break
        return list_relations
    
    def find_shortest_relation_path(self,term_id_start, term_id_end):
        shortest_id_path = self.find_shortest_id_path(term_id_start,term_id_end)
        return self.get_relation_path_for_id_path(shortest_id_path)
    
    def get_ids_directly_connected(self, term_id):
        ids = []
        if term_id in self.G:
            ids = [this_node for this_rel, this_node in self.G[term_id]]
        return ids
    
    
    def get_all_subsumed(self, this_term_id):
        ids_connected = self.get_ids_directly_connected(this_term_id)
        if len(ids_connected) == 0:
            return [this_term_id]
        else:
            superset = [this_term_id]
            for this_id in ids_connected:
                subsumed = self.get_all_subsumed(this_id)
                superset.extend(subsumed)
            return superset
     

class FeatureExtractor:
    def __init__(self, kafnafobj):
        self.obj = kafnafobj
        self.sentence_id_for_term_id = {}
        self.int_offset_for_term_id = {}
        self.graph_for_sentence_id = {}
        self.__create_indexes()
        
    def __create_indexes(self):
        for term in self.obj.get_terms():
            first_token_id = term.get_span().get_span_ids()[0]
            token_obj = self.obj.get_token(first_token_id)
            self.sentence_id_for_term_id[term.get_id()] = token_obj.get_sent()
            self.int_offset_for_term_id[term.get_id()] = int(token_obj.get_offset())
            
            
    def get_list_sorted_by_offset(self,list_term_ids):
        L = sorted([(tid, self.int_offset_for_term_id[tid]) for tid in list_term_ids], key=lambda t: t[1])
        sorted_list = [tid for tid, offset in L]
        return sorted_list

            
            
    def get_corefs(self,this_type=None):
        for coref in self.obj.get_corefs():
            if this_type is None or coref.get_type() == this_type:
                yield coref
                
    def get_span_ids_for_coref(self, coref):
        for span_obj in coref.get_spans():
            yield span_obj.get_span_ids()


    def get_lemma_for_term_id(self, term_id):
        term = self.obj.get_term(term_id)
        return term.get_lemma()
    
    
    def get_morphofeat_for_term_id(self, term_id):
        term = self.obj.get_term(term_id)
        return term.get_morphofeat()
    
  
    def get_dependencies_and_modifier(self, term_id, all_dependencies=False):
        for dep_obj in self.obj.get_dependencies():
            if dep_obj.get_from() == term_id:
                this_dependency = dep_obj.get_function()
                if all_dependencies or this_dependency in relevant_dependencies[self.obj.get_language()]:
                    term_obj_to = self.obj.get_term(dep_obj.get_to())
                    token_ids = term_obj_to.get_span().get_span_ids()
                    list_tokens = [self.obj.get_token(token_id).get_text() for token_id in token_ids]
                    yield (this_dependency,' '.join(list_tokens))
                    
    def __create_graph_for_sentence__(self, sentence_id):
        self.graph_for_sentence_id[sentence_id] = MyGraph()
        for dep in self.obj.get_dependencies():
            node_from = dep.get_from()
            if self.sentence_id_for_term_id[node_from] == sentence_id:
                #It is one dependency involving terms of the required sentence
                self.graph_for_sentence_id[sentence_id].add_node(node_from, dep.get_to(), dep.get_function())
    
                
    def get_graph_for_sentence(self,sentence_id):
        if sentence_id not in self.graph_for_sentence_id:
            self.__create_graph_for_sentence__(sentence_id)
        return self.graph_for_sentence_id.get(sentence_id)
            
        
    def get_list_term_ids_to_root(self, term_id):
        # Step 1, get which is the sentence of this term_id
        sentence_id = self.sentence_id_for_term_id.get(term_id)
        list_term_ids_to_root = []
        if sentence_id is not None:
            
            this_graph = self.get_graph_for_sentence(sentence_id)
            root_for_sentence = this_graph.get_root()
            list_term_ids_to_root = this_graph.find_shortest_id_path(term_id, root_for_sentence)
            if list_term_ids_to_root is None:
                list_term_ids_to_root = this_graph.find_shortest_id_path(root_for_sentence,term_id)
                
        
        return list_term_ids_to_root
    
    def get_lemmas_for_list_term_ids(self, list_term_ids):
        list_lemmas = []
        if list_term_ids is not None:
            for term_id in list_term_ids:
                term_obj = self.obj.get_term(term_id)
                list_lemmas.append(term_obj.get_lemma())
        return list_lemmas
             
    def get_morphofeat_for_list_term_ids(self, list_term_ids):
        list_morpho = []
        if list_term_ids is not None:
            for term_id in list_term_ids:
                term_obj = self.obj.get_term(term_id)
                list_morpho.append(term_obj.get_morphofeat())
        return list_morpho
    
    def get_modifiers_list_term_ids(self, list_term_ids):
        main_list = []
        if list_term_ids is not None:
            for term_id in list_term_ids:
                this_list = list(self.get_dependencies_and_modifier(term_id))
                if len(this_list) == 0:
                    main_list.append(None)
                else:
                    main_list.append(this_list)
        return main_list
    
    def get_argument_components_of_target_verb_as_list_of_ids(self, term_id):
        components = []
        sentence_id = self.sentence_id_for_term_id.get(term_id)
        this_graph = self.get_graph_for_sentence(sentence_id)
        term_ids_connected = this_graph.get_ids_directly_connected(term_id)
        for this_tid in term_ids_connected:
            subsumed = this_graph.get_all_subsumed(this_tid)
            components.append(self.get_list_sorted_by_offset(subsumed))
        return components
        
        
        
        
                