

dbs_data = {
    # Era C
    "JetMET_Run2022C" : { "dbs": "/JetMET/Run2022C-22Sep2023-v1/NANOAOD"},
    "EGamma_Run2022C" : { "dbs": "/EGamma/Run2022C-22Sep2023-v1/NANOAOD"},
    "MuonEG_Run2022C" : { "dbs": "/MuonEG/Run2022C-22Sep2023-v1/NANOAOD"},
    "Muon_Run2022C"   : { "dbs": "/Muon/Run2022C-22Sep2023-v1/NANOAOD"},
    # Era D
    "JetMET_Run2022D" : { "dbs": "/JetMET/Run2022D-22Sep2023-v1/NANOAOD"},
    "EGamma_Run2022D" : { "dbs": "/EGamma/Run2022D-22Sep2023-v1/NANOAOD"},
    "MuonEG_Run2022D" : { "dbs": "/MuonEG/Run2022D-22Sep2023-v1/NANOAOD"},
    "Muon_Run2022D"   : { "dbs": "/Muon/Run2022D-22Sep2023-v1/NANOAOD"},
    # Era E
    "JetMET_Run2022E" : { "dbs": "/JetMET/Run2022E-22Sep2023-v1/NANOAOD"},
    "EGamma_Run2022E" : { "dbs": "/EGamma/Run2022E-22Sep2023-v1/NANOAOD"},
    "MuonEG_Run2022E" : { "dbs": "/MuonEG/Run2022E-22Sep2023-v1/NANOAOD"},
    "Muon_Run2022E"   : { "dbs": "/Muon/Run2022E-22Sep2023-v1/NANOAOD"},
    # Era F
    "JetMET_Run2022F" : { "dbs": "/JetMET/Run2022F-22Sep2023-v2/NANOAOD"},
    "EGamma_Run2022F" : { "dbs": "/EGamma/Run2022F-22Sep2023-v1/NANOAOD"},
    "MuonEG_Run2022F" : { "dbs": "/MuonEG/Run2022F-22Sep2023-v1/NANOAOD"},
    "Muon_Run2022F"   : { "dbs": "/Muon/Run2022F-22Sep2023-v1/NANOAOD"},
    # Era G
    "JetMET_Run2022G" : { "dbs": "/JetMET/Run2022G-22Sep2023-v2/NANOAOD"},
    "EGamma_Run2022G" : { "dbs": "/EGamma/Run2022G-22Sep2023-v2/NANOAOD"},
    "MuonEG_Run2022G" : { "dbs": "/MuonEG/Run2022G-22Sep2023-v1/NANOAOD"},
    "Muon_Run2022G"   : { "dbs": "/Muon/Run2022G-22Sep2023-v1/NANOAOD"},
}

dbs_mc = {
    # Signal
    'WZto3LNu': {'dbs': '/WZto3LNu_TuneCP5_13p6TeV_powheg-pythia8/', 'xsec': 5.31}, 
    
    # Prompts
    'ZZto4L': {'dbs': '/ZZto4L_TuneCP5_13p6TeV_powheg-pythia8/', 'xsec': 1.65},
    'GluGlutoContinto2Zto2E2Mu': {'dbs': '/GluGlutoContinto2Zto2E2Mu_TuneCP5_13p6TeV_mcfm701-pythia8/', 'xsec': 0.006114},
    'GluGluToContinto2Zto2E2Tau': {'dbs': '/GluGluToContinto2Zto2E2Tau_TuneCP5_13p6TeV_mcfm701-pythia8/', 'xsec': 0.006114},
    'GluGluToContinto2Zto2Mu2Tau': {'dbs': '/GluGluToContinto2Zto2Mu2Tau_TuneCP5_13p6TeV_mcfm701-pythia8/', 'xsec': 0.006114},
    'GluGlutoContinto2Zto4E': {'dbs': '/GluGlutoContinto2Zto4E_TuneCP5_13p6TeV_mcfm-pythia8/', 'xsec': 0.003060},
    'GluGlutoContinto2Zto4Mu': {'dbs': '/GluGlutoContinto2Zto4Mu_TuneCP5_13p6TeV_mcfm-pythia8/', 'xsec': 0.003060},
    'GluGlutoContinto2Zto4Tau': {'dbs': '/GluGlutoContinto2Zto4Tau_TuneCP5_13p6TeV_mcfm-pythia8/', 'xsec': 0.003060},
    'TTG_1Jets_PTG_10to100': {'dbs': '/TTG-1Jets_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFXold-pythia8/', 'xsec': 4.216}, 
    'TTG_1Jets_PTG_100to200': {'dbs': '/TTG-1Jets_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFXold-pythia8/', 'xsec': 0.411}, 
    'TTG_1Jets_PTG_200': {'dbs': '/TTG-1Jets_PTG-200_TuneCP5_13p6TeV_amcatnloFXFXold-pythia8/', 'xsec': 0.128},  
    'TTHtoNon2B': {'dbs': '/TTHtoNon2B_M-125_TuneCP5_13p6TeV_powheg-pythia8/', 'xsec': 0.25}, 
    'TTLL_MLL_50': {'dbs': '/TTLL_MLL-50_TuneCP5_13p6TeV_amcatnlo-pythia8/', 'xsec': 0.08646}, 
    'TTLL_MLL_4to50': {'dbs': '/TTLL_MLL-4to50_TuneCP5_13p6TeV_amcatnlo-pythia8/', 'xsec': 0.03949}, 
    'TTLNu_1Jets': {'dbs': '/TTLNu-1Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 0.25}, 
    'TZQB': {'dbs': '/TZQB-Zto2L-4FS_MLL-30_TuneCP5_13p6TeV_amcatnlo-pythia8/', 'xsec': 0.07968}, 
    'WZZ': {'dbs': '/WZZ_TuneCP5_13p6TeV_amcatnlo-pythia8/', 'xsec': 0.06206}, 
    'WWW_4F': {'dbs': '/WWW_4F_TuneCP5_13p6TeV_amcatnlo-madspin-pythia8/', 'xsec': 1}, 
    'WWZ_4F': {'dbs': '/WWZ_4F_TuneCP5_13p6TeV_amcatnlo-pythia8/', 'xsec': 0.18510}, 
    'ZZZ': {'dbs': '/ZZZ_TuneCP5_13p6TeV_amcatnlo-pythia8/', 'xsec': 0.01591}, 
    #'TTWW': {'dbs': '/TTWW_TuneCP5_13p6TeV_madgraph-madspin-pythia8/', 'xsec': 1}, 
    #'TTWH': {'dbs': '/TTWH_TuneCP5_13p6TeV_madgraph-madspin-pythia8/', 'xsec': 1}, 
    #'TTTT': {'dbs': '/TTTT_TuneCP5_13p6TeV_amcatnlo-pythia8/', 'xsec': 1}, 
    #'TTHH': {'dbs': '/TTHH_TuneCP5_13p6TeV_madgraph-madspin-pythia8/', 'xsec': 1}, 
    #'TTWZ': {'dbs': '/TTWZ_TuneCP5_13p6TeV_madgraph-madspin-pythia8/', 'xsec': 1}, 
    #'TTZZ': {'dbs': '/TTZZ_TuneCP5_13p6TeV_madgraph-madspin-pythia8/', 'xsec': 1}, 
    
    # TOP Fakes
    'TTto2L2Nu': {'dbs': '/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/', 'xsec': 97.4488},
    'TTtoLNu2Q' : {'dbs' : '/TTtoLNu2Q_TuneCP5_13p6TeV_powheg-pythia8/', 'xsec':403.25},
 
    'TbarWplusto2L2Nu': {'dbs': '/TbarWplusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/', 'xsec': 23.8979}, 
    'TWminusto2L2Nu': {'dbs': '/TWminusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/', 'xsec': 23.8979}, 

    # Ewk fakes
    'WZto2L2Q': {'dbs': '/WZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/', 'xsec': 1}, 
    'WWto2L2Nu': {'dbs': '/WWto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/', 'xsec': 12.98}, 
    'ZZto2L2Nu': {'dbs': '/ZZto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8/', 'xsec': 1.19}, 
    'ZZto2L2Q': {'dbs': '/ZZto2L2Q_TuneCP5_13p6TeV_powheg-pythia8/', 'xsec': 8.08},
    'DYto2L_2Jets_MLL_50': {'dbs': '/DYto2L-2Jets_MLL-50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 6345.99},
    'DYto2L_2Jets_MLL_10to50': {'dbs': '/DYto2L-2Jets_MLL-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 19982.5}, 
    'WtoLNu_2Jets': {'dbs': '/WtoLNu-2Jets_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 64481.58}, 

    # Conversions
    'VH_HtoNonbb': {'dbs': '/VH_HtoNonbb_M-125_TuneCP5_13p6TeV_amcatnloFXFX-madspin-pythia8/', 'xsec': 1.01}, 
    'WGtoLNuG_PTG_10to100': {'dbs': '/WGtoLNuG-1Jets_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 662.2},
    'WGtoLNuG_PTG_100to200': {'dbs': '/WGtoLNuG-1Jets_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 2.214}, 
    'WGtoLNuG_PTG_200': {'dbs': '/WGtoLNuG-1Jets_PTG-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 0.319}, 
    'ZGto2LG': {'dbs': '/ZGto2LG_TuneCP5_13p6TeV_amcatnlo-pythia8/', 'xsec': 1}, 
    'WZGtoLNuZG': {'dbs': '/WZGtoLNuZG_TuneCP5_13p6TeV_amcatnlo-pythia8/', 'xsec': 0.08425}, 
    "DYGto2LG_MLL-4to50_PTG-10to100": {'dbs': '/DYGto2LG-1Jets_MLL-4to50_PTG-10to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 87.94},
    "DYGto2LG_MLL-4to50_PTG-100to200": {'dbs': '/DYGto2LG-1Jets_MLL-4to50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 0.2423},
    "DYGto2LG_MLL-4to50_PTG-200": {'dbs': '/DYGto2LG-1Jets_MLL-4to50_PTG-200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 0.04002},
    "DYGto2LG_MLL-50_PTG-10to50": {'dbs': '/DYGto2LG-1Jets_MLL-50_PTG-10to50_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 124.2},
    "DYGto2LG_MLL-50_PTG-50to100": {'dbs': '/DYGto2LG-1Jets_MLL-50_PTG-50to100_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 2.10},
    "DYGto2LG_MLL-50_PTG-100to200": {'dbs': '/DYGto2LG-1Jets_MLL-50_PTG-100to200_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 0.045},
    "DYGto2LG_MLL-50_PTG-200to400": {'dbs': '/DYGto2LG-1Jets_MLL-50_PTG-200to400_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 0.00329},
    "DYGto2LG_MLL-50_PTG-400to600": {'dbs': '/DYGto2LG-1Jets_MLL-50_PTG-400to600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 0.00067},
    "DYGto2LG_MLL-50_PTG-600": {'dbs': '/DYGto2LG-1Jets_MLL-50_PTG-600_TuneCP5_13p6TeV_amcatnloFXFX-pythia8/', 'xsec': 0.0007773},
    

    # QCD no skim
    # EM enriched
    'QCD_PT_10to30_EMEnriched': {'dbs': '/QCD_PT-10to30_EMEnriched_TuneCP5_13p6TeV_pythia8/', 'xsec':  6.896e+06}, 
    'QCD_PT_30to50_EMEnriched': {'dbs': '/QCD_PT-30to50_EMEnriched_TuneCP5_13p6TeV_pythia8/', 'xsec': 6.716e+06}, 
    'QCD_PT_50to80_EMEnriched': {'dbs': '/QCD_PT-50to80_EMEnriched_TuneCP5_13p6TeV_pythia8/', 'xsec': 2.106e+06}, 
    'QCD_PT_80to120_EMEnriched': {'dbs': '/QCD_PT-80to120_EMEnriched_TuneCP5_13p6TeV_pythia8/', 'xsec': 3.881e+05}, 
    'QCD_PT_120to170_EMEnriched': {'dbs': '/QCD_PT-120to170_EMEnriched_TuneCP5_13p6TeV_pythia8/', 'xsec': 7.132e+04}, 
    #'QCD_PT-170to300_EMEnriched': {'dbs': '/QCD_PT-170to300_EMEnriched_TuneCP5_13p6TeV_pythia8/', 'xsec': 1}, 
    #'QCD_PT_300_EMEnriched': {'dbs': '/QCD_PT-300_EMEnriched_TuneCP5_13p6TeV_pythia8/', 'xsec': 1}, 


    # MU enriched
    "QCD_PT-15to20_MuEnrichedPt5" : {'dbs' : "/QCD_PT-15to20_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/", 'xsec' : 2.956e+06}, 
    "QCD_PT-20to30_MuEnrichedPt5" : {'dbs' : "/QCD_PT-20to30_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/", 'xsec' : 2.689e+06}, 
    "QCD_PT-30to50_MuEnrichedPt5" : {'dbs' : "/QCD_PT-30to50_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/", 'xsec' : 1.442e+06}, 
    "QCD_PT-50to80_MuEnrichedPt5" : {'dbs' : "/QCD_PT-50to80_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/", 'xsec' : 4.058e+05}, 
    "QCD_PT-80to120_MuEnrichedPt5" : {'dbs' : "/QCD_PT-80to120_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/", 'xsec' : 9.606e+04}, 
    "QCD_PT-120to170_MuEnrichedPt5" : {'dbs' : "/QCD_PT-120to170_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/", 'xsec' : 2.323e+04}, 
    #"QCD_PT-170to300_MuEnrichedPt5" : {'dbs' : "/QCD_PT-170to300_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/", 'xsec' : 1}, 
    #"QCD_PT-300to470_MuEnrichedPt5" : {'dbs' : "/QCD_PT-300to470_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/", 'xsec' : 1}, 
    #"QCD_PT-470to600_MuEnrichedPt5" : {'dbs' : "/QCD_PT-470to600_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/", 'xsec' : 1}, 
    #"QCD_PT-600to800_MuEnrichedPt5" : {'dbs' : "/QCD_PT-600to800_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/", 'xsec' : 1}, 
    #"QCD_PT-800to1000_MuEnrichedPt5" : {'dbs' : "/QCD_PT-800to1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/", 'xsec' : 1}, 
    #"QCD_PT-1000_MuEnrichedPt5" : {'dbs' : "/QCD_PT-1000_MuEnrichedPt5_TuneCP5_13p6TeV_pythia8/", 'xsec' : 1}, 
  
    
    # bcToE enriched
    'QCD_PT-20to30_bcToE': {'dbs': '/QCD_PT-20to30_bcToE_TuneCP5_13p6TeV_pythia8/', 'xsec': 2.028e+06}, 
    'QCD_PT-30to80_bcToE': {'dbs': '/QCD_PT-30to80_bcToE_TuneCP5_13p6TeV_pythia8/', 'xsec': 1.308e+06}, 
    'QCD_PT-80to170_bcToE': {'dbs': '/QCD_PT-80to170_bcToE_TuneCP5_13p6TeV_pythia8/', 'xsec': 7.356e+04}, 
    #'QCD_PT-170to250_bcToE': {'dbs': '/QCD_PT-170to250_bcToE_TuneCP5_13p6TeV_pythia8/', 'xsec': 1}, 
    #'QCD_PT-250_bcToE': {'dbs': '/QCD_PT-250_bcToE_TuneCP5_13p6TeV_pythia8/', 'xsec': 1}, 
}
