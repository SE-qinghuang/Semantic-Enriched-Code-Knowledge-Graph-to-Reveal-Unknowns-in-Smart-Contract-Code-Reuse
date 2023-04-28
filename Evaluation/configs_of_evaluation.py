
class configs_RQ:

    def __init__(self):
        self.RQ1_1_benchmark = 'RQ1/RQ1_1/clone pairs(1740).csv'
        self.RQ1_1_PRF1_on_benchmark = 'RQ1/RQ1_1/PRF1_on_benchmark.csv'
        self.RQ1_1_samples = 'RQ1/RQ1_1/sample clones(384).csv'
        self.word_2vec_dim = 150
        self.word_2vec_dict_model = '../Model/dim_{}_dic.bin'.format(self.word_2vec_dim)


        self.RQ1_2_benchmark = 'RQ1/RQ1_2/cooccurrence_benchmark.csv'
        self.RQ1_2_PRF1_on_benchmark = 'RQ1/RQ1_2/PRF1_on_benchmark.csv'
        self.RQ1_2_samples = 'RQ1/RQ1_2/samples co-occurrence(384).csv'
        self.token2type_file = '../token2type'

        # CC : composition count
        self.RQ1_3_CC_before_accumulation = '../saved_datas/node_information_after_get_composition_count_from_calls_relation.csv'
        self.RQ1_3_CC_after_accumulation = '../saved_datas/node_information_after_getting_Composition_Count.csv'
        self.RQ1_3_CC_before_and_after_accumulation = 'RQ1/RQ1_3/CC_before_and_after_accumulation.csv'
        self.RQ1_3_CC_changes_in_different_ranges = 'RQ1/RQ1_3/CC_changes_in_different_ranges.csv'
        self.RQ1_3_functions_are_increased_with_CC = 'RQ1/RQ1_3/functions that are increased with composition count.csv'

        self.RQ1_4_functions_not_augmented_with_comments = '../saved_datas/node_information_after_getting_Composition_Count.csv'
        self.RQ1_4_functions_augmented_by_override = '../saved_datas/node_information_after_spread_comment_by_using_override.csv'
        self.RQ1_4_functions_augmented_by_function_clone = '../saved_datas/node_information_after_only_similar_clone_relation.csv'
        self.RQ1_4_functions_augmented_by_override_functionClone = '../saved_datas/node_information_after_add_fucntion_comment_by_using_similar_clone_relation.csv'
        self.RQ1_4_functions_augmented_with_different_types = 'RQ1/RQ1_4/functions_augmented_with_different_types.csv'
        self.RQ1_4_para_returns_element_augmented = '../saved_datas/node_information_after_add_comment_by_using_has_relation.csv'
        self.RQ1_4_augmented_at_parameter_level = 'RQ1/RQ1_4/augmented at parameter level.csv'
        self.has_para = '../relations/has_para.csv'
        self.has_returns = '../relations/has_returns.csv'
        self.has_element = '../relations/has_element.csv'

        # self.contracts_directory = 'little_contract'
        # self.token2type_file = 'token2type'
        # self.bug_file = 'output_from_process/bug'
        #
        # #node information
        # self.node_to_comment_file = 'node/node_to_comment.csv'
        # self.node_to_function_code_file = 'node/node_to_function_code.csv'
        # self.node_to_type_file = 'node/node_to_type.csv'
        # self.node_to_composition_count_file = 'node/node_to_composition_count.csv'
        # self.order_sequence_file = 'node/order_sequence.csv'
        # self.description_sentence_file = 'node/description_sentense.csv'
        # self.keywords_file = 'node/keywords.csv'
        # self.description_and_source_of_specific_variables_file = 'node/description_and_source_of_specific_variables.csv'
        # self.node_to_description_file = 'node/description.csv'
        # self.node_to_order_sequence = 'node/order_sequence.csv'
        # self.node_to_returns = 'node/returns.csv'
        #
        # self.node_file = 'node/node.csv'
        #
        # self.model = 'train'         #train,update,do nothing
        # self.word_2vec_dim = 150
        # self.word_2vec_dict_model = 'Model/dim_{}_dic.bin'.format(self.word_2vec_dim)
        # self.word_2vec_model = 'Model/dim_{}'.format(self.word_2vec_dim)
        # self.tokens_file = 'Model/tokens.npy'
        # self.functions_vecs_similarity_file = 'output_from_process/functions_vecs_similarity_file.csv'
        #
        # self.threshold = 0.97
        # self.epoch_num = 1
        #
        # #relation
        # self.emit_event_relation_file = 'relations/emit_event.csv'
        # self.calls_relation_file = 'relations/calls.csv'
        # self.function_clone_file = 'relations/function_clone.csv'
        # self.has_function_relation_file = 'relations/has_function.csv'
        # self.has_event_relation_file = 'relations/has_event.csv'
        # self.has_variable_file = 'relations/has_variable.csv'
        # self.has_structure_file = 'relations/has_structure.csv'
        # self.has_enum_file = 'relations/has_enum.csv'
        # self.has_para_file = 'relations/has_para.csv'
        # self.has_element_file = 'relations/has_element.csv'
        # self.has_returns_file = 'relations/has_returns.csv'
        # self.override_file = 'relations/override.csv'
        # self.cooccurrence_relation = 'relations/cooccurrence.csv'
        #
        # #searching by bm25
        # self.corpus_fpath = 'Model/bm25Model/corpus.txt'
        # self.bm25_model_path = 'Model/bm25Model/bm25.pkl'
        # self.dict_merged_tokens_to_FEN = 'Model/bm25Model/dict_merged_tokens_to_FEN.txt'
        # self.dict_corpusid_FEN = 'Model/bm25Model/dict_corpusid_FEN.txt'
        # self.dict_corpusid_pt = 'Model/bm25Model/dict_corpusid_pt.txt'
        #
        # # relation
        # self.input_code_emit_event_relation_file = 'input/emit_event.csv'
        # self.input_code_calls_relation_file = 'input/calls.csv'
        # self.input_code_function_clone_file = 'input/function_clone.csv'
        # self.input_code_has_function_relation_file = 'input/has_function.csv'
        # self.input_code_has_event_relation_file = 'input/has_event.csv'
        # self.input_code_has_variable_file = 'input/has_variable.csv'
        # self.input_code_has_structure_file = 'input/has_structure.csv'
        # self.input_code_has_enum_file = 'input/has_enum.csv'
        # self.input_code_has_para_file = 'input/has_para.csv'
        # self.input_code_has_element_file = 'input/has_element.csv'
        # self.input_code_has_returns_file = 'input/has_returns.csv'
        #
        #
        # #neo4j
        # self.graph = Graph('http://localhost:7474', username='neo4j', password='123456')
        #
        # self.saved_information_directory = 'saved_datas/'
        #
        # #code checking
        # self.model_threshold = 0.82
        # self.checked_code_file = 'tools/test.sol'
        # self.checking_result_file = 'tools/Templefile.json'
        #
        # #code recommendation
        # self.top_n = 5
