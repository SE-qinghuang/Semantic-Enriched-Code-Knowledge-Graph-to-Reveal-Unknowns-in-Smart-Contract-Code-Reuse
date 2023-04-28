from config import configs
import pandas as pd
class convert:
    def __init__(self,configs):
        self.configs = configs
        self.node_information = pd.read_csv(self.configs.node_file)

    def handle_description(self, node_name, description_sentence:str)->str:
        if type(description_sentence) == float:
            node_description_sentence = node_name.split(':')[-1]
            print(node_name)
        else:
            node_description_sentence = description_sentence.replace('\n', '\\n')

        return node_description_sentence

    def handle_funtion_code(self,description_sentence:str)->str:

        node_description_sentence = description_sentence.replace('\n','\\n')
        return node_description_sentence

    def handle_execution(self,execution:str)->str:
        node_execution = execution.replace('\n','\\n')
        return node_execution

    def handle_CFG(self,cfg:str)->str:
        node_cfg = cfg.replace('\n','\\n')
        return node_cfg

    def convert_special_symbol_to_string(self):

        self.node_information['Description'] = self.node_information.apply(
            lambda x: self.handle_description(x['FEN:ID'], x['Description']), axis=1)

        self.node_information['Function_Code'] = self.node_information.apply(
            lambda x: self.handle_funtion_code(x['Function_Code']), axis=1)

        self.node_information['Flow_Chart'] = self.node_information.apply(
            lambda x: self.handle_execution(x['Flow_Chart']), axis=1
        )

        self.node_information['CFG'] = self.node_information.apply(
            lambda x: self.handle_CFG(x['CFG']), axis=1
        )

        self.node_information.to_csv(self.configs.node_file, index=0)

        self.node_information.to_csv(
            self.configs.saved_information_directory + 'node_information_after_converting.csv',
            index=0)
