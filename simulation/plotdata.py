#!/usr/bin/env python

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

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

# Start the graphing
SHAPES = ['1.2', '2.2']

for shape in SHAPES:
  rcp_f = "lib/rcp/pareto-flowSizes/logs/flowSizeVsDelay-sh" + shape
  tcp_f = "lib/tcp/pareto-flowSizes/logs/flowSizeVsDelay-sh" + shape

  lines = [FlowData(rcp_f, 'b', '+', 'RCP'),
           FlowData(tcp_f, '#00FF00', '.', 'TCP')]

  # Average Flow Completion Time
  fig = plt.figure()
  graph = fig.add_subplot(111)

  for line in lines:
    graph.plot(line.flowsizes, line.avg_ct, linestyle='--',
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
    graph.plot(line.flowsizes, line.avg_ct, linestyle='--',
               color=line.color, marker=line.marker, label=line.label)

  graph.set_yscale("log")
  graph.set_xscale("log")
  for axis in [graph.xaxis, graph.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
  graph.axis([0, 100000, 0.1, 100])

  graph.set_ylabel("Average Flow Completion Time [sec]")
  graph.set_xlabel("flow size [pkts] (log scale)")
  plt.legend(loc='upper left')
  plt.savefig("graphs/fig12-afct-long-" + shape + ".png", format="png")

  # Max Flow Completion Time
  fig = plt.figure()
  graph = fig.add_subplot(111)

  for line in lines:
    graph.plot(line.flowsizes, line.max_ct, linestyle='--',
               color=line.color, marker=line.marker, label=line.label)

  graph.set_yscale("log")
  for axis in [graph.xaxis, graph.yaxis]:
    axis.set_major_formatter(ScalarFormatter())
  graph.axis([0, 2000, 0.1, 100])

  graph.set_ylabel("Max. Flow Completion Time [sec]")
  graph.set_xlabel("flow size [pkts] (normal scale)")
  plt.legend(loc='upper left')
  plt.savefig("graphs/fig12-maxct-" + shape + ".png", format="png")

