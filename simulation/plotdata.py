#!/usr/bin/env python

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import math

class FlowData:

  def __init__(self, filename, color, marker, label=''):
    """ Initialize FlowData
    Give it the filename where the data resides and it will read in the
    flow sizes, the average completion times, and max completion times.

      color: The color matplotlib will use for the line.
      marker: The marker matplotlib will use for the line.
      label: The label for the line.
    """
    self.color = color
    self.marker = marker
    self.linestyle = ':'
    self.label = label
    self.flowsizes = []
    self.avg_ct = []
    self.max_ct = []

    f = open(filename, 'r')

    for line in f:
      datum = line.rsplit(' ')
      self.flowsizes.append(float(datum[0]))
      self.avg_ct.append(float(datum[6]))
      self.max_ct.append(float(datum[8]))

    f.close()

# Following are equal to those set in simulation and needed for
# slow start analysis.
RTT = 0.1                   # Sec
C = 2.4*1000000000/(1000*8) # Pkts/Sec
LOAD = 0.9

def slowstart(L):
  """ Calculates SlowStart
  Why Flow-Completion Time is the Right metric for Congestion Control
  and why this means we need new algorithms
  Nandita Dukkipati, Nick McKeown
  http://yuba.stanford.edu/techreports/TR05-HPNG-112102.pdf
  Page 2
  """
  return (math.log(L + 1, 2) + 0.5)*RTT + L/C

class SlowStart:

  def __init__(self, maxsize, color):
    """ Initialize SlowStart Data
    Calculates slowstart average completion time from 0 to maxsize flows.
    """
    self.color = color
    self.marker = None
    self.linestyle = '-'
    self.label = "Slow Start"

    self.flowsizes = list(xrange(maxsize + 1))
    self.avg_ct = map(slowstart, self.flowsizes)
    self.max_ct = self.avg_ct

def ps(L):
  """ Calculates Processor Sharing
  Processor Sharing Flows in the Internet
  Nandita Dukkipati, Masayoshi Kobayashi, Rui Zhang-Shen, and Nick McKeown
  http://yuba.stanford.edu/~nanditad/RCP-IWQoS.pdf
  Page 10 (Page 276 on article)
  """
  return 1.5*RTT + L/(C*(1-LOAD))

class ProcessorSharing:

  def __init__(self, maxsize, color):
    """ Initialize Processor Sharing Data
    Calculates given processor sharing algorithm.
    """
    self.color = color
    self.marker = None
    self.linestyle = '-'
    self.label = "Processor Sharing"

    self.flowsizes = list(xrange(maxsize + 1))
    self.avg_ct = map(ps, self.flowsizes)
    self.max_ct = self.avg_ct

# Plotting
def save_figure(lines, axis_range, ylabel, xlabel, savefn, log_y=True, log_x=False):
  fig = plt.figure()
  graph = fig.add_subplot(111)

  for line in lines:
    graph.plot(line.flowsizes, line.max_ct, linestyle=line.linestyle,
               color=line.color, marker=line.marker, label=line.label)

  if log_y:
    graph.set_yscale("log")
  if log_x:
    graph.set_xscale("log")

  for axis in [graph.xaxis, graph.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
  graph.axis(axis_range)

  graph.set_ylabel(ylabel)
  graph.set_xlabel(xlabel)
  plt.legend(loc='upper left')
  plt.savefig(savefn, format="png")

# Start the graphing /////////////////////////////////////////////////////////

SHAPES = ['1.2', '2.2']

for shape in SHAPES:
  rcp_f = "lib/rcp/pareto-flowSizes/logs/flowSizeVsDelay-sh" + shape
  tcp_f = "lib/tcp/pareto-flowSizes/logs/flowSizeVsDelay-sh" + shape
  cps1_f  = "lib/ps/pareto-flowSizes/logs/flowSizeVsDelay-sh" + shape
  cps2_f = "lib/custom-ps/pareto-flowSizes/logs/flowSizeVsDelay-sh" + shape

  tcp_l = FlowData(tcp_f, '#00FF00', '.', 'TCP')
  rcp_l = FlowData(rcp_f, 'b', '+', 'RCP')
  ss_l = SlowStart(200000, 'r')
  ps_l = ProcessorSharing(200000, 'r')
  custom_ps_1 = FlowData(cps1_f, 'm', '.', 'Full PS Simulated')
  custom_ps_2 = FlowData(cps2_f, 'c', '.', 'PS Simulated')

  # Graph to look like those in paper
  lines = [tcp_l, rcp_l, ss_l, ps_l]
  # Average Flow Completion Time
  save_figure(lines,
              [0, 2000, 0.1, 100],
              "Average Flow Completion Time [sec]",
              "flow size [pkts] (normal scale)",
              "graphs/fig12-afct-tcp-rcp-" + shape + ".png",
              True,
              False)

  # Average Flow Completion Time (Long flows)
  save_figure(lines,
              [10, 100000, 0.1, 100],
              "Average Flow Completion Time [sec]",
              "flow size [pkts] (log scale)",
              "graphs/fig12-afct-long-tcp-rcp-" + shape + ".png",
              True,
              True)

  # Max Flow Completion Time
  save_figure(lines,
              [0, 2000, 0.1, 100],
              "Max. Flow Completion Time [sec]",
              "flow size [pkts] (normal scale)",
              "graphs/fig12-maxct-tcp-rcp-" + shape + ".png",
              True,
              False)

  # Graphs with Processor Sharing (Custom 1)
  ps_l.color = 'k'
  lines = [custom_ps_1, rcp_l, ps_l]
  # Average Flow Completion Time
  save_figure(lines,
              [0, 2000, 0.1, 10],
              "Average Flow Completion Time [sec]",
              "flow size [pkts] (normal scale)",
              "graphs/fig12-afct-custom-ps-1-" + shape + ".png",
              True,
              False)

  # Average Flow Completion Time (Long flows)
  save_figure(lines,
              [10, 100000, 0.1, 100],
              "Average Flow Completion Time [sec]",
              "flow size [pkts] (log scale)",
              "graphs/fig12-afct-long-custom-ps-1-" + shape + ".png",
              True,
              True)

  # Max Flow Completion Time
  save_figure(lines,
              [0, 2000, 0.1, 10],
              "Max. Flow Completion Time [sec]",
              "flow size [pkts] (normal scale)",
              "graphs/fig12-maxct-custom-ps-1-" + shape + ".png",
              True,
              False)

  # Graphs with Processor Sharing (Custom 2)
  ps_l.color = 'k'
  lines = [custom_ps_2, rcp_l, ps_l]
  # Average Flow Completion Time
  save_figure(lines,
              [0, 2000, 0.1, 10],
              "Average Flow Completion Time [sec]",
              "flow size [pkts] (normal scale)",
              "graphs/fig12-afct-custom-ps-2-" + shape + ".png",
              True,
              False)

  # Average Flow Completion Time (Long flows)
  save_figure(lines,
              [10, 100000, 0.1, 100],
              "Average Flow Completion Time [sec]",
              "flow size [pkts] (log scale)",
              "graphs/fig12-afct-long-custom-ps-2-" + shape + ".png",
              True,
              True)

  # Max Flow Completion Time
  save_figure(lines,
              [0, 2000, 0.1, 10],
              "Max. Flow Completion Time [sec]",
              "flow size [pkts] (normal scale)",
              "graphs/fig12-maxct-custom-ps-2-" + shape + ".png",
              True,
              False)

