#!/bin/bash

touch log
for i in 0.95 1 1.05 1.1 1.15 1.2 1.5 2
do
    for j in 0.95 1 1.05 1.1 1.15 1.2 1.5 2
    do 
        python2 vsm.py -i queries/query-train.xml -o myrank \
                       -m model -d NTCIR-dir $i $j
	echo 't = '$i 'q = ' $j >> log
        python2 map.py queries/ans_train.csv myrank >> log
    done
done
