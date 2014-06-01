import numpy as np
import sys
import Queue
from scipy.stats import pareto


# Network characteristics
num_flows = 100 
# Total number of flows in rcp simulation: 2399499
packet_size = 1000 # bytes
mean_npkts = 25
rtt = 0.1 # seconds
load = 0.9

# instantiate shape/capacity-dependent variables. 
shape = -1
link_rate = -1
scale = -1
lamb = -1

delta = 0.0000001

# Output parameters and details
debug_flag = False

class Flow(object):
    def __init__(self, arrival, length, inter_arrival):
        self.arrival = arrival # seconds
        self.bitlength = length # number of bits 
        self.packet_length = self.bitlength/(8*packet_size)
        self.complete_dl = arrival + length/(link_rate * 10 ** 9)
        self.buffered = 0.0
        # seconds lasted until this flow starts
        self.inter_arrival = inter_arrival
        self.fct = -1 # default: not complete 
        self.finished = False
        self.max_flows_bottleneck = 0 # how many flows this one competed with

    def __cmp__(self, other):
        return cmp(self.arrival, other.arrival)

def generate_flows(num_flows):
    print "Generating flows..."
    all_flows = Queue.Queue()
    inter_arrivals = np.random.exponential(1.0/lamb, num_flows)
    flow_lengths = pareto.rvs(shape, scale=scale, size=num_flows)
    print "average flow length:", sum(flow_lengths)/num_flows
    prev_time = 0
    for i in range(num_flows):
        curr_time = prev_time + inter_arrivals[i]
        flow = Flow(curr_time, int(8*packet_size*flow_lengths[i]), inter_arrivals[i])
        all_flows.put(flow)
        prev_time = curr_time
        if debug_flag:
            print "flow created: (%.8f, %d)." % (flow.arrival, flow.packet_length)
    max_packets = int(max(flow_lengths))
    print "Finished flow generation."
    print
    return inter_arrivals, all_flows, max_packets

def update_flows(curr_flows, duration, curr_time):
    stop_time = curr_time + duration
    print "Starting update in time (%.8f, %.8f) Current active flows: %d." % (curr_time, stop_time, len(curr_flows))

    # update flow lists
    new_curr_flows = []
    done_flows = []
    if not curr_flows:
        print "No flows to update in this interval."
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
                incoming = link_rate * (10 ** 9) * delta
                # incoming = link_rate * (10 ** 9) * min(delta, self.complete_dl - curr_time)
                flow.buffered += incoming
            outgoing = link_rate * (10**9) * delta / (num_flows)
            flow.buffered = max(0.0, flow.buffered - outgoing)
            if flow.buffered <= 0.0 and flow.complete_dl < curr_time:
                # this flow has completed, so remove.
                flow.fct = curr_time
                flow.finished = True
                print "Finished flow (arrival: %.8f, packets: %d); fct %f" % (flow.arrival, flow.packet_length, flow.fct)
        curr_time += delta

    for flow in curr_flows:
        if debug_flag:
            print "status of flow (%.8f, %d): (fct: %.8f, finished: %s)" % (flow.arrival, flow.packet_length, flow.fct, flow.finished)
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

    if debug_flag:
        for packet_length in fcts_aggregate.keys():
            print "packet length: %d" % (packet_length), fcts_aggregate[packet_length]
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

def simulate():
    """
    """
    print "Pareto distribution with shape:", shape, "mean:", mean_npkts
    print "Sanity check on pareto mean packets:", pareto.stats(shape, scale=scale, moments='m')
    print "Poisson process with lambda:", lamb
    inter_arrival, all_flows, max_packets = generate_flows(num_flows)
    curr_flows = []
    all_done_flows = []
    curr_time = 0
    while not all_flows.empty():
        new_flow = all_flows.get()
        inter_arrival = new_flow.inter_arrival
        init_active_count = len(curr_flows)
        # update flows
        curr_flows, done_flows = update_flows(curr_flows, inter_arrival, curr_time)

        # update loop state
        curr_time += inter_arrival
        all_done_flows += done_flows

        print update_log(curr_time, init_active_count, len(done_flows), len(all_done_flows))

        curr_flows.append(new_flow) # newest arriving flow
        print arrival_log(new_flow)
        print

    # all flows have arrived, so migrate to updating once every E[arrival] = 1/lamb.
    print "All flows have arrived. Updating remaining flows..."
    update_duration = 1.0/lamb
    while len(all_done_flows) != num_flows:
        init_active_count = len(curr_flows)
        curr_flows, done_flows = update_flows(curr_flows, update_duration, curr_time)
        curr_time += update_duration
        all_done_flows += done_flows
        print update_log(curr_time, init_active_count, len(done_flows), len(all_done_flows))
        print

    print "Finished simulation. FCT results:"
    for done_flow in all_done_flows:
        if debug_flag:
            print "(packets: %d, fct: %.8f, bottleneck: %d flows)" % (done_flow.packet_length, done_flow.fct, done_flow.flow_bottleneck)
    fcts_aggregate = packet_info(all_done_flows)
    avg_fcts = average_fct(fcts_aggregate)
    max_fcts = max_fct(fcts_aggregate)

    packet_list = avg_fcts.keys()
    packet_list.sort()
    ret_list = []
    for packet_length in packet_list:
        print "Packet length: %d, average FCT: %.8f, max FCT: %.8f" % (packet_length, avg_fcts[packet_length], max_fcts[packet_length])
        ret_list.append((packet_length, avg_fcts[packet_length], max_fcts[packet_length]))
    return ret_list # tuples (packet_length, average fct)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        shape = float(sys.argv[1])
    if len(sys.argv) > 2:
        link_rate = float(sys.argv[2])
    if len(sys.argv) > 3:
        num_flows = int(sys.argv[3])

    scale = (shape-1.0)/shape * mean_npkts
    lamb = link_rate * (10 ** 9)/(mean_npkts*(packet_size)*8.0)

    ret_list = simulate()
    output_file = "logs/flowSizeVsDelay-sh" + str(shape)
    f = open(output_file, 'w')
    for entry in ret_list:
        f.write('%d 0 0 0 0 0 %.12f 0 %.12f\n' % entry)
    f.close()
