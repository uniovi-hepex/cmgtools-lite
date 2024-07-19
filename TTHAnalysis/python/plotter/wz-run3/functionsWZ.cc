#include "TMath.h"
#include <assert.h>
#include <iostream>
#include "TH2F.h"
#include "TH1F.h"
#include "TFile.h"
#include "TSystem.h"
#include "TLorentzVector.h"
#include "TGraphAsymmErrors.h"

int nJB(int nJ, float nBJ) {
    int bin = 0;
    
    // Push SRs to make room for the new bins
    if (nJ==1) bin =  1+nBJ;
    if (nJ==2) bin =  3+nBJ;
    if (nJ==3) bin =  6+nBJ;
    if (nJ>=4) bin = 10+nBJ;
    
    return bin;
}

int classify_4leptons(int total_pdgId){
  if (total_pdgId == 44){return 0;}
  if (total_pdgId == 48){return 1;}
  if (total_pdgId == 52){return 2;}
  return -1;
}

Float_t WZdeltaPhi(Float_t phi1, Float_t phi2)
{
  Float_t res(phi1 - phi2);
  while(res >   M_PI) res -= Float_t(2*M_PI);
  while(res <= -M_PI) res += Float_t(2*M_PI);
  return res;
}

Float_t baseDeltaR(Float_t eta1, Float_t phi1, Float_t eta2, Float_t phi2)
{
  Float_t res;
  Float_t dEta(std::abs(eta1-eta2));
  Float_t dPhi(WZdeltaPhi(phi1, phi2));
  res= std::sqrt(dEta*dEta + dPhi*dPhi);
  return res;
}

Bool_t allTight(Bool_t isT1, Bool_t isT2){
  return isT1 && isT2;
}


Bool_t allTight(Bool_t isT1, Bool_t isT2, Bool_t isT3){
  return isT1 && isT2 && isT3;
}

Bool_t allTight(Bool_t isT1, Bool_t isT2, Bool_t isT3, Bool_t isT4){
  return isT1 && isT2 && isT3 && isT4;
}

Bool_t neutralCharge(int ch0, int ch1, int ch2, int ch3){
  int chsign0 = ch0/abs(ch0);
  int chsign1 = ch1/abs(ch1);
  int chsign2 = ch2/abs(ch2);
  int chsign3 = ch3/abs(ch3);
  int total_charge = chsign0 + chsign1 + chsign2 + chsign3;
  Bool_t isNeutral = (total_charge == 0);
  return isNeutral;
}

Bool_t lepMVACut(Float_t lep1mva, Float_t lep2mva, Float_t lep3mva, Int_t pdg1, Int_t pdg2, Int_t pdg3, Float_t elecut, Float_t mucut, Bool_t tightW){
  Bool_t pass1 = false;
  Bool_t pass2 = false;
  Bool_t pass3 = false;
  if (abs(pdg1) == 11 && lep1mva >= elecut) pass1 = true;
  if (abs(pdg1) == 13 && lep1mva >= mucut)  pass1 = true;
  if (abs(pdg2) == 11 && lep2mva >= elecut) pass2 = true;
  if (abs(pdg2) == 13 && lep2mva >= mucut)  pass2 = true;
  if (abs(pdg3) == 11 && lep3mva >= elecut) pass3 = true;
  if (abs(pdg3) == 13 && lep3mva >= mucut)  pass3 = true;
  return pass1 && pass2 && pass3 && tightW;
}

Int_t DiFakeRateBin(float pt1, float eta1, float pt2, float eta2, int pdgcode, int tightcode, int ptbin, int etabin)
{
 // First lepton is the one "in range", second lepton is "off range"
 // Returns flavorcode*4 + tightcode
 // Flavor code:
 // -1 == No lepton in range
 //   0 == ee
 //   1 == em
 //   2 == me
 //   3 == mm
 // Tight code:
 //   0 = Tight (in) Tight (out)
 //   1 = Loose (in) Tight (out)
 //   2 = Tight (in) Loose (out)
 //   3 = Loose (in) Loose (out)
  float ptmin; float ptmax; float etamax; float etamin;
 if (ptbin == 0){
   ptmax = 40;
   ptmin = 20;
 } 
 if (etabin == 0){
   etamax = 2.5;
   etamin = -2.5;
 }
 if (pt1 <= ptmax &&  pt1 >= ptmin && eta1 <= etamax && eta1 >= etamin && !( pt2 > ptmax ||  pt2 < ptmin || eta2 > etamax || eta2 < etamin )){
    // First one passes, second doesn't
    return pdgcode*4+tightcode;
 }
 if (pt2 <= ptmax &&  pt2 >= ptmin && eta2 <= etamax && eta2 >= etamin && !( pt1 > ptmax ||  pt1 < ptmin || eta1 > etamax || eta1 < etamin )){
    // Second one passes, first doesn't
    int newpdgcode;
    int newtightcode;
    if (pdgcode == 1) newpdgcode = 2;
    if (pdgcode == 2) newpdgcode = 1;
    if (tightcode == 1) newtightcode = 2;
    if (tightcode == 2) newtightcode = 1;
    return newpdgcode*4+newtightcode;
 }
 // If here, no candidate lepton
 return -1;   
}

//                balance = self.bestOSPair.l1.p4()
//                balance += self.bestOSPair.l2.p4()
//                self.ret["deltaR_WZ"] = deltaR(balance.Eta(), balance.Phi(), self.lepSelFO[i].p4().Eta(), self.lepSelFO[i].p4().Phi())
//                balance -= self.lepSelFO[i].p4()
//                metmom = ROOT.TLorentzVector()
//                metmom.SetPtEtaPhiM(self.met[0],0,self.metphi[0],0)
//                balance -= metmom
//                # Later do it with standalone function like makeMassMET
//                self.ret["wzBalance_pt"] = balance.Pt()
//                balance = self.bestOSPair.l1.p4(self.bestOSPair.l1.conePt)
//                balance += self.bestOSPair.l2.p4(self.bestOSPair.l2.conePt)
//                balance -= self.lepSelFO[i].p4(self.lepSelFO[i].conePt)
//                balance -= metmom
//                self.ret["wzBalance_conePt"] = balance.Pt()
//


// TBD: implement the same but with conePt
Float_t WZbalance(Float_t zpt, Float_t zeta, Float_t zphi, Float_t zm, Float_t wpt, Float_t weta, Float_t wphi, Float_t wm)
{
  TLorentzVector z; z.SetPtEtaPhiM(zpt, zeta, zphi, zm);
  TLorentzVector w; w.SetPtEtaPhiM(wpt, weta, wphi, wm);
  TLorentzVector balance = z + w;
  return balance.Pt();
}

Float_t WZdeltaR(Float_t zeta, Float_t zphi, Float_t weta, Float_t wphi)
{
  ///// save time //TLorentzVector  w; w.SetPtEtaPhiM(wpt ,  weta,  wphi,  wm);
  //
  //Float_t res(baseDeltaR(z.Eta(), z.Phi(), weta, wphi));
  Float_t res(baseDeltaR(zeta, zphi, weta, wphi));
  //std::cout << baseDeltaR(z.Eta(), z.Phi(), weta, wphi) << std::endl;
  // save time //return deltaR(z.Eta(), z.Phi(), w.Eta(), w.Phi());
  return res;
}

Int_t getWZRegion(Float_t met_pt, Float_t mll_3l, Float_t m3L, Int_t nBJetMedium30, Int_t nLepSel, Int_t LepSel4_isTight, Float_t LepSel4_pt){
  //Region index in the WZ analysis: SR->0; CRDY->1; CRTT->2; CRZZ->3; CRconv->4
  if (met_pt > 30    && nBJetMedium30 == 0 && abs(91.1876-mll_3l)<15  &&  nLepSel<4  && m3L > 100)                        return 1;
  else if (met_pt <= 30    && nBJetMedium30 == 0 && abs(91.1876-mll_3l)<15  &&  nLepSel<4  && m3L > 100)                  return 0;
  else if (met_pt > 30    && nBJetMedium30 > 0  && abs(91.1876-mll_3l)>5   &&  nLepSel<4  && m3L > 100)                   return 2;
  else if (met_pt > 30    && nBJetMedium30 == 0 && abs(91.1876-mll_3l)<15  &&  nLepSel==4 && m3L > 100  && LepSel4_isTight && LepSel4_pt > 10)     return 3;
  else if (met_pt <= 30   && nBJetMedium30 == 0 && abs(91.1876-mll_3l)>15  && m3L <= 100  &&  nLepSel<4)     return 4;
  else return -1;
}


/*Int_t getWWWRegion(Float_t met_pt, Float_t mllSFAS, Float_t mllSFOS, Int_t nOSSF, Float_t dPhi3lMet){
  //Region index in the WZ analysis: SR->0; CRDY->1; CRTT->2; CRZZ->3; CRconv->4
  if (met_pt > 30    && nBJetMedium30 == 0 && abs(91.1876-mll_3l)<15  &&  nLepSel<4  && m3L > 100)                        return 0;
  else if (met_pt <= 30    && nBJetMedium30 == 0 && abs(91.1876-mll_3l)<15  &&  nLepSel<4  && m3L > 100)                  return 1;
  else if (met_pt > 30    && nBJetMedium30 > 0  && abs(91.1876-mll_3l)>5   &&  nLepSel<4  && m3L > 100)                   return 2;
  else if (met_pt > 30    && nBJetMedium30 == 0 && abs(91.1876-mll_3l)<15  &&  nLepSel==4 && m3L > 100  && LepSel4_isTight && LepSel4_pt > 10)     return 3;
  else if (met_pt <= 30   && nBJetMedium30 == 0 && abs(91.1876-mll_3l)>15  && m3L <= 100  &&  nLepSel<4)     return 4;
  else return -1;
}*/




Float_t WZ_weight_W16(Float_t c, Int_t mode)
{
    Float_t fLSM = 0.481; Float_t fRSM = 0.272; Float_t fOSM = 0.247;
    Float_t den = 3./8. *( (1 -c)*(1-c)*fLSM + (1+c)*(1+c)*fRSM + 2*(1-c*c)*fOSM);
    if (mode ==  0) return 3./4.*(1-c*c)*fOSM/den;
    if (mode == -1) return 3./8.*(1-c)*(1-c)*fLSM/den;
    if (mode ==  1) return 3./8.*(1+c)*(1+c)*fRSM/den;
}

Float_t WZ_weight_Wp16(Float_t c, Int_t mode)
{
    Float_t fLSM = 0.538; Float_t fRSM = 0.233; Float_t fOSM = 0.229;
    Float_t den = 3./8. *( (1 -c)*(1-c)*fLSM + (1+c)*(1+c)*fRSM + 2*(1-c*c)*fOSM);
    if (mode ==  0) return 3./4.*(1-c*c)*fOSM/den;
    if (mode == -1) return 3./8.*(1-c)*(1-c)*fLSM/den;
    if (mode ==  1) return 3./8.*(1+c)*(1+c)*fRSM/den;
}


Float_t WZ_weight_Wm16(Float_t c, Int_t mode)
{
    Float_t fLSM = 0.389; Float_t fRSM = 0.333; Float_t fOSM = 0.278;
    Float_t den = 3./8. *( (1 -c)*(1-c)*fLSM + (1+c)*(1+c)*fRSM + 2*(1-c*c)*fOSM);
    if (mode ==  0) return 3./4.*(1-c*c)*fOSM/den;
    if (mode == -1) return 3./8.*(1-c)*(1-c)*fLSM/den;
    if (mode ==  1) return 3./8.*(1+c)*(1+c)*fRSM/den;
}


Float_t WZ_weight_Z16(Float_t c, Int_t mode)
{
    Float_t fLSM = 0.313; Float_t fRSM = 0.429; Float_t fOSM = 0.258;
    Float_t alpha = 0.213;
    Float_t den = 3./8. *( (1 -2*c*alpha + c*c)*fLSM + (1 +2*c*alpha + c*c)*fRSM + 2*(1-c*c)*fOSM);
    if (mode ==  0) return 3./4.*(1-c*c)*fOSM/den;
    if (mode == -1) return 3./8.*(1 -2*c*alpha + c*c)*fLSM/den;
    if (mode ==  1) return 3./8.*(1 +2*c*alpha + c*c)*fRSM/den;
}

Float_t WZ_weight_Zm16(Float_t c, Int_t mode)
{
    Float_t fLSM = 0.291; Float_t fRSM = 0.470; Float_t fOSM = 0.239;
    Float_t alpha = 0.213;
    Float_t den = 3./8. *( (1 -2*c*alpha + c*c)*fLSM + (1 +2*c*alpha + c*c)*fRSM + 2*(1-c*c)*fOSM);
    if (mode ==  0) return 3./4.*(1-c*c)*fOSM/den;
    if (mode == -1) return 3./8.*(1 -2*c*alpha + c*c)*fLSM/den;
    if (mode ==  1) return 3./8.*(1 +2*c*alpha + c*c)*fRSM/den;
}

Float_t WZ_weight_Zp16(Float_t c, Int_t mode)
{
    Float_t fLSM = 0.325; Float_t fRSM = 0.403; Float_t fOSM = 0.271;
    Float_t alpha = 0.213;
    Float_t den = 3./8. *( (1 -2*c*alpha + c*c)*fLSM + (1 +2*c*alpha + c*c)*fRSM + 2*(1-c*c)*fOSM);
    if (mode ==  0) return 3./4.*(1-c*c)*fOSM/den;
    if (mode == -1) return 3./8.*(1 -2*c*alpha + c*c)*fLSM/den;
    if (mode ==  1) return 3./8.*(1 +2*c*alpha + c*c)*fRSM/den;
}


/*Float_t WZ_weight_Z(Float_t c, Int_t mode)
{
    Float_t fLSM = 0.314; Float_t fRSM = 0.424; Float_t fOSM = 0.262;
    Float_t alpha = 0.213;
    Float_t den = 3./8. *( (1 -2*c*alpha + c*c)*fLSM + (1 +2*c*alpha + c*c)*fRSM + 2*(1-c*c)*fOSM);
    if (mode ==  0) return 3./4.*(1-c*c)*fOSM/den;
    if (mode == -1) return 3./8.*(1 -2*c*alpha + c*c)*fLSM/den;
    if (mode ==  1) return 3./8.*(1 +2*c*alpha + c*c)*fRSM/den;
}

Float_t WZ_weight_ZP(Float_t c, Int_t mode)
{
    Float_t fLSM = 0.335; Float_t fRSM = 0.389; Float_t fOSM = 0.275;
    Float_t alpha = 0.213;
    Float_t den = 3./8. *( (1 -2*c*alpha + c*c)*fLSM + (1 +2*c*alpha + c*c)*fRSM + 2*(1-c*c)*fOSM);
    if (mode ==  0) return 3./4.*(1-c*c)*fOSM/den;
    if (mode == -1) return 3./8.*(1 -2*c*alpha + c*c)*fLSM/den;
    if (mode ==  1) return 3./8.*(1 +2*c*alpha + c*c)*fRSM/den;
}


Float_t WZ_weight_ZM(Float_t c, Int_t mode)
{
    Float_t fLSM = 0.278; Float_t fRSM = 0.481; Float_t fOSM = 0.242;
    Float_t alpha = 0.213;
    Float_t den = 3./8. *( (1 -2*c*alpha + c*c)*fLSM + (1 +2*c*alpha + c*c)*fRSM + 2*(1-c*c)*fOSM);
    if (mode ==  0) return 3./4.*(1-c*c)*fOSM/den;
    if (mode == -1) return 3./8.*(1 -2*c*alpha + c*c)*fLSM/den;
    if (mode ==  1) return 3./8.*(1 +2*c*alpha + c*c)*fRSM/den;
}*/


float unrealnessW(Float_t ptl, Float_t etal, Float_t phil, Float_t ptnu, Float_t phinu){
   Float_t muVal = (80.385)*(80.385)/2. + ptl*ptnu*TMath::Cos(phil-phinu);
   Float_t disc  = (muVal*muVal*ptl*ptl*TMath::SinH(etal)*TMath::SinH(etal)/(ptl*ptl*ptl*ptl) - ((ptl*ptl*TMath::CosH(etal)*TMath::CosH(etal))*ptnu*ptnu - muVal*muVal)/ptl*ptl);        
   return disc;
}

float ISRUp(int nJet){
if (nJet <= 0) return 1.;
if (nJet == 1) return 0.98;
if (nJet == 2) return 1.02;
if (nJet == 3) return 1.06;
if (nJet == 4) return 1.08;
if (nJet == 5) return 1.10;
if (nJet == 6) return 1.12;
if (nJet >= 7) return 1.17;
}

float ISRDn(int nJet){
if (nJet <= 0) return 1.;
if (nJet == 1) return 1.02;
if (nJet == 2) return 0.98;
if (nJet == 3) return 0.95;
if (nJet == 4) return 0.93;
if (nJet == 5) return 0.91;
if (nJet == 6) return 0.88;
if (nJet >= 7) return 0.83;
}

float weight_mWZ(float mWZ){
 if (mWZ <= 200) return 1.03113;
 if (mWZ <= 300) return 0.994016;
 if (mWZ <= 400) return 1.00339;
 if (mWZ <= 500) return 0.999467;
 if (mWZ <= 1000) return 0.96045;
 if (mWZ <= 1500) return 0.822343;
 //if (mWZ <= 3000) return 0.740922;
 else return 1.;
}

float wz_TightBtag_clasifier(float nJet25,float nBJetTight25){
  if ((nJet25 == 0)*(nBJetTight25 == 0)) return 1;
  if ((nJet25 == 1)*(nBJetTight25 == 0)) return 2;
  if ((nJet25>2)*(nBJetTight25 == 0))    return 3;
  if ((nJet25 == 1)*(nBJetTight25 == 1)) return 4;
  if ((nJet25>2)*(nBJetTight25 == 1))    return 5;
  if ((nJet25>=2)*(nBJetTight25 >= 2))    return 6;
  else return -1;
}

float wz_MediumBtag_clasifier(float nJet25,float nBJetMedium25){
  if ((nJet25 == 0)*(nBJetMedium25 == 0)) return 1;
  if ((nJet25 == 1)*(nBJetMedium25 == 0)) return 2;
  if ((nJet25>2)*(nBJetMedium25 == 0))    return 3;
  if ((nJet25 == 1)*(nBJetMedium25 == 1)) return 4;
  if ((nJet25>2)*(nBJetMedium25 == 1))    return 5;
  if ((nJet25>2)*(nBJetMedium25 >= 2))    return 6;
  else return -1;
}

float wz_LooseBtag_clasifier(float nJet25,float nBJetLoose25){
  if ((nJet25 == 0)*(nBJetLoose25 == 0)) return 1;
  if ((nJet25 == 1)*(nBJetLoose25 == 0)) return 2;
  if ((nJet25>2)*(nBJetLoose25 == 0))    return 3;
  if ((nJet25 == 1)*(nBJetLoose25 == 1)) return 4;
  if ((nJet25>2)*(nBJetLoose25 == 1))    return 5;
  if ((nJet25>2)*(nBJetLoose25 >= 2))    return 6;
  else return -1;
}

float wz_tauClasifier(float lep1_pdgid, float lep2_pdgid, float lep3_pdgid){
  float atLeastOneTau = 1;
  if (lep1_pdgid == 15 || lep2_pdgid == 15 || lep3_pdgid == 15) {
    atLeastOneTau = 2;
  }
  return atLeastOneTau;
}

float smoothBFlav(float jetpt, float ptmin, float ptmax) {

    float wploose = 0.0614;
    float wpmedium = 0.3196;
    
    float x = std::min(std::max(0.f, jetpt - ptmin)/(ptmax-ptmin), 1.f); 
    return x*wploose + (1-x)*wpmedium;
}

float crzz_clasifier(int l1_pdgid, int l2_pdgid, int l3_pdgid, int l4_pdgid, float l1_eta, float l2_eta, float l3_eta, float l4_eta) {

    // Find out how many leptons fall in barrel and how many in endcap
    int channel = (abs(l1_pdgid) + abs(l2_pdgid) + abs(l3_pdgid) + abs(l4_pdgid) - 44)/4; 


    int nbarrel = 0;
    bool l1barrel = abs(l1_eta) < (abs(l1_pdgid) == 11 ? 1.445 : 1.2); 
    bool l2barrel = abs(l2_eta) < (abs(l2_pdgid) == 11 ? 1.445 : 1.2); 
    bool l3barrel = abs(l3_eta) < (abs(l3_pdgid) == 11 ? 1.445 : 1.2); 
    bool l4barrel = abs(l4_eta) < (abs(l4_pdgid) == 11 ? 1.445 : 1.2); 
    
    if (l1barrel) { nbarrel++; }
    if (l2barrel) { nbarrel++; }
    if (l3barrel) { nbarrel++; }
    if (l4barrel) { nbarrel++; }

    if (channel == 0 && nbarrel == 4) { return 0 ;}  // eeee, 4 leptons in barrel
    if (channel == 1 && nbarrel == 4) { return 1 ;}  // eemm, 4 leptons in barrel
    if (channel == 2 && nbarrel == 4) { return 2 ;}  // mmmm, 4 leptons in barrel

    if (channel == 0 && nbarrel == 3) { return 3 ;}  // eeee, 3 leptons in barrel
    if (channel == 1 && nbarrel == 3) { return 4 ;}  // eemm, 3 leptons in barrel
    if (channel == 2 && nbarrel == 3) { return 5 ;}  // mmmm, 3 leptons in barrel

    if (channel == 0 && nbarrel == 2) { return 6 ;}  // eeee, 2 leptons in barrel
    if (channel == 1 && nbarrel == 2) { return 7 ;}  // eemm, 2 leptons in barrel 
    if (channel == 2 && nbarrel == 2) { return 8 ;}  // mmmm, 2 leptons in barrel 

    if (channel == 0 && nbarrel == 1) { return 9 ;}  // eeee, 1 leptons in barrel 
    if (channel == 1 && nbarrel == 1) { return 10 ;} // eemm, 1 leptons in barrel 
    if (channel == 2 && nbarrel == 1) { return 11 ;} // mmmm, 1 leptons in barrel 

    if (channel == 0 && nbarrel == 0) { return 12 ;} // eeee, 0 leptons in endcap
    if (channel == 1 && nbarrel == 0) { return 13 ;} // eemm, 0 leptons in endcap
    if (channel == 2 && nbarrel == 0) { return 14 ;} // mmmm, 0 leptons in endcap
}


float dy_bias_2022EE(int lep0_pdgid, int lep1_pdgid, int lep2_pdgid, int lep3_pdgid){
  // lep4_pdgid can be 0 if there are only 3 selected leptons
  float unc = 1.0;

  // Add extra unc per electron
  if (lep0_pdgid == 11) { unc = unc + 0.03; }
  if (lep1_pdgid == 11) { unc = unc + 0.03; }
  if (lep2_pdgid == 11) { unc = unc + 0.03; }
  if (lep3_pdgid == 11) { unc = unc + 0.03; }
 
  return unc; 
}

float trig_eff_unc(int lep0_pdgid, int lep1_pdgid, int lep2_pdgid, int source, int year){
  // lep4_pdgid can be 0 if there are only 3 selected leptons
  // source is 0 for statistical uncertainty, 1 for systematic bias
  // Year is 0  for 2022PreEE, and 1 for 2022PostEE
  float unc = 1.0;

  int sum = lep0_pdgid + lep1_pdgid + lep2_pdgid;

  /* Just decorrelating
  // 2022 PreEE statistical uncertaintes
  if (sum == 33 && year == 0 && source == 0) { unc = 1.02; }
  if (sum == 35 && year == 0 && source == 0) { unc = 1.02; }
  if (sum == 37 && year == 0 && source == 0) { unc = 1.02; }
  if (sum == 39 && year == 0 && source == 0) { unc = 1.02; }

  // 2022 PostEE statistical uncertaintes
  if (sum == 33 && year == 1 && source == 0) { unc = 1.005; }
  if (sum == 35 && year == 1 && source == 0) { unc = 1.005; }
  if (sum == 37 && year == 1 && source == 0) { unc = 1.005; }
  if (sum == 39 && year == 1 && source == 0) { unc = 1.005; }

  // 2022 PreEE systematic uncertaintes
  if (sum == 33 && year == 0 && source == 1) { unc = 1.005; }
  if (sum == 35 && year == 0 && source == 1) { unc = 1.005; }
  if (sum == 37 && year == 0 && source == 1) { unc = 1.005; }
  if (sum == 39 && year == 0 && source == 1) { unc = 1.005; }

  // 2022 PostEE systematic uncertaintes
  if (sum == 33 && year == 1 && source == 1) { unc = 1.01; }
  if (sum == 35 && year == 1 && source == 1) { unc = 1.01; }
  if (sum == 37 && year == 1 && source == 1) { unc = 1.01; }
  if (sum == 39 && year == 1 && source == 1) { unc = 1.01; }
  */

//  /* With independent measurements
  // Add extra unc per electron
  // 2022 PreEE statistical uncertaintyes
  if (sum == 33 && year == 0 && source == 0) { unc = 1.07; }
  if (sum == 35 && year == 0 && source == 0) { unc = 1.05; }
  if (sum == 37 && year == 0 && source == 0) { unc = 1.05; }
  if (sum == 39 && year == 0 && source == 0) { unc = 1.10; }

  // 2022 PostEE statistical uncertaintyes
  if (sum == 33 && year == 1 && source == 0) { unc = 1.02; }
  if (sum == 35 && year == 1 && source == 0) { unc = 1.02; }
  if (sum == 37 && year == 1 && source == 0) { unc = 1.02; }
  if (sum == 39 && year == 1 && source == 0) { unc = 1.01; }

  // No need for PreEE systematics since everything closes well.
  // 2022 PostEE systematic uncertaintyes
  if (sum == 33 && year == 1 && source == 1) { unc = 1.02; }
  if (sum == 35 && year == 1 && source == 1) { unc = 1.02; }
  if (sum == 37 && year == 1 && source == 1) { unc = 1.07; }
  if (sum == 39 && year == 1 && source == 1) { unc = 1.02; }
//  */ 
  return unc; 
}

void functionsWZ() {}
