# -- Import libraries -- #
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from CMGTools.TTHAnalysis.tools.nanoAOD.friendVariableProducerTools import declareOutput, writeOutput
from CMGTools.TTHAnalysis.tools.nanoAOD.leptonJetRecleanerWZSM import passMllTLVeto, passTripleMllVeto

import itertools
import ROOT, copy, os
import array, math


""" These are just some stupid functions to print messages with coloring and all that. Useful for debugging. """
def color_msg(msg, color = "none"):
    """ Prints a message with ANSI coding so it can be printout with colors """
    codes = {
        "none" : "0m",
        "green" : "1;32m",
        "red" : "1;31m",
        "blue" : "1;34m",
        "yellow" : "1;35m"
    }

    print("\033[%s%s \033[0m"%(codes[color], msg))
    return

class OSpair:
  def __init__(self, l1, l2):
    self.l1 = l1
    self.l2 = l2
    self.load()
    return

  def load(self):
    self.isSF = False
    self.wTau = False

    # Check if we target Z leptons
    if self.l1.pdgId  == -self.l2.pdgId: self.isSF = True
    
    # Check if these are from tau decays
    if abs(self.l1.pdgId) == 15 or abs(self.l2.pdgId) == 15: self.wTau = True
    
    # Target cases:
    #   - 2 OSSF leptons should come from Z decay (target is Zmass)
    #   - 2 OSOF leptons may come from W (target is less than 80 due to neutrino)
    #         - 60 if there are taus
    #         - 50 if there are not taus.  
    if self.isSF: self.target = 91.1876
    elif abs(self.l1.pdgId) == 15 or abs(self.l2.pdgId) == 15: self.target = 60
    else: self.target = 50
   
    l1_p4 = self.l1.p4()
    l2_p4 = self.l2.p4()
    l1_p4.SetPtEtaPhiM(self.l1.conePt, self.l1.eta, self.l1.phi, self.l1.mass) 
    l2_p4.SetPtEtaPhiM(self.l2.conePt, self.l2.eta, self.l2.phi, self.l2.mass) 
    self.mll  = (l1_p4 + l2_p4).M()
    self.mllR = (self.l1.p4() + self.l2.p4()).M()
    self.diff = abs(self.target - self.mll)
    return

class leptonBuilderWZSM(Module):
  def __init__(self, 
               inputlabel, 
               metbranch = "MET",
               systsJEC = [],
               lepScaleSysts = [],
               verbosity = 0):
    
    ''' Initialise some variables '''
    self.mt2maker = None
    self.verbosity = verbosity
    self.inputlabel = '_' + inputlabel

    self.systsJEC = systsJEC

    self.lepScaleSysts = lepScaleSysts

    self.metbranch = metbranch
    self.isData = False
    self.listBranches()
    
    if self.verbosity > 0:
      color_msg(" >> Module %s initiated in debug mode"%(self.__class__.__name__), "green")
    return

  def listBranches(self):
    branches = [("MET_pt_central","F"),
        ("MET_phi_central","F"),
        ("MET_pt_ScaleUp", "F"),
        ("MET_pt_ScaleDown", "F"),
        ("MET_pt_SmearUp", "F"),
        ("MET_pt_SmearDown", "F"),
        ("MET_phi_ScaleUp", "F"),
        ("MET_phi_ScaleDown", "F"),
        ("MET_phi_SmearUp", "F"),
        ("MET_phi_SmearDown", "F")]

    for tag in [""] + self.lepScaleSysts:
      var = "_%s"%tag if tag != "" else tag
      branches += [
        ("iZ1" + var         , "I"),
        ("iZ2" + var         , "I"),
        ("iW"  + var         , "I"),
        ("is_3l" + var       , "I"),
        ("is_4l" + var       , "I"),
        ("is_5l" + var       , "I"),
        ("nOSSF_3l" + var    , "I"),
        ("nOSDF_3l" + var    , "I"),
        ("nOSLF_3l" + var    , "I"),
        ("nOSTF_3l" + var    , "I"),
        ("mll_3l"   + var    , "F"),
        ("m3L"      + var    , "F"),
        ("nOSSF_4l" + var    , "I"),
        ("nOSDF_4l" + var    , "I"),
        ("nOSLF_4l" + var    , "I"),
        ("nOSTF_4l" + var    , "I"),
        ("mll_4l"   + var    , "F"),
        ("m4L"      + var    , "F"),
        ("minDeltaR_3l" + var, "F"),
        ("minDeltaR_4l" + var, "F"),]
        
      branches.append(("nOS" + var  , "I"))
      branches.append(("mll" + var  , "F", 20, "nOS"))
      branches.append(("mll_i1"+ var, "I", 20, "nOS"))
      branches.append(("mll_i2"+ var, "I", 20, "nOS"))
      branches.append(("deltaR_WZ"+ var, "F"))
      branches.append(("nLepSel" + var  , "I"))
      branches.append(("nLepSel_forMemory" + var  , "I"))

      for vvar in ["pt", "eta", "phi", "mass", "conePt","genpt", "geneta", "genphi", "genmass","unc"]:
        if self.isData and ("gen" in vvar or "mc" in vvar or "Match" in vvar): continue
        branches.append(("LepSel_" + vvar+ var, "F", 20, "nLepSel_forMemory"))
        branches.append(("LepZ1_"  + vvar+ var, "F"))
        branches.append(("LepZ2_"  + vvar+ var, "F"))
        branches.append(("LepW_"   + vvar+ var, "F"))
        branches.append(("LepZ3_"   + vvar+ var, "F"))
      for vvar in ["pdgId", "isTight"]:
        if self.isData and ("gen" in vvar or "mc" in vvar or "Match" in vvar): continue
        branches.append(("LepSel_" + vvar+ var, "I", 20, "nLepSel_forMemory"))
        branches.append(("LepZ1_"  + vvar+ var, "I"))
        branches.append(("LepZ2_"  + vvar+ var, "I"))
        branches.append(("LepW_"   + vvar+ var, "I"))
        branches.append(("LepZ3_"   + vvar+ var, "I"))
      for vvar in ["pt", "conePt"]:
        branches.append(("wzBalance_" + vvar+ var, "F"))
      branches.append(("mT_3l"       + var, "F"))
      branches.append(("mT2L_3l"     + var, "F"))
      branches.append(("mT2T_3l"     + var, "F"))
      branches.append(("mT_4l"       + var, "F"))
      branches.append(("mT2L_4l"     + var, "F"))
      branches.append(("mT2T_4l"     + var, "F"))
      branches.append(("m3Lmet"      + var, "F"))
      # WARNING: I did not configure M3LmetUnc MET variations, as we will use it only as a quick comparison
      branches.append(("m3LmetUnc"   + var, "F"))
      branches.append(("m3LmetRecUp" + var, "F"))
      branches.append(("m3LmetRecDn" + var, "F"))

    for var in [""] + self.systsJEC:
        var = "_%s"%var if var != "" else var
        if var == "": continue
        branches.append(("mT_3l"       + var, "F"))
        branches.append(("mT2L_3l"     + var, "F"))
        branches.append(("mT2T_3l"     + var, "F"))
        branches.append(("mT_4l"       + var, "F"))
        branches.append(("mT2L_4l"     + var, "F"))
        branches.append(("mT2T_4l"     + var, "F"))
        branches.append(("m3Lmet"      + var, "F"))
        # WARNING: I did not configure M3LmetUnc MET variations, as we will use it only as a quick comparison
        branches.append(("m3LmetUnc"   + var, "F"))
        branches.append(("m3LmetRecUp" + var, "F"))
        branches.append(("m3LmetRecDn" + var, "F"))
    self.branches = branches
    return

  def analyze(self, event):
    ''' Called from postprocessor '''
    if self.verbosity > 0:
      color_msg("   ---- Analyzing event %d"%(event.event), "green")
    self.isData = (event.datatag != 0)

    if self.isData:
      self.systsJEC = []
      self.lepScaleSysts = []
      
    self.totalret = {}
    
    #lepVars = [-2, -1, 1, 2, 0] if not(self.isData) else [0]
    iterations = [""] + self.lepScaleSysts
    for lepVar in iterations:
      self.lepVar = lepVar if lepVar != "" else lepVar
      # -- Reset memory -- #
      self.resetMemory()    
      self.currentVar = lepVar
      # -- Collect objects -- #
      self.collectObjects(event)
      # -- Analyze objects -- #
      if self.verbosity > 0:
        color_msg("     * There are %d leptons in this event"%(len(self.lepSelFO)), "blue")
        print("     * ", [(lep, "PdgId: %3.2f, pT: %3.2f"%(lep.pdgId, lep.pt)) for lep in self.lepSelFO])
      self.analyzeTopology()
      # -- Write lepton objects -- #
      self.writeLepSel()     
      # -- Save branches -- #
      for branch in self.ret:
        self.totalret["%s%s"%(branch, "_%s"%lepVar if lepVar != "" else "")] = self.ret[branch]
    toPop = []
    for key in self.totalret:
      if "jes" in key and ("Scale" in key or "Smear" in key): toPop.append(key)
    for p in toPop: self.totalret.pop(p)
    
    self.totalret["MET_pt_central"]  = self.totalret["MET_pt"]
    self.totalret["MET_phi_central"] = self.totalret["MET_phi"]
    self.totalret.pop("MET_pt")
    self.totalret.pop("MET_phi")
    writeOutput(self, self.totalret)
    return True

  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    declareOutput(self, wrappedOutputTree, self.branches)
    return

  def writeLepSel(self):
    self.ret["nLepSel"] = len(self.lepSelFO)
    self.ret["nLepSel_forMemory"] = len(self.lepSelFO)

    for i, l in enumerate(self.lepSelFO):
      if i == 4: break # Only keep the first 4 entries
      for var in ["pt", "eta", "phi", "mass"]:
        self.ret["LepSel_" + var][i] = getattr(l, var, 0)
      for var in ["pdgId", "isTight"]:
        self.ret["LepSel_" + var][i] = int(getattr(l, var, 0))

    allpairs = []
    for os in self.OS:
      allpairs.append( (0 if os.isSF else 1, 1 if os.wTau else 0, os.diff, os) ) # Priority to SF-light-diff-target
    if allpairs:
      allpairs.sort()
      self.ret["nOS"] = len(allpairs)
      for i, os in enumerate(allpairs):
        self.ret["mll"][i] = os[3].mll
        self.ret["mll_i1"][i] = self.lepSelFO.index(os[3].l1)
        self.ret["mll_i2"][i] = self.lepSelFO.index(os[3].l2)
    return

  def analyzeTopology(self):
    if len(self.lepSelFO) >= 3: self.ret["is_3l"] = 1
    if len(self.lepSelFO) >= 4: self.ret["is_4l"] = 1
    self.getGenMatch() 
  
    if self.verbosity > 0:
      color_msg("     * Collecting OSpairs")
    self.collectOSpairs(3)
    self.makeMass(3)
    if self.verbosity > 0:
      color_msg("     * Finding best pair")
    self.findBestOSpair(3)
    self.findMtMin(3)
    self.makeMassMET(3)
    self.makeUncMassMET(3)
    return
 
  def makeUncMassMET(self, maxlep):
    return #Fix this
  
  def makeMassMET(self, maxlep):
    """ Compute invariant mass taking into account neutrino contributions. Assumming neutrino momentum in the Z plane to be 0"""
    # Using pt gives corrected pt
    if len(self.lepSelFO) < 3: return
    
    sumlep = self.lepSelFO[0].p4()
    metp4 = ROOT.TLorentzVector()
    for i in range(1, min(maxlep, len(self.lepSelFO))):
      sumlep += self.lepSelFO[i].p4()
    for var in [""] + self.systsJEC:
      var = "_%s"%var if var != "" else var
      metp4.SetPtEtaPhiM(self.met[var.replace("_","", 1)], 0, self.metphi[var.replace("_","", 1)], 0)
      sumtot = sumlep + metp4
      self.ret["m" + str(maxlep) + "Lmet" + var] = sumtot.M()
    return

  def findMtMin(self, maxlep):
    """ This method finds the minimum Mt between a lepton from W and the MET """
    used = [self.bestOSPair.l1, self.bestOSPair.l2] if self.bestOSPair else [] 
    leps = [l for l in self.lepSelFO if l not in used ]
    if len(leps) == 0:
      return
    
    if self.verbosity > 0:
      print("       + leps: ", leps) 
   
    for var in [""] + self.systsJEC:
      var = "_%s"%var if var != "" else var
      if var != "" and self.lepVar != "": continue

      
      bufferPF = []
      if not self.isData:
        bufferGEN = []

      # Iterate over the leptons that do not originate from Z
      for l in leps:
        bufferPF.append(self.mtW(l, var))
        if not self.isData:
          bufferGEN.append(self.mtW(l, var, True))

      if len(bufferPF):
        bufferPF.sort()
        self.ret["mT_" + str(maxlep) + "l" + var] = bufferPF[0]
      else:
        self.ret["mT_" + str(maxlep) + "l" + var] = -1
    return
  
  def mtW(self, lep, var, useGenMet = False):
    return self.mt(lep.conePt, self.met[var.replace("_","", 1)], lep.phi, self.metphi[var.replace("_","", 1)])


  def findBestOSpair(self, maxlep):
    """ Module to find the best OS pair from the ones available """
    self.bestOSPair = None
    allpairs = []

    if len(self.OS) == 0: return # No best OS pair if no OS pairs :)

    for os in self.OS:
      metadata = (0 if os.isSF else 1, os.diff, os)
      allpairs.append( metadata )
      
    # Make sure the first pair is the SF one (easier to tag from Z decays).
    # If there are none, then just use the first pair.
    allpairs.sort()
   
    if self.verbosity > 0: 
        print("      o There are %d pairs"%len(allpairs))
    for pair in range(len(allpairs)):
      ospair = allpairs[pair][2]
      if self.verbosity > 0:
        print("        o pair diff to target mass: %3.2f GeV (%3.2f GeV - %3.2f GeV)"%(ospair.diff, ospair.target, ospair.mll ), ", leptons: ", ospair.l1, " and ", ospair.l2)
    
    self.bestOSPair = allpairs[0][2]
    if self.verbosity > 0:
      print("       + My best pair is the one whose diff is: %3.2f"%self.bestOSPair.diff)
    
    
    self.ret["mll_" + str(maxlep) + "l"] = self.bestOSPair.mll
    
    lz1 = self.bestOSPair.l1
    lz2 = self.bestOSPair.l2

    # The following list, by construction, is never empty.
    used = [lz1, lz2] if self.bestOSPair else []
    if self.verbosity > 0:
      print("       + leps from best pair: ", used[0], used[1]) 


    # --- Fill info for the leptons coming from the Z decay (as tagged by the algorithm)
    self.ret["iZ1"] = lz1.idx
    self.ret["iZ2"] = lz2.idx
    for var in ["pt", "eta", "phi", "mass", "conePt", "genpt", "geneta", "genphi", "genmass"]:
      if self.isData and ("gen" in var or "mc" in var or "Match" in var): continue
      self.ret["LepZ1_" + var] = getattr(lz1, var, 0)
      self.ret["LepZ2_" + var] = getattr(lz2, var, 0)
    for var in ["pdgId", "isTight"]:
      if self.isData and ("gen" in var or "mc" in var or "Match" in var): continue
      self.ret["LepZ1_" + var] = int(getattr(lz1, var, 0))
      self.ret["LepZ2_" + var] = int(getattr(lz2, var, 0))

     
    # --- The remaining one (if any) is coming from the W
    lw_cands = [l for l in self.lepSelFO if l not in [lz1, lz2] ]
    if len(lw_cands) == 0:
      return
    

    # ----- If there's at least three leptons, the third hardest is the one tagged from W 
    lw = lw_cands[0] 
    self.ret["iW"] = lw.idx 
    for var in ["pt", "eta", "phi", "mass", "conePt", "genpt", "geneta", "genphi", "genmass"]:
        if self.isData and ("gen" in var or "mc" in var or "Match" in var): continue
        self.ret["LepW_" + var] = getattr(lw, var, 0)
    for var in ["pdgId", "isTight"]:
        if self.isData and ("gen" in var or "mc" in var or "Match" in var): continue
        self.ret["LepW_" + var] = int(getattr(lw, var, 0))
        self.ret["LepW_" + var] = int(getattr(lw, var, 0))

    if len(lw_cands) > 1: # For cases with 4l, useful to track which one is unused
        lz3 = lw_cands[1]
        for var in ["pt", "eta", "phi", "mass", "conePt", "genpt", "geneta", "genphi", "genmass"]:
            if self.isData and ("gen" in var or "mc" in var or "Match" in var): continue
            self.ret["LepZ3_" + var] = getattr(lz3, var, 0)
        for var in ["pdgId", "isTight"]:
            if self.isData and ("gen" in var or "mc" in var or "Match" in var): continue
            self.ret["LepZ3_" + var] = int(getattr(lz3, var, 0))
            self.ret["LepZ3_" + var] = int(getattr(lz3, var, 0))

    # Compute the difference in deltaR between the Z candidate and the W boson candidate.    
    Z_vecp4 = lz1.p4()
    Z_vecp4 += lz2.p4()
    Wnomet_vecp4 = lw.p4() 
    self.ret["deltaR_WZ"] = deltaR(Z_vecp4.Eta(), Z_vecp4.Phi(), Wnomet_vecp4.Eta(), Wnomet_vecp4.Phi())


    # Reconstruct the WZ system
    # ---- With the neutrino contribution
    WZ_vecp4 = Z_vecp4 + Wnomet_vecp4 
    metnom = ROOT.TLorentzVector()
    metnom.SetPtEtaPhiM(self.met[""], 0, self.metphi[""], 0)
    WZ_vecp4 += metnom
    self.ret["wzBalance_pt"] = WZ_vecp4.Pt()
    
    # ---- With the neutrino, using conePt
    WZ_vecp4_conePt = lz1.p4(lz1.conePt)
    WZ_vecp4_conePt += lz2.p4(lz2.conePt)
    WZ_vecp4_conePt += lw.p4(lw.conePt)
    WZ_vecp4_conePt += metnom
    self.ret["wzBalance_conePt"] = WZ_vecp4_conePt.Pt()

    # Now do the fit to the W mass, neglect lepton/neutrino masses
    phil  = getattr(lw, "phi", 0)
    etal  = getattr(lw, "eta", 0)
    ptl   = getattr(lw, "pt", 0)
    phinu = self.metphi[""]
    etanu = 0
    ptnu  = self.met[""]
    muVal = (80.385)**2/2. + ptl * ptnu * math.cos(phil-phinu)
    disc  = (muVal**2*ptl**2*math.sinh(etal)**2/ptl**4 - ((ptl**2*math.cosh(etal)**2)*ptnu**2 - muVal**2)/ptl**2)

    metUp = ROOT.TLorentzVector()
    metUp.SetPtEtaPhiM(self.met[""],0,self.metphi[""],0)
    metDn = ROOT.TLorentzVector()
    metDn.SetPtEtaPhiM(self.met[""],0,self.metphi[""],0)

    if disc < 0:
         metUp.SetPz(muVal*ptl*math.sinh(etal)/ptl**2)
         metDn.SetPz(muVal*ptl*math.sinh(etal)/ptl**2)
    else:
         metUp.SetPz(muVal*ptl*math.sinh(etal)/ptl**2 + math.sqrt(disc))
         metDn.SetPz(muVal*ptl*math.sinh(etal)/ptl**2 - math.sqrt(disc))

    sumlep = self.lepSelFO[0].p4()
    for i in range(1,min(maxlep,len(self.lepSelFO))):
      sumlep += self.lepSelFO[i].p4(self.lepSelFO[i].conePt) 
    for var in [""] + self.systsJEC:
      var = "_%s"%var if var != "" else var
      if var != "" and (self.lepVar != "" or self.isData): continue
      sumtotUp = sumlep + metUp
      sumtotDn = sumlep + metDn
      self.ret["m3LmetRecDn" + var] = sumtotDn.M()
      self.ret["m3LmetRecUp" + var] = sumtotUp.M()

    return

  def mt(self, pt1, pt2, phi1, phi2):
    return math.sqrt(2*pt1*pt2*(1-math.cos(phi1-phi2)))

  def makeMass(self, maxlep):
    if len(self.lepSelFO) < 3: return
    summed_p4 = self.lepSelFO[0].p4()
    for i in range(1, min(maxlep, len(self.lepSelFO))):
      summed_p4 += self.lepSelFO[i].p4(self.lepSelFO[i].conePt) 
    self.ret["m" + str(maxlep) + "L"] = summed_p4.M()
    return

  def collectOSpairs(self, maxlep):
    """ This function makes combination of pairs of leptons and counts how many
        types of pairs we have:
          + OSSF: Opposite sign, same flavor (ee, mm).
          + OSTF: Opposite sign, at least one of the leptons in the pair is a tau.
          + OSLF: Opossite sign, any flavor but no hadronic taus involved (em, me, ee, mm).
        This means OSSF <= OSLF
    """
    self.OS = []
    nFO = len(self.lepSelFO)
    
    # Now make pairs
    combs = itertools.combinations(self.lepSelFO, 2)

    for icomb, comb in enumerate(combs):
      if self.verbosity > 0: print("        o Checking combination %d: "%(icomb), (comb[0], comb[1]))
      l1 = comb[0]
      l2 = comb[1]
      
      if abs(l1.pdgId) == 15 and abs(l2.pdgId) == 15: # No tau tau SF pairs 
        if self.verbosity > 0: color_msg("        * Skipping pair of taus")
        continue
      
      if l1.pdgId * l2.pdgId < 0:
        self.OS.append( OSpair(l1, l2) )

    # Now count pairs
    self.ret["nOSSF_" + str(maxlep) + "l"] = self.countOSSF(maxlep)
    self.ret["nOSDF_" + str(maxlep) + "l"] = self.countOSDF(maxlep)
    self.ret["nOSTF_" + str(maxlep) + "l"] = self.countOSTF(maxlep)
    self.ret["nOSLF_" + str(maxlep) + "l"] = self.countOSLF(maxlep)
    if self.verbosity > 0: 
      print("      + Found: nOSSF = %d, nOSDF = %d, nOSTF = %d, nOSLF = %d "%(self.ret["nOSSF_" + str(maxlep) + "l"],
                                                                   self.ret["nOSDF_" + str(maxlep) + "l"],
                                                                   self.ret["nOSTF_" + str(maxlep) + "l"],
                                                                   self.ret["nOSLF_" + str(maxlep) + "l"]))
    return

  def countOSLF(self, maxlep):
    return sum(1 if not os.wTau else 0 for os in self.OS)
  def countOSSF(self, maxlep):
    return sum(1 if os.isSF else 0 for os in self.OS)
  def countOSDF(self, maxlep):
    return sum(1 if not os.isSF else 0 for os in self.OS)
  def countOSTF(self, maxlep):
    return sum(1 if os.wTau else 0 for os in self.OS)

  def getGenMatch(self):
    if not self.isData:
      for i in range(len(self.lepSelFO)):
        self.lepSelFO[i].genpt   = 0
        self.lepSelFO[i].geneta  = 0
        self.lepSelFO[i].genphi  = 0
        self.lepSelFO[i].genmass = 0

        if self.lepSelFO[i].genPartIdx < 0 or self.lepSelFO[i].genPartIdx >= len(self.genparts):
          self.lepSelFO[i].genpt   = 0
          self.lepSelFO[i].geneta  = 0
          self.lepSelFO[i].genphi  = 0
          self.lepSelFO[i].genmass = 0
        else:
          match  = self.genparts[self.lepSelFO[i].genPartIdx]
          self.lepSelFO[i].genpt   = match.pt
          self.lepSelFO[i].geneta  = match.eta
          self.lepSelFO[i].genphi  = match.phi
          self.lepSelFO[i].genmass = match.mass
    return

  def collectObjects(self, event):
    ''' Gather lepton collections into iterators '''
    self.leps     = [l for l in Collection(event, "LepGood", "nLepGood")]
    correctedLeps = self.correctTheLeptons(event, self.leps)

    # -- Collect Fakeable Objects (FO) -- # 
    nLepsFO     = getattr(event, "nLepFO" + self.inputlabel)
    chosenFO    = getattr(event, "iF" + self.inputlabel) 
    self.lepsFO = [self.leps[chosenFO[il]] for il in range(nLepsFO)]
 
    # -- Collect Tight leptons -- #
    nLepsTight  = getattr(event, "nLepTight" + self.inputlabel)
    chosenTight = getattr(event, "iT" + self.inputlabel) 
    self.lepsT  = [self.leps[chosenTight[il]] for il in range(nLepsTight)]

    for i in range(len(self.lepsT)):  self.lepsT[i].idx = i
    for i in range(len(self.lepsFO)): self.lepsFO[i].idx = i
 
    correctedLepsFO = self.correctTheLeptons(event, self.lepsFO)

    correctedLepsT  = self.correctTheLeptons(event, self.lepsT)
    

    # -- Collect Generated leptons -- #
    self.genparts = []
    if not self.isData:
      self.genparts = [p for p in Collection(event, "GenPart", "nGenPart")]

    ### FO, both flavors -- ordered by pT
    self.lepSelFO = self.lepsFO

    self.setAttributes(event, self.lepSelFO, self.isData)
    self.lepSelFO.sort(key = lambda x: x.pt, reverse = True)

    ### Tight leptons, both flavors
    self.lepsTT = [t for t in self.lepSelFO if t.isTight]
    
    self.met    = {}
    self.metphi = {}
    
    itervars = [""] + self.systsJEC
    for metvar in itervars:
      var = "_%s"%metvar if metvar != "" else ""
      metbranch = self.metbranch
      if hasattr(event, self.metbranch+"_T1_pt"): 
        metbranch = self.metbranch+"_T1"
        
      self.met[metvar]    = event.__getitem__("%s_pt%s"%(metbranch, var))
      self.metphi[metvar] = event.__getitem__("%s_phi%s"%(metbranch, var))
      

    ### Recorrect MET based on lepton corrections

    for l in self.leps:
      oldlep = ROOT.TLorentzVector() 
      newlep = ROOT.TLorentzVector()
      oldmet = ROOT.TLorentzVector()
      newmet = ROOT.TLorentzVector()
      oldlep.SetPtEtaPhiM(getattr(l, "uncorrpt"), l.eta,l.phi,l.mass)
      newlep.SetPtEtaPhiM(l.pt, l.eta, l.phi, l.mass)
      oldmet.SetPtEtaPhiM(self.met[""], 0, self.metphi[""], 0)
      newmet = oldmet + oldlep - newlep
      self.met[""]    = newmet.Pt()
      self.metphi[""] = newmet.Phi()
    self.OS = []
    self.ret["MET_pt"]  = self.met[""]
    self.ret["MET_phi"] = self.metphi[""]
    return 

  def setAttributes(self, event, lepSel, isData = False,  isGen = False):
    ''' Set properties in lepton objects '''
    for i, l in enumerate(lepSel): 
      if isGen:
        setattr(l, "motherId", l.motherId)
        setattr(l, "grandmotherId", l.grandmotherId)
      else:
        setattr(l, "isTight", (l in self.lepsT))
    return            


  def correctTheLeptons(self, event, leps):
    ''' Method to select the correct pT branch for leptons depending
        on the lepton scale we are currently processing '''

    # IMPORTANT NOTE: WE ARE NOT CURRENTLY TREATING SCALES, SO WE
    # WILL ONLY USE THE "PT"  BRANCH.
    correctedLeps = []
    for l in leps:
      setattr(l, "uncorrpt", l.correctedpt)
      l.pt = getattr(l, "correctedpt" + self.lepVar) 
      correctedLeps.append(l) 
    return correctedLeps

  def resetMemory(self):
    ''' Reset variables to a default state at each event iteration '''
    self.ret = {}

    self.ret["iZ1"]          = -1
    self.ret["iZ2"]          = -1
    self.ret["iW" ]          = -1
    self.ret["is_3l"]        = 0
    self.ret["is_4l"]        = 0
    self.ret["nOSSF_3l"]     = 0
    self.ret["nOSDF_3l"]     = 0
    self.ret["nOSLF_3l"]     = 0
    self.ret["nOSTF_3l"]     = 0
    self.ret["mll_3l"]       = 0
    self.ret["m3L"]          = 0
    self.ret["minDeltaR_3l"] = -1
    self.ret["deltaR_WZ"]    = 0

    self.ret["nOS"]          = 0
    self.ret["mll"]          = [0.]*20
    self.ret["mll_i1"]       = [-1]*20
    self.ret["mll_i2"]       = [-1]*20

    self.ret["nLepSel"] = 0
    self.ret["nLepSel_forMemory"] = 0
    for var in ["pt", "eta", "phi", "mass", "conePt", "genpt", "geneta", "genphi", "genmass"]:
      self.ret["LepSel_" + var] = [0.]*20
      self.ret["LepZ1_"  + var] = 0.
      self.ret["LepZ2_"  + var] = 0.
      self.ret["LepW_"   + var] = 0.
      self.ret["LepZ3_"   + var] = 0.
    for var in ["pdgId", "isTight"]:
      self.ret["LepSel_" + var] = [0]*20
      self.ret["LepZ1_"  + var] = 0
      self.ret["LepZ2_"  + var] = 0
      self.ret["LepW_"   + var] = 0
      self.ret["LepZ3_"   + var] = 0
    for var in ["pt", "conePt"]:
      self.ret["wzBalance_" + var] = 0

    for var in [""] + self.systsJEC:
      var = "_%s"%var if var != "" else var
      if var != "" and self.lepVar != "": continue
      self.ret["mT_3l"       + var] = 0.
      self.ret["mT2L_3l"     + var] = 0.  
      self.ret["mT2T_3l"     + var] = 0. 
      self.ret["m3Lmet"      + var] = 0. 
      self.ret["m3LmetUnc"   + var] = 0. 
      self.ret["m3LmetRecUp" + var] = 0. 
      self.ret["m3LmetRecDn" + var] = 0.
    return

def deltaPhi(phi1, phi2):
  res = phi1 - phi2
  while res >   math.pi: res -= 2*math.pi
  while res <= -math.pi: res += 2*math.pi
  return res

def deltaR(eta1, phi1, eta2, phi2):
  dEta = abs(eta1-eta2)
  dPhi = deltaPhi(phi1, phi2)
  return math.sqrt(dEta*dEta + dPhi*dPhi)

if __name__ == '__main__':
    """ Debug the module """
    from sys import argv
    from copy import deepcopy
    from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import eventLoop
    from PhysicsTools.NanoAODTools.postprocessing.framework.output import FriendOutput, FullOutput
    from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import InputTree
    
    mainpath = "/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v3/mc/2022/"
    process = "ZZto4L_part1"
#    process = "TTTo2L2Nu_part17"
    
    friends = [
      "jmeCorrections",
      "leptonJetRecleaning"
    ]
    nentries = int(argv[1])
    ### Open the main file
    file_ = ROOT.TFile( os.path.join(mainpath, process+".root") )
    tree = file_.Get("Events")
    for friend in friends:
      print(os.path.join(mainpath, friend, process+"_Friend.root"))
      friendfile = ROOT.TFile( os.path.join(mainpath, friend, process+"_Friend.root") ) 
      tree.AddFriend("Friends", friendfile)
    
    ### Replicate the eventLoop
    tree = InputTree(tree)
    outFile = ROOT.TFile.Open("test_%s.root"%process, "RECREATE")
    outTree = FriendOutput(file_, tree, outFile)
    
    module_test =  leptonBuilderWZSM("Mini", 
                        metbranch="PuppiMET",
                        systsJEC  = [],
                        lepScaleSysts = [],
                        verbosity = 2)
    module_test.beginJob()
    (nall, npass, timeLoop) = eventLoop([module_test], file_, outFile, tree, outTree, maxEvents = nentries)
    print(('Processed %d preselected entries from %s (%s entries). Finally selected %d entries' % (nall, __file__.split("/")[-1].replace(".py", ""), nentries, npass)))
    outTree.write()
    file_.Close()
    outFile.Close()
    print("Test done")
    module_test.endJob()











