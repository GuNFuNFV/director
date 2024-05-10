def evaluate_string(string):
    # try to evaluate the string as a list
    import ast
    try:
        result = ast.literal_eval(string)
        assert isinstance(result, list)
        return result
    except ValueError:
        print("Please input a list in Python format")
        raise ValueError

class logger():
    def __init__(self, file_name):
        self.current_line = 0
        self.file_name = file_name

    def log(self, message):
        file = open(self.file_name, "a")
        file.write(message)
        file.write("\n")
        file.close()

    def read_line(self):
        # read the current line and return it
        file = open(self.file_name, "r")
        lines = file.readlines()
        file.close()
        if self.current_line >= len(lines):
            raise Exception("End of file")
        else:
            self.current_line += 1
            return lines[self.current_line - 1]




class Logger_Singleton():
    __instance = None
    file_name = None

    def __init__(self, mode, file_name):
        if Logger_Singleton.__instance is not None:
            raise Exception("Singleton class - use 'get_instance()' to get the instance")
        Logger_Singleton.__instance = self
        # get the environment variable of file name
        import os
        if file_name is not None:
            Logger_Singleton.file_name = file_name
        else:
            Logger_Singleton.file_name = input("Please input the file name: ").rstrip('\n')
        Logger_Singleton.file_name = "log/" + self.file_name + ".mylog"
        # create the folder if it does not exist
        if not os.path.exists("log"):
            os.makedirs("log")
        self.logger = logger(Logger_Singleton.file_name)
        if mode == "file":
            # self.logger.log("This is a log file")
            pass
        else:
            # remove the file
            file = open(Logger_Singleton.file_name, "w")
            file.close()

    @staticmethod
    def get_instance(mode, file_name = None):
        if Logger_Singleton.__instance is None:
            Logger_Singleton(mode, file_name)
        return Logger_Singleton.__instance.logger

    @staticmethod
    def destroy_instance():
        Logger_Singleton.__instance = None

    @staticmethod
    def get_file_name():
        return Logger_Singleton.file_name

def custom_input(prompt_line, available_options = None):
    done = False
    while not done:
        from prompt_toolkit import prompt
        from prompt_toolkit.completion import WordCompleter
        if available_options is not None:
            completer = WordCompleter(available_options)
            value = prompt(prompt_line, completer=completer)
        else:
            value = input(prompt_line).rstrip('\n')
        if value == "":
            return None
        try:
            if value.startswith("[") and value.endswith("]"):
                value = value[1:-1]
            splitted = value.split(",")
            for i in range(len(splitted)):
                splitted[i] = "'" + splitted[i] + "'"
                # so don't have to add quotation mark in the input
            value = "[" + ",".join(splitted) + "]"
            result = evaluate_string(value)
            # remove space if the value is a string
            if isinstance(result, list):
                for i in range(len(result)):
                    if isinstance(result[i], str):
                        result[i] = result[i].strip()
            done = True
            return result
        except:
            print("Please input a list in Python format")


class IO_Multiplexer:
    __instance = None
    mode = None

    def __init__(self, mode = None):
        if IO_Multiplexer.__instance is not None:
            raise Exception("Singleton class - use 'get_instance()' to get the instance")
        IO_Multiplexer.__instance = self
        if mode is None:
            mode = input("from file or from input? (f/i) ").rstrip('\n')
        if mode == "f":
            IO_Multiplexer.mode = "file"
        elif mode == "i":
            IO_Multiplexer.mode = "input"
        else:
            raise ValueError("Please input f or i")

    @staticmethod
    def my_input(prompt, available_options = None):
        # get the class attribute of __mode
        self = IO_Multiplexer.get_instance()
        logger = Logger_Singleton.get_instance(mode=self.mode)
        if IO_Multiplexer.mode == "file":
            try:
                result = logger.read_line()
                result = result.split(":")[1].strip()
                result = evaluate_string(result)
                return result
            except Exception as e:
                print(e)
                IO_Multiplexer.mode = "input"
                print("switch to input mode")
        if IO_Multiplexer.mode == "input":
            result = custom_input(prompt, available_options)
            try:
                assert result is not None
            except:
                print("Please input a list in Python format")
                raise ValueError
            logger.log(prompt + str(result))
            return result
        else:
            raise ValueError("Please input f or i")

    @staticmethod
    def get_instance(mode=None):
        if IO_Multiplexer.__instance is None:
            IO_Multiplexer("f")
        return IO_Multiplexer.__instance

    @staticmethod
    def destroy_instance():
        del IO_Multiplexer.__instance
        IO_Multiplexer.__instance = None


my_input = IO_Multiplexer.my_input
