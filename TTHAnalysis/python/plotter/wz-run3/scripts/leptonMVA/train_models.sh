# macro to train models
# v1--> first version
# v2--> 
#      * fix the electron veto to EE region (one branch nos being read correctly)
#      * After results from v1, increased the number of trees for performance of BDTG2
#                               also changed number of cuts.
# nanoAODv12 -->
#      * Retrain with latest nanoAOD. 2022 and 2022EE trainings included

list=$1
if [[ -z $list ]]; then
  echo Please select a list of samples to use for the training
  exit 0
fi

nFiles=$2
if [[ -z $nFiles ]]; then
  echo Please select how many samples to use for training
  exit 0
fi


logoutput="lepmva_results/logs_training/"
if [[ ! -d $logoutput ]]; then
  mkdir -p $logoutput
fi

# Muons
for presel in tth ttw; do
  for btag in df pnet robust; do
    name="mu_${presel}_${btag}"
    sbatch -J mu_mva -e $logoutput/$name.err -o $logoutput/$name.out --wrap "./train_model.sh $name $list $nFiles"
    done
done

# Electrons 
for presel in tth ttw; do
  for btag in df pnet robust; do
    name="el_${presel}_${btag}"
    sbatch -J el_mva -e $logoutput/$name.err -o $logoutput/$name.out --wrap "./train_model.sh $name $list $nFiles"
    done
done
