# Just commands to plot stuff
# color
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

mode=$1
extra="${@:2}"

# -------------------------------------------- #
#   1. PRODUCE MAIN DISTRIBUTION FOR THE FIT   #
# -------------------------------------------- #
if [[ $mode == *main* ]]; then

    echo -e $GREEN SUBMITTING cards for SRWZ $NC
    python3 wz-run3/wz-run.py card $extra --outname cards/wz/srwz $extra --binname srwz.input2022EE --ncores 32 --year 2022EE
    python3 wz-run3/wz-run.py card $extra --outname cards/wz/srwz $extra --binname srwz.input2022 --ncores 32 --year 2022
    echo "-----------------------------"
    
    echo -e $GREEN SUBMITTING cards for CRZZ $NC
    python3 wz-run3/wz-run.py card $extra --cutfile wz-run3/common/cuts-crzz.txt --outname cards/wz/crzz --binname crzz.input2022EE --ncores 32 --year 2022EE
    python3 wz-run3/wz-run.py card $extra --cutfile wz-run3/common/cuts-crzz.txt --outname cards/wz/crzz --binname crzz.input2022 --ncores 32 --year 2022
    echo "-----------------------------"
    
    echo -e $GREEN SUBMITTING cards for CRTT $NC
    python3 wz-run3/wz-run.py card $extra --cutfile wz-run3/common/cuts-crtt.txt --outname cards/wz/crtt --binname crtt.input2022EE --year 2022EE --var "nJet25_Mini" --binning "[-0.5,0.5,1.5,2.5,3.5,4.5]" --ncores 32
    python3 wz-run3/wz-run.py card $extra --cutfile wz-run3/common/cuts-crtt.txt --outname cards/wz/crtt --binname crtt.input2022 --year 2022 --var "nJet25_Mini" --binning "[-0.5,0.5,1.5,2.5,3.5,4.5]" --ncores 32
    echo "-----------------------------"
    
    echo -e $GREEN SUBMITTING cards for CRCONV $NC
    python3 wz-run3/wz-run.py card $extra --cutfile wz-run3/common/cuts-crconv.txt --outname cards/wz/crconv --binname crconv.input2022EE --year 2022EE --ncores 32
    python3 wz-run3/wz-run.py card $extra --cutfile wz-run3/common/cuts-crconv.txt --outname cards/wz/crconv --binname crconv.input2022 --year 2022 --ncores 32
    echo "-----------------------------"

fi

# ----------------------------------------- #
#   2. PRODUCE CARDS FOR CHARGE ASYMMETRY   #
# ----------------------------------------- #
if [[ $mode == *chasymm* ]]; then
    echo -e $GREEN SUBMITTING cards for SRWZ $NC
    python3 wz-run3/wz-run.py card $extra --var '"4*(LepW_pdgId < 0) + (abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2"' --binning '"8,-0.5,7.5"' --outname cards/wz/chAsymm $extra
    echo "-----------------------------"
fi
