import glob
import os
import time
import pandas as pd
import yaml


# exp_filename is {exp_name}_ts{timestamp}.csv


def exp_loader(exp_name, latest = 0, timestamp = None):
    # if timestamp is not None, then load the csv file with the timestamp
    if timestamp is not None:
        current_path = os.path.dirname(os.path.realpath(__file__))
        file_name = exp_name + "_ts" + str(timestamp) + ".csv"
        df = pd.read_csv(current_path + "/" + file_name)
        print("load csv file: {}, timestamp: {}".format(file_name, timestamp))
        return df
    # list all the csv files in the directory
    current_path = os.path.dirname(os.path.realpath(__file__))
    csv_files_fullpath = glob.glob(current_path + "/*.csv")
    csv_files = [os.path.basename(x) for x in csv_files_fullpath]
    exp_to_exp_filename = {}
    for csv_file in csv_files:
        if csv_file.startswith(exp_name):
            # if None, then initialize the list
            # else append the csv_file to the list
            exp_to_exp_filename.setdefault(exp_name, []).append(csv_file)

    corresponding_exp_filename = exp_to_exp_filename[exp_name]
    # sort the csv files by timestamp
    def get_timestamp(filename):
        # if contains ts, then return the timestamp
        # else return 0
        if "ts" in filename:
            return int(filename.split("ts")[1].split(".")[0])
        else:
            return 0

    sorted_exp_filename = sorted(corresponding_exp_filename, key=get_timestamp)
    # load the latest csv file
    latest_exp_filename = sorted_exp_filename[-1 - latest]
    df = pd.read_csv(current_path + "/" + latest_exp_filename)
    print("load csv file: {}, timestamp: {}".format(latest_exp_filename, get_timestamp(latest_exp_filename)))
    return df

def exp_saver(exp_name, df):
    current_path = os.path.dirname(os.path.realpath(__file__))
    # get current timestamp using time.time()
    timestamp = int(time.time())
    filename = exp_name + "_ts" + str(timestamp) + ".csv"
    df.to_csv(current_path + "/" + filename)

def read_file(filename):
    current_path = os.path.dirname(os.path.realpath(__file__))
    # list all the files in the directory
    files_fullpath = glob.glob(current_path + "/*.txt")
    # get the file starting with filename
    for file in files_fullpath:
        if file.startswith(current_path + "/" + filename):
            with open(file, 'r') as stream:
                try:
                    lines = stream.readlines()
                except yaml.YAMLError as exc:
                    print(exc)
            return lines
