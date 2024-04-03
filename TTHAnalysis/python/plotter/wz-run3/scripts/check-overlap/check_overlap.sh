era=$1
extra=$2

mca_folder=$(dirname $BASH_SOURCE[0])/$era

year=2022EE
if [[ $era == 2022C || $era == 2022D ]]; then year=2022; fi

for mca in muon egamma muoneg; do
  python3 wz-run3/wz-run.py dump --mca $mca_folder/mca-${mca}.txt $extra --extra "--dumpFile $mca_folder/eventDump_${mca/.txt/}.txt " --outname $mca_folder --year $year
done


