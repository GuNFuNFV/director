def transform_to_float(string):
    # 62,928,382 to 62928382
    # 1,000,000 to 1000000
    # 1,000 to 1000
    # 1 to 1
    num = string.replace(",", "")
    return float(num)

def perf_parser(file_name, elapsed_time):
    with open(file_name, 'r') as file:
        # read lines
        lines = file.readlines()
    events = {}
    for line in lines:
        if "LLC-load-misses" in line:
            events["LLC-load-misses"] = transform_to_float(line.split()[0])/elapsed_time
        if "LLC-loads" in line:
            events["LLC-loads"] = transform_to_float(line.split()[0])/elapsed_time
        if "L1-dcache-load-misses" in line:
            events["L1-dcache-load-misses"] = transform_to_float(line.split()[0])/elapsed_time
        if "L1-dcache-loads" in line:
            events["L1-dcache-loads"] = transform_to_float(line.split()[0])/elapsed_time
        if "instructions" in line:
            events["instructions"] = transform_to_float(line.split()[0])/elapsed_time
        if "cycles" in line:
            events["cycles"] = transform_to_float(line.split()[0])/elapsed_time
        if "l2_rqsts.all_demand_data_rd" in line:
            events["l2_rqsts.all_demand_data_rd"] = transform_to_float(line.split()[0])/elapsed_time
        if "l2_rqsts.demand_data_rd_miss" in line:
            events["l2_rqsts.demand_data_rd_miss"] = transform_to_float(line.split()[0])/elapsed_time
        if "l1d.replacement" in line:
            events["l1d.replacement"] = transform_to_float(line.split()[0])/elapsed_time
        if "LLC-store-misses" in line:
            events["LLC-store-misses"] = transform_to_float(line.split()[0])/elapsed_time
        if "LLC-store" in line:
            events["LLC-store"] = transform_to_float(line.split()[0])/elapsed_time
        if "l2_rqsts.all_demand_miss" in line:
            events["l2_rqsts.all_demand_miss"] = transform_to_float(line.split()[0])/elapsed_time
        if "MEM_LOAD_RETIRED.L2_MISS" in line:
            events["MEM_LOAD_RETIRED.L2_MISS"] = transform_to_float(line.split()[0])/elapsed_time
        if "MEM_LOAD_RETIRED.L1_MISS" in line:
            events["MEM_LOAD_RETIRED.L1_MISS"] = transform_to_float(line.split()[0])/elapsed_time
        if "MEM_LOAD_RETIRED.L3_MISS" in line:
            events["MEM_LOAD_RETIRED.L3_MISS"] = transform_to_float(line.split()[0])/elapsed_time

    events["llc_miss_rate"] = events["LLC-load-misses"] / events["LLC-loads"]
    events["l1_miss_rate"] = events["L1-dcache-load-misses"] / events["L1-dcache-loads"]
    events["l2_miss_rate"] = events["l2_rqsts.demand_data_rd_miss"] / events["l2_rqsts.all_demand_data_rd"]
    events["ipc"] = events["instructions"] / events["cycles"]
    return events