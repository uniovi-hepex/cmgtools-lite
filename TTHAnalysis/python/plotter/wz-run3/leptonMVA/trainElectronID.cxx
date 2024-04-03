/* 
Script to launch TMVA training for lepton MVA used in Run2. Adapted to
be used in Run3 as well.

author: carlos.vico.villalba@cern.ch
*/

// Import libraries
#include <iostream>
#include <fstream>
#include <assert.h>
using namespace std;


// Main macro implementation
void trainElectronID(TString name, TString inputFile, int nFiles) {
  std::ifstream samples_file;


  // 1. Read input file and load samples to do the training
  TChain *dSig1 = new TChain("Events");
  TChain *dBg1  = new TChain("Events");

  samples_file.open( inputFile );
  if ( samples_file.is_open() ){
    std::string filename;
    for (int iFile = 0; iFile < nFiles; iFile++) {
      std::getline(samples_file, filename);
      dSig1 -> AddFile( (TString) filename);
      dBg1 -> AddFile( (TString) filename);
    }
  }
  std::cout << " >> Number of files " << nFiles << std::endl;
  std::cout << " >> Statistics: " << dSig1->GetEntries() << std::endl;

  // 2. Prepare outputs
  TString mkdir = "mkdir -p " + name;
  gSystem -> Exec(mkdir);
  TFile *fOut = new TFile(name + "/" + name + ".root", "RECREATE");
 
  // Now prepare training
  TString factory_conf = "!V:!Color:Transformations=I";

  TMVA::Factory    *factory    = new TMVA::Factory(name, fOut, factory_conf.Data());
  TMVA::DataLoader *dataloader = new TMVA::DataLoader("dataset");


  // This will be used to cut on the lepton properties for the training
  // 3. Configure the training

  //  -- 3.1: Input variables
  dataloader->AddVariable("Electron_pt",'D');
  dataloader->AddVariable("Electron_eta",'D');
  dataloader->AddVariable("Electron_pfRelIso03_all",'D'); 
  dataloader->AddVariable("Electron_miniPFRelIso_chg",'D'); 
  dataloader->AddVariable("Electron_miniRelIsoNeutral := Electron_miniPFRelIso_all - Electron_miniPFRelIso_chg", 'D');
  dataloader->AddVariable("Electron_jetNDauCharged",'D'); 
  dataloader->AddVariable("Electron_jetPtRelv2", 'D');

  // Test out the performance for different taggers
  if (name.Contains("df")){
    std::cout << "    - Using DF b tagger" << std::endl;
    dataloader->AddVariable("Electron_jetBTagDeepFlavB := Electron_jetIdx > -1 ? Jet_btagDeepFlavB[Electron_jetIdx] : 0", 'D');
  } else if (name.Contains("pnet")) {
    std::cout << "    - Using ParticleNet b tagger" << std::endl;
    dataloader->AddVariable("Electron_jetBTagPNET := Electron_jetIdx > -1 ? Jet_btagPNetB[Electron_jetIdx] : 0", 'D');
  } else if (name.Contains("robust")) {
    std::cout << "    - Using Robust PT b tagger" << std::endl;
    dataloader->AddVariable("Electron_jetbtagRobustParTAK4B := Electron_jetIdx > -1 ? Jet_btagRobustParTAK4B[Electron_jetIdx] : 0", 'D');
  } 
  dataloader->AddVariable("Electron_jetPtRatio := min(1 / (1 + Electron_jetRelIso), 1.5)", 'D'); 
  dataloader->AddVariable("Electron_sip3d", 'D'); 
  dataloader->AddVariable("Electron_log_dxy := log(abs(Electron_dxy))",'D'); 
  dataloader->AddVariable("Electron_log_dz  := log(abs(Electron_dz))",'D'); 
  dataloader->AddVariable("Electron_mvaIso", 'D');


  // -- 3.2: preselection
  TCut lepton = "1";
  lepton += "Electron_miniPFRelIso_all < 0.4 && Electron_sip3d < 8";
  lepton += "Electron_lostHits <= 1"; 
  lepton += "abs(Electron_dxy) < 0.05 && abs(Electron_dz) < 0.1"; 

  if (name.Contains("tth")){
    std::cout << "    - Using TTH-like preselection" << std::endl;
    lepton += "abs(Electron_eta) < 2.5 && Electron_pt > 5 ";
  } else if (name.Contains("ttw")){
    std::cout << "    - Using TTW-like preselection" << std::endl;
    lepton += "Electron_pt > 10 && abs(Electron_eta) < 2.5";
  }


  // 4. Prepare TMVA BDT and run it
  double wSig = 1.0, wBkg = 1.0;
  dataloader->AddSignalTree(dSig1, wSig);
  dataloader->AddBackgroundTree(dBg1, wBkg);

  // Apply preselection and divide the sample in signal and background
  dataloader->PrepareTrainingAndTestTree(lepton+" Electron_genPartFlav == 1 || Electron_genPartFlav == 15", lepton+" Electron_genPartFlav != 1 && Electron_genPartFlav != 15", "");
  
  TString BDTGopt  = "!H:!V:NTrees=500:BoostType=Grad:Shrinkage=0.10:!UseBaggedGrad:nCuts=2000:UseNvars=9:MaxDepth=8";

  BDTGopt += ":CreateMVAPdfs"; // Create Rarity distribution
  factory->BookMethod(dataloader, TMVA::Types::kBDT, "BDTG", BDTGopt);
  factory->TrainAllMethods();
  factory->TestAllMethods();
  factory->EvaluateAllMethods();

  fOut->Close();  

}

