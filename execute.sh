#!/bin/bash

python2 vsm.py -i queries/query-train.xml -o myrank \
              -m model -d NTCIR-dir
python2 map.py queries/ans_train.csv myrank
