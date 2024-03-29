#! /bin/bash
#$ -q hpc@@colon
#$ -pe smp 1
#$ -N CU-BTC_CH4

export RASPA_DIR=${HOME}/RASPA/simulations/
export DYLD_LIBRARY_PATH=${RASPA_DIR}/lib
export LD_LIBRARY_PATH=${RASPA_DIR}/lib
$RASPA_DIR/bin/simulate -i simulation.input
