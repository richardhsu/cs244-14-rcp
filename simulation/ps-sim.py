import numpy as np
import os
import Queue
from scipy.stats import pareto

# Output parameters and details
debug_flag = False
super_debug_flag = False

# Network characteristics
num_flows = 1000
# Total number of flows in rcp simulation: 2399499
link_rates = [2.4]
pareto_shapes = [1.2]
mean_npkts = 25
packet_size = 1000 # bytes
rtt = 0.1
load = 0.9

delta = 0.000001

for shape in pareto_shapes:
    log_file_str = "lib/ps/pareto-flowSizes/logs/logFile-sh" + str(shape)
    try:
        os.remove(log_file_str)
    except OSError:
            pass

def log(log_str, shape):
    if debug_flag:
        print log_str
        log_file_str = "lib/ps/pareto-flowSizes/logs/logFile-sh" + str(shape)
        log_file = open(log_file_str, 'a')
        log_file.write(log_str)
        log_file.close()

class Flow(object):
    def __init__(self, arrival, length, inter_arrival, link_rate=2.4):
        self.arrival = arrival # seconds
        self.bitlength = length # number of bits 
        self.packet_length = self.bitlength/(8*packet_size)
        self.complete_dl = arrival + length/(link_rate*(10**9))
        self.buffered = 0.0
        # seconds lasted until this flow starts
        self.inter_arrival = inter_arrival
        self.fct = -1 # default: not complete 
        self.finished = False
        self.max_flows_bottleneck = 0 # how many flows this one competed with

    def __cmp__(self, other):
        return cmp(self.arrival, other.arrival)

def generate_flows(num_flows, link_rate, lamb, shape):
    print "Generating flows..."
    log("Generating flows...", shape)
    all_flows = Queue.Queue()
    inter_arrivals = np.random.exponential(1.0/lamb, num_flows)
    flow_lengths = pareto.rvs(shape, scale=scale, size=num_flows)
    log("average flow length:%f " % (sum(flow_lengths)/num_flows), shape)
    prev_time = 0
    for i in range(num_flows):
        curr_time = prev_time + inter_arrivals[i]
        flow = Flow(curr_time, int(8*packet_size*flow_lengths[i]), inter_arrivals[i], link_rate)
        all_flows.put(flow)
        prev_time = curr_time
        if super_debug_flag:
            log("flow created: (%.8f, %d)." % (flow.arrival, flow.packet_length), shape)
    max_packets = int(max(flow_lengths))
    print "Finished flow generation."
    log("Finished flow generation.", shape)
    return inter_arrivals, all_flows, max_packets

def update_flows(curr_flows, duration, curr_time, link_rate=2.4):
    stop_time = curr_time + duration
    log("Starting update in time (%.8f, %.8f) Current active flows: %d." % (curr_time, stop_time, len(curr_flows)), shape)

    # update flow lists
    new_curr_flows = []
    done_flows = []
    if not curr_flows:
        log("No flows to update in this interval.", shape)
    num_flows = len(curr_flows)
    # update how many flows each flow competed with
    for flow in curr_flows:
        flow.max_flows_bottleneck = max(num_flows, flow.max_flows_bottleneck)
    while curr_time < stop_time:
        for i in range(len(curr_flows)):
            flow = curr_flows[i]
            if flow.finished:
                continue
            if flow.arrival < curr_time and curr_time < flow.complete_dl:
                incoming = (link_rate * (10**9)) * delta
                # incoming = (link_rate * (10**9)) * min(delta, self.complete_dl - curr_time)
                flow.buffered += incoming
            outgoing = (link_rate * (10**9)) * delta / (num_flows)
            flow.buffered = max(0.0, flow.buffered - outgoing)
            if flow.buffered <= 0.0 and flow.complete_dl < curr_time:
                # this flow has completed, so remove.
                flow.fct = curr_time
                flow.finished = True
                log("Finished flow (arrival: %.8f, packets: %d); fct %f" % (flow.arrival, flow.packet_length, flow.fct), shape)
        curr_time += delta

    for flow in curr_flows:
        if super_debug_flag:
            log("status of flow (%.8f, %d): (fct: %.8f, finished: %s)" % (flow.arrival, flow.packet_length, flow.fct, flow.finished), shape)
        if flow.finished:
            done_flows.append(flow)
        else:
            new_curr_flows.append(flow)
    
    return new_curr_flows, done_flows # flows completed in this duration

def arrival_log(new_flow):
    return "Arrival at time %.8f (after %.8f s): flow (%d packets, %.8f completion)" % (new_flow.arrival, new_flow.inter_arrival, new_flow.packet_length, new_flow.complete_dl)

def update_log(curr_time, init_active_count, finished, total_finished):
    return "Update at time %.8f: Initially active: %d, finished: %d, total_finished: %d" % (curr_time, init_active_count, finished, total_finished)

def packet_info(all_done_flows):
    fcts_aggregate = {}
    for flow in all_done_flows:
        if int(flow.packet_length) not in fcts_aggregate:
            fcts_aggregate[int(flow.packet_length)] = []
        entries = fcts_aggregate[int(flow.packet_length)]
        entries.append(flow.fct)

    return fcts_aggregate

def average_fct(fcts_aggregate):
    avg_fcts = {}
    for packet_length in fcts_aggregate.keys():
        packet_entries = fcts_aggregate[packet_length]
        avg_fcts[packet_length] = sum(packet_entries)/len(packet_entries)
    return avg_fcts

def max_fct(fcts_aggregate):
    max_fcts = {}
    for packet_length in fcts_aggregate.keys():
        max_fcts[packet_length] = max(fcts_aggregate[packet_length]) 
    return max_fcts

def simulate(shape, lamb, link_rate):
    """
    """
    print "Pareto distribution with shape: %d, mean: %d" % (shape, mean_npkts)
    print "Sanity check on pareto mean packets: %f" % (pareto.stats(shape, scale=scale, moments='m'))
    print "Poisson process with lambda: %f" % (lamb)
    log("Pareto distribution with shape: %d, mean: %d" % (shape, mean_npkts), shape)
    log("Sanity check on pareto mean packets: %f" % (pareto.stats(shape, scale=scale, moments='m')), shape)
    log("Poisson process with lambda: %f" % (lamb), shape)

    inter_arrival, all_flows, max_packets = generate_flows(num_flows, link_rate, lamb, shape)

    print "Starting simulation..."
    log("Starting simulation...", shape)
    curr_flows = []
    all_done_flows = []
    curr_time = 0
    count = 0
    count_50 = 0
    while not all_flows.empty():
        count += 1
        if count /50 > count_50:
            count_50 += 1
            print "%d flows have arrived..." % count
        new_flow = all_flows.get()
        inter_arrival = new_flow.inter_arrival
        init_active_count = len(curr_flows)
        # update flows
        curr_flows, done_flows = update_flows(curr_flows, inter_arrival, curr_time, link_rate)

        # update loop state
        curr_time += inter_arrival
        all_done_flows += done_flows

        log(update_log(curr_time, init_active_count, len(done_flows), len(all_done_flows)), shape)

        curr_flows.append(new_flow) # newest arriving flow
        log(arrival_log(new_flow), shape)
        log("\n", shape)

    # all flows have arrived, so migrate to updating once every E[arrival] = 1/lamb.
    log("All flows have arrived. Updating remaining flows...", shape)
    update_duration = 1.0/lamb
    while len(all_done_flows) != num_flows:
        init_active_count = len(curr_flows)
        curr_flows, done_flows = update_flows(curr_flows, update_duration, curr_time, link_rate)
        curr_time += update_duration
        all_done_flows += done_flows
        log(update_log(curr_time, init_active_count, len(done_flows), len(all_done_flows)), shape)

    print "Finished simulation. Generating FCT results..."
    log("Finished simulation. FCT results:", shape)
    if super_debug_flag:
        for done_flow in all_done_flows:
            log("(packets: %d, fct: %.8f, bottleneck: %d flows)" % (done_flow.packet_length, done_flow.fct, done_flow.flow_bottleneck), shape)
    fcts_aggregate = packet_info(all_done_flows)
    avg_fcts = average_fct(fcts_aggregate)
    max_fcts = max_fct(fcts_aggregate)

    packet_list = avg_fcts.keys()
    packet_list.sort()
    ret_list = []
    for packet_length in packet_list:
        log("Packet length: %d, average FCT: %.8f, max FCT: %.8f" % (packet_length, avg_fcts[packet_length], max_fcts[packet_length]), shape)
        ret_list.append((packet_length, avg_fcts[packet_length], max_fcts[packet_length]))
    return ret_list # tuples (packet_length, average fct)

if __name__ == "__main__":
    for shape in pareto_shapes:
        for cap in link_rates:
            output_file_str = "lib/ps/pareto-flowSizes/logs/flowSizeVsDelay-sh" + str(shape)
            output_file = open(output_file_str, 'w')

            scale = (shape-1.0)/shape * mean_npkts
            lamb = (cap * (10**9))*load/(mean_npkts*(packet_size)*8.0)

            ret_list = simulate(shape, cap, lamb)
            print "Writing FCT results to file %s." % (output_file_str)
            log("Writing FCT results to file %s." % (output_file_str), shape)
            for entry in ret_list:
                output_file.write('%d 0 0 0 0 0 %.12f 0 %.12f' % entry)
            output_file.close()
