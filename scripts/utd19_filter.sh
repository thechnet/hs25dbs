#!/bin/bash

# This filter was used to create a smaller version of the UTD19 dataset.
# We always use the full dataset outside of testing.

clear

in="utd19_u.csv"
out="utd19_u-filtered.csv"

head -n 1 $in > $out
grep -E "^(?:[^,]*,){6}.*(?:basel|luzern|zurich).*" $in >> $out
