import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from CMGTools.TTHAnalysis.tools.nanoAOD.friendVariableProducerTools import declareOutput, writeOutput
from copy import copy, deepcopy
import math
from CMGTools.TTHAnalysis.tools.nanoAOD.wzsm_modules import btag_wps

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

class bTagEffCount(Module):
    """ Module to compute btagging efficiencies in WZ Run3 """
    def __init__(self, tagger = "btagDeepFlavB", year = "2022EE", verbosity = 0): #Default is DeepCSV for 2016
        self.tagger = tagger
        self.WPs   = btag_wps[year][tagger]
        self.flavors = {
            0 : 'L',
            1 : 'C', 
            2 : 'B'
        }
        self.verbosity = verbosity
        self.listBranches()
        return 
    
    def listBranches(self):
        self.branches = []
        #Now create a passing and failing collection for each wp and flavor
        for wp in self.WPs:
            for fl in self.flavors:
                    self.branches.append(("nJetPassWP%sFL%s"%(wp,self.flavors[fl]),"I"))
                    self.branches.append(("nJetFailWP%sFL%s"%(wp,self.flavors[fl]),"I"))
                    for var in ["pt_nom","eta"]:
                        self.branches.append(("JetFailWP%sFL%s_%s"%(wp,self.flavors[fl], var) ,"F", 20, "nJetFailWP%sFL%s"%(wp,self.flavors[fl])))
                        self.branches.append(("JetPassWP%sFL%s_%s"%(wp,self.flavors[fl], var) ,"F", 20, "nJetPassWP%sFL%s"%(wp,self.flavors[fl])))
        return self.branches
    
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        declareOutput(self, wrappedOutputTree, self.branches)
        return
    
    def analyze(self,event):
        ret = self.reset()
        if self.verbosity > 0:
            color_msg("   ---- Analyzing event %d"%(event.event), "green")

        # Dirty jets
        jets       = [j for j in Collection(event,"Jet","nJet")]
        cleanindex = getattr(event, "iJSel_Mini")
        cleanindex = filter(lambda x: x <= len(jets), cleanindex)

        # Clean jets
        cleanjets = [jets[i] for i in cleanindex]

        if self.verbosity > 0:
            color_msg("  >> Clean jets: ", "blue")
            print("    + ", [i for i in cleanindex])

        for j in cleanjets:
            flav = getattr(j, "hadronFlavour")
            btag = getattr(j, self.tagger)
            
            # Classify jet at gen level
            if flav == 5   : fl = 2
            elif flav == 4 : fl = 1
            else           : fl = 0

            if self.verbosity > 0:
                if fl == 2: origin="B"
                elif fl == 1: origin="C"
                elif fl == 0: origin="Light"
                
                color_msg("    + Classifying a jet of flavor: %d (from %s)"%(fl, origin))
            
            for wp in self.WPs:
                passes = "Pass" if btag >= self.WPs[wp] else "Fail"
                
                if self.verbosity > 0:
                    message="      * Jet %s: %3.2f ---> Passes wp %s (%3.2f)? %s"%(self.tagger, btag, wp, self.WPs[wp],  "True" if passes == "Pass" else "False")
                    color = "green" if passes == "Pass" else "red"
                        
                    color_msg(message, color)

                ret["nJet%sWP%sFL%s"%(passes, wp, self.flavors[fl])] += 1
                for var in ["pt_nom","eta"]:
                    ret["Jet%sWP%sFL%s_%s"%(passes, wp, self.flavors[fl], var)].append(getattr(j, var))
        writeOutput(self, ret)
        return True 

    def reset(self):
        ret = {}
        for l in self.listBranches():
            if len(l) <= 2: ret[l[0]] = 0
            else: ret[l[0]] = []
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


    mainpath = "/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v2/mc/2022EE/"
    process = "TTto2L2Nu_part9"
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
    
    module_test =  bTagEffCount(verbosity = 1)
    module_test.beginJob()
    (nall, npass, timeLoop) = eventLoop([module_test], file_, outFile, tree, outTree, maxEvents = nentries)
    print(('Processed %d preselected entries from %s (%s entries). Finally selected %d entries' % (nall, __file__.split("/")[-1].replace(".py", ""), nentries, npass)))
    outTree.write()
    file_.Close()
    outFile.Close()
    print("Test done")
    module_test.endJob()
      
