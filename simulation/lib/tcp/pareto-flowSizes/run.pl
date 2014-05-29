#!/usr/bin/perl -w

$numFlows = 100000;
$cap = 2.4;
$rtt = 0.1;
$load = 0.8;
$numbneck = 1;
$BWdelay = ($rtt*$cap*1000000000)/(1000*8);
$init_nr_flows = 10000;
$meanFlowSize = $BWdelay/1000;
@pareto_shape = (1.6, 1.8, 2.2);

for ($i = 0; $i < @pareto_shape; $i++) {

`nice -n +20 ns sim-tcp-pareto.tcl $numFlows $cap $rtt $load $numbneck $init_nr_flows $meanFlowSize $pareto_shape[$i] > logFile`;
`mv logFile logFile-pareto-sh$pareto_shape[$i]`;
`mv flow.tr flow-pareto-sh$pareto_shape[$i].tr`;
`mv queue.tr queue-pareto-sh$pareto_shape[$i].tr`;

}

