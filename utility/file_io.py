def read_file_from_folder(folder_path):
    # get all the files in the folder
    import os
    files = os.listdir(folder_path)
    if len(files) == 0:
        raise Exception("No file found in the folder")
    files_without_extension = [file.split(".")[0] for file in files]
    from prompt_toolkit import prompt
    from prompt_toolkit.validation import Validator
    from prompt_toolkit.completion import WordCompleter
    # only allow the user to select files in the folder of folder_path
    # prefill the folder_path

    html_completer = WordCompleter(files_without_extension, ignore_case=True, sentence=True)

    def validate_file_name(text):
        if text in files_without_extension:
            return True
        else:
            return False

    validator = Validator.from_callable(validate_file_name, error_message='File name not found',
                                        move_cursor_to_end=True)
    file_name = prompt('Please enter the file name: ', completer=html_completer, validator=validator, default=files_without_extension[0])
    index = files_without_extension.index(file_name)
    file_name = files[index]
    # read the file as a dictionary
    # if the file is a yaml file, then use yaml.load
    # if the file is a json file, then use json.load
    if file_name.endswith(".yaml"):
        with open(folder_path + "/" + file_name, "r") as f:
            import yaml
            return yaml.load(f, Loader=yaml.FullLoader)
    elif file_name.endswith(".json"):
        with open(folder_path + "/" + file_name, "r") as f:
            import json
            return json.load(f)
    else:
        raise Exception("File type not supported")

def return_file_name_from_folder(folder_path):
    # get all the files in the folder
    import os
    files = os.listdir(folder_path)
    if len(files) == 0:
        raise Exception("No file found in the folder")
    files_without_extension = [file.split(".")[0] for file in files]
    from prompt_toolkit import prompt
    from prompt_toolkit.validation import Validator
    from prompt_toolkit.completion import WordCompleter
    # only allow the user to select files in the folder of folder_path
    # prefill the folder_path

    html_completer = WordCompleter(files_without_extension, ignore_case=True, sentence=True)

    def validate_file_name(text):
        if text in files_without_extension:
            return True
        else:
            return False

    validator = Validator.from_callable(validate_file_name, error_message='File name not found',
                                        move_cursor_to_end=True)
    file_name = prompt('Please enter the file name: ', completer=html_completer, validator=validator, default=files_without_extension[0])
    index = files_without_extension.index(file_name)
    file_name = files[index]
    return file_name

def get_folder_based_on_current_path(folder_name):
    # get the current path of the caller of this function
    import inspect
    import os
    path_of_caller = inspect.stack()[1][1]
    current_path = os.path.dirname(path_of_caller)
    # get the folder path
    folder_path = current_path + "/" + folder_name
    return folder_path

def load_file(file_name):
    # read the file as a dictionary
    # if the file is a yaml file, then use yaml.load
    # if the file is a json file, then use json.load
    if file_name.endswith(".yaml"):
        with open(file_name, "r") as f:
            import yaml
            return yaml.load(f, Loader=yaml.FullLoader)
    elif file_name.endswith(".json"):
        with open(file_name, "r") as f:
            import json
            return json.load(f)
    else:
        raise Exception("File type not supported")