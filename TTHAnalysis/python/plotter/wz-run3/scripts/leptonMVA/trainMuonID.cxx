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
void trainMuonID(TString name, TString inputFile, int nFiles) {
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
  dataloader->AddVariable("Muon_LepGood_pt",'D');
  dataloader->AddVariable("Muon_LepGood_eta",'D');
  dataloader->AddVariable("Muon_LepGood_pfRelIso03_all",'D'); 
  dataloader->AddVariable("Muon_LepGood_miniRelIsoCharged",'D'); 
  dataloader->AddVariable("Muon_LepGood_miniRelIsoNeutral", 'D');
  dataloader->AddVariable("Muon_LepGood_jetNDauChargedMVASel",'D'); 
  dataloader->AddVariable("Muon_LepGood_jetPtRelv2", 'D'); 

  if (name.Contains("df")){
    std::cout << "    - Using DF b tagger" << std::endl;
    dataloader->AddVariable("Muon_LepGood_jetDF", 'D');
  } else if (name.Contains("pnet")) {
    std::cout << "    - Using ParticleNet b tagger" << std::endl;
    dataloader->AddVariable("Muon_LepGood_jetPNET", 'D');
  } else if (name.Contains("robust")) {
    std::cout << "    - Using robust particle transformer b tagger" << std::endl;
    dataloader->AddVariable("Muon_LepGood_jetRobustPT", 'D');
  }

  dataloader->AddVariable("Muon_LepGood_jetPtRatio", 'D'); 
  dataloader->AddVariable("Muon_LepGood_sip3d", 'D'); 
  dataloader->AddVariable("Muon_LepGood_dxy",'D'); 
  dataloader->AddVariable("Muon_LepGood_dz",'D'); 
  dataloader->AddVariable("Muon_LepGood_segmentComp", 'D');  

  // -- 3.2: preselection
  TCut lepton = "1";
  lepton += "Muon_miniPFRelIso_all < 0.4 && Muon_sip3d < 8 && abs(Muon_dxy) < 0.05 && abs(Muon_dz) < 0.1"; 
  if (name.Contains("tth")){
    std::cout << "    - Using TTH-like preselection" << std::endl;

    lepton += "abs(Muon_eta) < 2.4 && Muon_pt > 5";
    lepton += "Muon_looseId == 1"; 
  } else if (name.Contains("ttw")){
    std::cout << "    - Using TTW-like preselection" << std::endl;

    lepton += "Muon_pt > 10 && abs(Muon_eta) < 2.4";
    lepton += "(Muon_isGlobal == 1 || Muon_isTracker == 1)";
    lepton += "Muon_isPFcand == 1";
    lepton += "Muon_mediumId == 1";
  }

  // 4. Prepare TMVA BDT and run it
  double wSig = 1.0, wBkg = 1.0;
  dataloader->AddSignalTree(dSig1, wSig);
  dataloader->AddBackgroundTree(dBg1, wBkg);

  // Apply preselection and divide the sample in signal and background
  dataloader->PrepareTrainingAndTestTree(lepton+" Muon_genPartFlav == 1 || Muon_genPartFlav == 15", lepton+" Muon_genPartFlav != 1 && Muon_genPartFlav != 15", "");
  
  TString BDTGopt  = "!H:!V:NTrees=500:BoostType=Grad:Shrinkage=0.10:!UseBaggedGrad:nCuts=2000:UseNvars=9:MaxDepth=8";

  BDTGopt += ":CreateMVAPdfs"; // Create Rarity distribution
  factory->BookMethod(dataloader, TMVA::Types::kBDT, "BDTG", BDTGopt);
  factory->TrainAllMethods();
  factory->TestAllMethods();
  factory->EvaluateAllMethods();

  fOut->Close();  

}

