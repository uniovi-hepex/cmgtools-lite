from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from copy import deepcopy
import math
import ROOT as r
import os
import sys

# -- Define where to extrac the SFs from

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

class lepScaleFactors_wzrun3(Module):
  # ============ MAIN METHODS =============== #
  def __init__(self, year_, lepenvars = [], keepOutput = 1, summary = False, verbosity = 0):
    self.files =  {
        # ----- MVATTH 2023
        "muon"     : {
          "IDTight"  : { "file" : "MUO/{year}/Muons-mvaTTH-WP064_nanoAODv12", "hist" : "EGamma_SF2D", "unc"  : [("total", "EGamma_SF2D")]} 
        },
        
        "electron" : { 
          "IDTight"    : { "file" : "EGM/{year}/Electrons-mvaTTH-WP090_nanoAODv12", "hist" : "EGamma_SF2D", "unc"  : [("total", "EGamma_SF2D")]},
          #"IDTight"    : { "file" : "EGM/{year}/Electrons-mvaTTH-WP097_nanoAODv12", "hist" : "EGamma_SF2D", "unc"  : [("total", "EGamma_SF2D")]},
          "recoLowPt"  : { "file" : "EGM/{year}/Electrons-recoSF-lowPt",            "hist" : "EGamma_SF2D", "unc"  : [("total", "EGamma_SF2D")]},
          "recoMidPt"  : { "file" : "EGM/{year}/Electrons-recoSF-mediumPt",         "hist" : "EGamma_SF2D", "unc"  : [("total", "EGamma_SF2D")]},
          "recoHighPt" : { "file" : "EGM/{year}/Electrons-recoSF-highPt",           "hist" : "EGamma_SF2D", "unc"  : [("total", "EGamma_SF2D")]}
        }
    }
    
       
    self.lepsfpath  = os.path.join( os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/data/WZRun3/")

    self.keepOutput = keepOutput
    self.year = year_
    self.verbosity = verbosity
    
    # Containers
    self.leptonSF     = {"muon" : {}, "electron" : {} }    
    # For systematics on the lepton energy corrections
    self.systsLepEn = {}
    if len(lepenvars):
      for i, var in enumerate(lepenvars):
        self.systsLepEn[i+1]    = "%sUp"%var
        self.systsLepEn[-(i+1)] = "%sDown"%var
        
    # Now load required histograms
    self.load_histograms()
    
  
    return 
  
  def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    self.out = wrappedOutputTree    
    # -- This is the global SF
    # -- Separated in flavor
    for lep in ["muon", "electron"]:
      self.out.branch("%sSF"%lep, 'F')
      self.out.branch("%sSF_Up"%lep, 'F')
      self.out.branch("%sSF_Down"%lep, 'F')
      
      # -- Separated on type of SF 
      for source_sf, info_sf in self.files[lep].items():
        self.out.branch("%sSF_%s"%(lep, source_sf), 'F')
        self.out.branch("%sSF_%sUp"%(lep, source_sf), 'F')
        self.out.branch("%sSF_%sDown"%(lep, source_sf), 'F')
      
    return
  
  def create_outdict(self):
    
    self.outdict = {}
    # -- Separated in flavor
    for lep in ["muon", "electron"]:
      self.outdict["%sSF"%lep] = 1
      self.outdict["%sSF_Up"%lep] = 1
      self.outdict["%sSF_Down"%lep] = 1
      
      # -- Separated on type of SF 
      for source_sf, info_sf in self.files[lep].items():
        self.outdict["%sSF_%s"%(lep, source_sf)] = 1
        self.outdict["%sSF_%sUp"%(lep, source_sf)] = 1
        self.outdict["%sSF_%sDown"%(lep, source_sf)] = 1
      
    return 
  
  def analyze(self, event):
    
    self.create_outdict()
    
    year = self.year  
    # -- Get the collection of leptons and analyze the topology (i.e. how many leptons are in the event)
    leps = [l for l in Collection(event, "LepGood")]    
    nleps = len(leps)
    self.event = event
    if self.verbosity > 0:
      color_msg("   ---- Analyzing event %d"%(event.event), "green")
      color_msg("     - Number of leptons %d"%(len(leps)), "green")

    self.nmuons = 0
    self.nelectrons = 0
    
    # Iterate over the leptons
    sfs = {
      "muon" : [], 
      "electron" : []
    } 
    
    for ilep, lep in enumerate(leps):
      lep_pt  = getattr(lep, "conePt")
      lep_eta = lep.eta
      lep_pdg = abs(lep.pdgId)
      if self.verbosity > 0:
          color_msg("  >> Getting SF for lepton %d (pdgID = %d )"%(ilep, lep.pdgId), "green")
          color_msg("    + pT: %3.2f"%(lep_pt), "blue")
          color_msg("    + eta: %3.2f"%(lep_eta), "blue")
      if lep_pdg == 13: # Muon
        sfs["muon"].append(self.getLepSF(lep_pt, lep_eta, "muon"))
        self.nmuons += 1
      elif lep_pdg == 11: # Electron
        sfs["electron"].append( self.getLepSF(lep_pt, (lep_eta + lep.deltaEtaSC), "electron") )
        self.nelectrons += 1
      else: # who knows
        raise RuntimeError("[lepScaleFactors_wzRun3::analyze]: Wrong pdgId %d"%lep_pdg)
      
      if ilep > 4:
        self.computeSF( sfs )
        if self.verbosity > 0: self.printSummary()
        self.write_output() 
        return True # Stop beyond the fourth lepton
    
    self.computeSF( sfs )
    if self.verbosity > 0: self.printSummary()
    self.write_output()  
    return True
  
  def printSummary( self ):
    """ Print a summary of the scale factors """
    for sftype, value in self.outdict.items():
      color_msg("    *%s : %3.2f"%(sftype, value), "red")
    color_msg(" ----- ", "red")
    return
  
  
  def computeSF(self, sfs):
    """ Here just iterate over each leptons and compute the global event SF """
    ret = {}
    if self.verbosity > 0:
      color_msg("  >> Computing SF for this event...", "green")
    
    for flav, leps in sfs.items():
      
      if self.verbosity > 0:
        color_msg("    + %s"%flav, "blue")
      for ilep, lep in enumerate(leps):

        if self.verbosity > 0:
          color_msg("      + Index: %d"%ilep)
        
        for lepsf_source, values in lep.items():
 
          if self.verbosity > 0:
            color_msg("        o Source: %s"%lepsf_source, "yellow")
          
          sf_nom = values["nominal"]
          
          # Multiply the nominal scale factors
          self.outdict["%sSF"%(flav)] *= sf_nom
          self.outdict["%sSF_%s"%(flav, lepsf_source)] *= sf_nom
          
          if self.verbosity > 0:
            color_msg("          - Nominal: %3.4f"%sf_nom)
          for uncsource, uncinfo in values.items():
            if uncsource == "nominal":  continue
            
            # Multiply the variated scale factors
            up = uncinfo["up"]
            self.outdict["%sSF_Up"%(flav)] *= up
            self.outdict["%sSF_%sUp"%(flav, lepsf_source)] *= up
            
            dn = uncinfo["dn"]
            self.outdict["%sSF_Down"%(flav)] *= dn
            self.outdict["%sSF_%sDown"%(flav, lepsf_source)] *= dn
            
            if self.verbosity > 0:
              color_msg("          > Source of uncertainty: %s"%uncsource)
              color_msg("            > Up: %3.4f"%up)
              color_msg("            > Dn: %3.4f"%dn)
              
    return
  
  def write_output(self):
    for sfname, sf in self.outdict.items():
      self.out.fillBranch(sfname, sf)        
    return
  
  
  def getLepSF(self,  pt, eta, flav):
    ''' Function to get all the SFs for a given lepton '''    
    sfret = {}
    for source, histograms in list(self.leptonSF[flav].items()):
      
      ## Nominal histogram
      h_nom = histograms["nominal"]      
      sf = self.getFromHisto(pt, abs(eta), h_nom)

      skipThese = []        

      if flav == "electron" and (pt < 20): skipThese = ["recoMidPt", "recoHighPt"]
      if flav == "electron" and (pt > 20 and pt < 75): skipThese = ["recoLowPt", "recoHighPt"]
      if flav == "electron" and (pt > 75): skipThese = ["recoLowPt", "recoMidPt"]
      if source in skipThese:
      #    print("Skipping %s since %s pT is %3.2f"%(source, flav, pt))
          continue

      sfret[source] = {"nominal" : sf}
      ## Now compute uncertainties
      for uncsource, h_unc in histograms.items():
        if uncsource == "nominal" : continue 

        variation = self.getFromHisto( pt, abs(eta), h_unc, err=True )
        
        var_sf_up = sf + variation
        var_sf_dn = sf - variation
        
        # -- Consider Extrapolation to top-like from DY-like phase space 
        #    (CMS-AN-"2018"-210) ---> Only for muons!

        #if flav == "muon":
        #  var_sf_up += 0.005
        #  var_sf_dn += 0.005
      
          
        sfret[source][uncsource] = {"up" : var_sf_up, "dn" : var_sf_dn}
       
    return sfret
  
  def getFromHisto(self, pt, eta, histo, err = False):
        #### NOTE: this method obtains the information for a given pt and eta. 
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

        if err: return histo.GetBinError(xbin, ybin)
        else:   return histo.GetBinContent(xbin, ybin)
        

  # ============ LOADING METHODS =============== #
  def load_histograms(self):
    ''' Method to load histograms for muon and electron SFs'''
    for flav in ["muon", "electron"]:
      for type_ in self.files[flav]:
        self.leptonSF[flav][type_] = self.load_histo(self.files[flav][type_])          
    return
  
  def load_histo(self, info):
    ''' Method to load histograms '''
    fil      = os.path.join( self.lepsfpath, info["file"].format(year = self.year) + ".root" )
    histname = info["hist"]
    uncs     = info["unc"]
    ret = {}
    
    # -- Open file
    tf = r.TFile.Open( fil )
    if not tf: 
      raise RuntimeError("[lepScaleFactors_wzRun3::loadHisto] FATAL: no such file %s"%fil)
    
    histnom = tf.Get(histname)
    # -- Get the histogram
    if not histnom: 
      raise RuntimeError("[lepScaleFactors_wzRun3::loadHistoWithVars] FATAL: no such object %s in %s"%(hist,fil))
    ret["nominal"] = deepcopy(histnom)
    
    # -- Get the uncertainty histos otherwise
    for var, histname in uncs:
      tmphist = tf.Get(histname)
      ret[var] = deepcopy(tmphist)
        
    # -- Finally, close the file and return
    tf.Close()
    return ret 

  

  
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


    mainpath = "/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees/mc/2022EE/"
    process = "WZto3LNu"
#    process = "TTTo2L2Nu_part17"
    
    friends = [
      "jmeCorrections",
      "lepmva",
      "leptonJetRecleaning",
      "leptonBuilder",
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
    
    module_test =  lepScaleFactors_wzrun3( "2022EE", keepOutput = 2, summary = False, verbosity = 2)
    module_test.beginJob()
    (nall, npass, timeLoop) = eventLoop([module_test], file_, outFile, tree, outTree, maxEvents = nentries)
    print(('Processed %d preselected entries from %s (%s entries). Finally selected %d entries' % (nall, __file__.split("/")[-1].replace(".py", ""), nentries, npass)))
    outTree.write()
    file_.Close()
    outFile.Close()
    print("Test done")
    module_test.endJob()
