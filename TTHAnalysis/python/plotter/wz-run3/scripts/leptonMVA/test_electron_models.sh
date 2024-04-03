sbatch -J lepmva --wrap "root -l -b -q 'trainElectronID_NanoAODv11.cxx('test_electron_noIso_PNET', 'el_ttw', '2022')'"
sbatch -J lepmva --wrap "root -l -b -q 'trainElectronID_NanoAODv11_noISO.cxx('test_electron_noIso_PNET', 'el_ttw', '2022')'"
sbatch -J lepmva --wrap "root -l -b -q 'trainElectronID_NanoAODv11_PNET.cxx('test_electron_noIso_PNET', 'el_ttw', '2022')'"
sbatch -J lepmva --wrap "root -l -b -q 'trainElectronID_NanoAODv11_noIso_PNET.cxx('test_electron_noIso_PNET', 'el_ttw', '2022')'"

