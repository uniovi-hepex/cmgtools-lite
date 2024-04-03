#!/bin/bash

name=$1
list=$2
nFiles=$3

if [[ $name == *"mu"* ]]; then
    echo Submitting muon training...
    root -l -b -q "trainMuonID.cxx(\"$name\", \"$list\", $nFiles)"
else
    echo Submitting electron training...
    root -l -b -q "trainElectronID.cxx(\"$name\", \"$list\", $nFiles)"
fi



