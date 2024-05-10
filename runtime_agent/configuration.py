import os

import yaml
def runtime_path_loader():
    try:
        # read configuration.yaml in the same directory
        file_path = os.path.join(os.path.dirname(__file__), "configuration.yaml")
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
            assert config["nflambda_runtime_path"] != None
            return config["nflambda_runtime_path"]
    except Exception as e:
        print(e)
        raise Exception("Please check the configuration.yaml file")


def parameter_loader():
    try:
        # read configuration.yaml in the same directory
        file_path = os.path.join(os.path.dirname(__file__), "configuration.yaml")
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
            assert config["parameters"] != None
            return config["parameters"]
    except Exception as e:
        print(e)
        raise Exception("Please check the configuration.yaml file")


if __name__ == "__main__":
    print(runtime_path_loader())