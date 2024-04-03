# Script to compute efficiencies
RED='\033[0;31m'
GREEN='\033[0;32m'
PURPLE='\033[0;35m'
CYAN='\033[1;36m'
NC='\033[0m' # No Color


measure=$1 ## eff , acc_pow or acc_amc
year=$2 ## For the year: 2022, 2022EE or all
extra=$3



echo -e "$CYAN WARNING!! Remember that you are using the $year dataset!! :D $NC"

function measure_efficiency() {
    # Computes the efficiency using mcPlots
    extra=$1
    mca="wz-run3/inclusive_xsec/mca-eff.txt"
    cuts="wz-run3/inclusive_xsec/cuts-total.txt"
    outname="wz-run3/inclusive_xsec/efficiency_unskim/$year"
    basecmd="python3 wz-run3/wz-run.py plot"
    basecmd="$basecmd --unfriend" # Remove all ftrees
    basecmd="$basecmd --ncores 32" # Add cores
    basecmd="$basecmd --mca $mca" # add mca
    basecmd="$basecmd --cutfile $cuts" # add cuts
    basecmd="$basecmd --mcpath /lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v2/mc_unskim_march2024" #Use unSkim samples trees


    ftrees="--FMCs {P}/pileupfix"
    ftrees="$ftrees --Fs {P}/leptonJetRecleaning_Elewp090"
    ftrees="$ftrees --Fs {P}/leptonBuilder_Elewp090"
    ftrees="$ftrees --FMCs {P}/scalefactors_Elewp090"
    ftrees="$ftrees --FMCs {P}/lepGEN_withDressed"

    ##For the year: 2022, 2022EE or all
    basecmd="$basecmd --year $year"

    echo -e "$PURPLE >> Computing efficiency $NC"

    # INCLUSIVE
    ## Denominator: Fiducial
    echo -e "$GREEN Inclusive Fiducial Denominator: $NC"
    cmd_den="$basecmd --extra \"-E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees\" --unweight --outname $outname/denominator/inclusive $extra"
    echo $cmd_den | bash 
    ##Numerator: Reco
    echo -e "$GREEN Inclusive Fiducial Numerator: $NC"
    cmd_num="$basecmd --extra \" -E ^SR.* -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees \"  --outname $outname/numerator/inclusive $extra"
    echo $cmd_num | bash 


    # eee
    ## Denominator: Fiducial
    echo -e "$GREEN eee Fiducial Denominator: $NC"
    cmd_den="$basecmd --extra \"-E ^eee_fid -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees\" --unweight --outname $outname/denominator/eee $extra"
    echo $cmd_den | bash 
    ##Numerator: Reco
    echo -e "$GREEN eee Fiducial Numerator: $NC"
    cmd_num="$basecmd --extra \" -E ^eee_reco -E ^SR.* -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees \" --outname $outname/numerator/eee $extra"
    echo $cmd_num | bash 
    
    # eem
    ## Denominator: Fiducial
    echo -e "$GREEN eem Fiducial Denominator: $NC"
    cmd_den="$basecmd --extra \"-E ^eem_fid -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees\" --unweight --outname $outname/denominator/eem $extra"
    echo $cmd_den | bash 
    ##Numerator: Reco
    echo -e "$GREEN eem Fiducial Numerator: $NC"
    cmd_num="$basecmd --extra \" -E ^eem_reco  -E ^SR.* -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees\" --outname $outname/numerator/eem $extra"
    echo $cmd_num | bash 

    # mme
    ## Denominator: Fiducial
    echo -e "$GREEN mme Fiducial Denominator: $NC"
    cmd_den="$basecmd --extra \"-E ^mme_fid -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees\" --unweight --outname $outname/denominator/mme $extra"
    echo $cmd_den | bash 
    ##Numerator: Reco
    echo -e "$GREEN mme Fiducial Numerator: $NC"
    cmd_num="$basecmd --extra \" -E ^mme_reco  -E ^SR.* -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees \"   --outname $outname/numerator/mme $extra"
    echo $cmd_num | bash 

    # mmm
    ## Denominator: Fiducial
    echo -e "$GREEN mmm Fiducial Denominator: $NC"
    cmd_den="$basecmd --extra \"-E ^mmm_fid -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees\" --unweight --outname $outname/denominator/mmm $extra"
    echo $cmd_den | bash 
    ##Numerator: Reco
    echo -e "$GREEN mmm Fiducial Numerator: $NC"
    cmd_num="$basecmd --extra \" -E ^mmm_reco  -E ^SR.* -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees\"  --outname $outname/numerator/mmm $extra"
    echo $cmd_num | bash 
}

function measure_acceptance() {
    # Computes the acceptance using mcPlots
    sample=$1
    extra=$2
    mcpath="/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v2/mc_unskim_march2024"
    
    case $sample in
        pow)
            mca="wz-run3/inclusive_xsec/mca-acc-powheg.txt"
            outname="wz-run3/inclusive_xsec/acceptance_powheg/$year"
            ;;
        amc)
            mca="wz-run3/inclusive_xsec/mca-acc-amcnlo.txt"
            outname="wz-run3/inclusive_xsec/acceptance_amcnlo/$year"
    esac
    
    cuts="wz-run3/inclusive_xsec/cuts-total.txt"

    basecmd="python3 wz-run3/wz-run.py plot"
    basecmd="$basecmd --ncores 32" # Add cores
    basecmd="$basecmd --mca $mca"
    #basecmd="$basecmd --uncfile wz-run3/inclusive_xsec/systs-acc.txt --unc  "
    basecmd="$basecmd --cutfile $cuts" # add cuts
    basecmd="$basecmd --unweight " # Unweight everything since this is fiducial level
    basecmd="$basecmd --unfriend " # There are no friend trees for the acceptance sample
    basecmd="$basecmd --unweight"
    basecmd="$basecmd --mcpath $mcpath " # Unweight everything since this is fiducial level
    basecmd="$basecmd --year $year"

    ftrees="--FMCs {P}/pileupfix"
    ftrees="$ftrees --Fs {P}/leptonJetRecleaning_Elewp090"
    ftrees="$ftrees --Fs {P}/leptonBuilder_Elewp090"
    ftrees="$ftrees --FMCs {P}/scalefactors_Elewp090"


    #echo $basecmd 
    echo -e "$PURPLE >> Computing acceptance ($sample) $NC"

    # INCLUSIVE
    ## Denominator: Fiducial
    echo -e "$GREEN Inclusive Fiducial Denominator: $NC"
    cmd_den="$basecmd --extra \"-E ^TOTAL.* --sP tot_weight $ftrees  --FMCs {P}/lepGEN\" --outname $outname/denominator/inclusive $extra"
    echo $cmd_den | bash 
    ##Numerator: Reco
    echo -e "$GREEN Inclusive Fiducial Numerator: $NC"
    cmd_num="$basecmd --extra \" -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees  --FMCs {P}/lepGEN_withDressed\"  --outname $outname/numerator/inclusive $extra"
    echo $cmd_num | bash 

    # eee
    ## Denominator: Fiducial
    echo -e "$GREEN eee Fiducial Denominator: $NC"
    cmd_den="$basecmd --extra \"-E ^TOTAL.* --sP tot_weight $ftrees --FMCs {P}/lepGEN\" --outname $outname/denominator/eee $extra"
    echo $cmd_den | bash 
    ##Numerator: Reco
    echo -e "$GREEN eee Fiducial Numerator: $NC"
    cmd_num="$basecmd --extra \"-E ^eee_fid -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees  --FMCs {P}/lepGEN_withDressed\" --outname $outname/numerator/eee $extra"
    echo $cmd_num | bash 
    
    # eem
    ## Denominator: Fiducial
    echo -e "$GREEN eem Fiducial Denominator: $NC"
    cmd_den="$basecmd --extra \"-E ^TOTAL.* --sP tot_weight $ftrees  --FMCs {P}/lepGEN\" --outname $outname/denominator/eem $extra"
    echo $cmd_den | bash 
    ##Numerator: Reco
    echo -e "$GREEN eem Fiducial Numerator: $NC"
    cmd_num="$basecmd --extra \"-E ^eem_fid -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees  --FMCs {P}/lepGEN_withDressed \" --outname $outname/numerator/eem $extra"
    echo $cmd_num | bash 

    # mme
    ## Denominator: Fiducial
    echo -e "$GREEN mme Fiducial Denominator: $NC"
    cmd_den="$basecmd --extra \"-E ^TOTAL.* --sP tot_weight $ftrees  --FMCs {P}/lepGEN\" --outname $outname/denominator/mme $extra"
    echo $cmd_den | bash 
    ##Numerator: Reco
    echo -e "$GREEN mme Fiducial Numerator: $NC"
    cmd_num="$basecmd --extra \"-E ^mme_fid -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees  --FMCs {P}/lepGEN_withDressed \" --outname $outname/numerator/mme $extra"
    echo $cmd_num | bash 

    # mmm
    ## Denominator: Fiducial
    echo -e "$GREEN mmm Fiducial Denominator: $NC"
    cmd_den="$basecmd --extra \"-E ^TOTAL.* --sP tot_weight $ftrees  --FMCs {P}/lepGEN\" --outname $outname/denominator/mmm $extra"
    echo $cmd_den | bash 
    ##Numerator: Reco
    echo -e "$GREEN mmm Fiducial Numerator: $NC"
    cmd_num="$basecmd --extra \"-E ^mmm_fid -E ^TOTAL.* -E ^FID.* --sP tot_weight $ftrees  --FMCs {P}/lepGEN_withDressed \" --outname $outname/numerator/mmm $extra"
    echo $cmd_num | bash 
}

if [[ $measure == *"eff"* ]];     then measure_efficiency $extra; fi
if [[ $measure == *"acc_pow"* ]]; then measure_acceptance pow $extra; fi
if [[ $measure == *"acc_amc"* ]]; then measure_acceptance amc $extra; fi

