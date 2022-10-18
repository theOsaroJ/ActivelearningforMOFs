#!/bin/bash

'''
author: Etinosa Osaro, krishnendu mukherjee & Yamil J Colon
'''

#### ------- Objective ------- ####
## To run CH4 in NU800  MOF simulations until we get a max. relative error within 2%

#Making a datafile
data="Prior.csv"

#Initialising a variable called one
One=1

# Declaring the number of samples present in the prior sample
N_Samp=$(wc -l < Prior.csv)

#Removing 1 from N_Samp, since the first row was coloumn names
N_Samp=$[ $N_Samp - $One ]

#populating the top row
for ((i=1;i<=63;i++))
do
        echo -n "${i}," >> rel_true.csv
        echo -n "${i}," >> rel.csv
done

#Last row without the comma at the end
for ((i=64;i<=64;i++))
do
        echo -n "${i}" >> rel_true.csv
        echo -n "${i}" >> rel.csv
done

echo "GP-based_rel_Error,RRMSE" >> mean.csv

#going to the next line in these files
echo " " >> rel_true.csv
echo " " >> rel.csv

#Declaring a string variable Fin which would compare if the active learning was successful or not
Fin="NOT_DONE"

#for loop is finished
#Going for the max number of loops, in case if loop inside our for does not stop
for ((i=1;i<=64;i++))
do

        #creating output for python
        if [[ -f output ]]; then
        rm output
        touch output
        fi

        #Loading modules
        module load python

        # funneling the python output to output
        python3 GP.py > output

        #Initialising variables that will store the array Index for max. uncertainty, and the flag which tells if the code has converged or not
        Index=$(awk 'FNR==1 {print $1}' output)
        Flag=$(awk 'FNR==2 {print $1}' output)

        #going to the next line in these files
        echo " " >> rel_true.csv
        echo " " >> rel.csv
        echo " " >> mean.csv

        #Removing brackets in the mean.csv from rrmse output from error_estimator code
        sed -i 's/[][]//' mean.csv
        sed -i 's/[][]//' mean.csv

        #### --------- Error extraction is completed  --------- ####

        #converting Index from a string to integer
        Index=${Index#0}

        #unloading python 3.7 (the latest version) since RASPA is incompatible with Python 3.7
        module unload python

        ##Checking if the uncertainty (sigma) is lower than the limit; if not we need to do more simulations
        if [[ $Flag == $Fin ]];
        then
                # Printing whether the code has converged or not, and the index with max. uncertainty
                echo "Active learning still not finished!"
                echo $Index

                #Adding the next pressure simulation point
                N_Samp=$[ $N_Samp + $One ]

                #### ---------- Preparing for submitting the next simulation ---------- ####
                #making the directory for next simulation step
                mkdir $N_Samp
                
                #copying the forcefield, CIF and input files (simulation package) to the next simulation folder
                cp *.def *.cif *.input $N_Samp
                #changing current directory to next simulation point
                cd $N_Samp

                #changing the placeholder to Pressure
                sed -i 's/XXX/'${Index}'/' simulation.input
                #removing the brackets from input file
                sed 's/[][]//g' simulation.input

                #### ----------- Conducting the simulation ------------ ####
                #declaring variables for RASPA
                export RASPA_DIR=${HOME}/RASPA/simulations
                export DYLD_LIBRARY_PATH=${RASPA_DIR}/lib
                export LD_LIBRARY_PATH=${RASPA_DIR}/lib
                $RASPA_DIR/bin/simulate -i simulation.input
                #### ------------ Simulation is DONE ----------------- ####

                #### ----------- Extracting Uptake and then Error ------------ ####
                #changing current directory to output
                cd Output/System_0/
                #creating sample file to print output to extract relevant data
                rm -f sample.txt
                touch sample.txt
                grep -F 'Average loading absolute [cm^3 (STP)/gr framework]' *.data > sample.txt
                Uptake=$(awk 'FNR==1 { print $7 }' sample.txt)
                Error=$(awk 'FNR==1 { print $9 }' sample.txt)
                # After extracting the adsorption data and error value, printing it out
                echo "$Index,$Uptake,$Error" >> ../../../${data}
                # removing the sample file
                #### ----------- Data Extraction completed ------------ ####
                rm sample.txt

                #Changing the file location to the current one
                cd ../../
                cd ..
        else
                #In case If doesn't satisfy, (which means the uncertainty is lower than 2% for all points), break out of this loop and finish Active learning, the model is ready
                break
        fi
done
