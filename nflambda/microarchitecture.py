import time

# import pysftp
import os
import pickle
# import pandas as pd

def start_pcm():
    os.system(
    )
    return

def kill_pcm():
    os.system(
    )
    return

def get_microarchitecture_snapshot():
    os.system(
    )
    myHostname = "aum"
    myUsername = "ziyan"
    remoteFilePath = '/tmp/test.pkl'
    localFilePath = './profiling/test.pkl'
    with pysftp.Connection(host=myHostname, username=myUsername) as sftp:
        sftp.get(remoteFilePath, localFilePath)
    with open(localFilePath, 'rb') as infile:
        result = pickle.load(infile)

    return result

def get_microarchitecture_snapshot_2():
    myHostname = "aum"
    myUsername = "ziyan"
    remoteFilePath = '/tmp/log/output.csv'
    localFilePath = './profiling/1_memory_bound.csv'
    with pysftp.Connection(host=myHostname, username=myUsername) as sftp:
        sftp.get(remoteFilePath, localFilePath)

    df = pd.read_csv("profiling/1_memory_bound.csv", header=None)
    df[0] = pd.to_datetime(df[0])
    Counter_list = df[1].unique()
    DataFrameDict = {elem: pd.DataFrame for elem in Counter_list}

    for key in DataFrameDict.keys():
        DataFrameDict[key] = df[:][df[1] == key]
        DataFrameDict[key].set_index(0, inplace=True)
        DataFrameDict[key].drop(columns=[1], axis=1, inplace=True)
        DataFrameDict[key].columns = [i for i in range(0, 48, 1)]

    DataFrameDict["IPS"] = DataFrameDict['INST_RETIRED.ANY'] / DataFrameDict['INST_RETIRED.TOTAL_CYCLES_PS']
    DataFrameDict["L1_MISS"] = DataFrameDict['L1D.REPLACEMENT'] / DataFrameDict['MEM_INST_RETIRED.ALL_LOADS']
    DataFrameDict["L2_MISS"] = DataFrameDict['MEM_LOAD_RETIRED.L2_MISS'] / DataFrameDict['L1D.REPLACEMENT']
    DataFrameDict["L3_MISS"] = DataFrameDict['MEM_LOAD_RETIRED.L3_MISS'] / DataFrameDict['MEM_LOAD_RETIRED.L2_MISS']
    DataFrameDict["IPS"].dropna(inplace = True)
    DataFrameDict["L1_MISS"].dropna(inplace=True)
    DataFrameDict["L2_MISS"].dropna(inplace=True)
    DataFrameDict["L3_MISS"].dropna(inplace=True)
    return DataFrameDict