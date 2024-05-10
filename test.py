from matplotlib import pyplot as plt
if __name__ == "__main__":
    runtime_path = "/home/ziyan/project/nflambda_runtime/cmake-build-release/nflr"
    import os
    ret = os.system("sudo " + runtime_path + " &")
    ret = os.system("sudo pkill nflr")
    print(ret)