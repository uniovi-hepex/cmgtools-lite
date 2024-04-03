import os
import json
import sys
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3"))
from scripts.make_latex_table import dict_to_latex_table

import scripts.triggerSFs.trigger_modes as trg
data_folder = 'results'
years = ['PreEE', 'PostEE']
channels = ['inclusive']


measurements = ["inclusive", "lowpt", "highpt", "barrel0", "barrel1", "barrel2", "barrel3"]
for meas in measurements:
    effs = {
        "Year": [],
        "Sample": []*len(years),
        "Pass PR": [],
        "Pass PR and HLT": [],
        "$\epsilon$(HLT)" : [],
        "$\alpha$" : []
    }
    print(" >>> MEASUREMENT: %s"%meas)
    if meas == "inclusive": 
        function = trg.inclusive
        title = "Inclusive phase space"
        label = "trigEff1"
    elif meas == "lowpt": 
        function = trg.lowpt
        title = r"15 < p_{T}(#ell_3) #leq 25 "
        label = "trigEff3"
    elif meas == "highpt": 
        function = trg.highpt
        title = r"p_{T}(#ell_3) > 25 "
        label = "trigEff2"
    elif meas == "barrel0": 
        function = trg.barrel0
        title = r"0 barrel leptons"
        label = "trigeff_barrel0"
    elif meas == "barrel1": 
        function = trg.barrel1
        title = r"1 barrel lepton"
        label = "trigeff_barrel1"
    elif meas == "barrel2": 
        function = trg.barrel2
        title = r"2 barrel leptons"
        label = "trigeff_barrel2"
    elif meas == "barrel3": 
        function = trg.barrel3
        title = r"3 barrel leptons"
        label = "trigeff_barrel3"
    else:
        print(f" >> Mode {meas} not available. ")


    _, caption = function( selection = [], flav_cut = "1" )
    for year in years:
        effs["Year"].append((year, 2))
        effs["Year"].append(" {} ")
        for sample in ["Data", "MC"]:
            effs["Sample"].append(sample)
            data_file_path = os.path.join(data_folder, year, "inclusive", meas, f'{sample.lower()}_results.json')
            if os.path.exists(data_file_path):
                with open(data_file_path, 'r') as file:
                    data = json.load(file)
                    effs["Pass PR"].append("%3.3f"%data["pass_den"])
                    effs["Pass PR and HLT"].append("%3.3f"%(data["pass_num"]))
                    effs["$\epsilon$(HLT)"].append("$%3.3f^{+%3.3f}_{-%3.3f}$"%(data["eff"], data["eff_errup"], data["eff_errdn"]))
                    effs["$\alpha$"].append("%3.3f"%(data["corr"]))


    table = dict_to_latex_table(effs, caption = caption, label = label)
    print(table)
