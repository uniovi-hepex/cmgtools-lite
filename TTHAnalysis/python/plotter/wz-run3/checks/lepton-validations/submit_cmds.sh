#!/bin/bash

dataset=$1
mode=$2
ch=$3
extra=$4

if [[ $ch == *"mu"* ]]; then
  flavor="flav_mm"
elif [[ $ch == *"el"* ]]; then
  flavor="flav_ee"
fi

cmd="python3 wz-run3/wz-run.py plot"
cmd="$cmd --plotfile wz-run3/checkLeptons/plots-leptonSF-xvars.txt"
cmd="$cmd --cutfile wz-run3/checkLeptons/cuts-OS.txt" 
cmd="$cmd --unc --uncfile wz-run3/checkLeptons/systs-leptons.txt" 
cmd="$cmd --ncores 32" 


function plot() {
  mode=$1
  cmd_era=$2
  outfolder=$3
  flavor=$4
  extra=$5
  case $mode in
    noWeight)
        cmd_era="$cmd_era --unweight --extra \"-E ^$flavor\" "
    ;;
    noLeptonWeights)
        cmd_era="$cmd_era --unweight --extra \"-E ^$flavor -W 'puWeight*bTagWeight'\" " 
    ;;
    onlyRecoWeights)
        cmd_era="$cmd_era --unweight --extra \"-E ^$flavor -W 'puWeight*bTagWeight*electronSF_recoHighPt*electronSF_recoMidPt*electronSF_recoLowPt'\" " 
    ;;
    allWeights)
        cmd_era="$cmd_era --extra \"-E ^$flavor\" " 
    ;;
  esac
  echo $cmd_era --outname validate_leptons/$flavor/$outfolder/$mode $extra | bash 
}

function plot_by_era() {
  # Produce plots per data taking era, weighted
  cmd=$1
  extra=$2
  flavor=$3
  eras="C D E F G"
  cmd="$cmd --mca wz-run3/checkLeptons/mca-2lOS-perEra.txt"
  for era in $eras; do
    if [[ $era == C || $era == D ]]; then
      year=2022
    else
      year=2022EE
    fi
  
    echo ">> Submitting job for era $era (year $year)"
    echo "  + Mode: $mode"
    
    cmd_era="$cmd --year $year --era 2022$era "
    plot $mode "$cmd_era" 2022$era $flavor $extra
  done
}

function plot_by_year() {
  # Produce plots per data taking year, weighted, all eras included
  cmd=$1
  extra=$2
  flavor=$3
  cmd="$cmd --mca wz-run3/checkLeptons/mca-2lOS.txt"
  for year in 2022 2022EE all; do
    echo ">> Submitting job for era $era (year $year)"
    echo "  + Mode: $mode"
    cmd_era="$cmd --year $year "
    plot $mode "$cmd_era" $year $flavor $extra
  done
}

if [[ $dataset == "perEra" ]]; then 
  plot_by_era "$cmd" $extra $flavor
elif [[ $dataset == "perYear" ]]; then 
  plot_by_year "$cmd" $extra $flavor 
fi 
