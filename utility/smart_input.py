def input_with_available_values_autocompletion(input_dict:dict) -> dict[str, str]:
    """
    This function is used to get user input with autocompletion.
    :param input_dic: a dictionary that contains the input information
    :return: a dict of input option and corresponding value
    """
    assert isinstance(input_dict, dict)
    assert "available_values" in input_dict
    assert "options" in input_dict
    options = []
    if "options" in input_dict:
        options = input_dict["options"]
    available_values = {}
    if "available_values" in input_dict:
        available_values = input_dict["available_values"]
    result = {}
    if len(options) == 0:
        return result
    # first, select the options
    displayed_prompt = "Select the option you want to change (e to quit): \n"
    for index, option in enumerate(options):
        displayed_prompt += str(index) + ": " + option + "\n"
    displayed_prompt += "Your choice: "
    from prompt_toolkit import prompt
    from prompt_toolkit.validation import Validator
    from prompt_toolkit.completion import WordCompleter

    completer = WordCompleter(options, ignore_case=True, sentence=True)
    def validate_option(text):
        if text == "e" or text == "exit":
            return True
        # must be a list of integers, separated by comma
        try:
            import ast
            result =  ast.literal_eval(text)
            range_options = len(options)
            assert isinstance(result, list)
            for item in result:
                assert isinstance(item, int)
                assert item >= 0 and item < range_options
            return True
        except:
            return False


    validator = Validator.from_callable(validate_option, error_message='Option not valid',
                                        move_cursor_to_end=True)
    option = prompt(displayed_prompt, completer=completer, validator=validator, default="e")
    if option == "e" or option == "exit":
        return result

    import ast
    options_index = ast.literal_eval(option)
    selected_options = [options[index] for index in options_index]

    # second, select the value
    for option in selected_options:
        displayed_prompt = "Input the value for " + str(option)
        while True:
            assert option in available_values
            if available_values[option] is None:
                displayed_prompt += ": "
                def validate_value(text):
                    # if it is not empty and no space then it is valid
                    if len(text) > 0 and text.find(" ") == -1:
                        return True
                    else:
                        return False
                validator = Validator.from_callable(validate_value, error_message='Value not found',
                                                    move_cursor_to_end=True)
                value = prompt(displayed_prompt, validator=validator)
            else:
                for value in available_values[option]:
                    displayed_prompt += value + ", "
                displayed_prompt = displayed_prompt[:-2]
                displayed_prompt += ": "
                completer = WordCompleter(available_values[option], ignore_case=True, sentence=True)
                def validate_value(text):
                    if text in available_values[option]:
                        return True
                    else:
                        return False

                validator = Validator.from_callable(validate_value, error_message='Value not found',
                                                    move_cursor_to_end=True)
                value = prompt(displayed_prompt, completer=completer, validator=validator)
            result[option] = str(value)
            break
