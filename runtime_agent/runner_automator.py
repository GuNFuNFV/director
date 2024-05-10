# the script is to run the same experiment multiple times
def call_runtime(exp_name):
    import os
    os.system("python3 runner.py " + exp_name)

def call_runtime_multiple_times(exp_name, times):
    for i in range(times):
        call_runtime(exp_name)


if __name__ == "__main__":
    exp_name = "bess_nat"
    call_runtime_multiple_times(exp_name, 10)