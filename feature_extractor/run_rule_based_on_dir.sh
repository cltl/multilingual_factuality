#!/bin/bash

for f in $1*
do
bn=$(basename $f)
echo $f
cat $f | python rule_based_factuality.py $3 > $2/$bn
done
