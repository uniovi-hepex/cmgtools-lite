# Script to produce plots used in the analysis note
RED='\033[0;31m'
GREEN='\033[0;16m'
NC='\033[0m' # No Color


mode=$1
extra=$2

if [[ $mode == "srwz" || $mode == "all" ]]; then
    echo -e " $GREEN >> Plots from analysis signal region $NC"
    
    echo -e " $GREEN o Blinded  $NC"
    python3 wz-run3/wz-run.py plot --outname plots_AN23147_noAdditionalUnc/SRWZ/all    --ncores 32 --unc  $extra --extra "--addspam 'WZ SR'  --sP flavor3l --pseudoData all_asimov --perBin " --blind --year all
    python3 wz-run3/wz-run.py plot --outname plots_AN23147_noAdditionalUnc/SRWZ/2022   --ncores 32 --unc  $extra --extra "--addspam 'WZ SR'  --sP flavor3l --pseudoData all_asimov --perBin " --blind --year 2022
    python3 wz-run3/wz-run.py plot --outname plots_AN23147_noAdditionalUnc/SRWZ/2022EE --ncores 32 --unc  $extra --extra "--addspam 'WZ SR'  --sP flavor3l --pseudoData all_asimov --perBin " --blind --year 2022EE

    python3 wz-run3/wz-run.py plot --outname plots_AN23147_noAdditionalUnc/SRWZ_unblind/2022   --year 2022   --ncores 32 --unc  $extra --extra "--xP flavor3l --addspam 'WZ SR' --perBin "
    python3 wz-run3/wz-run.py plot --outname plots_AN23147_noAdditionalUnc/SRWZ_unblind/2022EE --year 2022EE --ncores 32 --unc  $extra --extra "--xP flavor3l --addspam 'WZ SR' --perBin "
    python3 wz-run3/wz-run.py plot --outname plots_AN23147_noAdditionalUnc/SRWZ_unblind/all    --year all    --ncores 32 --unc  $extra --extra "--xP flavor3l --addspam 'WZ SR' --perBin "

#    for flav in flav_eee flav_eem flav_mme flav_mmm; do
#        echo -e " $GREEN o Unblinded ($flav)  $NC"
#        python3 wz-run3/wz-run.py plot --outname plots_AN23147_noAdditionalUnc/SRWZ_unblind/all/$flav --year all --ncores 8 --unc  $extra --extra "--xP flavor3l -E ^$flav --addspam 'WZ SR' --perBin"
#    done
fi

if [[ $mode == "crzz" || $mode == "all" ]]; then    
    echo -e  " $GREEN >> Plots from analysis ZZ control region $NC"
    python3 wz-run3/wz-run.py plot --extra "--addspam 'ZZ CR'" --outname plots_AN23147_noAdditionalUnc/CRZZ/2022   --year 2022   --ncores 32 --unc --cutfile wz-run3/common/cuts-crzz.txt $extra
    python3 wz-run3/wz-run.py plot --extra "--addspam 'ZZ CR'" --outname plots_AN23147_noAdditionalUnc/CRZZ/2022EE --year 2022EE --ncores 32 --unc --cutfile wz-run3/common/cuts-crzz.txt $extra
    python3 wz-run3/wz-run.py plot --extra "--addspam 'ZZ CR'" --outname plots_AN23147_noAdditionalUnc/CRZZ/all    --year all    --ncores 32 --unc --cutfile wz-run3/common/cuts-crzz.txt $extra
fi

if [[ $mode == "crtt" || $mode == "all"  ]]; then    
    echo -e " $GREEN >> Plots from analysis ttZ control region $NC"
    python3 wz-run3/wz-run.py plot --extra "--addspam 'ttZ CR' " --year 2022   --outname plots_AN23147_noAdditionalUnc/CRTT/2022   --ncores 32 --unc --cutfile wz-run3/common/cuts-crtt.txt $extra
    python3 wz-run3/wz-run.py plot --extra "--addspam 'ttZ CR' " --year 2022EE --outname plots_AN23147_noAdditionalUnc/CRTT/2022EE --ncores 32 --unc --cutfile wz-run3/common/cuts-crtt.txt $extra
    python3 wz-run3/wz-run.py plot --extra "--addspam 'ttZ CR' " --year all    --outname plots_AN23147_noAdditionalUnc/CRTT/all    --ncores 32 --unc --cutfile wz-run3/common/cuts-crtt.txt $extra 
fi

if [[ $mode == "crconv" || $mode == "all"  ]]; then    
    echo -e " $GREEN >> Plots from analysis Conversions control region $NC"
    python3 wz-run3/wz-run.py plot --extra "--addspam 'Conv CR' " --year 2022   --outname plots_AN23147_noAdditionalUnc/CRCONV/2022   --ncores 32 --unc --cutfile wz-run3/common/cuts-crconv.txt $extra
    python3 wz-run3/wz-run.py plot --extra "--addspam 'Conv CR' " --year 2022EE --outname plots_AN23147_noAdditionalUnc/CRCONV/2022EE --ncores 32 --unc --cutfile wz-run3/common/cuts-crconv.txt $extra
    python3 wz-run3/wz-run.py plot --extra "--addspam 'Conv CR' " --year all    --outname plots_AN23147_noAdditionalUnc/CRCONV/all    --ncores 32 --unc --cutfile wz-run3/common/cuts-crconv.txt $extra
fi
