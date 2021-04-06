from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from copy import deepcopy
import ROOT
import os 

class lepScaleFactors_WZ5TeV(Module):
    def __init__(self):
        self.recoToLoose   = {} 
        self.looseToTight  = {} 

        for fl in ['ele','mu']:
            self.recoToLoose['%s'%(fl)]  = self.loadHisto(os.environ['CMSSW_BASE'] + '/src/CMGTools/TTHAnalysis/data/leptonSF/refinal_%s_recotolooseSF.root'%(fl),"EGamma_SF2D")
            self.looseToTight['%s'%(fl)] = self.loadHisto(os.environ['CMSSW_BASE'] + '/src/CMGTools/TTHAnalysis/data/leptonSF/refinal_%s_loosetotightSF.root'%(fl), "EGamma_SF2D")


    def loadHisto(self, fil, hist):
        tf = ROOT.TFile.Open(fil)
        if not tf: raise RuntimeError("No such file %s"%fil)
        hist = tf.Get(hist)
        if not hist: raise RuntimeError("No such object %s in %s"%(hist,fil))
        ret = deepcopy(hist)
        tf.Close()
        return ret


    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for var in ',_ele_up,_ele_dn,_mu_up,_mu_dn'.split(','):
            self.out.branch('leptonSF_2l_br%s'%var,'F')
            self.out.branch('leptonSF_2l_sr%s'%var,'F')
            self.out.branch('leptonSF_3l_br%s'%var,'F')
            self.out.branch('leptonSF_3l_sr%s'%var,'F')


    def getLooseToTight(self,lep,var_str):
        out = 1
        hist = self.looseToTight['%s'%('ele' if abs(lep.pdgId) == 11 else 'mu')]
        etabin = max(1, min(hist.GetNbinsX(), hist.GetXaxis().FindBin(abs(lep.eta))));
        ptbin  = max(1, min(hist.GetNbinsY(), hist.GetYaxis().FindBin(lep.pt)));
        if abs(lep.pdgId) == 13: 
            var = 0 if var_str == '' or 'mu' not in var_str else  1 if 'up' in var_str else -1 
            out = out * hist.GetBinContent(etabin,ptbin)+var*hist.GetBinError(etabin,ptbin)
            #print 'Muon out: ', out, hist.GetBinContent(etabin,ptbin), hist.GetBinError(etabin,ptbin)
        if abs(lep.pdgId) == 11: 
            var = 0 if var_str == '' or 'ele' not in var_str else  1 if 'up' in var_str else -1 
            out = out * hist.GetBinContent(etabin,ptbin)+var*hist.GetBinError(etabin,ptbin)
            #print 'Electron out: ', out, hist.GetBinContent(etabin,ptbin), hist.GetBinError(etabin,ptbin)
        
        return out

    def getRecoToLoose(self,lep,var_str):
        out = 1
        hist = self.recoToLoose['%s'%('ele' if abs(lep.pdgId) == 11 else 'mu')]
        etabin = max(1, min(hist.GetNbinsX(), hist.GetXaxis().FindBin(abs(lep.eta))));
        ptbin  = max(1, min(hist.GetNbinsY(), hist.GetYaxis().FindBin(lep.pt)));
        if abs(lep.pdgId) == 13: 
            var = 0 if var_str == '' or 'mu' not in var_str else  1 if 'up' in var_str else -1 
            out = out * hist.GetBinContent(etabin,ptbin)+var*hist.GetBinError(etabin,ptbin)
        if abs(lep.pdgId) == 11: 
            var = 0 if var_str == '' or 'ele' not in var_str else  1 if 'up' in var_str else -1 
            out = out * hist.GetBinContent(etabin,ptbin)+var*hist.GetBinError(etabin,ptbin)
            
        return out

    def analyze(self, event):
        
        # leptons
        all_leps = [l for l in Collection(event,"LepGood")]
        nFO      = getattr(event,"nLepFO_Recl")
        chosen   = getattr(event,"iLepFO_Recl")
        leps     = [all_leps[chosen[i]] for i in xrange(nFO)]
        if len(leps) >= 3:
            ilepW    = int(getattr(event,"idx_lW"))
            lepsW    = leps[ilepW]
            ilepZ1   = int(getattr(event,"idx_lZ1"))
            lepsZ1   = leps[ilepZ1]
            #print 'Check: lepW eta and pt,  id, tight SF: ', lepsW.eta, lepsW.pt, lepsW.pdgId, self.getLooseToTight(lepsW,'')
            #print 'Check: lepZ1 eta and pt, id, tight SF: ', lepsZ1.eta, lepsZ1.pt, lepsZ1.pdgId, self.getLooseToTight(lepsZ1,'')

        # lepton scale factors
        for var in ''.split(','):
            leptonSF_2l_br = 1
            leptonSF_2l_sr = 1
            leptonSF_3l_br = 1
            leptonSF_3l_sr = 1

            if len(leps) >= 2:
                leptonSF_2l_br = self.getRecoToLoose(leps[0],var) * self.getRecoToLoose(leps[1],var)
                leptonSF_2l_sr = leptonSF_2l_br * self.getLooseToTight(leps[0],var) * self.getLooseToTight(leps[1],var)

            if len(leps) >= 3:
                leptonSF_3l_br = self.getRecoToLoose(leps[0],var) * self.getRecoToLoose(leps[1],var) * self.getRecoToLoose(leps[2],var)
                leptonSF_3l_sr = leptonSF_3l_br * self.getLooseToTight(lepsW,var) * self.getLooseToTight(lepsZ1,var) 


            self.out.fillBranch('leptonSF_2l_br%s'%var, leptonSF_2l_br)
            self.out.fillBranch('leptonSF_2l_sr%s'%var, leptonSF_2l_sr)
            self.out.fillBranch('leptonSF_3l_br%s'%var, leptonSF_3l_br)
            self.out.fillBranch('leptonSF_3l_sr%s'%var, leptonSF_3l_sr)

        for var in '_ele_up,_ele_dn,_mu_up,_mu_dn'.split(','):
            leptonSF_2l_br = 1
            leptonSF_2l_sr = 1
            leptonSF_3l_br = 1
            leptonSF_3l_sr = 1

            if len(leps) >= 2:
                leptonSF_2l_br = self.getRecoToLoose(leps[0],var) * self.getRecoToLoose(leps[1],var)
                leptonSF_2l_sr = leptonSF_2l_br * self.getLooseToTight(leps[0],var) * self.getLooseToTight(leps[1],var)

            if len(leps) >= 3:
                leptonSF_3l_br = self.getRecoToLoose(leps[0],var) * self.getRecoToLoose(leps[1],var) * self.getRecoToLoose(leps[2],var)
                leptonSF_3l_sr = leptonSF_3l_br * self.getLooseToTight(lepsW,var) * self.getLooseToTight(lepsZ1,var)


            self.out.fillBranch('leptonSF_2l_br%s'%var, leptonSF_2l_br)
            self.out.fillBranch('leptonSF_2l_sr%s'%var, leptonSF_2l_sr)
            self.out.fillBranch('leptonSF_3l_br%s'%var, leptonSF_3l_br)
            self.out.fillBranch('leptonSF_3l_sr%s'%var, leptonSF_3l_sr)
        

        return True
