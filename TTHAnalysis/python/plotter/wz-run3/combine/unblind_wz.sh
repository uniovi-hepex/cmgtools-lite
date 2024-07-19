# Scripts to do the different steps of the WZ unblinding
RED='\033[0;31m'
GREEN='\033[0;32m'
ORANGE='\033[0;33m'

NC='\033[0m' # No Color

step=$1
mode=$2
extra=$3

cardspath="cards/inclusive/approval-04thJuly2024/total/flavor3l/"
fits_folder="fit-results_approval/total/"
mask=" "

# --------------- Select mode to run (basically how many things we fit)
echo -e "$GREEN ---- $mode mode $NC"
subfolder="$mode"

# By default combine everything
case $mode in
  inclusive)
    title_for_gof="Pre-fit GOF test (SR+CRs)"
    ;;
  eee)
    mask="$mask --mask .*eee.*"
    title_for_gof="Pre-fit GOF test (SR+CRs - eee)"
    ;;
  eem)
    mask="$mask --mask .*eem.*"
    title_for_gof="Pre-fit GOF test (SR+CRs - eem)"
    ;;
  mme)
    mask="$mask --mask .*mme.*"
    title_for_gof="Pre-fit GOF test (SR+CRs - mme)"
    ;;
  mmm)
    mask="$mask --mask .*mmm.*"
    title_for_gof="Pre-fit GOF test (SR+CRs - mmm)"
    ;;
  crtt)
    extra="$extra --mask .*crtt.* -r crtt"
    title_for_gof="Pre-fit GOF test (CR ttZ only)"
    ;;
  crzz)
    mask="$mask --mask .*crzz.* -r crzz"
    title_for_gof="Pre-fit GOF test (CR ZZ only)"
    ;;
  crconv)
    mask="$mask --mask .*crconv.* -r crconv"
    title_for_gof="Pre-fit GOF test (CR Xg only)"
    ;;
esac

if [[ $step == 0 ]]; then
  echo -e "$ORANGE >> Ground step is to combine cards and create workspaces: $NC"
  echo -e "      + We will make a card and a workspace with channel masking."
  python3 run_combine.py --mode combinecards --output $fits_folder --inpath $cardspath $extra
  python3 run_combine.py --mode workspace    --output $fits_folder --inpath $cardspath $extra 
elif [[ $step == 1 ]]; then
  echo -e "$ORANGE >> First step of the unblinding, GOF tests: $NC"
  echo -e "      + We will make GoodnessOfFit (GOF) tests for the different regions (srwz, crzz, crtt and crconv). "
  echo -e "        These GOF are performed using the saturated model from combine:  "
  echo -e "        https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest/part3/commonstatsmethods/?h=goodness#goodness-of-fit-tests"
  python3 run_combine.py --mode multigof --output $fits_folder/$subfolder/gof --workspace $fits_folder/workspace_wz.root --cluster $extra $mask
elif [[ $step == 2 ]]; then
  echo -e "$ORANGE >> Second step of the unblinding, plot GOF tests: $NC"
  echo -e "      + Just gather the outputs of the GOFs and plot them "
  python plot_gof.py --inpath $fits_folder/$subfolder/gof/ --region srwz --title $title_for_gof
elif [[ $step == 3 ]]; then
  echo -e "$ORANGE >> Third step of the unblinding, Impacts"
  echo -e "      + We will make impact plots for the different cases. At this stage, the plotImpacts.py option should be run with the --blind option so it does not show the final signal strength "
  echo -e "        We will produce also output for the fit in which the signal is blinded (expectSignal = 1) and when everything is blinded (-t -1) "  
  echo -e " $RED + Unblinded $NC"
  python3 run_combine.py --mode impacts              --output $fits_folder/$subfolder/impacts-unblinded/ --workspace $fits_folder/workspace_wz.root $extra $mask
  echo -e " $RED + Blind SR only (--expectSignal 1) $NC"
  python3 run_combine.py --mode impacts  --blind-sr  --output $fits_folder/$subfolder/impacts-blind-sr   --workspace $fits_folder/workspace_wz.root $extra $mask
  echo -e " $RED + Blind everything (-t -1) $NC"
  python3 run_combine.py --mode impacts  --blind-all --output $fits_folder/$subfolder/impacts-blind-all  --workspace $fits_folder/workspace_wz.root $extra $mask
elif [[ $step == 4 ]]; then
  echo -e "$ORANGE >> Fourth step is to produce fitDiagnostics: $NC"
  echo -e "      + We will create a fitDiagnostics file with the fits to all SR+CR " # (doesn't make much sense to do one for CRs alone)
  python3 run_combine.py --mode fitDiagnostics --output $fits_folder/$subfolder/fitDiagnostics --workspace $fits_folder/workspace_wz.root --cluster $extra $mask
elif [[ $step == 5 ]]; then
  echo -e "$ORANGE >> Fifth step is to produce postfit distribuitons: $NC"
  echo -e "      + In this case we will run the PostFitShapesFromWorkspace script from combineHarvester. "
  echo -e "        https://cms-analysis.github.io/CombineHarvester/post-fit-shapes-ws.html"
  echo -e "        Basically this takes the output of fitDiagnostics and propagates the results of the fit to any distribution."
  echo -e "        This has to actually be ran for each variable separately. We are going to run it only in the distributions that enter"
  echo -e "        the fit. We could in principle do this with the fitDiagnostics output, but running the tool is easy and it uniformizes"
  echo -e "        the histogram that are used for plotting postfit distributions. "
  python3 run_combine.py --mode combinecards --inpath $cardspath/srwz --output $fits_folder/$subfolder/postfit-histograms/flavor3l/ $extra 
  python3 run_combine.py --mode workspace    --output $fits_folder/$subfolder/postfit-histograms/flavor3l/ --workspace workspace_wz_flavor3l.root $extra 
  python3 run_combine.py --mode make_postfit --output $fits_folder/$subfolder/postfit-histograms/flavor3l/ --cluster --fitDiagnostics $fits_folder/$subfolder/fitDiagnostics/fitDiagnosticsTest.root --workspace $fits_folder/workspace_wz.root $extra 
elif [[ $step == 6 ]]; then
  echo -e "$ORANGE >> Sixth step is to run iterative freezing of systematics: $NC"
  echo -e "      + In this case we will iteratively freeze groups of systematics to estimate their impact in the final result. "
  python3 run_combine.py --mode scan_groups --output $fits_folder/$subfolder/uncertainty-table/ --workspace $fits_folder/workspace_wz.root $extra $mask 
elif [[ $step == 7 ]]; then
  echo -e "$ORANGE >> Seventh step is to run iterative freezing of systematics: $NC"
  echo -e "      + In this case we will gather the output from the previous step and build the table of systematics "
  python3 run_combine.py --mode sys_table --output $fits_folder/$subfolder/uncertainty-table/ --workspace $fits_folder/workspace_wz.root $extra $mask
elif [[ $step == 8 ]]; then
  echo -e "$ORANGE >> Eigth step is to run iterative produce likelihood scans of systematics: $NC"
  echo -e "      + In this case we will produce scans only freezing experimental and theoretical in two big groups. "
  python3 run_combine.py --mode scan_groups --output $fits_folder/$subfolder/scan/ --workspace $fits_folder/workspace_wz.root -j scan_groupings.json $extra $mask 
fi
