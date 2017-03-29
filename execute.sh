#!/bin/bash

python2 vsm.py -i queries/query-train.xml -o myrank.csv \
              -m model -d NTCIR-dir 2 1.15 0.95
python2 map.py queries/ans_train.csv myrank.csv
