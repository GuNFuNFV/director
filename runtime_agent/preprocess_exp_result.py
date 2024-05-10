from orchestration.configuration_bundle import parameter_space_data_loader
exp_name_list = [
    "scalability_cuckoo_hash_generic",
    "scalability_cuckoo_hash_generic_baseline",
]
import pandas as pd
if __name__ == "__main__":
    for exp_name in exp_name_list:
        parameter_data = parameter_space_data_loader(exp_name + ".csv")
        df = pd.DataFrame(parameter_data)
        print(df)

        # read exp_name + "csv" and convert to a dataframe

        df2 = pd.read_csv(exp_name + ".csv")
        print(df2)

        #concatenate the two dataframes
        df3 = pd.concat([df, df2], axis=1)
        # save as a new csv file
        df3.to_csv(exp_name + "_processed.csv", index=False)