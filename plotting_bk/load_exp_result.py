import sys
import os
from typing import Dict, List

import yaml

if len(sys.argv) != 2:
    exp_name = "motivation"
else:
    exp_name = sys.argv[1]
# get the path of the current file
current_path = os.path.dirname(os.path.realpath(__file__))
exp_path = current_path + "/../exp/" + exp_name
# check if the path exists
if not os.path.exists(exp_path):
    print("exp path does not exist")
    exit(1)
# list all the subfolders under exp_path, ignore the composed_nf_definition_file
# only get the directory name
dir_list =  [x[0] for x in os.walk(exp_path)][1:]
map_exp_id_to_config: Dict[int, List[Dict]] = {}
for dir in dir_list:
    # get the exp_id
    exp_id = dir.split("/")[-1]
    # list all the composed_nf_definition_file under the directory
    file_list = os.listdir(dir)
    # print(exp_id)
    # print(file_list)
    # load the yaml file in the file_list as dict
    for file in file_list:
        if file.endswith(".yaml"):
            # print(file)
            # load the yaml file as dict
            with open(dir + "/" + file, "r") as f:
                config_dict = yaml.load(f, Loader=yaml.FullLoader)
            # print(config_dict)
            # add the config_dict to the map
            if int(exp_id) not in map_exp_id_to_config:
                map_exp_id_to_config[int(exp_id)] = []
            map_exp_id_to_config[int(exp_id)].append(config_dict)


# load the summary.txt as csv
import pandas as pd
df = pd.read_csv(exp_path + "/summary.txt")
# add the configuration to the dataframe
for exp_id in map_exp_id_to_config:
    # get the configuration
    config_list = map_exp_id_to_config[exp_id]
    nf_config = config_list[0]
    tg_config = config_list[1]
    # get the row in df with the same exp_id
    row_index = df.index[df["exp_id"] == exp_id]
    # get all the fields in the nf_config["workers"]["worker_0"]
    for field in nf_config["workers"]["worker_0"]:
        # print(field)
        df.loc[row_index, field] = nf_config["workers"]["worker_0"][field]
    # get all the fields in the tg_config["workers"]["worker_0"]
    for field in tg_config["workers"]["worker_0"]:
        # if the field not in columns, add it to the dataframe
        if field not in df.columns:
            df[field] = None
        # if the field for the row is not set
        if pd.isnull(df.loc[row_index, field]).any():
            df.loc[row_index, field] = tg_config["workers"]["worker_0"][field]

# save the dataframe as csv
save_path = current_path + "/data/" +  exp_name + ".csv"
# if the csv already exists, load it replace the rows with the same exp_id
if os.path.exists(save_path):
    df_old = pd.read_csv(save_path)
    # get the exp_id in df_old
    exp_id_list = df_old["exp_id"].tolist()
    # get the exp_id in df
    exp_id_list_new = df["exp_id"].tolist()
    # get the index of the rows in df_old that have the same exp_id as df
    row_index_list = df_old.index[df_old["exp_id"].isin(exp_id_list_new)].tolist()
    # replace the rows in df_old with the same exp_id as df
    for row_index in row_index_list:
        # get the exp_id
        exp_id = df_old.loc[row_index, "exp_id"]
        # get the row in df with the same exp_id
        row_index_new = df.index[df["exp_id"] == exp_id]
        # replace the row
        df_old.loc[row_index] = df.loc[row_index_new].values[0]
    # save the dataframe as csv
    df_old.to_csv(save_path, index=False)
    exit(0)

# create the folder if it does not exist
if not os.path.exists(os.path.dirname(save_path)):
    os.makedirs(os.path.dirname(save_path))

df.to_csv(save_path, index=False)