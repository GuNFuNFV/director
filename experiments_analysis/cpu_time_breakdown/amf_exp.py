import matplotlib.pyplot as plt
import numpy as np

# Define the data
labels = ['item 1', 'item 2', 'item 3', 'item 5', 'item 6']

# Packets per second for the three methods
pps_single = [505080, 562967, 429429, 681724, 656493]
pps_interleaved = [770132, 919040, 610560, 1215244, 967317]
pps_interleaved_data_packing = [734835, 984701, 610089, 1311912, 1008752]


l1_miss_per_packet_single = [83.27847004228737, 68.33665145863873, 82.87172913198997, 59.59624704877071, 58.96648402607897]
l2_miss_per_packet_single = [38.56813853459268, 30.565766160500214, 37.25390902437991, 26.005333999126275, 23.495342960036215]




l1_miss_per_packet_interleaved = [75.97784192122336, 59.4012727378806, 77.25851000818913, 44.86485113103203, 47.857148833823715]
l2_miss_per_packet_interleaved = [17.528642846617053, 10.595072343996806, 16.855045633666215, 9.182715945011212, 9.922943726044672]

l1_miss_per_packet_interleaved_data_packing = [77.48703648666344, 42.091415814439664, 66.68104371780034, 35.06945439704076, 41.602774820459814]
l2_miss_per_packet_interleaved_data_packing = [16.827033977613056, 9.85997678144637, 17.257864546173813, 7.994049831815341, 9.636949549342967]

l3_miss_per_packet_single = [23.056511640968424, 15.417637861840603, 18.39047090576226, 12.669139867541807,
                             9.984344819199194]
l3_miss_per_packet_interleaved = [5.483042096741357, 0.3568786734013451, 2.9585440208888727, 0.861239982862096,
                                  0.2820084304789655]
l3_miss_per_packet_interleaved_data_packing = [4.489783848106181, 0.207683426490129, 3.3013656166092384,
                                               0.14509181668546028, 0.1713031030459645]


# load csv file: amf_free5gc_ts1695223348.csv, timestamp: 1695223348
# [38.800000000000004, 43.3, 36.68, 48.08, 37.84]
# [623736, 648300, 464861, 823668, 708011]
# [51699315.41668158, 42559099.00703343, 38753697.7287637, 42824052.42561059, 40641926.71567006]
# [2203575.0318489275, 2108445.209116977, 1894943.24734473, 2491138.0669400315, 2275410.4000318674]
# [10157933.890305104, 7709873.938964522, 6272091.418721205, 7880100.295255138, 5964466.521165365]
# item 1, n_blocks 23, pps 623736, l1_miss_per_packet 82.88653439384865, l2_miss_per_packet 3.5328649169663566, l3_miss_per_packet 16.285630283172853, state_access_per_packet 622.058050200726
# item 2, n_blocks 18, pps 648300, l1_miss_per_packet 65.64722968846742, l2_miss_per_packet 3.2522677913265112, l3_miss_per_packet 11.892447846621197, state_access_per_packet 667.900663273176
# item 3, n_blocks 18, pps 464861, l1_miss_per_packet 83.36620565881779, l2_miss_per_packet 4.076365294883266, l3_miss_per_packet 13.492401855008712, state_access_per_packet 789.0530717784455
# item 5, n_blocks 13, pps 823668, l1_miss_per_packet 51.991885596636735, l2_miss_per_packet 3.0244443962130756, l3_miss_per_packet 9.567083212234952, state_access_per_packet 583.730337951699
# item 6, n_blocks 11, pps 708011, l1_miss_per_packet 57.402959439429694, l2_miss_per_packet 3.2138065651972463, l3_miss_per_packet 8.42425685641235, state_access_per_packet 534.4549731571968


pps_single = [623736, 648300, 464861, 823668, 708011]
l1_miss_per_packet_single = [82.88653439384865, 65.64722968846742, 83.36620565881779, 51.991885596636735, 57.402959439429694]
l2_miss_per_packet_single = [3.5328649169663566, 3.2522677913265112, 4.076365294883266, 3.0244443962130756, 3.2138065651972463]
l3_miss_per_packet_single = [16.285630283172853, 11.892447846621197, 13.492401855008712, 9.567083212234952, 8.42425685641235]
#
#
#
#
# load csv file: amf_free5gc_ts1695223470.csv, timestamp: 1695223470
# [27.259999999999998, 22.44, 17.97, 24.020000000000003, 18.69]
# [815887, 958259, 626036, 1266071, 990051]
# [58092530.79137019, 52776243.72638769, 44918124.125023, 56783973.36409858, 45996852.74289174]
# [2536816.493497203, 2703936.454264709, 2235019.8503951496, 3034286.4553582165, 2691317.587246792]
# [4350998.902751037, 1823512.629242415, 2298769.2799403984, 2341534.956663764, 1315974.5348492614]
# item 1, n_blocks 23, pps 815887, l1_miss_per_packet 71.20168698774486, l2_miss_per_packet 3.109274315557428, l3_miss_per_packet 5.332844992935342, state_access_per_packet 334.11489581277795
# item 2, n_blocks 18, pps 958259, l1_miss_per_packet 55.07513493365331, l2_miss_per_packet 2.8217177759506655, l3_miss_per_packet 1.9029433892532344, state_access_per_packet 234.17468554952265
# item 3, n_blocks 18, pps 626036, l1_miss_per_packet 71.75006569114716, l2_miss_per_packet 3.5701139397656836, l3_miss_per_packet 3.6719442331437784, state_access_per_packet 287.04419554147046
# item 5, n_blocks 13, pps 1266071, l1_miss_per_packet 44.85054421442287, l2_miss_per_packet 2.396616347233462, l3_miss_per_packet 1.8494499571222816, state_access_per_packet 189.72079764878904
# item 6, n_blocks 11, pps 990051, l1_miss_per_packet 46.459074070822346, l2_miss_per_packet 2.718362576520595, l3_miss_per_packet 1.3291987330443193, state_access_per_packet 188.77815385268036

pps_interleaved = [815887, 958259, 626036, 1266071, 990051]
l1_miss_per_packet_interleaved = [71.20168698774486, 55.07513493365331, 71.75006569114716, 44.85054421442287, 46.459074070822346]
l2_miss_per_packet_interleaved = [3.109274315557428, 2.8217177759506655, 3.5701139397656836, 2.396616347233462, 2.718362576520595]
l3_miss_per_packet_interleaved = [5.332844992935342, 1.9029433892532344, 3.6719442331437784, 1.8494499571222816, 1.3291987330443193]

pps_interleaved_data_packing = [833268, 988728, 624132, 1332643, 1009416]
l1_miss_per_packet_interleaved_data_packing = [65.60816140469478, 43.54524578904141, 64.0928012458867, 35.11970652081404, 41.95354723726641]
l2_miss_per_packet_interleaved_data_packing = [2.8439239309214828, 2.7178489913846544, 3.5915624472308476, 2.3314333177112174, 2.5188567010574254]


#
# load csv file: amf_free5gc_ts1695224607.csv, timestamp: 1695224607
# [28.22, 24.45, 19.78, 25.700000000000003, 18.4]
# [833268, 988728, 624132, 1332643, 1009416]
# [54669181.437367216, 43054403.77850734, 40002368.22719776, 46802031.057017185, 42348581.83805251]
# [2369750.806071082, 2687213.3975537666, 2241609.0533150835, 3106968.2908146298, 2542574.255754582]
# [3699466.5574607835, 887115.5711201987, 1952879.3970678914, 986174.534458995, 999834.4729309797]
# item 1, n_blocks 23, pps 833268, l1_miss_per_packet 65.60816140469478, l2_miss_per_packet 2.8439239309214828, l3_miss_per_packet 4.439707942055597, state_access_per_packet 338.6665514576342
# item 2, n_blocks 18, pps 988728, l1_miss_per_packet 43.54524578904141, l2_miss_per_packet 2.7178489913846544, l3_miss_per_packet 0.8972291379633213, state_access_per_packet 247.28742384154185
# item 3, n_blocks 18, pps 624132, l1_miss_per_packet 64.0928012458867, l2_miss_per_packet 3.5915624472308476, l3_miss_per_packet 3.1289525245747556, state_access_per_packet 316.9201386886108
# item 5, n_blocks 13, pps 1332643, l1_miss_per_packet 35.11970652081404, l2_miss_per_packet 2.3314333177112174, l3_miss_per_packet 0.740014043115069, state_access_per_packet 192.8498480088066
# item 6, n_blocks 11, pps 1009416, l1_miss_per_packet 41.95354723726641, l2_miss_per_packet 2.5188567010574254, l3_miss_per_packet 0.9905078510059081, state_access_per_packet 182.28361745801527




def pps_to_mps(pps_l):
    return [i/1000000 for i in pps_l]

if __name__ == "__main__":
    hatch_list = ['/', 'x', '\\', 'o', '.']

    color_list = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7', '#9C755F',
                  '#BAB0AC']
    # to 2^14, 2^15, 2^16, 2^17 in latex
    subgroups = ["$2^{14}$", "$2^{15}$", "$2^{16}$", "$2^{17}$"]

    # Define bar width
    bar_width = 0.25

    # Create an index for each tick position
    ind = np.arange(len(labels))

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(7, 3))
    i = 0
    bar1 = ax.bar(ind - bar_width, pps_to_mps(pps_single), bar_width, label='L25GC',
                    hatch= hatch_list[i], color=color_list[i], alpha=0.99)
    bar2 = ax.bar(ind, pps_to_mps(pps_interleaved), bar_width, label='Interleaved Execution',
                    hatch= hatch_list[i+1], color=color_list[i+1], alpha=0.99)
    bar3 = ax.bar(ind + bar_width, pps_to_mps(pps_interleaved_data_packing), bar_width, label='Interleaved + Data Packing',
                    hatch= hatch_list[i+2], color=color_list[i+2], alpha=0.99)
    ax.set_ylim([0.3, 1.5])
    x_values = np.array(["Initial UE", "Authentication Response", "Security Mode Complete", "Registration Complete",
                         "Transport 5GSM"])  # Corresponding x-axis values
    ax.set_xticklabels(x_values, rotation=10)
    ax.set_xticks(ind + bar_width / 2)
    ax.set_xlabel('AMF Message Type')
    ax.set_ylabel('Packets per Second (mps)')
    ax.legend()

    plt.tight_layout()
    # Show the chart
    # plt.show()
    plt.savefig("amf_pps.pdf")

    # for l1 miss
    fig, ax = plt.subplots(figsize=(7, 3))
    i = 0
    bar1 = ax.bar(ind - bar_width, l1_miss_per_packet_single, bar_width, label='L25GC',
                  hatch= hatch_list[i], color=color_list[i], alpha=0.99)
    i += 1
    bar2 = ax.bar(ind, l1_miss_per_packet_interleaved, bar_width, label='16 NFTasks',
                    hatch= hatch_list[i], color=color_list[i], alpha=0.99)
    i += 1
    bar3 = ax.bar(ind + bar_width, l1_miss_per_packet_interleaved_data_packing, bar_width, label='16 NFTasks + Data Packing',
                    hatch= hatch_list[i], color=color_list[i], alpha=0.99)

    ax.set_ylim([30, 90])

    ax.set_xticklabels(x_values, rotation=10)
    ax.set_xticks(ind + bar_width / 2)
    ax.set_xlabel('AMF Message Type')
    ax.set_ylabel('L1 Misses Per Packet')
    ax.legend()

    plt.tight_layout()
    # Show the chart
    # plt.show()
    plt.savefig("amf_l1_miss_per_packet.pdf")


    # for l2 miss
    fig, ax = plt.subplots(figsize=(7, 3))
    i = 0
    bar1 = ax.bar(ind - bar_width, l2_miss_per_packet_single, bar_width, label='L25GC',
                    hatch= hatch_list[i], color=color_list[i], alpha=0.99)
    i += 1
    bar2 = ax.bar(ind, l2_miss_per_packet_interleaved, bar_width, label='Interleaved Execution',
                    hatch= hatch_list[i], color=color_list[i], alpha=0.99)
    i += 1
    bar3 = ax.bar(ind + bar_width, l2_miss_per_packet_interleaved_data_packing, bar_width, label='Interleaved + Data Packing',
                    hatch= hatch_list[i], color=color_list[i], alpha=0.99)


    ax.set_ylim([2, 5])

    ax.set_xticklabels(x_values, rotation=10)
    ax.set_xticks(ind + bar_width / 2)
    ax.set_xlabel('AMF Message Type')
    ax.set_ylabel('L2 Misses Per Packet')
    ax.legend()

    plt.tight_layout()
    # Show the chart

    # plt.show()
    plt.savefig("amf_l2_miss_per_packet.pdf")




    # for l3 miss
    fig, ax = plt.subplots(figsize=(7, 3))
    i = 0
    bar1 = ax.bar(ind - bar_width, l3_miss_per_packet_single, bar_width, label='L25GC',
                    hatch= hatch_list[i], color=color_list[i], alpha=0.99)
    i += 1
    bar2 = ax.bar(ind, l3_miss_per_packet_interleaved, bar_width, label='Interleaved Execution',
                    hatch= hatch_list[i], color=color_list[i], alpha=0.99)

    # show number for second bar
    for i in range(len(l3_miss_per_packet_interleaved)):
        plt.text(x=i, y=l3_miss_per_packet_interleaved[i] + 0.2, s=str(round(l3_miss_per_packet_interleaved[i], 2)), ha='center', va='bottom', fontsize=8)
    i = 2
    bar3 = ax.bar(ind + bar_width, l3_miss_per_packet_interleaved_data_packing, bar_width, label='Interleaved + Data Packing',
                    hatch= hatch_list[i], color=color_list[i], alpha=0.99)

    # show number for third bar
    for i in range(len(l3_miss_per_packet_interleaved_data_packing)):
        plt.text(x=i + bar_width, y=l3_miss_per_packet_interleaved_data_packing[i] + 0.2, s=str(round(l3_miss_per_packet_interleaved_data_packing[i], 2)), ha='center', va='bottom', fontsize=8)

    ax.set_ylim([0, 30])

    ax.set_xticklabels(x_values, rotation=10)
    ax.set_xticks(ind + bar_width / 2)
    ax.set_xlabel('AMF Message Type')
    ax.set_ylabel('L3 Misses Per Packet')
    ax.legend()

    plt.tight_layout()
    # Show the chart
    # plt.show()
    plt.savefig("amf_l3_miss_per_packet.pdf")