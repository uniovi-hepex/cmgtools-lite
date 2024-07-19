""" Module to compute Jet Energy Corrections with CorrectionLib:
---------------------------------------------------------------------------------------------------
Example module provided by JETMET group: 
  https://github.com/cms-jet/JECDatabase/blob/master/scripts/JERC2JSON/minimalDemo.py

The code here has been adapted from:
  https://github.com/uniovi-hepex/nanoAOD-tools/blob/postproc_py3/python/postprocessing/modules/jme/jetmetUncertainties.py

Reason: deprecation of nanoAODtools.
"""

# Import libraries
import correctionlib._core as core
from copy import deepcopy
import ROOT
import os
from sys import argv
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel   import Collection
from CMGTools.TTHAnalysis.tools.nanoAOD.friendVariableProducerTools import declareOutput, writeOutput
from math import hypot, pi, sqrt, cos, sin, atan2


"""
---------------------------------------------------------------
Functions used during the JER computation 
---------------------------------------------------------------
"""

def deltaPhi(phi1, phi2):
    # Catch if being called with two objects
    if type(phi1) != float and type(phi1) != int:
        phi1 = phi1.phi
    if type(phi2) != float and type(phi2) != int:
        phi2 = phi2.phi
    # Otherwise
    dphi = (phi1 - phi2)
    while dphi > pi:
        dphi -= 2 * pi
    while dphi < -pi:
        dphi += 2 * pi
    return dphi

def deltaR(eta1, phi1, eta2=None, phi2=None):
    # catch if called with objects
    if eta2 == None:
        return deltaR(eta1.eta, eta1.phi, phi1.eta, phi1.phi)
    # otherwise
    return hypot(eta1 - eta2, deltaPhi(phi1, phi2))

def closest(obj, collection, presel=lambda x, y: True):
        ret = None
        drMin = 999
        for x in collection:
            if not presel(obj, x):
                continue
            dr = deltaR(obj, x)
            if dr < drMin:
                ret = x
                drMin = dr
        return (ret, drMin)

def matchObjectCollection(objs, collection, dRmax=0.4, presel=lambda x, y: True):
    pairs = {}
    if len(objs) == 0:
        return pairs
    if len(collection) == 0:
        return dict(list(zip(objs, [None] * len(objs))))
    for obj in objs:
        (bm, dR) = closest(obj,
                        [mobj for mobj in collection if presel(obj, mobj)])
        if dR < dRmax:
            pairs[obj] = bm
        else:
            pairs[obj] = None
    return pairs

""" 
---------------------------------------------------------------
Class implementation
---------------------------------------------------------------
"""
class JetEnergyCorrector( Module ):
    def __init__(self, year = "2022", jec = "Winter22Run3", jer = "Winter22Run3", jecveto = "Winter22Run3", isMC = True, era = "CD",
                 algo = "AK4PFPuppi", metbranchname = "PuppiMET", rhoBranchName = "Rho_fixedGridRhoFastjetAll",
                 hjetvetomap = "jetvetomap",
                 unc = "Total", saveMETUncs = ["T1", "T1Smear"], 
                 splitJers = False, applyVetoMaps = True):
        """ Constructor """
        # Save in attributes
        self.year = year
        self.jetvetopmap = hjetvetomap
        self.jec = jec
        self.jer = jer
        self.jecveto = jecveto
        self.isMC = isMC
        self.era = era
        self.runOn = "MC" if self.isMC else "DATA"
        self.algo = algo
        self.unc = unc        
        self.metbranchname = metbranchname
        self.rhoBranchName = rhoBranchName
        self.saveMETUncs = saveMETUncs
        self.splitJers = splitJers
        self.applyVetoMaps = applyVetoMaps

        # This function is used to evaluate 
        self.evaluate = lambda corrector, inputs : corrector.evaluate(*inputs)

        # Dictionary with the JECs and JERs
        self.jecs_jsons = {
            "Summer22EE_22Sep2023" : "jet_jerc_2022PostEE_JEC.json",
            "Summer22EEPrompt22" : "jet_jerc_2022PostEE_JR.json",
            "Summer22_22Sep2023" : "jet_jerc_2022_JEC.json",
            "JR_Winter22Run3" : "jet_jerc_2022_JR.json",
        }
        self.eraCorrection = { # This is how data corrections are grouped in the json
            "CD" : ["CD"],
            "EFG" : ["E", "F", "G"],
        }

        # Check if we need a different JSON for JER
        self.differentJERjson = False
        if self.jer != self.jec:
            self.differentJERjson = True

        # Create the evaluators need to compute the SFs
        self.jsonpath = os.path.join( os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/data/WZRun3/JME/{}/".format(year))
        self.create_correctors()
        
        
        # This stuff is need to compute splitted JERs
        self.splitJERIDs = list(range(6)) # From NanoAODTools

        # Threshold for unclustered energy        
        self.unclEnThreshold = 15.
        
        self.listBranches()
        
        # Store this function to generate random values for JER
        self.rnd = ROOT.TRandom3(12345)

        return
    
    def setSeed(self, event):
        """Set seed deterministically."""
        # (cf. https://github.com/cms-sw/cmssw/blob/master/PhysicsTools/PatUtils/interface/SmearedJetProducerT.h)
        runnum = int(event.run) << 20
        luminum = int(event.luminosityBlock) << 10
        evtnum = event.event
        jet0eta = int(event.Jet_eta[0] / 0.01 if event.nJet > 0 else 0)
        seed = 1 + runnum + evtnum + luminum + jet0eta
        self.rnd.SetSeed(seed)
        return
    
    def analyze(self, event):
        """ Method to apply JEC scale factors """

        # Set seed for Smearing calculation
        if self.isMC:
            self.setSeed(event)
            
        # Collect objects
        self.collect_objects(event)
       
        # Veto jets
        if self.applyVetoMaps:
            self.veto_jets(event)

        # Get a new return dictionary
        ret = self.clear() 
    
        # Create containers to keep track of everything
        self.create_containers()
        
        # Now loop over jets
        ret = self.loop_jets(ret, event)

        writeOutput(self, ret)
        
        return True
    
    def create_correctors(self):
        """
        -----------------------------------------------------------------------------
        This function divides all the methods to evaluate SF and uncertainties inside 
        the json into two groups:
            + jes_corrs : contains the L1FastJet, L2Relative, L2L3Residual, L3Absolute,
                          as well as the L1L2L3Res corrections (all grouped together).
            + jer_corrs: contains the jet energy corrections
            + uncs  : uncertainty sources for the JECs
            + vetomaps: to veto regions of detector that were not used to compute JECs.
        -----------------------------------------------------------------------------
        """
        jsonName = self.jecs_jsons[self.jec]
        print(" >> This is %s for year %s"%( "MC" if self.isMC else "Data", self.year))
        self.jerc_corrs = core.CorrectionSet.from_file(os.path.join(self.jsonpath, jsonName))

        if self.differentJERjson:
            jsonName = self.jecs_jsons[self.jer]
            self.jerc_corrs_jer = core.CorrectionSet.from_file(os.path.join(self.jsonpath, jsonName))

        self.jes_corrs = {}
        self.jer_corrs = {}
        self.uncs      = {}

        # Get the JEC correctors
        # -- Save also the separate correctors
        corrList = ["L1FastJet", "L2Relative", "L2L3Residual"]
        if self.isMC:
            # + For MC it's easy, we just have an entry in the json with the corrections.
            mainJECname = "{}_V2_{}_{}_{}".format(self.jec, self.runOn, "L1L2L3Res", self.algo)
            print(" >> Applying %s"%mainJECname)
            for key in list(self.jerc_corrs):
                if self.runOn not in key: continue
                sourcename = key.split("_")[-2]
                corrector = self.jerc_corrs[key]
                
                # JECs
                if sourcename in corrList:
                    saveOn = self.jes_corrs
                # JERs
                elif "JR" in key:
                    saveOn = self.jer_corrs
                # JEC uncertainty sources
                else:
                    saveOn = self.uncs
                saveOn[sourcename] = corrector   
            self.jes_corrs["L1L2L3Res"] = self.jerc_corrs.compound[mainJECname]

            if self.differentJERjson:
                for key in list(self.jerc_corrs_jer):
                    if self.runOn not in key: continue
                    sourcename = key.split("_")[-2]
                    corrector = self.jerc_corrs_jer[key]
                    # JERs
                    if "JR" in key:
                        saveOn = self.jer_corrs
                        saveOn[sourcename] = corrector
        
        else:
            # For corrections in data, we need to know at anytime which era we are considering. There's an entry
            # for each era in 2022: C or D so far (for EFG we also apply era D corrections...)
            # Solution: load all corrections into memory an select which one to use on the fly when looping over jets...
            for era in self.eraCorrection[self.era]:
                mainJECname = "{}_{}_V2_{}_{}_{}".format(self.jec, "Run%s"%era, self.runOn, "L1L2L3Res", self.algo)
                print(" >> Applying %s"%mainJECname)
                for key in list(self.jerc_corrs):
                    if self.runOn not in key: continue
                    sourcename = key.split("_")[-2]
                    corrector = self.jerc_corrs[key]
                    # JECs
                    if sourcename in corrList:
                        self.jes_corrs[sourcename] = corrector

                self.jes_corrs["L1L2L3Res_era{}".format(era)] = self.jerc_corrs.compound[mainJECname]
            
            self.uncs = {}
            self.jer_corrs = {}
        
        if self.applyVetoMaps:
            # Now to the VetoMaps. So far these are only available in root format.
            # For the vetomaps we should use eras CD for preEE MC as well as E for postEE MC.
            # post: https://cms-talk.web.cern.ch/t/question-concerning-jme-recommendations-for-run3/23756/6
            # Open rootfile and load histogram
            rfilename = "{}_Run{}_v1.root".format(self.jecveto, self.era)
            print(" >> Applying %s for veto maps (era: %s)"%(rfilename, self.era))
            rfile = ROOT.TFile.Open( os.path.join(self.jsonpath, rfilename) )
            self.vmap = deepcopy(rfile.Get("jetvetomap"))
            rfile.Close()
             
        return
    
    def collect_objects(self, event):
        """ This method collects all the necessary objects: jet, met. It also matches jets to gen jets for JER corrections """
        # ------------------------------------------------------------- #
        # This is the rho from all PF Candidates, no foreground removal
        self.rho = getattr(event, self.rhoBranchName)

        # ---------------------------  Jets ---------------------------- #
        self.jets = Collection(event, "Jet")
        self.jets_vetoed = []

        # ---------------------------  Muons --------------------------- #
        self.muons = Collection(event, "Muon")

        
        # ---------------------------  Gen jets (only for MC) ---------- #
        if self.isMC:
            def resolution_matching(jet, genjet):
                """ Helper function to match to gen based on pt difference """
                corrector = self.jer_corrs["PtResolution"]
                resolution = self.evaluate(corrector, [jet.eta, jet.pt, self.rho])
                return abs(jet.pt - genjet.pt) < 3 * resolution * jet.pt
            
            self.genjets = Collection(event, "GenJet")
            self.pairs = matchObjectCollection(self.jets, self.genjets, 
                                                dRmax=0.2, 
                                                presel = resolution_matching)
            
            
        # --------------------------- MET ----------------------------- #
        self.met_pt = getattr(event, self.metbranchname + "_pt" )
        self.rawmet_pt = getattr(event, "Raw"+self.metbranchname + "_pt" )
        self.met_phi = getattr(event, self.metbranchname + "_phi" )
        self.rawmet_phi = getattr(event, "Raw"+self.metbranchname + "_phi" )
        (self.t1met_px, self.t1met_py) = (self.met_pt * cos(self.met_phi),
                                          self.met_pt * sin(self.met_phi))
        (self.met_px, self.met_py) = (self.rawmet_pt * cos(self.rawmet_phi),
                                      self.rawmet_pt * sin(self.rawmet_phi))
        (self.met_T1_px, self.met_T1_py) = (self.met_px, self.met_py)
        (self.met_T1Smear_px, self.met_T1Smear_py) = (self.met_px, self.met_py)        
        return
    
    def veto_jets(self, event):
        vetojets = []
        for ijet, jet in enumerate(self.jets): 
            jet_eta  = jet.eta
            jet_phi  = jet.phi

            # Check if this jet falls in the veto region
            etabin = max(1, min(self.vmap.GetNbinsX(), self.vmap.GetXaxis().FindBin(jet_eta)))
            phibin = max(1, min(self.vmap.GetNbinsY(), self.vmap.GetYaxis().FindBin(jet_phi)))
            vetoed = self.vmap.GetBinContent(etabin, phibin) # This can be either 100 or 0. 100 means that it should be vetoed.
            if vetoed: vetojets.append(ijet)

        # Update the list of vetoed
        self.jets_vetoed = vetojets
        return
    
    def loop_jets(self, ret, event):
        """ This is where all the corrections are made """
        
        if self.isMC:
            L1L2L3Res_corrector = self.jes_corrs["L1L2L3Res"]
        else:
            # This is vastly inefficient thanks to JME.
            datasetname = "".join(event.DatasetName_name)
            era = None
            if self.year == "2022EE" or self.year == 2022: year = 2022
            if "Run%sC"%year in datasetname: 
                era = "CD"
            elif "Run%sD"%year in datasetname: 
                era = "CD"
            elif "Run%sE"%year in datasetname: 
                era = "E"
            elif "Run%sF"%year in datasetname: 
                era = "F"
            elif "Run%sG"%year in datasetname: 
                era = "G"

            L1L2L3Res_corrector = self.jes_corrs["L1L2L3Res_era{}".format(era)]
        
        L1_corrector = self.jes_corrs["L1FastJet"]
        jets = self.jets
        for ijet, jet in enumerate(jets): 
            # ---------------------------------------------- #
            #     Apply Jet Energy Scale corrections         #
            # ---------------------------------------------- #
            
            rawFactor = jet.rawFactor
            jet_pt_raw  = jet.pt * (1. - jet.rawFactor)
            jet_pt  = jet.pt * (1 - jet.rawFactor) # Branch to be used in Analysis
            jet_mass_raw  = jet.mass * (1 - jet.rawFactor)
            jet_mass  = jet.mass * (1 - jet.rawFactor) # Branch to be used in Analysis
            jet_eta  = jet.eta
            jet_phi  = jet.phi
            jet_area = jet.area
            
            # Get the SFs for two levels of correction: complete and only L1
            L1L2L3Res_sf = self.evaluate(L1L2L3Res_corrector, [jet_area, jet_eta, jet_pt_raw, self.rho])
            L1_sf = self.evaluate(L1_corrector, [jet_area, jet_eta, jet_pt_raw, self.rho])

            # Use L1L2L3Res to compute jet_pt_nom and jet_mass_nom
            jet_pt   *= L1L2L3Res_sf
            jet_mass *= L1L2L3Res_sf

            # Save values withouth applying JER
            jet.pt = jet_pt
            jet.mass = jet_mass
            jet_pt_l1 = jet_pt_raw*L1_sf
            jet_mass_l1 = jet_pt_raw*L1_sf


            # Now consider the muon contributions. This is important for proper JES propagation
            # to MET uncertainties. This is specifically done before doing smearing.
            newjet, muon_pt = self.remove_muon(jet)
            jet.pt = newjet.Pt()
            jet.rawFactor = 0

            # Get propert jet pts for T1 met
            jet_pt_noMuL1L2L3 = jet.pt * jet_pt/jet_pt_raw
            jet_pt_noMuL1 = jet.pt * jet_pt_l1/jet_pt_raw
            
            # Set back to central values (Done in nanoAODTools)
            jet.pt = jet_pt
            jet.rawFactor = rawFactor

            # ---------------------------------------------------- #
            #      Apply Jet Energy Resolution corrections         #
            # ---------------------------------------------------- #
            jet_pt_jerNomVal, jet_pt_jerUpVal, jet_pt_jerDownVal = (1, 1, 1) # used in the case of data when no smearing is done
            if self.isMC:
                genjet = self.pairs[jet]
                jet_pt_jerNomVal, jet_pt_jerUpVal, jet_pt_jerDownVal = self.getSmearValsPt(jet, genjet, self.rho)
            
            # And correct the pt by the smear value
            # This takes into account (jet_pt+muon_pt)*correction
            jet_pt_nom   = jet_pt*jet_pt_jerNomVal
            jet_mass_nom = jet_mass*jet_pt_jerNomVal

            # Recover quantities summing up the muon_pt again.
            # This takes into account (real jet pt)_corrected + muon pt
            jet_pt_L1L2L3 = jet_pt_noMuL1L2L3 + muon_pt
            jet_pt_L1 = jet_pt_noMuL1 + muon_pt
            

            if jet_mass_nom < 0.0: # This is done in nanoAODtools
                jet_mass_nom *= -1.0 
            
            # Add correction branches to the return dictionary
            ret["Jet_pt_raw"].append(jet_pt_raw)
            ret["Jet_pt_nom"].append(jet_pt_nom)
            ret["Jet_mass_raw"].append(jet_mass_raw) 
            ret["Jet_mass_nom"].append(jet_mass_nom) 
            ret["Jet_corr_JEC"].append(jet_pt_nom/jet_pt_raw) 
            ret["Jet_corr_JER"].append(jet_pt_jerNomVal)
            # Save jets that are vetoed
            if ijet in self.jets_vetoed:
                ret["Jet_idx_veto"].append(ijet)
            else:
                ret["Jet_idx_veto"].append(-1) 
            
            # Add JER branches to the return dictionary
            if self.isMC:
                ret["Jet_pt_jerUp"].append(jet_pt_nom*jet_pt_jerUpVal/jet_pt_jerNomVal)
                ret["Jet_mass_jerUp"].append(jet_mass_nom*jet_pt_jerUpVal/jet_pt_jerNomVal)
                ret["Jet_pt_jerDown"].append(jet_pt_nom*jet_pt_jerDownVal/jet_pt_jerNomVal)
                ret["Jet_mass_jerDown"].append(jet_mass_nom*jet_pt_jerDownVal/jet_pt_jerNomVal)

            # ----------------------------------------------- #
            #      Compute JET sources of uncertainty         #
            # ----------------------------------------------- #
            # Here we will store jet JES, for each source of  #
            # uncertainty, and for a given jet. This will be  #
            # used to later correct the met.                  #
            # ----------------------------------------------- #   

            self.jet_pt_jesUp     = {}
            self.jet_pt_jesDown   = {}
            self.jet_pt_jesUpT1   = {}
            self.jet_pt_jesDownT1 = {}
            self.jet_mass_jesUp   = {}
            self.jet_mass_jesDown = {}

            # Consider the splitted jers if needed
            if self.isMC and self.splitJers:
                #thisJERID = self.getJERsplitID(jet_pt_nom, jet_eta)
                pass
            
            for jesUncertainty, jesUncCorrector in self.uncs.items(): 
                # Compute the uncertainty using the corrected pt

                delta = self.evaluate(jesUncCorrector, [jet_eta, jet_pt_nom])
                
                self.jet_pt_jesUp[jesUncertainty]   = jet_pt_nom * (1 + delta)
                self.jet_pt_jesDown[jesUncertainty]   = jet_pt_nom * (1 - delta)
                self.jet_mass_jesUp[jesUncertainty]   = jet_mass_nom * (1 + delta)
                self.jet_mass_jesDown[jesUncertainty] = jet_mass_nom * (1 - delta)
                
                # Save also in the return histogram (exactly the same information)
                ret["Jet_pt_jes{}{}".format(jesUncertainty, "Up")].append(jet_pt_nom * (1 + delta))
                ret["Jet_pt_jes{}{}".format(jesUncertainty, "Down")].append(jet_pt_nom * (1 - delta))
                ret["Jet_mass_jes{}{}".format(jesUncertainty, "Up")].append(jet_mass_nom * (1 + delta))
                ret["Jet_mass_jes{}{}".format(jesUncertainty, "Down")].append(jet_mass_nom * (1 - delta))

                # Redo the JES for T1 met using the unsmeared jet pt: used later for propagating JEC sources
                # to MET.
                delta = self.evaluate(jesUncCorrector, [jet_eta, jet_pt_L1L2L3])
                self.jet_pt_jesUpT1[jesUncertainty] = jet_pt_L1L2L3 * (1 + delta)
                self.jet_pt_jesDownT1[jesUncertainty] = jet_pt_L1L2L3 * (1 - delta)

                ret["Jet_pt_jesT1{}{}".format(jesUncertainty, "Up")].append(jet_pt_L1L2L3 * (1 + delta))
                ret["Jet_pt_jesT1{}{}".format(jesUncertainty, "Down")].append(jet_pt_L1L2L3 * (1 - delta))
 
            # ---------------------------------------------- #
            #     Propagate uncertainties to the MET         #
            # ---------------------------------------------- #
            if jet_pt_noMuL1L2L3 > self.unclEnThreshold and (jet.neEmEF + jet.chEmEF) < 0.9:
                if not (self.metbranchname == "METFixEE2017" and 
                        (2.65 < abs(jet.eta) < 3.14) and 
                        jet_pt_raw < 50):
                    jet_cosPhi = cos(jet.phi)
                    jet_sinPhi = sin(jet.phi)
                    self.met_T1_px = self.met_T1_px - (jet_pt_L1L2L3 - jet_pt_L1) * jet_cosPhi
                    self.met_T1_py = self.met_T1_py - (jet_pt_L1L2L3 - jet_pt_L1) * jet_sinPhi
                    if self.isMC:
                        self.met_T1Smear_px = self.met_T1Smear_px - (jet_pt_L1L2L3*jet_pt_jerNomVal -jet_pt_L1)*jet_cosPhi
                        self.met_T1Smear_py = self.met_T1Smear_py - (jet_pt_L1L2L3*jet_pt_jerNomVal -jet_pt_L1)*jet_sinPhi
                        if "T1" in self.saveMETUncs: # This is from nanoAODTools. Why is it inside the IF block?
                            # Save split JER sources
                            if self.splitJers:
                                pass # TBD
                            for jesUncertainty in self.uncs:
                                corr_up = self.jet_pt_jesUpT1[jesUncertainty] - jet_pt_L1
                                corr_dn = self.jet_pt_jesDownT1[jesUncertainty] - jet_pt_L1
                        
                                self.met_T1_px_jesUp[jesUncertainty]   = self.met_T1_px_jesUp[jesUncertainty] - corr_up*jet_cosPhi 
                                self.met_T1_py_jesUp[jesUncertainty]   = self.met_T1_py_jesUp[jesUncertainty] - corr_up*jet_sinPhi 
                                self.met_T1_px_jesDown[jesUncertainty] = self.met_T1_px_jesDown[jesUncertainty] - corr_dn*jet_cosPhi 
                                self.met_T1_py_jesDown[jesUncertainty] = self.met_T1_py_jesDown[jesUncertainty] - corr_dn*jet_sinPhi 
                        
                                
                        if "T1Smear" in self.saveMETUncs:
                            # Save split JER sources
                            if self.splitJers:
                                pass # TBD
                            for jesUncertainty in self.uncs:
                                # very long expression...
                                corr_up_smear = (
                                    jet_pt_L1L2L3 * jet_pt_jerNomVal - jet_pt_L1
                                    ) + ( 
                                    self.jet_pt_jesUpT1[jesUncertainty]- jet_pt_L1L2L3
                                )
                                corr_dn_smear = (
                                    jet_pt_L1L2L3 * jet_pt_jerNomVal - jet_pt_L1
                                    ) + (
                                    self.jet_pt_jesDownT1[jesUncertainty] - jet_pt_L1L2L3
                                )
                                
                                self.met_T1Smear_px_jesUp[jesUncertainty]   = self.met_T1Smear_px_jesUp[jesUncertainty] - corr_up_smear * jet_cosPhi
                                self.met_T1Smear_py_jesDown[jesUncertainty] = self.met_T1Smear_py_jesDown[jesUncertainty] - corr_dn_smear*jet_sinPhi 
                                self.met_T1Smear_px_jesUp[jesUncertainty]   = self.met_T1Smear_px_jesUp[jesUncertainty] - corr_up_smear*jet_cosPhi 
                                self.met_T1Smear_py_jesDown[jesUncertainty] = self.met_T1Smear_py_jesDown[jesUncertainty] - corr_dn_smear*jet_sinPhi
        
        # Propagate unclustered uncertainty to the MET
        if self.isMC:
            (met_T1_px_unclEnUp, met_T1_py_unclEnUp) = (self.met_T1_px, self.met_T1_py)
            (met_T1_px_unclEnDown, met_T1_py_unclEnDown) = (self.met_T1_px, self.met_T1_py)
            (met_T1Smear_px_unclEnUp, met_T1Smear_py_unclEnUp) = (self.met_T1Smear_px, self.met_T1Smear_py)
            (met_T1Smear_px_unclEnDown, met_T1Smear_py_unclEnDown) = (self.met_T1Smear_px, self.met_T1Smear_py)
            
            if self.metbranchname == 'PuppiMET':
                met_deltaPx_unclEn = getattr(event, self.metbranchname + "_ptUnclusteredUp") * cos(getattr(event, self.metbranchname + "_phiUnclusteredUp")) - \
                    getattr(event, self.metbranchname + "_pt") * cos(getattr(event, self.metbranchname + "_phi"))
                met_deltaPy_unclEn = getattr(event, self.metbranchname + "_ptUnclusteredUp") * sin(getattr(event, self.metbranchname + "_phiUnclusteredUp")) - \
                    getattr(event, self.metbranchname + "_pt") * sin(getattr(event, self.metbranchname + "_phi"))
            else:
                met_deltaPx_unclEn = getattr(
                    event, self.metbranchname + "_MetUnclustEnUpDeltaX")
                met_deltaPy_unclEn = getattr(
                    event, self.metbranchname + "_MetUnclustEnUpDeltaY")
                
            met_T1_px_unclEnUp = met_T1_px_unclEnUp + met_deltaPx_unclEn
            met_T1_py_unclEnUp = met_T1_py_unclEnUp + met_deltaPy_unclEn
            met_T1_px_unclEnDown = met_T1_px_unclEnDown - met_deltaPx_unclEn
            met_T1_py_unclEnDown = met_T1_py_unclEnDown - met_deltaPy_unclEn
            met_T1Smear_px_unclEnUp = met_T1Smear_px_unclEnUp + met_deltaPx_unclEn
            met_T1Smear_py_unclEnUp = met_T1Smear_py_unclEnUp + met_deltaPy_unclEn
            met_T1Smear_px_unclEnDown = met_T1Smear_px_unclEnDown - met_deltaPx_unclEn
            met_T1Smear_py_unclEnDown = met_T1Smear_py_unclEnDown - met_deltaPy_unclEn
            
            # For T1 met
            ret["%s_T1_pt_unclustEnUp"%self.metbranchname] = sqrt(met_T1_px_unclEnUp**2 + met_T1_py_unclEnUp**2)
            ret["%s_T1_phi_unclustEnUp"%self.metbranchname] = atan2(met_T1_py_unclEnUp, met_T1_px_unclEnUp)
            ret["%s_T1_pt_unclustEnDown"%self.metbranchname] = sqrt(met_T1_px_unclEnDown**2 + met_T1_py_unclEnDown**2)
            ret["%s_T1_phi_unclustEnDown"%self.metbranchname] = atan2(met_T1_py_unclEnDown, met_T1_px_unclEnDown)
            
            # For T1Smear met
            ret["%s_T1Smear_pt_unclustEnUp"%self.metbranchname] = sqrt(met_T1Smear_px_unclEnUp**2 + met_T1Smear_py_unclEnUp**2)
            ret["%s_T1Smear_phi_unclustEnUp"%self.metbranchname] = atan2(met_T1Smear_py_unclEnUp, met_T1Smear_px_unclEnUp)
            ret["%s_T1Smear_pt_unclustEnDown"%self.metbranchname] = sqrt(met_T1Smear_px_unclEnDown**2 + met_T1Smear_py_unclEnDown**2)
            ret["%s_T1Smear_phi_unclustEnDown"%self.metbranchname] = atan2(met_T1Smear_py_unclEnDown, met_T1Smear_px_unclEnDown)
        
        # Save MET uncertainties output dictionary
        ret["%s_T1_pt"%(self.metbranchname)] = sqrt(self.met_T1_px**2 + self.met_T1_py**2)
        ret["%s_T1_phi"%(self.metbranchname)] = atan2(self.met_T1_py, self.met_T1_px)

        if self.isMC:
            for jerID in self.splitJERIDs:
                pass
            ret["%s_T1Smear_pt"%(self.metbranchname)] = sqrt(self.met_T1Smear_px**2 + self.met_T1Smear_py**2)
            ret["%s_T1Smear_phi"%(self.metbranchname)] = atan2(self.met_T1Smear_py, self.met_T1Smear_px)
            
            if "T1" in self.saveMETUncs:
                for jerID in self.splitJERIDs:
                    pass
                for jesUncertainty in self.uncs:
                    # Compute pT and phi for up variation
                    met_px_jesup = self.met_T1_px_jesUp[jesUncertainty]
                    met_py_jesup = self.met_T1_py_jesUp[jesUncertainty]
                    met_pt_jesup = sqrt(met_px_jesup**2 + met_py_jesup**2)
                    met_phi_jesup = atan2(met_py_jesup, met_px_jesup)

                    # Compute pT and phi for down variation
                    met_px_jesdn = self.met_T1_px_jesDown[jesUncertainty]
                    met_py_jesdn = self.met_T1_py_jesDown[jesUncertainty]
                    met_pt_jesdn = sqrt(met_px_jesdn**2 + met_py_jesdn**2)
                    met_phi_jesdn = atan2(met_py_jesdn, met_px_jesdn)

                    # Now save in output dictionary
                    ret["%s_T1_pt_jes%sUp"%(self.metbranchname, jesUncertainty)]  = met_pt_jesup
                    ret["%s_T1_phi_jes%sUp"%(self.metbranchname, jesUncertainty)] = met_phi_jesup
                    ret["%s_T1_pt_jes%sDown"%(self.metbranchname, jesUncertainty)]  = met_pt_jesdn
                    ret["%s_T1_phi_jes%sDown"%(self.metbranchname, jesUncertainty)] = met_phi_jesdn

            if "T1Smear" in self.saveMETUncs:
                for jerID in self.splitJERIDs:
                    pass
                
                for jesUncertainty in self.uncs:
                    # Compute pT and phi for up variation
                    met_pxsmear_jesup = self.met_T1Smear_px_jesUp[jesUncertainty]
                    met_pysmear_jesup = self.met_T1Smear_py_jesUp[jesUncertainty]
                    met_ptsmear_jesup = sqrt(met_pxsmear_jesup**2 + met_pysmear_jesup**2)
                    met_phismear_jesup = atan2(met_pysmear_jesup, met_pxsmear_jesup)

                    # Compute pT and phi for down variation
                    met_pxsmear_jesdn = self.met_T1Smear_px_jesDown[jesUncertainty]
                    met_pysmear_jesdn = self.met_T1Smear_py_jesDown[jesUncertainty]
                    met_ptsmear_jesdn = sqrt(met_pxsmear_jesdn**2 + met_pysmear_jesdn**2)
                    met_phismear_jesdn = atan2(met_pysmear_jesdn, met_pxsmear_jesdn)

                    # Now save in output dictionary
                    ret["%s_T1Smear_pt_jes%sUp"%(self.metbranchname, jesUncertainty)]  = met_ptsmear_jesup
                    ret["%s_T1Smear_phi_jes%sUp"%(self.metbranchname, jesUncertainty)] = met_phismear_jesup
                    ret["%s_T1Smear_pt_jes%sDown"%(self.metbranchname, jesUncertainty)]  = met_ptsmear_jesdn
                    ret["%s_T1Smear_phi_jes%sDown"%(self.metbranchname, jesUncertainty)] = met_phismear_jesdn

        return ret
    
    def getJERsplitID(self, pt, eta):
        if abs(eta) < 1.93:
            return 0
        elif abs(eta) < 2.5:
            return 1
        elif abs(eta) < 3:
            if pt < 50:
                return 2
            else:
                return 3
        else:
            if pt < 50:
                return 4
            else:
                return 5
            
    def getSmearValsPt(self, jetIn, genJetIn, rho):
        """ 
            Snippet extracted from: 
            https://github.com/uniovi-hepex/nanoAOD-tools/blob/postproc_py3/python/postprocessing/modules/jme/jetSmearer.py#L101

            Smear jet pT to account for measured difference in JER between data and simulation.
            The function computes the nominal smeared jet pT simultaneously with the JER up and down shifts,
            in order to use the same random number to smear all three (for consistency reasons). """
        
        if hasattr(jetIn, "p4"):
            jet = jetIn.p4()
        else:
            jet = jetIn
        if hasattr(genJetIn, "p4"):
            genjet = genJetIn.p4()
        else:
            genjet = genJetIn

        if not (jet.Perp() > 0.):
            print(("WARNING: jet pT = %1.1f !!" % jet.Perp()))
            return (jet.Perp(), jet.Perp(), jet.Perp())
        

        # Get the scale factor
        corrector = self.jer_corrs["ScaleFactor"]
        scalefactor = self.evaluate(corrector, [jet.Eta(), jet.Pt(), "nom"])
        scalefactor_up = self.evaluate(corrector, [jet.Eta(), jet.Pt(),  "up"])
        scalefactor_dn = self.evaluate(corrector, [jet.Eta(), jet.Pt(), "down"])

        smear_vals = {}

        if genjet:
            dPt = jet.Perp() - genjet.Perp()
            smear_vals[0] = 1. + (scalefactor - 1)*dPt / jet.Perp()
            smear_vals[1] = 1. + (scalefactor_up - 1)*dPt / jet.Perp()
            smear_vals[2] = 1. + (scalefactor_dn - 1)*dPt / jet.Perp()
        else:
            resolution = self.evaluate(self.jer_corrs["PtResolution"], [jet.Eta(), jet.Pt(), rho])
            rand = self.rnd.Gaus(0, resolution)
            smear_vals[0] = 1 + rand*sqrt(max(scalefactor**2 - 1, 0))
            smear_vals[1] = 1 + rand*sqrt(max(scalefactor_up**2 - 1, 0))
            smear_vals[2] = 1 + rand*sqrt(max(scalefactor_dn**2 - 1, 0))

        for index in [0, 1, 2]:
            # check that smeared jet energy remains positive,
            # as the direction of the jet would change ("flip")
            # otherwise - and this is not what we want
            if smear_vals[index] * jet.E() < 1.e-2:
                smear_vals[index] = 1.e-2 / jet.E()
        return (smear_vals[0], smear_vals[1], smear_vals[2])
    
    def remove_muon(self, jet):
        """ Function to remove the muon contributions of a jet """
        newjet = ROOT.TLorentzVector()
        newjet.SetPtEtaPhiM(jet.pt * (1 - jet.rawFactor), jet.eta, jet.phi, jet.mass)
        muon_pt = 0
        if jet.muonIdx1 > -1:
            if self.muons[jet.muonIdx1].isGlobal:
                newjet = newjet - self.muons[jet.muonIdx1].p4()
                muon_pt += self.muons[jet.muonIdx1].pt
        if jet.muonIdx2 > -1:
            if self.muons[jet.muonIdx2].isGlobal:
                newjet = newjet - self.muons[jet.muonIdx2].p4()
                muon_pt += self.muons[jet.muonIdx2].pt
        return newjet, muon_pt
    
    
    def create_containers(self):
        """ Create some dictionaries to keep track of all the JET and MET variations properly """

        if self.splitJers:
            pass # TBD
        if 'T1' in self.saveMETUncs:
            (self.met_T1_px_jesUp, self.met_T1_py_jesUp) = ({}, {})
            (self.met_T1_px_jesDown, self.met_T1_py_jesDown) = ({}, {})
            for jesUncertainty in self.uncs:
                self.met_T1_px_jesUp[jesUncertainty] = self.met_px
                self.met_T1_py_jesUp[jesUncertainty] = self.met_py
                self.met_T1_px_jesDown[jesUncertainty] = self.met_px
                self.met_T1_py_jesDown[jesUncertainty] = self.met_py
        if 'T1Smear' in self.saveMETUncs:
            (self.met_T1Smear_px_jesUp, self.met_T1Smear_py_jesUp) = ({}, {})
            (self.met_T1Smear_px_jesDown, self.met_T1Smear_py_jesDown) = ({}, {})
            for jesUncertainty in self.uncs:
                self.met_T1Smear_px_jesUp[jesUncertainty] = self.met_px
                self.met_T1Smear_py_jesUp[jesUncertainty] = self.met_py
                self.met_T1Smear_px_jesDown[jesUncertainty] = self.met_px
                self.met_T1Smear_py_jesDown[jesUncertainty] = self.met_py
        return
    
    def listBranches(self):
        # Corrections
        branches = [
            ("Jet_pt_raw",   "F", 20, "nJet"),
            ("Jet_pt_nom",   "F", 20, "nJet"),
            ("Jet_mass_raw", "F", 20, "nJet"),
            ("Jet_mass_nom", "F", 20, "nJet"),
            ("Jet_corr_JEC", "F", 20, "nJet"),
            ("Jet_corr_JER", "F", 20, "nJet"),
            ("Jet_idx_veto", "I", 20, "nJet"),
        ]
        
        branches.append(("%s_T1_pt"%(self.metbranchname), "F"))
        branches.append(("%s_T1_phi"%(self.metbranchname), "F"))
        branches.append(("%s_T1Smear_pt"%(self.metbranchname), "F"))
        branches.append(("%s_T1Smear_phi"%(self.metbranchname), "F"))
        
        #  Save uncertainties only for MC
        if self.isMC:
            # JEC and JER Uncertainties
            for jesUncertainty in self.uncs:
                for direction in ["Up", "Down"]:
                    branches.append(("Jet_pt_jes{}{}".format(jesUncertainty, direction),  "F", 20, "nJet"))
                    branches.append(("Jet_pt_jesT1{}{}".format(jesUncertainty, direction),  "F", 20, "nJet"))
                    branches.append(("Jet_mass_jes{}{}".format(jesUncertainty, direction),  "F", 20, "nJet"))
        
            # JER uncertainties
            branches.append(("Jet_pt_jerUp", "F", 20, "nJet"))
            branches.append(("Jet_mass_jerUp", "F", 20, "nJet"))
            branches.append(("Jet_pt_jerDown", "F", 20, "nJet"))
            branches.append(("Jet_mass_jerDown", "F", 20, "nJet"))
            # Consider the splitted jers if needed
            if self.splitJers:
                for thisJERID in self.splitJERIDs:
                    branches.append(("Jet_pt_jer{}Up".format(thisJERID), "F", 20, "nJet"))
                    branches.append(("Jet_mass_jer{}Up".format(thisJERID), "F", 20, "nJet"))
                    branches.append(("Jet_pt_jer{}Down".format(thisJERID), "F", 20, "nJet"))
                    branches.append(("Jet_mass_jer{}Down".format(thisJERID), "F", 20, "nJet"))
            # Met uncertainties
            if 'T1' in self.saveMETUncs:
                if self.splitJers:
                    pass # TBD
                branches.append(("%s_T1_pt_unclustEnUp"%self.metbranchname, "F"))
                branches.append(("%s_T1_phi_unclustEnUp"%self.metbranchname, "F"))
                branches.append(("%s_T1_pt_unclustEnDown"%self.metbranchname, "F"))
                branches.append(("%s_T1_phi_unclustEnDown"%self.metbranchname, "F"))
                for jesUncertainty in self.uncs:
                    branches.append(("%s_T1_pt_jes%sUp"%(self.metbranchname, jesUncertainty), "F"))
                    branches.append(("%s_T1_phi_jes%sUp"%(self.metbranchname, jesUncertainty), "F"))
                    branches.append(("%s_T1_pt_jes%sDown"%(self.metbranchname, jesUncertainty), "F"))
                    branches.append(("%s_T1_phi_jes%sDown"%(self.metbranchname, jesUncertainty), "F"))

            if 'T1Smear' in self.saveMETUncs:
                if self.splitJers:
                    pass # TBD
                branches.append(("%s_T1Smear_pt_unclustEnUp"%self.metbranchname, "F"))
                branches.append(("%s_T1Smear_phi_unclustEnUp"%self.metbranchname, "F"))
                branches.append(("%s_T1Smear_pt_unclustEnDown"%self.metbranchname, "F"))
                branches.append(("%s_T1Smear_phi_unclustEnDown"%self.metbranchname, "F"))
                for jesUncertainty in self.uncs:
                    branches.append(("%s_T1Smear_pt_jes%sUp"%(self.metbranchname, jesUncertainty), "F"))
                    branches.append(("%s_T1Smear_phi_jes%sUp"%(self.metbranchname, jesUncertainty), "F"))
                    branches.append(("%s_T1Smear_pt_jes%sDown"%(self.metbranchname, jesUncertainty), "F"))
                    branches.append(("%s_T1Smear_phi_jes%sDown"%(self.metbranchname, jesUncertainty), "F"))

        self.branches = branches
        return
       
    
    
    def clear(self):
        """ Method called at each event. Clears return dictionary"""        
        # Corrections
        ret = {
            "Jet_pt_raw"       : [],
            "Jet_pt_nom"       : [],
            "Jet_mass_raw"     : [],
            "Jet_mass_nom"     : [],
            "Jet_corr_JEC"     : [],
            "Jet_corr_JER"     : [],
            "Jet_idx_veto" : [], # indices of the jets that should not be removed
        }
        
        if self.isMC:
            # JER uncertainties
            ret["Jet_pt_jerUp"] = []
            ret["Jet_mass_jerUp"] = []
            ret["Jet_pt_jerDown"] = []
            ret["Jet_mass_jerDown"] = []

            # Consider the splitted jers if needed
            if self.isMC and self.splitJers:
                for thisJERID in self.splitJERIDs:
                    ret["Jet_pt_jer{}Up".format(thisJERID)] = []
                    ret["Jet_mass_jer{}Up".format(thisJERID)] = []
                    ret["Jet_pt_jer{}Down".format(thisJERID)] = []
                    ret["Jet_mass_jer{}Down".format(thisJERID)] = []
        
            ## JEC Uncertainties
            for jesUncertainty in self.uncs:
                for direction in ["Up", "Down"]:
                    # For Jets
                    ret["Jet_pt_jes{}{}".format(jesUncertainty, direction)] = []
                    ret["Jet_mass_jes{}{}".format(jesUncertainty, direction)] = []
                    ret["Jet_pt_jesT1{}{}".format(jesUncertainty, direction)] = []

        return ret
    
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        declareOutput(self, wrappedOutputTree, self.branches)
        return
