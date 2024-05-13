""" General class to read ntuples for quick checks """
import ROOT as r
from copy import deepcopy
import os

class ntuple_reader:
    def __init__(self, samplename, friends, ftreename):
        self.samplename = samplename
        self.friends = friends
        self.open_tree()
        for friend in self.friends:
            self.add_friend( friend, ftreename )
        return

    def open_tree(self):
        """ Open the tree """
        if isinstance(self.samplename, list):
            self.files = []
            self.tree = r.TChain()
            self.runs = r.TChain()
            print(" >> Creating chain")
            for sample in self.samplename:
                print(f"   o Adding {sample} -- total entries {self.tree.GetEntries()}")
                self.tree.Add( sample )
                self.runs.Add( sample )
            print(f"  o Total entries: {self.tree.GetEntries()}")
           
        else:
            self.rf = r.TFile.Open( self.samplename, "READ" )
            self.tree = self.rf.Get( "Events" )
            self.runs = self.rf.Get("Runs")

    
    def add_friend(self, friend, ftreename):
        """ Add friends """
        self.tree.AddFriend(ftreename , r.TFile.Open(friend))

        #ftree = r.TFile.Open(friend)
        #tree = ftree.Get(ftreename)
        #self.tree.AddFriend(tree)

    def add_ntuple(self, ntuple):
        """ Basically adds the tree of another ntuple """
        self.tree.Add( ntuple.get_tree() )
        return

    def get_tree(self):
        return self.tree

    def _treeSum(self):
        if self.runs.GetEntries() == 0: return 0.
        r.gROOT.cd()
        if r.gROOT.FindObject("dummy") != None: r.gROOT.FindObject("dummy").Delete()
        histo = r.TH1D("dummy","dummy",1,0.0,1.0); histo.Sumw2()
        self.runs.Draw("0.5>>dummy", "genEventSumw", "goff")
        return histo.GetBinContent(1)

    def draw(self, what, binning, selection, name, normToGenSum = True):
        """ Draws a histogram of this root file and returns it """
        self.tree.Draw( f"{what} >> {name}({binning})", selection, "hist")
        # Get the histogram
        histo = r.gDirectory.Get(f"{name}")
        histo.SetDirectory(0)
        histo.Integral() # Do not remove, otherwise root might delete things
        if normToGenSum:
            gsw = self._treeSum()
            histo.Scale( 1 / gsw )    
        return deepcopy(histo)
 
    def scan(self, what, selection):
        """ Scans a tree of this root file """
        self.tree.Scan( f"{what}", selection)
 
