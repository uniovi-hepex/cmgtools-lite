#!/bin/bash
mode=$1
extra=$2 

cmd="python3 wz-run3/wz-run.py plot"
cmd="$cmd --mca wz-run3/checkLeptons/mca-2lOS.txt"
cmd="$cmd --plotfile wz-run3/checkLeptons/plots-leptonSF-xvars.txt"
cmd="$cmd --cutfile wz-run3/checkLeptons/cuts-OS.txt" 
cmd="$cmd --unc --uncfile wz-run3/checkLeptons/systs-leptons.txt" 
cmd="$cmd --ncores 16" 


# Produce plots per data taking era, weighted
for year in 2022 2022EE all; do

  echo ">> Submitting job for era $era (year $year)"
  echo "  + Mode: $mode"
  
  cmd_era="$cmd --year $year "
  case $mode in
    noWeight)
        cmd_era="$cmd_era --unweight --extra \"-E ^flav_ee\" "
    ;;
    noLeptonWeights)
        cmd_era="$cmd_era --unweight --extra \"-E ^flav_ee -W 'puWeight*bTagWeight'\" " 
    ;;
    onlyRecoWeights)
        cmd_era="$cmd_era --unweight --extra \"-E ^flav_ee -W 'puWeight*bTagWeight*electronSF_recoHighPt*electronSF_recoMidPt*electronSF_recoLowPt'\" " 
    ;;
    allWeights)
        cmd_era="$cmd_era --extra \"-E ^flav_ee\" " 
    ;;
  esac
  echo $cmd_era --outname validate_electrons/$year/$mode $extra | bash 
done



