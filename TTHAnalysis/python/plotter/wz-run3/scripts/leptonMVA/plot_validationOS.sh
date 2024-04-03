RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color


cuts="wz-run3/leptonMVA/cuts-mvaValidation-2l.txt"
plot="wz-run3/leptonMVA/plots-mvaValidation-2l.txt"
mca="wz-run3/leptonMVA/mca-2l.txt"
uncfile="wz-run3/leptonMVA/systs.txt"
outname="./plots_validation_mva"

extra=$1

# Plot mva variables per flavor on OS events
for flav in  flav_mm; do
    echo -e $GREEN ">> Command for running the plot for $flav: OS events $NC"
    python3 wz-run3/wz-run.py plot --outname ${outname}/OS/$flav --unc --plotfile $plot --cutfile $cuts --mca $mca --extra "-E ^$flav -E ^os_only --sP mllZ --sP mva_lep1_eta --sP mva_lep2_eta" --uncfile $uncfile $extra 
    echo "-----------------------------"
done

