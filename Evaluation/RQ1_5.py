from configs_of_evaluation import configs_RQ
import pandas as pd
from now_tools import get_functions_df
import re
import tqdm

node_information = pd.read_csv('/home/auatac/liao_system/node/node.csv')
functions = get_functions_df(node_information)
CFGs = functions['CFG'].to_list()
CFG_Node_num = 0

for CFG in tqdm.tqdm(CFGs):
    CFG = CFG.replace('\\n', '\n')
    tuple_cfgNodes = re.findall('\n(\d+)\[label = "(.*)"\];', CFG)
    CFG_Node_num += len(tuple_cfgNodes)
print(CFG_Node_num)
