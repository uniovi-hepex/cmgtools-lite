# Script to test mvas
inpath=/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/ttSemilep_nanoAODv12_postEE/testing/

year=$1
if [[ -z $year ]]; then
  echo Please select a year for the training
  exit 0
fi

# Electrons 

logoutput="lepmva_results/logs_evaluation/$year"
if [[ ! -d $logoutput ]]; then
  mkdir -p $logoutput
fi

#sbatch --wrap "python3 evaluate_mva.py --inpath $inpath --year $year --nfiles 100 --mode muon_legacy"
#for mode in muon_df_train_pt5_tth muon_df_train_pt5_ttw muon_pnet_train_pt5_tth muon_pnet_train_pt5_ttw; do
#    echo " >>> $mode"
#    sbatch -e $logoutput/$mode.err -o $logoutput/$mode.out --wrap "python3 evaluate_mva.py --inpath $inpath --year $year --nfiles 100 --mode $mode "
#    echo " ---- "
#done

sbatch --wrap "python3 evaluate_mva.py --inpath $inpath --year $year --nfiles 100 --mode electron_legacy"
for mode in electron_mvaISO electron_pnet_wIso electron_df_wIso; do
    echo " >>> $mode"
    sbatch -e $logoutput/$mode.err -o $logoutput/$mode.out --wrap "python3 evaluate_mva.py --inpath $inpath --year $year --nfiles 100 --mode $mode "
    echo " ---- "
done
