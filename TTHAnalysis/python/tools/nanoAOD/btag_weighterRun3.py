from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop   import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel   import Collection
from CMGTools.TTHAnalysis.tools.nanoAOD.friendVariableProducerTools import writeOutput
import ROOT as r
from copy import deepcopy
import correctionlib._core as core

# Mainly based on https://github.com/cericeci/cmgtools-lite/blob/RunII_SUSY_EWK_fromWZ/TTHAnalysis/python/tools/bTagWeightAnalyzer.py

def color_msg(msg, color = "none", indentlevel = 0):
    """ Prints a message with ANSI coding so it can be printout with colors """
    codes = {
        "none" : "0m",
        "green" : "1;32m",
        "red" : "1;31m",
        "blue" : "1;34m",
        "yellow" : "1;35m"
    }
    indent = " "*indentlevel + "+"
    print("\033[%s%s %s \033[0m"%(codes[color], indent, msg))
    return  

class btag_weighterRun3(Module):
    def __init__(self, json=None, eff=None, json_ptrel=None, algo = 'deepJet', wp = "M", branchJet = "JetSel30", labelJet = "_Recl", branchflavour = 'hadronFlavour',
                 label = "", year = "2022", SFmeasReg = "mujets",
                 minptlow = 20, minpthigh = 30, maxeta = 2.4,
                 jecvars = ["jesTotal", "jer"], lepenvars = ["mu"],
                 splitCorrelations = False, useCombnuisances = False, debug = False,
                 verbosity = 0):

        self.algo      = algo
        self.wp        = wp
        self.branchJet = branchJet
        self.labelJet  = labelJet
        self.label     = label
        self.year      = year
        self.minptlow  = minptlow
        self.minpthigh = minpthigh
        self.maxeta    = maxeta
        self.branchflavour = branchflavour
        self.splitCorr     = splitCorrelations
        self.useCombnuisances = useCombnuisances
        self.debug         = debug
        self.SFmeasReg    = SFmeasReg
        self.verbosity = verbosity

        self.systsJEC   = {0: ""}
        self.systsLepEn = {}
        self.systsCorr  = {}
        self.nominaljecscaff = "_nom"

        if (SFmeasReg != "mujets" and SFmeasReg != "comb") and splitCorrelations:
            raise RuntimeError("FATAL: splitting corrs. for a b-tag. SF non-mujets measurement! This is not implemented :(.")

        if   len(jecvars):
            for i, var in enumerate(jecvars):
                self.systsJEC[i+1]    = "_%sUp"%var
                self.systsJEC[-(i+1)] = "_%sDown"%var
        if   len(lepenvars):
            for i, var in enumerate(lepenvars):
                self.systsLepEn[i+1]    = "_%sUp"%var
                self.systsLepEn[-(i+1)] = "_%sDown"%var

        btagDefaultNuisances = ['btag_correlated', 'mistag_correlated', 'btag_uncorrelated', 'mistag_uncorrelated', "btag_jes", "btag_pileup", "btag_type3", "btag_stat"]
        btagCombNuisances = ['btag_correlated', 'btag_uncorrelated', 'mistag_correlated', 'mistag_uncorrelated', 'btag_bfragmentation', 'btag_colorreconnection', 'btag_hdamp', 'btag_jer', 'btag_jes', 'btag_pdf', 'btag_pileup', 'btag_stat', 'btag_topmass', 'btag_type3']
        if self.useCombnuisances:
            btagNuisances = btagCombNuisances
        else:
            btagNuisances = btagDefaultNuisances
        if self.splitCorr:
            for i, var in enumerate(btagNuisances):
                self.systsCorr[i+1]    = "_%sUp"%var
                self.systsCorr[-(i+1)] = "_%sDown"%var


        #self.btagWPs   = {"DeepFlav_2022_L"   : 0.0490, #copied from 2018
        #                  "DeepFlav_2022_M"   : 0.2783,
        #                  "DeepFlav_2022_T"   : 0.7100,
        #                  "DeepCSV_2022_L"    : 0.1208,
        #                  "DeepCSV_2022_M"    : 0.4168,
        #                  "DeepCSV_2022_T"    : 0.7665,
        #                 }

        self.algodict = {"deepJet" : "DeepFlav",
                         "particleNet"     : "PNet",
                         "robustParticleTransformer" : "RobustParTAK4"
                         }    
        self.branchbtag = "btag" + self.algodict[self.algo] + "B"

        self.ret = {}

        self.btvjson = core.CorrectionSet.from_file(json)
        self.btaggingWPsEvaluator = self.btvjson[self.algo + "_wp_values"]

        self.btvjson_ptrel = core.CorrectionSet.from_file(json_ptrel)
        

        self.btagWPs = {}
        for _wp_ in ["L", "M", "T"]:
            self.btagWPs[self.algodict[self.algo] + "_{y}_{wp}".format(y = self.year, wp = _wp_)] = self.btaggingWPsEvaluator.evaluate(_wp_)
        
        self.cutVal = self.btagWPs[ self.algodict[self.algo] + "_" + self.year + "_" + self.wp ]
        #### Eficiencias
        f_eff        = r.TFile.Open(eff, "read")
        self.h_eff_b = deepcopy(f_eff.Get("btagEff_TT_dilep_{}_B_h2d".format(self.wp)).Clone())
        self.h_eff_c = deepcopy(f_eff.Get("btagEff_TT_dilep_{}_C_h2d".format(self.wp)).Clone())
        self.h_eff_l = deepcopy(f_eff.Get("btagEff_TT_dilep_{}_L_h2d".format(self.wp)).Clone())
        f_eff.Close()

        return


    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.wrappedOutputTree = wrappedOutputTree

        self.wrappedOutputTree.branch("bTagWeight" + self.label + "_btag_Up"  , "F")
        self.wrappedOutputTree.branch("bTagWeight" + self.label + "_btag_Dn"  , "F")
        self.wrappedOutputTree.branch("bTagWeight" + self.label + "_mistag_Up", "F")
        self.wrappedOutputTree.branch("bTagWeight" + self.label + "_mistag_Dn", "F")

        for delta,corrVar in self.systsCorr.items():
            self.wrappedOutputTree.branch("bTagWeight" + self.label + corrVar , "F")

        for delta,jecVar in self.systsJEC.items():
            self.wrappedOutputTree.branch("bTagWeight" + self.label + jecVar , "F")

        for delta,lepVar in self.systsLepEn.items():
            self.wrappedOutputTree.branch("bTagWeight" + self.label + lepVar , "F")

        return


    def analyze(self, event):
        self.event = event
        self.ret.clear()
        self.all_jets  = [j for j in Collection(event, "Jet")]
        self.jets = []
        self.computeWeights(event)

        writeOutput(self, self.ret)
        return True


    def computeWeights(self, event):

        if self.verbosity > 0:
            color_msg(f"Analyzing event: {event.event}", color = "green", indentlevel = 0)
        for delta,jecVar in self.systsJEC.items():
            mcTag     = 1.
            mcNoTag   = 1.
            dataTag   = 1.
            dataNoTag = 1.
            sysHFup   = 1.
            sysHFdn   = 1.
            sysLFup   = 1.
            sysLFdn   = 1.

            sysHFupCorr   = 1.
            sysHFdnCorr   = 1.
            sysLFupCorr   = 1.
            sysLFdnCorr   = 1.
            sysHFupUncorr = 1.
            sysHFdnUncorr = 1.
            sysLFupUncorr = 1.
            sysLFdnUncorr = 1.

            sysHFupJes    = 1.
            sysHFdnJes    = 1.
            sysHFupPileup = 1.
            sysHFdnPileup = 1.
            sysHFupType3  = 1.
            sysHFdnType3  = 1.
            sysHFupStat   = 1.
            sysHFdnStat   = 1.

            self.jets = [self.all_jets[getattr(event, 'iJSel{label}{v}'.format(branch = self.branchJet, v = "%s"%jecVar if jecVar != "" else "", label = self.labelJet))[j]]
                         #for j in xrange(min([getattr(event, 'nJetSel30{v}_Recl'.format(v = jecVar)), 5]))] #### WARNING: this is only valid when ignoring events with nJet>5!!!!!!!!!!
                         for j in range(getattr(event, 'n{branch}{label}{v}'.format(branch = self.branchJet, v = "%s"%jecVar if jecVar != "" else "", label = self.labelJet) ))] #### WARNING: this is only valid when ignoring events with nJet>5!!!!!!!!!!

            jetjecsysscaff = (jecVar if jecVar != "" else self.nominaljecscaff)

            if self.verbosity > 0:
                color_msg(f"Have {len(self.jets)} jets", indentlevel = 1)

            for ij, jet in enumerate(self.jets):
                flavour = getattr(jet, self.branchflavour) if hasattr(jet, self.branchflavour) else jet.mcFlavour
                jet.pt = getattr(jet, "pt" + jetjecsysscaff)

                if self.verbosity > 0 and flavour == 5:
                    color_msg(f"Jet {ij} is: flavor = {flavour}, pT = {jet.pt}, eta = {jet.eta}", "blue", indentlevel = 2)
                    if abs(jet.eta) >= self.maxeta or abs(jet.pt)  <= self.minptlow:
                        color_msg(f"Skipping this jet because eta requirements (abs(eta) > {self.maxeta} or pT < {self.minptlow})", indentlevel = 3)

                if abs(jet.eta) >= self.maxeta:    continue
                if abs(jet.pt)  <= self.minptlow : continue
               

                eff = self.getEffFromHisto(jet.pt, jet.eta, flavour) # WARNING: do not use later without changing it back!
                SF  = self.getSF (jet.pt, jet.eta, flavour)

                if self.verbosity > 0  and flavour == 5:
                    color_msg(f"Jet {ij}: efficiency = {eff}, SF = {SF}", "blue", indentlevel = 3)
                    
                #istag = (getattr(jet, self.branchbtag) > self.cutVal) and (abs(jet.eta) < self.maxeta and jet.pt > self.minptlow)
                istag = (getattr(jet, self.branchbtag) > self.cutVal) and (abs(jet.eta) < self.maxeta and jet.pt > self.minptlow) # AT THIS MOMENT ONLY ONE JET COLLECTION IS ADMITTED

                if self.debug and jecVar == "":
                    print("[btag_weighter::computeWeights] -", jet.pt, jet.eta, getattr(jet, self.branchbtag), eff, SF)

                if eff == 0:
                    print("[btag_weighter::computeWeights] - WARNING: jet b-tagging is zero. To prevent a ZeroDivision error, we will fix its value to 10^-5.")
                    eff = 1e-5

                if istag:
                    mcTag   *= eff
                    dataTag *= eff*SF[0]

                    if (flavour in [4, 5]) and (jecVar == ""):
                        sysHFup *= eff*SF[1]
                        sysHFdn *= eff*SF[2]
                        sysLFup *= eff*SF[0]
                        sysLFdn *= eff*SF[0]

                        if self.splitCorr:
                            sysHFupCorr   *= eff*SF[3]
                            sysHFdnCorr   *= eff*SF[4]
                            sysHFupUncorr *= eff*SF[5]
                            sysHFdnUncorr *= eff*SF[6]
                            sysLFupCorr   *= eff*SF[0]
                            sysLFdnCorr   *= eff*SF[0]
                            sysLFupUncorr *= eff*SF[0]
                            sysLFdnUncorr *= eff*SF[0]

                            sysHFupJes    *= eff*SF[7]
                            sysHFdnJes    *= eff*SF[8]
                            sysHFupPileup *= eff*SF[9]
                            sysHFdnPileup *= eff*SF[10]
                            sysHFupType3  *= eff*SF[11]
                            sysHFdnType3  *= eff*SF[12]
                            sysHFupStat   *= eff*SF[13]
                            sysHFdnStat   *= eff*SF[14]

                    elif jecVar == "":
                        sysHFup *= eff*SF[0]
                        sysHFdn *= eff*SF[0]
                        sysLFup *= eff*SF[1]
                        sysLFdn *= eff*SF[2]

                        if self.splitCorr:
                            sysHFupCorr   *= eff*SF[0]
                            sysHFdnCorr   *= eff*SF[0]
                            sysHFupUncorr *= eff*SF[0]
                            sysHFdnUncorr *= eff*SF[0]
                            sysLFupCorr   *= eff*SF[3]
                            sysLFdnCorr   *= eff*SF[4]
                            sysLFupUncorr *= eff*SF[5]
                            sysLFdnUncorr *= eff*SF[6]

                            sysHFupJes    *= eff*SF[0]
                            sysHFdnJes    *= eff*SF[0]
                            sysHFupPileup *= eff*SF[0]
                            sysHFdnPileup *= eff*SF[0]
                            sysHFupType3  *= eff*SF[0]
                            sysHFdnType3  *= eff*SF[0]
                            sysHFupStat   *= eff*SF[0]
                            sysHFdnStat   *= eff*SF[0]

                else:
                    mcNoTag   *= (1 - eff      )
                    dataNoTag *= (1 - eff*SF[0])

                    if (flavour in [4, 5]) and (jecVar == ""):
                        sysHFup *= (1 - eff*SF[1])
                        sysHFdn *= (1 - eff*SF[2])
                        sysLFup *= (1 - eff*SF[0])
                        sysLFdn *= (1 - eff*SF[0])

                        if self.splitCorr:
                            sysHFupCorr   *= (1 - eff*SF[3])
                            sysHFdnCorr   *= (1 - eff*SF[4])
                            sysHFupUncorr *= (1 - eff*SF[5])
                            sysHFdnUncorr *= (1 - eff*SF[6])
                            sysLFupCorr   *= (1 - eff*SF[0])
                            sysLFdnCorr   *= (1 - eff*SF[0])
                            sysLFupUncorr *= (1 - eff*SF[0])
                            sysLFdnUncorr *= (1 - eff*SF[0])

                            sysHFupJes    *= (1 - eff*SF[7] )
                            sysHFdnJes    *= (1 - eff*SF[8] )
                            sysHFupPileup *= (1 - eff*SF[9] )
                            sysHFdnPileup *= (1 - eff*SF[10])
                            sysHFupType3  *= (1 - eff*SF[11])
                            sysHFdnType3  *= (1 - eff*SF[12])
                            sysHFupStat   *= (1 - eff*SF[13])
                            sysHFdnStat   *= (1 - eff*SF[14])

                    elif jecVar == "":
                        sysHFup *= (1 - eff*SF[0])
                        sysHFdn *= (1 - eff*SF[0])
                        sysLFup *= (1 - eff*SF[1])
                        sysLFdn *= (1 - eff*SF[2])

                        if self.splitCorr:
                            sysHFupCorr   *= (1 - eff*SF[0])
                            sysHFdnCorr   *= (1 - eff*SF[0])
                            sysHFupUncorr *= (1 - eff*SF[0])
                            sysHFdnUncorr *= (1 - eff*SF[0])
                            sysLFupCorr   *= (1 - eff*SF[3])
                            sysLFdnCorr   *= (1 - eff*SF[4])
                            sysLFupUncorr *= (1 - eff*SF[5])
                            sysLFdnUncorr *= (1 - eff*SF[6])

                            sysHFupJes    *= (1 - eff*SF[0])
                            sysHFdnJes    *= (1 - eff*SF[0])
                            sysHFupPileup *= (1 - eff*SF[0])
                            sysHFdnPileup *= (1 - eff*SF[0])
                            sysHFupType3  *= (1 - eff*SF[0])
                            sysHFdnType3  *= (1 - eff*SF[0])
                            sysHFupStat   *= (1 - eff*SF[0])
                            sysHFdnStat   *= (1 - eff*SF[0])

            central = (dataNoTag * dataTag ) / ( mcNoTag * mcTag )
            if self.verbosity > 0:
                color_msg(f"central = {central} = ({dataNoTag} * {dataTag})/({mcNoTag} * {mcTag}) ", "blue", indentlevel = 2)
                color_msg(f"_btag_correlatedUp = {sysHFupCorr   / ( mcNoTag * mcTag )} = {sysHFupCorr} / ({mcNoTag} * {mcTag}) ", "blue", indentlevel = 2)
                color_msg(f"_btag_correlatedDown = {sysHFdnCorr   / ( mcNoTag * mcTag )} = {sysHFdnCorr} / ({mcNoTag} * {mcTag})", "blue", indentlevel = 2)


            self.ret["bTagWeight" + self.label + jecVar] = central


            # b-tagging & mistagging eff. unc. varied weights
            if jecVar == "":
                self.ret["bTagWeight" + self.label + "_btag_Up"]   = sysHFup / ( mcNoTag * mcTag )
                self.ret["bTagWeight" + self.label + "_btag_Dn"]   = sysHFdn / ( mcNoTag * mcTag )
                self.ret["bTagWeight" + self.label + "_mistag_Up"] = sysLFup / ( mcNoTag * mcTag )
                self.ret["bTagWeight" + self.label + "_mistag_Dn"] = sysLFdn / ( mcNoTag * mcTag )

                if self.splitCorr:
                    self.ret["bTagWeight" + self.label + "_btag_correlatedUp"]       = sysHFupCorr   / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_btag_correlatedDown"]     = sysHFdnCorr   / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_mistag_correlatedUp"]     = sysLFupCorr   / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_mistag_correlatedDown"]   = sysLFdnCorr   / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_btag_uncorrelatedUp"]     = sysHFupUncorr / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_btag_uncorrelatedDown"]   = sysHFdnUncorr / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_mistag_uncorrelatedUp"]   = sysLFupUncorr / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_mistag_uncorrelatedDown"] = sysLFdnUncorr / ( mcNoTag * mcTag )

                    self.ret["bTagWeight" + self.label + "_btag_jesUp"]              = sysHFupJes    / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_btag_jesDown"]            = sysHFdnJes    / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_btag_pileupUp"]           = sysHFupPileup / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_btag_pileupDown"]         = sysHFdnPileup / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_btag_type3Up"]            = sysHFupType3  / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_btag_type3Down"]          = sysHFdnType3  / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_btag_statUp"]             = sysHFupStat   / ( mcNoTag * mcTag )
                    self.ret["bTagWeight" + self.label + "_btag_statDown"]           = sysHFdnStat   / ( mcNoTag * mcTag )


                for ldelta,lepVar in self.systsLepEn.items():
                    mcTag     = 1.
                    mcNoTag   = 1.
                    dataTag   = 1.
                    dataNoTag = 1.

                    self.jets    = [self.all_jets[getattr(event, 'iJSel{label}{v}'.format(v = lepVar))[j]]
                                for j in range(min([getattr(event, 'nJet30{label}{v}'.format(v = lepVar)), 5]))]

                    jetjecsysscaff = self.nominaljecscaff

                    for jet in self.jets:
                        flavour = getattr(jet, self.branchflavour) if hasattr(jet, self.branchflavour) else jet.mcFlavour
                        jet.pt = getattr(jet, "pt" + jetjecsysscaff)

                        if abs(jet.eta) >= self.maxeta:    continue
                        if abs(jet.pt)  <= self.minptlow : continue

                        eff = self.getEffFromHisto(jet.pt, jet.eta, flavour) # WARNING: do not use later without changing it back!
                        SF  = self.getSF (jet.pt, jet.eta, flavour)

                        istag = (getattr(jet, self.branchbtag) > self.cutVal) and (abs(jet.eta) < self.maxeta and jet.pt > self.minptlow)

                        if eff == 0:
                            print("[btag_weighter::computeWeights] - WARNING: jet b-tagging is zero. To prevent a ZeroDivision error, we will fix its value to 10^-5.")
                            eff = 1e-5

                        if istag:
                            mcTag   *= eff
                            dataTag *= eff*SF[0]
                        else:
                            mcNoTag   *= (1 - eff      )
                            dataNoTag *= (1 - eff*SF[0])

                    central = (dataNoTag * dataTag ) / ( mcNoTag * mcTag )

                    self.ret["bTagWeight" + self.label + lepVar] = central

        return


    def getEffFromHisto(self, pt, eta, mcFlavour):
        histo = [self.h_eff_b, self.h_eff_c, self.h_eff_l][self.pogFlavor(mcFlavour)]

        normal = True # normal := {x: pt, y: eta}
        if (histo.GetXaxis().GetBinUpEdge(histo.GetNbinsX())) < 10: normal = False

        tmpeta = eta

        if    ((normal     and histo.GetYaxis().GetBinLowEdge(1) >= 0)
            or (not normal and histo.GetXaxis().GetBinLowEdge(1) >= 0)):
            tmpeta = abs(tmpeta)

        if normal:
            xbin = max(1, min(histo.GetNbinsX(), histo.GetXaxis().FindBin(pt)))
            ybin = max(1, min(histo.GetNbinsY(), histo.GetYaxis().FindBin(tmpeta)))

        else:
            xbin = max(1, min(histo.GetNbinsX(), histo.GetXaxis().FindBin(tmpeta)))
            ybin = max(1, min(histo.GetNbinsY(), histo.GetYaxis().FindBin(pt)))
            if self.verbosity > 0:
                color_msg(f"Choosing bin: x={xbin} (eta = {tmpeta}), y={ybin} (pt = {pt}).", "red", indentlevel=3)

        return histo.GetBinContent(xbin, ybin)


    def getSF(self, pt, eta, flavour):
        pt_cutoff  = max(20. , min(999., pt))
        eta_cutoff = min(2.49, abs(eta))

#        if flavour != 0:
#            measurementRegion = self.SFmeasReg
#        else:
#            measurementRegion = "incl"
#
#        theReader  = self.btvjson[self.algo + "_" + measurementRegion]

        #if flavour == 4: # is a charm jet
        #    flavour = 5 # use the b flavour SFs (preliminary version)

        if flavour != 0:
            measurementRegion = self.SFmeasReg
            theReader  = self.btvjson_ptrel[self.algo + "_" + measurementRegion]
        else:
            measurementRegion = "light"
            theReader  = self.btvjson[self.algo + "_" + measurementRegion]

        SF = theReader.evaluate("central", self.wp, flavour, eta_cutoff, pt_cutoff)
        SFup = theReader.evaluate("up", self.wp, flavour, eta_cutoff, pt_cutoff)
        SFdn = theReader.evaluate("down", self.wp, flavour, eta_cutoff, pt_cutoff)

        if not self.splitCorr:
            return [SF, SFup, SFdn]
        else:
            # PRELIMINARY PATH
            if self.useCombnuisances:
                if flavour in [4, 5]:
                    SFupCorr   = theReader.evaluate("up_correlated",self.wp,     flavour, eta_cutoff, pt_cutoff)
                    SFdnCorr   = theReader.evaluate("down_correlated",self.wp,   flavour, eta_cutoff, pt_cutoff)
                    SFupUncorr = theReader.evaluate("up_uncorrelated",self.wp,   flavour, eta_cutoff, pt_cutoff)
                    SFdnUncorr = theReader.evaluate("down_uncorrelated",self.wp, flavour, eta_cutoff, pt_cutoff)
                    SFupjes    = theReader.evaluate("up_jes", self.wp,           flavour, eta_cutoff, pt_cutoff)
                    SFdnjes    = theReader.evaluate("down_jes", self.wp,         flavour, eta_cutoff, pt_cutoff)
                    SFuppileup = theReader.evaluate("up_pileup", self.wp,        flavour, eta_cutoff, pt_cutoff)
                    SFdnpileup = theReader.evaluate("down_pileup", self.wp,      flavour, eta_cutoff, pt_cutoff)
                    SFuptype3  = theReader.evaluate("up_type3", self.wp,         flavour, eta_cutoff, pt_cutoff)
                    SFdntype3  = theReader.evaluate("down_type3", self.wp,       flavour, eta_cutoff, pt_cutoff)
                    SFupstat   = theReader.evaluate("up_statistic", self.wp,     flavour, eta_cutoff, pt_cutoff)
                    SFdnstat   = theReader.evaluate("down_statistic", self.wp,   flavour, eta_cutoff, pt_cutoff)
                    #WIP falta incluir mas unc 'btag_bfragmentation', 'btag_colorreconnection', 'btag_hdamp'
                    #SFupjer    = theReader.evaluate("up_jer", self.wp,           flavour, eta_cutoff, pt_cutoff)
                    #SFdnjer    = theReader.evaluate("down_jer", self.wp,         flavour, eta_cutoff, pt_cutoff)
                    #SFuppdf    = theReader.evaluate("up_pdf", self.wp,           flavour, eta_cutoff, pt_cutoff)
                    #SFdnpdf    = theReader.evaluate("down_pdf", self.wp,         flavour, eta_cutoff, pt_cutoff)
                    #SFuptopmass= theReader.evaluate("up_topmass", self.wp,           flavour, eta_cutoff, pt_cutoff)
                    #SFdntopmass= theReader.evaluate("down_topmass", self.wp,         flavour, eta_cutoff, pt_cutoff)
                    #SFuphdamp  = theReader.evaluate("up_hdamp", self.wp,           flavour, eta_cutoff, pt_cutoff)
                    #SFdnhdamp  = theReader.evaluate("down_hdamp", self.wp,         flavour, eta_cutoff, pt_cutoff) 
                else:
                    SFupCorr   = 1.
                    SFdnCorr   = 1.
                    SFupUncorr = 1.
                    SFdnUncorr = 1.
                    SFupjes    = 1.
                    SFdnjes    = 1.
                    SFuppileup = 1.
                    SFdnpileup = 1.
                    SFuptype3  = 1.
                    SFdntype3  = 1.
                    SFupstat   = 1.
                    SFdnstat   = 1.

                return [SF, SFup, SFdn,
                        SFupCorr, SFdnCorr, SFupUncorr, SFdnUncorr,
                        SFupjes, SFdnjes, SFuppileup, SFdnpileup, SFuptype3, SFdntype3, SFupstat, SFdnstat]

            #USUAL PATH
            else:
                SFupCorr   = theReader.evaluate("up_correlated",self.wp,     flavour, eta_cutoff, pt_cutoff)
                SFdnCorr   = theReader.evaluate("down_correlated",self.wp,   flavour, eta_cutoff, pt_cutoff)
                SFupUncorr = theReader.evaluate("up_uncorrelated",self.wp,   flavour, eta_cutoff, pt_cutoff)
                SFdnUncorr = theReader.evaluate("down_uncorrelated",self.wp, flavour, eta_cutoff, pt_cutoff)
                if flavour in [4, 5]:
                    SFupjes    = theReader.evaluate("up_jes", self.wp,           flavour, eta_cutoff, pt_cutoff)
                    SFdnjes    = theReader.evaluate("down_jes", self.wp,         flavour, eta_cutoff, pt_cutoff)
                    SFuppileup = theReader.evaluate("up_pileup", self.wp,        flavour, eta_cutoff, pt_cutoff)
                    SFdnpileup = theReader.evaluate("down_pileup", self.wp,      flavour, eta_cutoff, pt_cutoff)
                    SFuptype3  = theReader.evaluate("up_type3", self.wp,         flavour, eta_cutoff, pt_cutoff)
                    SFdntype3  = theReader.evaluate("down_type3", self.wp,       flavour, eta_cutoff, pt_cutoff)
                    SFupstat   = theReader.evaluate("up_statistic", self.wp,     flavour, eta_cutoff, pt_cutoff)
                    SFdnstat   = theReader.evaluate("down_statistic", self.wp,   flavour, eta_cutoff, pt_cutoff)
                else:
                    SFupjes    = 1.
                    SFdnjes    = 1.
                    SFuppileup = 1.
                    SFdnpileup = 1.
                    SFuptype3  = 1.
                    SFdntype3  = 1.
                    SFupstat   = 1.
                    SFdnstat   = 1.
    
    
                return [SF, SFup, SFdn,
                        SFupCorr, SFdnCorr, SFupUncorr, SFdnUncorr,
                        SFupjes, SFdnjes, SFuppileup, SFdnpileup, SFuptype3, SFdntype3, SFupstat, SFdnstat]


    def pogFlavor(self, hadronFlavor):
        match = {5:0, # b
                 4:1, # c
                 0:2, # l
                 1:2, # l
                 2:2, # l
                 3:2, # l
        }
        if hadronFlavor in list(match.keys()): return match[hadronFlavor]
        return 2

if __name__ == '__main__':
    """ Debug the module """
    from sys import argv
    from copy import deepcopy
    import os
    from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import eventLoop
    from PhysicsTools.NanoAODTools.postprocessing.framework.output import FriendOutput, FullOutput
    from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import InputTree
    ## Loose selections
    from CMGTools.TTHAnalysis.tools.nanoAOD.functions_wz import _loose_muon
    from CMGTools.TTHAnalysis.tools.nanoAOD.functions_wz import _loose_electron
    from CMGTools.TTHAnalysis.tools.nanoAOD.functions_wz import _loose_lepton

    ## Fakeable selections
    from CMGTools.TTHAnalysis.tools.nanoAOD.functions_wz import _fO_muon
    from CMGTools.TTHAnalysis.tools.nanoAOD.functions_wz import _fO_electron
    from CMGTools.TTHAnalysis.tools.nanoAOD.functions_wz import _fO_lepton

    ## Tight selections
    from CMGTools.TTHAnalysis.tools.nanoAOD.functions_wz import _tight_muon
    from CMGTools.TTHAnalysis.tools.nanoAOD.functions_wz import _tight_electron
    from CMGTools.TTHAnalysis.tools.nanoAOD.functions_wz import _tight_lepton
    
    from CMGTools.TTHAnalysis.tools.nanoAOD.functions_wz import conept
    
    # --- b tagging working points from 2018
    looseDeepFlavB = 0.0494
    mediumDeepFlavB = 0.2770
    looselep = lambda lep          : _loose_lepton(lep, looseDeepFlavB, mediumDeepFlavB)
    cleanlep = lambda lep, jetlist :    _fO_lepton(lep, looseDeepFlavB, mediumDeepFlavB, jetlist)
    folep    = lambda lep, jetlist :    _fO_lepton(lep, looseDeepFlavB, mediumDeepFlavB, jetlist)
    tightlep = lambda lep, jetlist : _tight_lepton(lep, looseDeepFlavB, mediumDeepFlavB, jetlist)


    mainpath = "/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v2/mc/2022EE/"
    process = "WZto3LNu"
#    process = "TTTo2L2Nu_part17"
    
    friends = [
      "jmeCorrections",
      "lepmva",
      "leptonJetRecleaning_Elewp090",
      "leptonBuilder_Elewp090",
    ]
    nentries = int(argv[1])
    ### Open the main file
    file_ = r.TFile( os.path.join(mainpath, process+".root") )
    tree = file_.Get("Events")
    for friend in friends:
      print(os.path.join(mainpath, friend, process+"_Friend.root"))
      friendfile = r.TFile( os.path.join(mainpath, friend, process+"_Friend.root") ) 
      tree.AddFriend("Friends", friendfile)
    
    ### Replicate the eventLoop
    tree = InputTree(tree)
    outFile = r.TFile.Open("test_%s.root"%process, "RECREATE")
    outTree = FriendOutput(file_, tree, outFile)
    btagpath = os.environ['CMSSW_BASE'] + "/src/CMGTools/TTHAnalysis/data/WZRun3/BTV"

    module_test =  btag_weighterRun3(
        json = btagpath + "/2022EE/" + "btagging.json",
        eff  = btagpath + "/2022EE/" + "btagEff_DeepJet_TT.root",
        json_ptrel = btagpath + "/2022EE/" + "btagging_v0.json",
        algo = 'deepJet',
        wp = "T",
        branchJet = "Jet30", 
        labelJet = "_Mini",
        jecvars   = [] ,
        lepenvars = [],
        splitCorrelations = True, ## TEMPORAL
        useCombnuisances = True, ## TEMPORAL
        year = "2022PostEE",
        SFmeasReg = "comb",
        verbosity = 1
    )
    module_test.beginJob()
    (nall, npass, timeLoop) = eventLoop([module_test], file_, outFile, tree, outTree, maxEvents = nentries)
    print(('Processed %d preselected entries from %s (%s entries). Finally selected %d entries' % (nall, __file__.split("/")[-1].replace(".py", ""), nentries, npass)))
    outTree.write()
    file_.Close()
    outFile.Close()
    print("Test done")
    module_test.endJob()
