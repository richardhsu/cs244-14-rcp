
Class TCP_pair

#Variables:
#tcps tcpr:  Sender TCP, Receiver TCP
#sn   dn  :  source/dest node which TCP sender/receiver exist
#:  (only for setup_wnode)
#delay    :  delay between sn and san (dn and dan)
#:  (only for setup_wnode)
#san  dan :  nodes to which sn/dn are attached
#aggr_ctrl:  Agent_Aggr_pair for callback
#start_cbfunc:  callback at start
#fin_cbfunc:  callback at start
#group_id :  group id
#pair_id  :  group id
#id       :  flow id
#Public Functions:
#setup{snode dnode}       <- either of them
#setup_wnode{snode dnode} <- must be called
#setgid {gid}             <- if applicable (default 0)
#setpairid {pid}          <- if applicable (default 0)
#setfid {fid}             <- if applicable (default 0)
#start { nr_pkts } ;# let start sending nr_pkts
#set_debug_mode { mode }    ;# change to debug_mode
#setcallback { controller } #; only Agent_Aggr_pair uses to
##; registor itself
#fin_notify {}  #; Callback .. this is called
##; by agent when it finished
#Private Function
#flow_finished {} {

TCP_pair instproc init {args} {
    $self instvar pair_id group_id id debug_mode
    $self instvar tcps tcpr;# Sender TCP,  Receiver TCP

    eval $self next $args

    $self set tcps [new Agent/TCP/Reno]  ;# Sender TCP
    $self set tcpr [new Agent/TCPSink]  ;# Receiver TCP

    $tcps set_callback $self
#$tcpr set_callback $self

    $self set pair_id  0
    $self set group_id 0
    $self set id       0
    $self set debug_mode 1
}

TCP_pair instproc set_debug_mode { mode } {
    $self instvar debug_mode
    $self set debug_mode $mode
}


TCP_pair instproc setup {snode dnode} {
#Directly connect agents to snode, dnode.
#For faster simulation.
    global ns link_rate
    $self instvar tcps tcpr;# Sender TCP,  Receiver TCP
    $self instvar san dan  ;# memorize dumbell node (to attach)

    $self set san $snode
    $self set dan $dnode

    $ns attach-agent $snode $tcps;
    $ns attach-agent $dnode $tcpr;

    $ns connect $tcps $tcpr
}

TCP_pair instproc create_agent {} {
    $self instvar tcps tcpr;# Sender TCP,  Receiver TCP
    $self set tcps [new Agent/TCP/Reno]  ;# Sender TCP
    $self set tcpr [new Agent/TCPSink]  ;# Receiver TCP
}

TCP_pair instproc setup_wnode {snode dnode link_dly} {

#New nodes are allocated for sender/receiver agents.
#They are connected to snode/dnode with link having delay of link_dly.
#Caution: If the number of pairs is large, simulation gets way too slow,
#and memory consumption gets very very large..
#Use "setup" if possible in such cases.

    global ns link_rate
    $self instvar sn dn    ;# Source Node, Dest Node
    $self instvar tcps tcpr;# Sender TCP,  Receiver TCP
    $self instvar san dan  ;# memorize dumbell node (to attach)
    $self instvar delay    ;# local link delay

    $self set delay link_dly

    $self set sn [$ns node]
    $self set dn [$ns node]

    $self set san $snode
    $self set dan $dnode

    $ns duplex-link $snode $sn  [set link_rate]Gb $delay  DropTail
    $ns duplex-link $dn $dnode  [set link_rate]Gb $delay  DropTail

    $ns attach-agent $sn $tcps;
    $ns attach-agent $dn $tcpr;

    $ns connect $tcps $tcpr
}

TCP_pair instproc set_fincallback { controller func} {
    $self instvar aggr_ctrl fin_cbfunc
    $self set aggr_ctrl  $controller
    $self set fin_cbfunc  $func
}

TCP_pair instproc set_startcallback { controller func} {
    $self instvar aggr_ctrl start_cbfunc
    $self set aggr_ctrl $controller
    $self set start_cbfunc $func
}

TCP_pair instproc setgid { gid } {
    $self instvar group_id
    $self set group_id $gid
}

TCP_pair instproc setpairid { pid } {
    $self instvar pair_id
    $self set pair_id $pid
}

TCP_pair instproc setfid { fid } {
    $self instvar tcps tcpr
    $self instvar id
    $self set id $fid
    $tcps set fid_ $fid;
    $tcpr set fid_ $fid;
}

TCP_pair instproc set_debug_mode { mode } {
    $self instvar debug_mode
    $self set debug_mode $mode
}

TCP_pair instproc start { nr_pkts } {
    global ns
    $self instvar tcps id group_id
    $self instvar start_time pkts
    $self instvar aggr_ctrl start_cbfunc

    $self instvar debug_mode

    $self set start_time [$ns now] ;# memorize
    $self set pkts       $nr_pkts  ;# memorize
    set pktsize [$tcps set packetSize_]

    if { $debug_mode == 1 } {
	puts "stats: [$ns now] start grp $group_id fid $id $nr_pkts pkts ($pktsize +40)"
    }

    if { [info exists aggr_ctrl] } {
	$aggr_ctrl $start_cbfunc
    }
    $tcps send [expr $pktsize * $nr_pkts]
}


TCP_pair instproc stop {} {
    $self instvar tcps tcpr

    $tcps reset
    $tcpr reset
}

TCP_pair instproc fin_notify {} {
    global ns
    $self instvar sn dn san dan
    $self instvar tcps tcpr
    $self instvar aggr_ctrl fin_cbfunc
    $self instvar pair_id
    $self instvar pkts

    $self instvar dt
    $self instvar pps

    $self flow_finished

    $tcps reset
    $tcpr reset

    if { [info exists aggr_ctrl] } {
	$aggr_ctrl $fin_cbfunc $pair_id $pkts $dt $pps
    }
}

TCP_pair instproc flow_finished {} {
    global ns
    $self instvar start_time pkts id group_id
    $self instvar dt pps
    $self instvar debug_mode

    set ct [$ns now]
    $self set dt  [expr $ct - $start_time]
    $self set pps [expr $pkts / $dt ]

    if { $debug_mode == 1 } {
	puts "stats: $ct fin grp $group_id fid $id fldur $dt sec $pps pps"
    }
}

Agent/TCP/Reno instproc set_callback {tcp_pair} {
    $self instvar ctrl
    $self set ctrl $tcp_pair
}

Agent/TCP/Reno instproc done {} {
    global ns sink
    $self instvar ctrl
#puts "[$ns now] $self fin-ack received";
    if { [info exists ctrl] } {
	$ctrl fin_notify
    }
}

Class Agent_Aggr_pair
#Note:
#Contoller and placeholder of Agent_pairs
#Let Agent_pairs to arrives according to
#random process.
#Currently, the following two processes are defined
#- PParrival:
#flow arrival is poissson and
#each flow contains pareto
#distributed number of packets.
#- PEarrival
#flow arrival is poissson and
#each flow contains pareto
#distributed number of packets.
#- PBarrival
#flow arrival is poissson and
#each flow contains bimodal
#distributed number of packets.

#Variables:#
#apair:    array of Agent_pair
#nr_pairs: the number of pairs
#rv_flow_intval: (r.v.) flow interval
#rv_npkts: (r.v.) the number of packets within a flow
#last_arrival_time: the last flow starting time
#logfile: log file (should have been opend)
#stat_nr_finflow ;# statistics nr  of finished flows
#stat_sum_fldur  ;# statistics sum of finished flow durations
#fid             ;# current flow id of this group
#last_arrival_time ;# last flow arrival time
#actfl             ;# nr of current active flow
#stat_nr_arrflow  ;# statistics nr of arrived flows
#stat_nr_arrpkts  ;# statistics nr of arrived packets

#Public functions:
#attach-logfile {logf}  <- call if want logfile
#setup {snode dnode gid nr} <- must
#set_PParrival_process {lambda mean_npkts shape rands1 rands2}  <- call either
#set_PEarrival_process {lambda mean_npkts rands1 rands2}        <-
#set_PBarrival_process {lambda mean_npkts S1 S2 rands1 rands2}  <- of them
#init_schedule {}       <- must
#statistics   {}         ;# Print statistics

#fin_notify { pid pkts fldur pps } ;# Callback
#start_notify {}                   ;# Callback

#Private functions:
#init {args}
#resetvars {}


Agent_Aggr_pair instproc init {args} {
    eval $self next $args
}


Agent_Aggr_pair instproc attach-logfile { logf } {
#Public
    $self instvar logfile
    $self set logfile $logf
}

Agent_Aggr_pair instproc setup {snode dnode gid nr agent_pair_type} {
#Public
#Note:
#Create nr pairs of Agent_pair
#and connect them to snode-dnode bottleneck.
#We may refer this pair by group_id gid.
#All Agent_pairs have the same gid,
#and each of them has its own flow id [0 .. nr-1]

    $self instvar apair     ;# array of Agent_pair
    $self instvar group_id  ;# group id of this group (given)
    $self instvar nr_pairs  ;# nr of pairs in this group (given)

    $self set group_id $gid
    $self set nr_pairs $nr

    for {set i 0} {$i < $nr_pairs} {incr i} {
 	$self set apair($i) [new $agent_pair_type]
	$apair($i) setup $snode $dnode
	$apair($i) setgid $group_id  ;# let each pair know our group id
	$apair($i) setpairid $i      ;# let each pair know his pair id
    }
    $self resetvars                  ;# other initialization
}


Agent_Aggr_pair instproc init_schedule {} {
#Public
#Note:
#Initially schedule flows for all pairs
#according to the arrival process.
    global ns
    $self instvar nr_pairs apair
    for {set i 0} {$i < $nr_pairs} {incr i} {

	#### Callback Setting ########################
	$apair($i) set_fincallback $self   fin_notify
	$apair($i) set_startcallback $self start_notify
	###############################################

	$self schedule $i
    }
}


Agent_Aggr_pair instproc set_PParrival_process {lambda mean_npkts shape rands1 rands2} {
#Public
#setup random variable rv_flow_intval and rv_npkts.
#To get the r.v.  call "value" function.
#ex)  $rv_flow_intval  value

#- PParrival:
#flow arrival: poissson with rate $lambda
#flow length : pareto with mean $mean_npkts pkts and shape parameter $shape.

    $self instvar rv_flow_intval rv_npkts

    set pareto_shape $shape
    set rng1 [new RNG]

    $rng1 seed $rands1
    $self set rv_flow_intval [new RandomVariable/Exponential]
    $rv_flow_intval use-rng $rng1
    $rv_flow_intval set avg_ [expr 1.0/$lambda]

    set rng2 [new RNG]
    $rng2 seed $rands2
    $self set rv_npkts [new RandomVariable/Pareto]
    $rv_npkts use-rng $rng2
    $rv_npkts set avg_ $mean_npkts
    $rv_npkts set shape_ $pareto_shape
}

Agent_Aggr_pair instproc set_PEarrival_process {lambda mean_npkts rands1 rands2} {

#setup random variable rv_flow_intval and rv_npkts.
#To get the r.v.  call "value" function.
#ex)  $rv_flow_intval  value

#- PEarrival
#flow arrival: poissson with rate lambda
#flow length : exp with mean mean_npkts pkts.

    $self instvar rv_flow_intval rv_npkts

    set rng1 [new RNG]
    $rng1 seed $rands1

    $self set rv_flow_intval [new RandomVariable/Exponential]
    $rv_flow_intval use-rng $rng1
    $rv_flow_intval set avg_ [expr 1.0/$lambda]


    set rng2 [new RNG]
    $rng2 seed $rands2
    $self set rv_npkts [new RandomVariable/Exponential]
    $rv_npkts use-rng $rng2
    $rv_npkts set avg_ $mean_npkts
}

Agent_Aggr_pair instproc set_PBarrival_process {lambda mean_npkts S1 S2 rands1 rands2} {
#Public
#setup random variable rv_flow_intval and rv_npkts.
#To get the r.v.  call "value" function.
#ex)  $rv_flow_intval  value

#- PParrival:
#flow arrival: poissson with rate $lambda
#flow length : pareto with mean $mean_npkts pkts and shape parameter $shape.

    $self instvar rv_flow_intval rv_npkts

    set rng1 [new RNG]

    $rng1 seed $rands1
    $self set rv_flow_intval [new RandomVariable/Exponential]
    $rv_flow_intval use-rng $rng1
    $rv_flow_intval set avg_ [expr 1.0/$lambda]

    set rng2 [new RNG]

    $rng2 seed $rands2
    $self set rv_npkts [new Binomial_RV]
    $rv_npkts use-rng $rng2

    $rv_npkts set p_ [expr  (1.0*$mean_npkts - $S2)/($S1-$S2)]
    $rv_npkts set S1_ $S1
    $rv_npkts set S2_ $S2

    if { $p < 0 } {
	puts "In PBarrival, prob for bimodal p_ is negative %p_ exiting.. "
	exit 0
    } else {
	puts "# PBarrival S1: $S1 S2: $S2 p_: $p_ mean $mean_npkts"
    }

}

Agent_Aggr_pair instproc resetvars {} {
#Private
#Reset variables
    $self instvar stat_nr_finflow ;# statistics nr  of finished flows
    $self instvar stat_sum_fldur  ;# statistics sum of finished flow durations
    $self instvar fid             ;# current flow id of this group
    $self instvar last_arrival_time ;# last flow arrival time
    $self instvar actfl             ;# nr of current active flow
    $self instvar stat_nr_arrflow  ;# statistics nr of arrived flows
    $self instvar stat_nr_arrpkts  ;# statistics nr of arrived packets

    $self set last_arrival_time 0.0
    $self set fid 0 ;#  flow id starts from 0
    $self set stat_nr_finflow 0
    $self set stat_sum_fldur 0.0
    $self set stat_sum_pps 0.0
    $self set actfl 0
    $self set stat_nr_arrflow 0
    $self set stat_nr_arrpkts 0
}

Agent_Aggr_pair instproc schedule { pid } {
#Private
#Note:
#Schedule  pair (having pid) next flow time
#according to the flow arrival process.

    global ns
    $self instvar apair
    $self instvar fid
    $self instvar last_arrival_time
    $self instvar rv_flow_intval rv_npkts
    $self instvar stat_nr_arrflow
    $self instvar stat_nr_arrpkts


    set dt [$rv_flow_intval value]
    set tnext [expr $last_arrival_time + $dt]
    set t [$ns now]

    if { $t > $tnext } {
	puts "Error, Not enough flows ! Aborting! pair id $pid"
	flush stdout
	exit
    }
    $self set last_arrival_time $tnext

    $apair($pid) setfid $fid
    incr fid

    set tmp_ [expr ceil ([$rv_npkts value])]

    incr stat_nr_arrflow
    $self set stat_nr_arrpkts [expr $stat_nr_arrpkts + $tmp_]

    $ns at $tnext "$apair($pid) start $tmp_"
}


Agent_Aggr_pair instproc fin_notify { pid pkts fldur pps } {
#Callback Function
#pid  : pair_id
#pkts : nr of pkts of the flow which has just finished
#fldur: duration of the flow which has just finished
#pps  : avg packet/sec of the flow which has just finished
#Note:
#If we registor $self as "setcallback" of
#$apair($id), $apair($i) will callback this
#function with argument id when the flow between the pair finishes.
#i.e.
#If we set:  "$apair(13) setcallback $self" somewhere,
#"fin_notify 13 $pkts $fldur $pps" is called when the $apair(13)'s flow is finished.
#
    global ns
    $self instvar logfile
    $self instvar stat_sum_fldur stat_nr_finflow stat_sum_pps
    $self instvar group_id
    $self instvar actfl
    $self instvar apair

    #Here, we re-schedule $apair($pid).
    #according to the arrival process.

    $self set actfl [expr $actfl - 1]

    incr stat_nr_finflow
    $self set stat_sum_fldur [expr $stat_sum_fldur + $fldur]
    $self set stat_sum_pps   [expr $stat_sum_pps   + $pps]

    set fin_fid [$apair($pid) set id]

    ###### OUPUT STATISTICS #################
    if { [info exists logfile] } {
        puts $logfile "flow_stats: [$ns now] gid $group_id fid $fin_fid pkts $pkts fldur $fldur avgfldur [expr $stat_sum_fldur/$stat_nr_finflow] actfl $actfl avgpps [expr $stat_sum_pps/$stat_nr_finflow] finfl $stat_nr_finflow"

	}

    $self schedule $pid ;# re-schedule a pair having pair_id $pid.
}

Agent_Aggr_pair instproc start_notify {} {
#Callback Function
#Note:
#If we registor $self as "setcallback" of
#$apair($id), $apair($i) will callback this
#function with argument id when the flow between the pair finishes.
#i.e.
#If we set:  "$apair(13) setcallback $self" somewhere,
#"start_notyf 13" is called when the $apair(13)'s flow is started.
    $self instvar actfl;
    incr actfl;
}


Agent_Aggr_pair instproc statistics {} {
    $self instvar stat_nr_finflow ;# statistics nr  of finished flows
    $self instvar stat_sum_fldur  ;# statistics sum of finished flow durations
    $self instvar fid             ;# current flow id of this group
    $self instvar last_arrival_time ;# last flow arrival time
    $self instvar actfl             ;# nr of current active flow
    $self instvar stat_nr_arrflow  ;# statistics nr of arrived flows
    $self instvar stat_nr_arrpkts  ;# statistics nr of arrived packets

    puts "Aggr_pair statistics1: $self arrflows $stat_nr_arrflow finflow $stat_nr_finflow remain [expr $stat_nr_arrflow - $stat_nr_finflow]"
    puts "Aggr_pair statistics2: $self arrpkts $stat_nr_arrpkts avg_flowsize [expr $stat_nr_arrpkts/$stat_nr_arrflow]"
}

#add/remove packet headers as required
#this must be done before create simulator, i.e., [new Simulator]
remove-all-packet-headers       ;# removes all except common
add-packet-header Flags IP TCP  ;# hdrs reqd for TCP (Do not remove "Flags")

set ns [new Simulator]
#puts "Date: [clock format [clock seconds]]"  # Errors in newer TCL
set sim_start [clock seconds]
puts "Host: [exec uname -a]"

#set tf [open traceall.tr w]
#$ns trace-all $tf
#set nf [open out.nam w]
#$ns namtrace-all $nf

if {$argc != 8} {
    puts "usage: ns xxx.tcl numflows link_rate(Gbps) RTT(per hop,sec) load numbneck init_nr_flows meanFlowSize pareto_shape"
    exit 0
}
set numflows [lindex $argv 0]
set link_rate [lindex $argv 1]
set mean_link_delay [expr [lindex $argv 2] / 2.0]
set load [lindex $argv 3]
set numbneck 1
set init_nr_flow [lindex $argv 5]
set mean_npkts [lindex $argv 6]
set pareto_shape [lindex $argv 7]

puts "Simulation input:"
puts "TCP Single bottleneck"
puts "numflows $numflows"
puts "link_rate $link_rate Gbps"
puts "RTT  [expr $mean_link_delay * 2.0] sec"
puts "load $load"
puts "numbneck $numbneck"
puts "init_nr_flow $init_nr_flow"
puts "mean flow size $mean_npkts pkts"
puts "pareto shape $pareto_shape"
puts " "

#packet size is in bytes.
set pktSize 960
puts "pktSize(payload) $pktSize Bytes"
puts "pktSize(include header) [expr $pktSize + 40] Bytes"

#Random Seed
set arrseed  4
set pktseed  7
puts "arrseed $arrseed pktseed $pktseed"

set lambda [expr ($link_rate*$load*1000000000)/($mean_npkts*($pktSize+40)*8.0)]
puts "Arrival: Poisson with lambda $lambda, FlowSize: Pareto with avg $mean_npkts pkts shape $pareto_shape"

set sim_end  3000
puts "sim_end $sim_end sec (may not be reached)"

#Only for TCP
Agent/TCP/Newreno set packetSize_ $pktSize
Agent/TCP/Reno set packetSize_ $pktSize
set tcpwin_ [expr 4 * int (ceil (($mean_link_delay * 2.0 * $link_rate * 1000000000.0/8.0) / ($pktSize+40.0)))]
Agent/TCP set window_ $tcpwin_
Agent/TCP/Newreno set window_ $tcpwin_
Agent/TCP/Reno set window_ $tcpwin_
puts "Agent/TCP set window_ $tcpwin_"

############ Buffer SIZE ######################

#In case TCP , BWxRTT
set queueSize [expr int (ceil (($mean_link_delay * 2.0 * $link_rate * 1000000000.0/8.0) / ($pktSize+40.0)))]

Queue set limit_ $queueSize
puts "queueSize $queueSize packets"

############# Topoplgy #########################
set n0    [$ns node]
set n1    [$ns node]

$ns duplex-link $n0 $n1    [set link_rate]Gb $mean_link_delay DropTail
set bnecklink [$ns link $n0 $n1]

#############  Agents          #########################
set agtagr0 [new Agent_Aggr_pair]
puts "Creating initial $init_nr_flow agents ..."; flush stdout

$agtagr0 setup $n0 $n1 0 $init_nr_flow "TCP_pair"

set flowlog [open flow.tr w]
$agtagr0 attach-logfile $flowlog

puts "Initial agent creation done";flush stdout
#For Poisson/Pareto
$agtagr0 set_PParrival_process $lambda $mean_npkts  $pareto_shape $arrseed $pktseed

$agtagr0 init_schedule

puts "Simulation started!"

$ns at 0.0 "check_fin"

proc check_fin {} {
    global ns agtagr0 numflows
    set nrf [$agtagr0 set stat_nr_finflow]
    if { $nrf > $numflows } {
	$agtagr0 statistics
	finish
    }
#puts "nr_finflow $nrf"
    $ns after 1 "check_fin"
}


#############  Queue Monitor   #########################
set qf [open queue.tr w]
set qm [$ns monitor-queue $n0 $n1 $qf 0.1]
$bnecklink queue-sample-timeout
#$bnecklink start-tracing

$ns at $sim_end "finish"

proc finish {} {
    global ns qf flowlog
    global sim_start
    $ns flush-trace
    close $qf
    close $flowlog

    set t [clock seconds]
    puts "Simulation Finished!"
    puts "Time [expr $t - $sim_start] sec"
#    puts "Date [clock format [clock seconds]]"  # Errors in newer TCL
    exit 0
}

$ns run
