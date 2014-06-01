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
      self.flowsizes.append(int(datum[0]))
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

  def __init__(self, maxsize):
    """ Initialize SlowStart Data
    Calculates slowstart average completion time from 0 to maxsize flows.
    """
    self.color = 'r'
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

  def __init__(self, maxsize):
    """ Initialize Processor Sharing Data
    Calculates given processor sharing algorithm.
    """
    self.color = 'r'
    self.marker = None
    self.linestyle = ':'
    self.label = "Processor Sharing"

    self.flowsizes = list(xrange(maxsize + 1))
    self.avg_ct = map(ps, self.flowsizes)
    self.max_ct = self.avg_ct

# Start the graphing
SHAPES = ['1.2', '2.2']

for shape in SHAPES:
  rcp_f = "lib/rcp/pareto-flowSizes/logs/flowSizeVsDelay-sh" + shape
  tcp_f = "lib/tcp/pareto-flowSizes/logs/flowSizeVsDelay-sh" + shape
  ps_f  = "lib/ps/pareto-flowSizes/logs/flowSizeVsDelay-sh" + shape

  lines = [FlowData(rcp_f, 'b', '+', 'RCP'),
           FlowData(tcp_f, '#00FF00', '.', 'TCP'),
           SlowStart(200000),
           ProcessorSharing(200000)]
           FlowData(ps_f, 'm', '.', 'Custom PS')]

  # Average Flow Completion Time
  fig = plt.figure()
  graph = fig.add_subplot(111)

  for line in lines:
    graph.plot(line.flowsizes, line.avg_ct, linestyle=line.linestyle,
               color=line.color, marker=line.marker, label=line.label)

  graph.set_yscale("log")
  for axis in [graph.xaxis, graph.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
  graph.axis([0, 2000, 0.1, 100])

  graph.set_ylabel("Average Flow Completion Time [sec]")
  graph.set_xlabel("flow size [pkts] (normal scale)")
  plt.legend(loc='upper left')
  plt.savefig("graphs/fig12-afct-" + shape + ".png", format="png")

  # Average Flow Completion Time (Long flows)
  fig = plt.figure()
  graph = fig.add_subplot(111)

  for line in lines:
    graph.plot(line.flowsizes, line.avg_ct, linestyle=line.linestyle,
               color=line.color, marker=line.marker, label=line.label)

  graph.set_yscale("log")
  graph.set_xscale("log")
  for axis in [graph.xaxis, graph.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
  graph.axis([10, 100000, 0.1, 100])

  graph.set_ylabel("Average Flow Completion Time [sec]")
  graph.set_xlabel("flow size [pkts] (log scale)")
  plt.legend(loc='upper left')
  plt.savefig("graphs/fig12-afct-long-" + shape + ".png", format="png")

  # Max Flow Completion Time
  fig = plt.figure()
  graph = fig.add_subplot(111)

  for line in lines:
    graph.plot(line.flowsizes, line.max_ct, linestyle=line.linestyle,
               color=line.color, marker=line.marker, label=line.label)

  graph.set_yscale("log")
  for axis in [graph.xaxis, graph.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
  graph.axis([0, 2000, 0.1, 100])

  graph.set_ylabel("Max. Flow Completion Time [sec]")
  graph.set_xlabel("flow size [pkts] (normal scale)")
  plt.legend(loc='upper left')
  plt.savefig("graphs/fig12-maxct-" + shape + ".png", format="png")

