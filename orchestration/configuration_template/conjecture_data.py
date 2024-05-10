import os

import yaml

from orchestration.configuration_template.template_data import get_options_name_with_conjecture
from utility import read_file_from_folder
from utility.multiplex_input import IO_Multiplexer, Logger_Singleton, my_input

class Conjecture_Input:
    def __init__(self, variables):
        self.variables = variables
        self.value_dict = {}

    def run(self):
        print("Welcome to the input framework.")
        while True:
            if len(self.variables) == 0:
                print("All form_variable.py have been input.")
                break
            print("\nPlease select a variable to input a value for:")
            for i, variable in enumerate(self.variables):
                print(f"{i + 1}: {variable}")
            print(f"{len(self.variables) + 1}: Exit")
            choice = my_input("Enter your choice: ")
            choice = choice[0]
            if choice.lower() == 'exit' or choice.lower() == 'quit':
                break
            elif choice.isdigit():
                index = int(choice) - 1
                if index >= 0 and index < len(self.variables):
                    value = (my_input(f"Please enter a value for {self.variables[index]}: "))
                    try:
                        value = int(value[0])
                    except ValueError:
                        pass
                    self.value_dict[self.variables[index]] = value
                    # remove the variable from the list
                    self.variables.pop(index)
                    continue
                if index == len(self.variables):
                    break
                else:
                    print("Invalid choice. Please try again.")
            else:
                print("Invalid choice. Please try again.")

        return self.value_dict


def conjecture_data_loader(file_name):
    current_path = os.path.dirname(os.path.abspath(__file__))
    folder = current_path + "/conjecture_data"
    if file_name is None:
        result = read_file_from_folder("conjecture_data")
        return result
    with open(folder + "/" + file_name + ".yaml", "r") as file:
        result = yaml.load(file, Loader=yaml.FullLoader)
    return result

def save_conjecture_data(data_dic):
    # we assume that the data is valid
    file_name = ""
    key_list = list(data_dic.keys())
    key_list.sort()
    for key in key_list:
        result_value = data_dic[key]
        key = key.split("_")[0]  # make it shorter
        # change it to CAML case, replace _ with space, capitalize the first letter of each word, and remove space
        key = "".join([word.capitalize() for word in key.split("_")])
        file_name += key + str(result_value) + "_"
    file_name = file_name[:-1]
    current_path = os.path.dirname(os.path.abspath(__file__))
    folder = current_path + "/conjecture_data"
    if not os.path.exists(folder):
        os.makedirs(folder)
    with open(folder + "/" + file_name + ".yaml", "w") as file:
        yaml.dump(data_dic, file)
    return file_name

def create_conjecture_data(file_name=None):
    # get the command line argument file_name if it exists
    # format is python conjecture_data.py f=filename
    import sys
    import os
    if file_name is None:
        file_name = "temp"
        # remove temp.mylog if it exists
        current_path = os.path.dirname(os.path.realpath(__file__))
        log_folder = current_path + "/log"
        if os.path.exists(log_folder + "/temp.mylog"):
            os.remove("log/temp.mylog")
    IO_Multiplexer.get_instance()
    Logger_Singleton.get_instance(IO_Multiplexer.mode, file_name)
    framework = Conjecture_Input(get_options_name_with_conjecture())
    result = framework.run()
    print(result)
    # construct file name based on the result
    file_name = ""
    key_list = list(result.keys())
    key_list.sort()
    for key in key_list:
        result_value = result[key]
        key = key.split("_")[0]  # make it shorter
        # change it to CAML case, replace _ with space, capitalize the first letter of each word, and remove space
        key = "".join([word.capitalize() for word in key.split("_")])
        file_name += key + str(result_value) + "_"
    file_name = file_name[:-1]
    # save the result to folder conjecture_data
    current_path = os.path.dirname(os.path.realpath(__file__))
    folder = current_path + "/conjecture_data"
    if not os.path.exists(folder):
        os.makedirs(folder)
    # save the result as yaml file
    with open(folder + "/" + file_name + ".yaml", "w") as file:
        yaml.dump(result, file)
    return file_name


if __name__ == '__main__':
    # get the command line argument file_name if it exists
    # format is python conjecture_data.py f=filename
    import sys

    file_name = None
    for arg in sys.argv:
        if arg.startswith("f="):
            file_name = arg[2:]
    if file_name is None:
        file_name = "temp"
        # remove temp.mylog if it exists
        import os

        if os.path.exists("log/temp.mylog"):
            os.remove("log/temp.mylog")
    create_conjecture_data(file_name)
