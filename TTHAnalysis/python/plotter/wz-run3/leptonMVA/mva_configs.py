""" Define how different mvas are evaluated with some basic rules"""
import array as ar
import ROOT as r
from copy import deepcopy
import os, sys
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3"))
from functions import color_msg
import numpy as np


class MVAvar:
    def __init__(self, name):
        self.name = name
        self.var = ar.array('f', [0.])

    def set(self, val):
        self.var[0] = val
        
class mva_histo(object):
    def __init__(self, 
                 name, 
                 xmlpath,
                 vars_,
                 useBranch = None,
                 convert = lambda s, lep: s):
        self.name = name
        self.xmlpath = xmlpath
        self.vars_ = vars_
        self.useBranch = useBranch
        self.convert = convert
        self.create_histos()
        return
    
    def open_model(self):
        """ Method to open a model a load variables """
        print(" >> Opening model: %s"%self.xmlpath)
        self.reader = r.TMVA.Reader()
        for vname, v in self.vars_.items():
                color_msg("    + Adding variable: %s "%vname) 
                self.reader.AddVariable(v[0].name, v[0].var)

        print(self.name, self.xmlpath)
        self.reader.BookMVA(self.name, self.xmlpath)
        return 
    
    def create_histos(self):
        histos = {}
        name = self.name
        histos["signal_total"] = deepcopy(r.TH1F("h_signal_{}_total".format(name), "", 1000, -1., 1.))
        histos["signal"] = deepcopy(r.TH1F("h_signal_{}".format(name), "", 1000, -1., 1.))
        histos["bkg_total"] = deepcopy(r.TH1F("h_bkg_{}_total".format(name), "", 1000, -1., 1.))
        histos["bkg"] = deepcopy(r.TH1F("h_bkg_{}".format(name), "", 1000, -1., 1.))
        self.histos = histos
        return
    
    def set_vars(self, lep, jets):
        """ Set the values of the variables before evaluating MVA """
        for vname, v in self.vars_.items():
            lambda_func = v[1]
            v[0].set( lambda_func(lep, jets) )
        return
    
    def summarize(self):
        """ To print out """
        print(" >> Summary mva: %s"%self.name)
        for hname, histo in self.histos.items():
            print("         + %s:  %3.2f"%(hname, histo.GetEntries()))

        return
            
    def evaluate(self, lep):
        raw_score = self.reader.EvaluateMVA(self.name)
        convert_score = self.convert(raw_score, lep)
        return convert_score
    
    def fill(self, what, score):
        self.histos[what].Fill(score)
        return
    
    def write(self, outpath):
        f_out = r.TFile(os.path.join(outpath, "%s_mvaEvaluate.root"%self.name), "recreate")
        for hname, histo in self.histos.items():
            histo.Write()
        f_out.Close()
        return

"""
Define dictionaries for muon evaluators
"""
def muon_legacy(year):
    muon_legacy_mva = mva_histo(
        name = "muon_legacy",
        xmlpath=None,
        vars_ = {},
        useBranch = "mvaTTH"
    )
    return muon_legacy_mva

def electron_legacy(year):
    electron_legacy_mva = mva_histo(
        name = "electron_legacy",
        xmlpath=None,
        vars_ = {},
        useBranch = "mvaTTH"
    )
    return electron_legacy_mva


def electron_mvaISO(year):
    electron_legacy_mva = mva_histo(
        name = "electron_mvaISO",
        xmlpath=None,
        vars_ = {},
        useBranch = "mvaIso"
    )
    return electron_legacy_mva

def electron_mvaNOISO(year):
    electron_legacy_mva = mva_histo(
        name = "electron_mvaNoISO",
        xmlpath=None,
        vars_ = {},
        useBranch = "mvaNoIso"
    )
    return electron_legacy_mva

def muon_df_train_pt5_tth(year):
    vars_muons_jetdf_train_pt5  = {
        "pt" : 
            [MVAvar("LepGood_pt"), lambda lep, jets: lep.pt],
        "eta" : 
            [MVAvar("LepGood_eta"), lambda lep, jets: lep.eta],
        "pfRelIso03_all" : 
            [MVAvar("LepGood_pfRelIso03_all"), lambda lep, jets: lep.pfRelIso03_all],
        "miniPFRelIso_chg" : 
            [MVAvar("LepGood_miniRelIsoCharged"), lambda lep, jets: lep.miniPFRelIso_chg ],
        "LepGood_miniRelIsoNeutral" :
            [MVAvar("LepGood_miniRelIsoNeutral"), lambda lep, jets: lep.miniPFRelIso_all - lep.miniPFRelIso_chg],
        "LepGood_jetNDauChargedMVASel" :
            [MVAvar("LepGood_jetNDauChargedMVASel"), lambda lep, jets: lep.jetNDauCharged],
        "jetPtRelv2" :
            [MVAvar("LepGood_jetPtRelv2"), lambda lep, jets: lep.jetPtRelv2],
        "LepGood_jetDF" : 
            [MVAvar("LepGood_jetDF"), lambda lep, jets: jets[lep.jetIdx].btagDeepFlavB if lep.jetIdx > -1 else 0],
        "LepGood_jetPtRatio" : 
            [MVAvar("LepGood_jetPtRatio"), lambda lep, jets: min(1. / (1. + lep.jetRelIso), 1.5) ],
        "LepGood_sip3d" : 
            [MVAvar("LepGood_sip3d"), lambda lep, jets: lep.sip3d],
        "LepGood_dxy" :
            [MVAvar("LepGood_dxy"), lambda lep, jets: np.log(abs(lep.dxy))],
        "LepGood_dz" : 
            [MVAvar("LepGood_dz"), lambda lep, jets: np.log(abs(lep.dz))],
        "LepGood_segmentComp" : 
            [MVAvar("LepGood_segmentComp"),lambda lep, jets: lep.segmentComp],
    }

    mva_muon_df_train_pt5 = mva_histo(
        name = "muon_df_train_pt5_tth",
        xmlpath= os.path.join(os.environ["PWD"], "dataset/weights/mu_tth_df_train_pt5_BDTG.weights.xml"),
        vars_ = vars_muons_jetdf_train_pt5,
        useBranch = None,
        convert = lambda s, lep: s #(-1)*(lep.mediumId == 0) + (lep.mediumId == 1)*s
    )
    return mva_muon_df_train_pt5

def muon_df_train_pt5_ttw(year):
    vars_muons_jetdf_train_pt5  = {
        "pt" : 
            [MVAvar("LepGood_pt"), lambda lep, jets: lep.pt],
        "eta" : 
            [MVAvar("LepGood_eta"), lambda lep, jets: lep.eta],
        "pfRelIso03_all" : 
            [MVAvar("LepGood_pfRelIso03_all"), lambda lep, jets: lep.pfRelIso03_all],
        "miniPFRelIso_chg" : 
            [MVAvar("LepGood_miniRelIsoCharged"), lambda lep, jets: lep.miniPFRelIso_chg ],
        "LepGood_miniRelIsoNeutral" :
            [MVAvar("LepGood_miniRelIsoNeutral"), lambda lep, jets: lep.miniPFRelIso_all - lep.miniPFRelIso_chg],
        "LepGood_jetNDauChargedMVASel" :
            [MVAvar("LepGood_jetNDauChargedMVASel"), lambda lep, jets: lep.jetNDauCharged],
        "jetPtRelv2" :
            [MVAvar("LepGood_jetPtRelv2"), lambda lep, jets: lep.jetPtRelv2],
        "LepGood_jetDF" : 
            [MVAvar("LepGood_jetDF"), lambda lep, jets: jets[lep.jetIdx].btagDeepFlavB if lep.jetIdx > -1 else 0],
        "LepGood_jetPtRatio" : 
            [MVAvar("LepGood_jetPtRatio"), lambda lep, jets: min(1. / (1. + lep.jetRelIso), 1.5) ],
        "LepGood_sip3d" : 
            [MVAvar("LepGood_sip3d"), lambda lep, jets: lep.sip3d],
        "LepGood_dxy" :
            [MVAvar("LepGood_dxy"), lambda lep, jets: np.log(abs(lep.dxy))],
        "LepGood_dz" : 
            [MVAvar("LepGood_dz"), lambda lep, jets: np.log(abs(lep.dz))],
        "LepGood_segmentComp" : 
            [MVAvar("LepGood_segmentComp"),lambda lep, jets: lep.segmentComp],
    }

    mva_muon_df_train_pt5 = mva_histo(
        name = "muon_df_train_pt5_ttw",
        xmlpath= os.path.join(os.environ["PWD"], "dataset/weights/mu_ttw_df_train_pt5_BDTG.weights.xml"),
        vars_ = vars_muons_jetdf_train_pt5,
        useBranch = None,
        convert = lambda s, lep: (-1)*(lep.mediumId == 0) + (lep.mediumId == 1)*s
    )
    return mva_muon_df_train_pt5

def muon_pnet_train_pt5_tth(year):
    vars_muons_jetpnet_train_pt5  = {
        "pt" : 
            [MVAvar("LepGood_pt"), lambda lep, jets: lep.pt],
        "eta" : 
            [MVAvar("LepGood_eta"), lambda lep, jets: lep.eta],
        "pfRelIso03_all" : 
            [MVAvar("LepGood_pfRelIso03_all"), lambda lep, jets: lep.pfRelIso03_all],
        "miniPFRelIso_chg" : 
            [MVAvar("LepGood_miniRelIsoCharged"), lambda lep, jets: lep.miniPFRelIso_chg ],
        "LepGood_miniRelIsoNeutral" :
            [MVAvar("LepGood_miniRelIsoNeutral"), lambda lep, jets: lep.miniPFRelIso_all - lep.miniPFRelIso_chg],
        "LepGood_jetNDauChargedMVASel" :
            [MVAvar("LepGood_jetNDauChargedMVASel"), lambda lep, jets: lep.jetNDauCharged],
        "jetPtRelv2" :
            [MVAvar("LepGood_jetPtRelv2"), lambda lep, jets: lep.jetPtRelv2],
        "LepGood_jetDF" : 
            [MVAvar("LepGood_jetPNET"), lambda lep, jets: jets[lep.jetIdx].btagPNetB if lep.jetIdx > -1 else 0],
        "LepGood_jetPtRatio" : 
            [MVAvar("LepGood_jetPtRatio"), lambda lep, jets: min(1. / (1. + lep.jetRelIso), 1.5) ],
        "LepGood_sip3d" : 
            [MVAvar("LepGood_sip3d"), lambda lep, jets: lep.sip3d],
        "LepGood_dxy" :
            [MVAvar("LepGood_dxy"), lambda lep, jets: np.log(abs(lep.dxy))],
        "LepGood_dz" : 
            [MVAvar("LepGood_dz"), lambda lep, jets: np.log(abs(lep.dz))],
        "LepGood_segmentComp" : 
            [MVAvar("LepGood_segmentComp"),lambda lep, jets: lep.segmentComp],
    }

    mva_muon_pnet_train_pt5 = mva_histo(
        name = "muon_pnet_train_pt5_tth",
        xmlpath= os.path.join(os.environ["PWD"], "dataset/weights/mu_tth_pnet_train_pt5_BDTG.weights.xml"),
        vars_ = vars_muons_jetpnet_train_pt5,
        useBranch = None,
        convert = lambda s, lep: s #(-1)*(lep.mediumId == 0) + (lep.mediumId == 1)*s
    )
    return mva_muon_pnet_train_pt5

def muon_pnet_train_pt5_ttw(year):
    vars_muons_jetpnet_train_pt5  = {
        "pt" : 
            [MVAvar("LepGood_pt"), lambda lep, jets: lep.pt],
        "eta" : 
            [MVAvar("LepGood_eta"), lambda lep, jets: lep.eta],
        "pfRelIso03_all" : 
            [MVAvar("LepGood_pfRelIso03_all"), lambda lep, jets: lep.pfRelIso03_all],
        "miniPFRelIso_chg" : 
            [MVAvar("LepGood_miniRelIsoCharged"), lambda lep, jets: lep.miniPFRelIso_chg ],
        "LepGood_miniRelIsoNeutral" :
            [MVAvar("LepGood_miniRelIsoNeutral"), lambda lep, jets: lep.miniPFRelIso_all - lep.miniPFRelIso_chg],
        "LepGood_jetNDauChargedMVASel" :
            [MVAvar("LepGood_jetNDauChargedMVASel"), lambda lep, jets: lep.jetNDauCharged],
        "jetPtRelv2" :
            [MVAvar("LepGood_jetPtRelv2"), lambda lep, jets: lep.jetPtRelv2],
        "LepGood_jetDF" : 
            [MVAvar("LepGood_jetPNET"), lambda lep, jets: jets[lep.jetIdx].btagPNetB if lep.jetIdx > -1 else 0],
        "LepGood_jetPtRatio" : 
            [MVAvar("LepGood_jetPtRatio"), lambda lep, jets: min(1. / (1. + lep.jetRelIso), 1.5) ],
        "LepGood_sip3d" : 
            [MVAvar("LepGood_sip3d"), lambda lep, jets: lep.sip3d],
        "LepGood_dxy" :
            [MVAvar("LepGood_dxy"), lambda lep, jets: np.log(abs(lep.dxy))],
        "LepGood_dz" : 
            [MVAvar("LepGood_dz"), lambda lep, jets: np.log(abs(lep.dz))],
        "LepGood_segmentComp" : 
            [MVAvar("LepGood_segmentComp"),lambda lep, jets: lep.segmentComp],
    }

    mva_muon_pnet_train_pt5 = mva_histo(
        name = "muon_pnet_train_pt5_ttw",
        xmlpath= os.path.join(os.environ["PWD"], "dataset/weights/mu_ttw_pnet_train_pt5_BDTG.weights.xml"),
        vars_ = vars_muons_jetpnet_train_pt5,
        useBranch = None,
        convert = lambda s, lep: (-1)*(lep.mediumId == 0) + (lep.mediumId == 1)*s
    )
    return mva_muon_pnet_train_pt5

def electron_pnet_wIso(year):
    vars_electron_pnet_wIso  = {
        "Electron_pt" : 
            [MVAvar("Electron_pt"), lambda lep, jets: lep.pt],
        "Electron_eta" : 
            [MVAvar("Electron_eta"), lambda lep, jets: lep.eta],
        "Electron_pfRelIso03_all" : 
            [MVAvar("Electron_pfRelIso03_all"), lambda lep, jets: lep.pfRelIso03_all],
        "Electron_miniPFRelIso_chg" : 
            [MVAvar("Electron_miniPFRelIso_chg"), lambda lep, jets: lep.miniPFRelIso_chg ],
        "Electron_miniRelIsoNeutral := Electron_miniPFRelIso_all - Electron_miniPFRelIso_chg" :
            [MVAvar("Electron_miniRelIsoNeutral := Electron_miniPFRelIso_all - Electron_miniPFRelIso_chg"), lambda lep, jets: lep.miniPFRelIso_all - lep.miniPFRelIso_chg],
        "Electron_jetNDauCharged" :
            [MVAvar("Electron_jetNDauCharged"), lambda lep, jets: lep.jetNDauCharged],
        "Electron_jetPtRelv2" :
            [MVAvar("Electron_jetPtRelv2"), lambda lep, jets: lep.jetPtRelv2],
        "Electron_jetBTagPNET := Electron_jetIdx > -1 ? Jet_btagPNetB[Electron_jetIdx] : 0" : 
            [MVAvar("Electron_jetBTagPNET := Electron_jetIdx > -1 ? Jet_btagPNetB[Electron_jetIdx] : 0"), lambda lep, jets: jets[lep.jetIdx].btagPNetB if lep.jetIdx > -1 else 0],
        "Electron_jetPtRatio := min(1 / (1 + Electron_jetRelIso), 1.5)" : 
            [MVAvar("Electron_jetPtRatio := min(1 / (1 + Electron_jetRelIso), 1.5)"), lambda lep, jets: min(1. / (1. + lep.jetRelIso), 1.5) ],
        "Electron_sip3d" : 
            [MVAvar("Electron_sip3d"), lambda lep, jets: lep.sip3d],
        "Electron_log_dxy := log(abs(Electron_dxy))" :
            [MVAvar("Electron_log_dxy := log(abs(Electron_dxy))"), lambda lep, jets: np.log(abs(lep.dxy))],
        "Electron_log_dz  := log(abs(Electron_dz))" : 
            [MVAvar("Electron_log_dz  := log(abs(Electron_dz))"), lambda lep, jets: np.log(abs(lep.dz))],
        "Electron_mvaIso" : 
            [MVAvar("Electron_mvaIso"),lambda lep, jets: lep.mvaIso],
    }

    mva_electron_pnet_wIso = mva_histo(
        name = "electron_pnet_wIso",
        xmlpath= os.path.join(os.environ["PWD"], "dataset/weights/el_ttw_pnet_BDTG.weights.xml"),
        vars_ = vars_electron_pnet_wIso,
        useBranch = None,
        #convert = lambda s, lep: (-1)*(lep.mvaNoIso == 0) + (lep.mvaNoIso == 1)*s
    )
    return mva_electron_pnet_wIso


def electron_df_wIso(year):
    vars_electron_df_wIso  = {
        "Electron_pt" : 
            [MVAvar("Electron_pt"), lambda lep, jets: lep.pt],
        "Electron_eta" : 
            [MVAvar("Electron_eta"), lambda lep, jets: lep.eta],
        "Electron_pfRelIso03_all" : 
            [MVAvar("Electron_pfRelIso03_all"), lambda lep, jets: lep.pfRelIso03_all],
        "Electron_miniPFRelIso_chg" : 
            [MVAvar("Electron_miniPFRelIso_chg"), lambda lep, jets: lep.miniPFRelIso_chg ],
        "Electron_miniRelIsoNeutral := Electron_miniPFRelIso_all - Electron_miniPFRelIso_chg" :
            [MVAvar("Electron_miniRelIsoNeutral := Electron_miniPFRelIso_all - Electron_miniPFRelIso_chg"), lambda lep, jets: lep.miniPFRelIso_all - lep.miniPFRelIso_chg],
        "Electron_jetNDauCharged" :
            [MVAvar("Electron_jetNDauCharged"), lambda lep, jets: lep.jetNDauCharged],
        "Electron_jetPtRelv2" :
            [MVAvar("Electron_jetPtRelv2"), lambda lep, jets: lep.jetPtRelv2],
        "Electron_jetBTagDeepFlavB := Electron_jetIdx > -1 ? Jet_btagDeepFlavB[Electron_jetIdx] : 0" : 
            [MVAvar("Electron_jetBTagDeepFlavB := Electron_jetIdx > -1 ? Jet_btagDeepFlavB[Electron_jetIdx] : 0"), lambda lep, jets: jets[lep.jetIdx].btagDeepFlavB if lep.jetIdx > -1 else 0],
        "Electron_jetPtRatio := min(1 / (1 + Electron_jetRelIso), 1.5)" : 
            [MVAvar("Electron_jetPtRatio := min(1 / (1 + Electron_jetRelIso), 1.5)"), lambda lep, jets: min(1. / (1. + lep.jetRelIso), 1.5) ],
        "Electron_sip3d" : 
            [MVAvar("Electron_sip3d"), lambda lep, jets: lep.sip3d],
        "Electron_log_dxy := log(abs(Electron_dxy))" :
            [MVAvar("Electron_log_dxy := log(abs(Electron_dxy))"), lambda lep, jets: np.log(abs(lep.dxy))],
        "Electron_log_dz  := log(abs(Electron_dz))" : 
            [MVAvar("Electron_log_dz  := log(abs(Electron_dz))"), lambda lep, jets: np.log(abs(lep.dz))],
        "Electron_mvaIso" : 
            [MVAvar("Electron_mvaIso"),lambda lep, jets: lep.mvaIso],
    }

    mva_electron_df_wIso = mva_histo(
        name = "electron_df_wIso",
        xmlpath= os.path.join(os.environ["PWD"], "dataset/weights/el_ttw_df_BDTG.weights.xml"),
        vars_ = vars_electron_df_wIso,
        useBranch = None,
        #convert = lambda s, lep: (-1)*(lep.mvaNoIso == 0) + (lep.mvaNoIso == 1)*s
    )
    return mva_electron_df_wIso


