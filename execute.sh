#!/bin/bash

touch log
for i in 1.9 2 2.1
do
    for j in 1.1 1.15 1.2
    do
	for k in 1.0 1.05 1.1
	do
            python2 vsm.py -i queries/query-train.xml -o myrank \
                           -m model -d NTCIR-dir $i $j $k
	    echo 't = '$i 'q = ' $j 'k = ' $k >> log
            python2 map.py queries/ans_train.csv myrank >> log
        done
    done
done
