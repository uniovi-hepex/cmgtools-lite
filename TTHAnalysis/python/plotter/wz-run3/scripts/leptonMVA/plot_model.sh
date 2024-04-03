folder=$1
name=$2
year=$3

if [[ $name == *"mu"* ]]; then
    echo Submitting muon plots...
    root -l -b -q 'plot_tmva.C("'"$folder"'", "'"$name"'", "'"$year"'")'
else
    echo Submitting electron plots...
    root -l -b -q 'plot_tmva.C("'"$folder"'", "'"$name"'", "'"$year"'")'
fi
