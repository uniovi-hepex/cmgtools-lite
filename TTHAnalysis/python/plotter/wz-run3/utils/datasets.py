import os, re, sys
from copy import deepcopy

# Add some other functions useful for debugging
sys.path.append( os.path.join( os.environ["HOME"], "WorkSpace/wz-run3/CMSSW_12_4_12/src/CMGTools/TTHAnalysis/python/plotter/wz-run3/"))
from cfgs.samplepaths import samplepaths as paths
from functions import color_msg


class dataset(object):
    """ Objects from this class inherit different useful metadata for a given dataset """
    def __init__(self, info):        
        # dataset metadata
        self.exists = True
        self.dbsname = info["dbs"]
        return
    
    def raise_not_exist(self):
        color_msg(" Dataset {} does not exist in {}".format(self.datasetname, self.raw_nano ), "red")
        return
        
    def raise_no_files(self):
        color_msg(" Dataset {} has no rootfiles in {}".format(self.datasetname, self.raw_nano ), "red")
        return
    
    def get_pure_nanoaod(self, raw_nano):
        """ 
        This function finds a match to a local directory and provides the raw nanoAOD files
        in a list. 
        """
        
        # Ideally there will be just one matched folder
        # Now get the full path where the raw nanoAOD files are stored
        nanofiles = []
        for root, dirs, files in os.walk( raw_nano ):      
            # -- First find the folders with rootfiles only
            are_there_rfiles = any([".root" in f for f in files])
            if not are_there_rfiles: continue
            nanofiles.append(root)

        if len(nanofiles) == 0:
            self.exists = False
            return None, raw_nano
        
        return nanofiles, raw_nano


class dataset_data(dataset):
    def __init__(self, info):
        super().__init__(info)
        self.isData = True 
        self.datasetname = self.dbsname.split("/")[1]
        self.era = re.match(".*(Run2....).*", self.dbsname).groups()[0]
        self.processname = "{}_{}".format(self.datasetname, self.era) # Thanks to Run3 dataset naming!
        self.regex = self.era
       
        if self.era in ["Run2022E", "Run2022F", "Run2022G"]:
            self.year = "2022EE"
        elif self.era in ["Run2022C", "Run2022D"]:
            self.year = "2022"
        return
    
    def get_pure_nanoaod(self, year):
        """ Get the nanoAOD files for a given year """
        raw_nano = os.path.join(paths["nanoaod"]["data"], year, self.datasetname)
        folder = [f for f in os.listdir(raw_nano) if self.era in f]
        if folder != []:      
            raw_nano = os.path.join(raw_nano, folder[0])
            return super().get_pure_nanoaod(raw_nano)
        else:
            return [], raw_nano

class dataset_mc(dataset):
    def __init__(self, info, color):
        super().__init__(info)
        self.datasetname = self.dbsname.replace("/", "")
        self.processname = self.datasetname.split("_Tune")[0].replace("-","_") # Thanks to Run3 dataset naming!
        self.regex = self.dbsname.replace("/", "")
        self.xsec = info["xsec"]
        self.fC = color
        return
    
    def get_pure_nanoaod(self, year):
        raw_nano = os.path.join(paths["nanoaod"]["mc"], year, self.datasetname)
        return super().get_pure_nanoaod(raw_nano)

class dataset_fr(dataset):
    def __init__(self, info, color, cut = ""):
        super().__init__(info)
        self.datasetname = self.dbsname.replace("/", "")
        self.processname = self.datasetname.split("_Tune")[0].replace("-","_") # Thanks to Run3 dataset naming!
        self.regex = self.dbsname.replace("/", "")
        self.xsec = info["xsec"]
        self.fC = color
        self.cut = cut

        return
    
    def get_pure_nanoaod(self, year):
        raw_nano = os.path.join(paths["nanoaod_FR"]["mc"], year, self.datasetname)
        return super().get_pure_nanoaod(raw_nano)

class dataset_fr_data(dataset):
    def __init__(self, info, cut = ""):
        super().__init__(info)
        self.isData = True 
        self.datasetname = self.dbsname.split("/")[1]
        self.era = re.match(".*(Run2....).*", self.dbsname).groups()[0]
        self.processname = "{}_{}".format(self.datasetname, self.era) # Thanks to Run3 dataset naming!
        self.regex = self.era
       
        if self.era in ["Run2022E", "Run2022F", "Run2022G"]:
            self.year = "2022EE"
        elif self.era in ["Run2022C", "Run2022D"]:
            self.year = "2022"
        return
    
    def get_pure_nanoaod(self, year):
        """ Get the nanoAOD files for a given year """
        raw_nano = os.path.join(paths["nanoaod_FR"]["data"], year, self.datasetname)
        folder = [f for f in os.listdir(raw_nano) if self.era in f]
        if folder != []:      
            raw_nano = os.path.join(raw_nano, folder[0])
            return super().get_pure_nanoaod(raw_nano)
        else:
            return [], raw_nano
        
class mca(object):
    """ Class that stores datasets """
    def __init__(self, name, groups):
        self.name = name
        self.datasets = { g : [] for g in groups }
        return
    
    def add_dataset(self, dataset, group):
        if group not in list(self.datasets.keys()):
            color_msg(" >> Group %s not available for mca %s"%(group, self.name))
            sys.exit(1)
        self.datasets[group].append(dataset)
        return
    
    def get_datasets(self):
        return self.datasets
