#!/bin/bash

cwd=$(pwd)
sim=("lib/rcp/pareto-flowSizes/" "lib/tcp/pareto-flowSizes/")

echo "Working on RCP and TCP"
for dir in "${sim[@]}"
do
  echo "Working on $dir"
  cd $dir
  perl run.pl
  echo "> Completed run simulation."
  perl average.pl
  echo "> Completed average calculations."
  perl queueProcess.pl
  echo "> Completed queueProcess calculations."
  cd $cwd
done

echo "Working on Full PS Simulation."
# Execute Processor Sharing Simulation
cd "lib/ps/pareto-flowSizes/"
./ps-bash-sim.sh
cd $cwd

echo "Working on PS RCP Simulation."
# Execute PS RCP Simulation
cd "lib/custom-ps/pareto-flowSizes/"
python custom-ps.py
cd $cwd

echo "Plotting Data."
# Plot all Data
python plotdata.py
