# -- Utilities

# ---- Working points for the MVA

el_mva_wp = 0.90
mu_mva_wp = 0.64

import math
def deltaR(eta1, phi1, eta2, phi2):
    dEta = abs(eta1-eta2)
    dPhi = deltaPhi(phi1, phi2)
    return math.sqrt(dEta*dEta + dPhi*dPhi)

def deltaPhi(phi1, phi2):
    res = phi1 - phi2
    while res >     math.pi: res -= 2*math.pi
    while res <= -math.pi: res += 2*math.pi
    return res

def conept(lep):
    """ Function to compute cone pT for fake estimation """
    isMu = abs(lep.pdgId) == 13
    isEl = abs(lep.pdgId) == 11

    if not (isEl  or isMu): return lep.pt

    passesTight_mu = (isMu and lep.mvaTTH_run3 > mu_mva_wp)
    passesTight_el = (isEl and lep.mvaTTH_run3 > el_mva_wp)

    if passesTight_mu or passesTight_el:
        # This passes tight criteria, so just use reco pT
        return lep.pt 
    else:
        # It is a FO lepton, so return 0.9 times the pT of the closest jet
        return 0.90 * lep.pt * (1 + lep.jetRelIso)

def closest_b(lep, jetlist):
    dR = 200000
    jetbTag = -1.
    for j in jetlist: 
        testR = deltaR(lep.eta, lep.phi, j.eta, j.phi)
        if testR < dR:
            dR = testR
            jetbTag = j.btagDeepFlavB
    return jetbTag

# ==== Looose definitions ==== #
def _loose_muon(lep):
    """ Muon loose ID criteria    """
    # Common selections
    #if         lep.pt < 10: return False # changed wrt Run2 to match preselection cuts
    if         conept(lep) < 10: return False # changed wrt Run2 to match preselection cuts
    if not (abs(lep.eta)<2.4): return False
    if not (lep.sip3d<8): return False
    if not (abs(lep.dxy)<0.05): return False
    if not (abs(lep.dz)<0.1): return False
    if not (lep.miniPFRelIso_all < 0.4): return False
    if not (lep.mediumId): return False
    if not (lep.isGlobal or lep.isTracker): return False
    if not (lep.isPFcand): return False
    return True

def _loose_electron(lep):
    """ Electron loose ID criteria """
    #if         lep.pt < 10: return False # changed wrt Run2 to match preselection cuts
    if         conept(lep) < 10: return False # changed wrt Run2 to match preselection cuts
    if not (abs(lep.eta)<2.5): return False
    if not (lep.sip3d<8): return False
    if not (abs(lep.dxy)<0.05): return False
    if not (abs(lep.dz)<0.1): return False
    if not (lep.miniPFRelIso_all < 0.4): return False
    #if not (lep.cutBased >= 2): return False
    if not (lep.lostHits < 2): return False
    return True

# ==== Fakeable definitions ==== #
def _fO_muon(lep, btagWPM, btagWPL, jetlist):
    """ 
        Fakeable muon ID criteria
        -------------------------
    Fakeable muons need to pass minimum selection criteria, and then they are
    required to either:
     1. Pass the tight MVA working point
     2. Not pass the tight MVA working point, but satisfy certain ISO requirements.
    """
    
    # ---- Common selection criteria ---- #
    # + At least loose ID    
    if not _loose_muon(lep): return False
    
    # + Kinematic cuts must be applied using cone corrected pT
    ptcone = conept(lep)
    if ptcone < 15: return False # Cut on ptcone for FO

    # + Get the WP of the nearest jet in the \eta-\phi plane
    jetbTag = closest_b(lep, jetlist)

    
    
    # + Check MVA score
    passTight = (lep.mvaTTH_run3 > mu_mva_wp)
    if passTight:
        # This is a possible fake muon that passes tight criteria
        # Ask for tight requirements.
        #if (jetbTag > btagWPM): return False
        return True
    else:
        # This is a possible fake lepton that does not pass tight criteria.
        # Ask for a bit of iso.
        ptmin = 20
        ptmax = 45
        ptcone_hat = max(0, ptcone - ptmin)
        den = ptmax - ptmin # This is always 25 GeV    
        # + Interpolated WP of the b jet
        x = min(ptcone_hat/den, 1.0)    
        interpBFlav = (1-x)*btagWPM + x*btagWPL
    
        # + Interpolated WP of the b jet
        if (jetbTag > interpBFlav): return False

        # + Jet relative isolation (the less the more isolated)
        if (lep.jetRelIso > 0.5): return False 
        
    return True

def _fO_electron(lep, btagWPM, jetlist):
    """ Fakeable electron ID criteria """
    # ---- Common selection criteria ---- #
    # + At least loose ID     
    if not _loose_electron(lep): return False
    
    # + Kinematic cuts must be applied using cone corrected pT
    ptcone = conept(lep)
    if ptcone < 15: return False # Cut on ptcone for FO
    
    # ID criteria
    if (lep.hoe >= 0.10): return False
    if (lep.eInvMinusPInv <= (-0.04)): return False
    if (lep.sieie >= (0.011+0.019*( abs(lep.eta) > 1.479 ))): return False
    if (lep.lostHits != 0): return False
    if not(lep.convVeto): return False

    # -- Better not to use MVAs at the beginning of Run3
    #if not (lep.cutBased == 2 or lep.cutBased == 4): return False
    #if not ((lep.mvaNoIso_WPL and lep.cutBased == 4) or lep.mvaNoIso_WP80): return False
    
    # + Get the closest b tag in the \eta-\phi plane
    jetbTag = closest_b(lep, jetlist)
    if (jetbTag > btagWPM): return False
    
    # + Check MVA score
    passTight = (lep.mvaTTH_run3 > el_mva_wp) 
    if passTight:
        # No additional requirements considered as of now (october 2023)
        # Possible Fake lepton that also passes Tight criteria
        return True 
    else:
        # Possible fake lepton that does not pass tight criteria. We ask
        # for a little bit of ISO to pass it for true.
        if (lep.jetRelIso > 0.7): return False
            
    return True

# ==== Tight definitions ==== #
def _tight_electron(lep, btagWPM, jetlist):
    """ Tight electron criteria """
    if not _fO_electron(lep, btagWPM, jetlist): return False
    
    # Tight electrons must pass mva requirements
    passTight = (lep.mvaTTH_run3 > el_mva_wp)
    if not passTight: return False

    jetbTag = closest_b(lep, jetlist)
    if (jetbTag > btagWPM): return False
    return True

def _tight_muon(lep, btagWPM, btagWPL,jetlist):
    """ Tight muon criteria """
    if not _fO_muon(lep,btagWPM,btagWPL,jetlist): return False
    
    # Tight muons must pass mva requirements
    passTight = (lep.mvaTTH_run3 > mu_mva_wp)
    if not passTight: return False 
    if not (lep.mediumId): return False

    jetbTag = closest_b(lep, jetlist)
    if (jetbTag > btagWPM): return False
    return True

# ==== Helper functions ==== #
def _loose_lepton(lep, btagWPM, btagWPL):
    """ Function called by the CMGTools modules """
    return _loose_muon(lep) if abs(lep.pdgId) == 13 else _loose_electron(lep)

def _fO_lepton(lep, btagWPM, btagWPL, jetlist):
    """ Function called from the CMGTools modules """
    return _fO_muon(lep, btagWPM, btagWPL, jetlist) if abs(lep.pdgId) == 13 else _fO_electron(lep, btagWPM, jetlist)

def _tight_lepton(lep, btagWPM, btagWPL, jetlist):
    """ Function called by the CMGTools modules """
    return _tight_muon(lep, btagWPM, btagWPL, jetlist) if abs(lep.pdgId) == 13 else _tight_electron(lep, btagWPM, jetlist)






