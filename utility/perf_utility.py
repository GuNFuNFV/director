import subprocess
from runtime_agent.configuration import runtime_path_loader

nflambda_runtime_path = runtime_path_loader()
process_name = nflambda_runtime_path.split("/")[-1]
cmd = """sudo perf stat -e LLC-store-misses,LLC-store,LLC-load-misses,LLC-loads,\
l2_rqsts.demand_data_rd_miss,l2_rqsts.all_demand_data_rd,\
L1-dcache-load-misses,L1-dcache-store-misses,L1-dcache-loads,\
instructions,cycles,l1d.replacement,MEM_LOAD_RETIRED.L1_MISS,MEM_LOAD_RETIRED.L2_MISS,MEM_LOAD_RETIRED.L3_MISS \
-C 2 -p $(pgrep {}) -o test_output.txt &""".format(process_name)


def run_perf_command_in_background():
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)