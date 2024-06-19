

def inclusive(selection, flav_cut):
	""" For inclusive measurement """
	selection.append( "LepZ2_pt > 15" )
	selection.append( flav_cut )
	caption = """Trigger efficiency measurements in different data and MC. Uncertainties in the efficiency
        measurements are statistical only. \WZ events are not normalized to the cross section to properly account
        for the full statistical power of the sample."""
	return " && ".join(selection), caption

def lowpt_closeToOffline_lz1_lz2(selection, flav_cut):
	""" For inclusive measurement """
	selection.append( "LepZ1_pt >= 25 && LepZ1_pt < 35" )
	#selection.append( "LepW_pt >= 25 && LepW_pt < 35" )
	selection.append( "LepZ2_pt <= 25 && LepZ2_pt > 15" )
	selection.append( flav_cut )
	caption = """Trigger efficiency measurements in different data
        and MC samples in a \pt region close to the offline threshold of all the trigger legs ($25 < \pt(\ell_{1}) < 35 \GeV$, $25 < \pt(\ell_{1}) < 35 \GeV$, $\pt(\ell_{3}) < 25 \GeV$). Uncertainties in the efficiency measurements are statistical only. \WZ events are not normalized to the cross section to properly account for the full statistical power of the sample."""
	return " && ".join(selection), caption

def lowpt_closeToOffline_lw_lz2(selection, flav_cut):
	""" For inclusive measurement """
	#selection.append( "LepZ1_pt >= 25 && LepZ1_pt < 35" )
	selection.append( "LepW_pt >= 25 && LepW_pt < 35" )
	selection.append( "LepZ2_pt <= 25 && LepZ2_pt > 15" )
	selection.append( flav_cut )
	caption = """Trigger efficiency measurements in different data
        and MC samples in a \pt region close to the offline threshold of all the trigger legs ($25 < \pt(\ell_{1}) < 35 \GeV$, $25 < \pt(\ell_{1}) < 35 \GeV$, $\pt(\ell_{3}) < 25 \GeV$). Uncertainties in the efficiency measurements are statistical only. \WZ events are not normalized to the cross section to properly account for the full statistical power of the sample."""
	return " && ".join(selection), caption



def lowpt_closeToOffline_lz1(selection, flav_cut):
	""" For inclusive measurement """
	selection.append( "LepZ1_pt >= 25 && LepZ1_pt < 35" )
	#selection.append( "LepW_pt >= 25 && LepW_pt < 35" )
	#selection.append( "LepZ2_pt <= 25 && LepZ2_pt > 15" )
	selection.append( flav_cut )
	caption = """Trigger efficiency measurements in different data
        and MC samples in a \pt region close to the offline threshold of all the trigger legs ($25 < \pt(\ell_{1}) < 35 \GeV$, $25 < \pt(\ell_{1}) < 35 \GeV$, $\pt(\ell_{3}) < 25 \GeV$). Uncertainties in the efficiency measurements are statistical only. \WZ events are not normalized to the cross section to properly account for the full statistical power of the sample."""
	return " && ".join(selection), caption

def lowpt_closeToOffline_lw(selection, flav_cut):
	""" For inclusive measurement """
	#selection.append( "LepZ1_pt >= 25 && LepZ1_pt < 35" )
	selection.append( "LepW_pt >= 25 && LepW_pt < 35" )
	#selection.append( "LepZ2_pt <= 25 && LepZ2_pt > 15" )
	selection.append( flav_cut )
	caption = """Trigger efficiency measurements in different data
        and MC samples in a \pt region close to the offline threshold of all the trigger legs ($25 < \pt(\ell_{1}) < 35 \GeV$, $25 < \pt(\ell_{1}) < 35 \GeV$, $\pt(\ell_{3}) < 25 \GeV$). Uncertainties in the efficiency measurements are statistical only. \WZ events are not normalized to the cross section to properly account for the full statistical power of the sample."""
	return " && ".join(selection), caption

def lowpt(selection, flav_cut):
	""" For inclusive measurement """
	selection.append( "LepZ2_pt <= 25 && LepZ2_pt > 15" )
	selection.append( flav_cut )
	caption = """Trigger efficiency measurements in different data
        and MC samples in the high \pt region ($\pt(\ell_{3}) > 25 \GeV$). Uncertainties in the efficiency
        measurements are statistical only. \WZ events are not normalized to the cross section to properly account
        for the full statistical power of the sample."""
	return " && ".join(selection), caption

def highpt(selection, flav_cut):
	""" For inclusive measurement """
	selection.append( "LepZ2_pt > 25 " )
	selection.append( flav_cut )
	caption = """Trigger efficiency measurements in different data
        and MC samples in the high \pt region ($\pt(\ell_{3}) > 25 \GeV$). Uncertainties in the efficiency
        measurements are statistical only. \WZ events are not normalized to the cross section to properly account
        for the full statistical power of the sample."""
	return " && ".join(selection), caption

def barrel0(selection, flav_cut):
	""" For 0 barrel lepton measurement """
	selection.append( "LepZ2_pt > 15 " )
	selection.append( "(abs(LepSel_eta[0]) < (1.2+0.245*(abs(LepSel_pdgId[0])==11))) + (abs(LepSel_eta[1]) < (1.2+0.245*(abs(LepSel_pdgId[1])==11))) + (abs(LepSel_eta[0]) < (1.2+0.245*(abs(LepSel_pdgId[0])==11))) == 0" )
	selection.append( flav_cut )
	caption = """Trigger efficiency measurements in different data
      and MC samples in the in the region with no barrel leptons. Uncertainties in the efficiency
      measurements are statistical only. \WZ events are not normalized to the cross section to properly account
      for the full statistical power of the sample. """
	return " && ".join(selection), caption

def barrel1(selection, flav_cut):
	""" For 1 barrel lepton measurement """
	selection.append( "LepZ2_pt > 15 " )
	selection.append( "(abs(LepSel_eta[0]) < (1.2+0.245*(abs(LepSel_pdgId[0])==11))) + (abs(LepSel_eta[1]) < (1.2+0.245*(abs(LepSel_pdgId[1])==11))) + (abs(LepSel_eta[0]) < (1.2+0.245*(abs(LepSel_pdgId[0])==11))) == 1" )
	selection.append( flav_cut )
	caption = """Trigger efficiency measurements in different data
      and MC samples in the in the region with one barrel leptons. Uncertainties in the efficiency
      measurements are statistical only. \WZ events are not normalized to the cross section to properly account
      for the full statistical power of the sample. """
	return " && ".join(selection), caption

def barrel2(selection, flav_cut):
	""" For 2 barrel lepton measurement """
	selection.append( "LepZ2_pt > 15 " )
	selection.append( "(abs(LepSel_eta[0]) < (1.2+0.245*(abs(LepSel_pdgId[0])==11))) + (abs(LepSel_eta[1]) < (1.2+0.245*(abs(LepSel_pdgId[1])==11))) + (abs(LepSel_eta[0]) < (1.2+0.245*(abs(LepSel_pdgId[0])==11))) == 2" )
	selection.append( flav_cut )
	caption = """Trigger efficiency measurements in different data
      and MC samples in the in the region with two barrel leptons. Uncertainties in the efficiency
      measurements are statistical only. \WZ events are not normalized to the cross section to properly account
      for the full statistical power of the sample."""
	return " && ".join(selection), caption


def barrel3(selection, flav_cut):
	""" For 3 barrel lepton measurement """
	selection.append( "LepZ2_pt > 15 " )
	selection.append( "(abs(LepSel_eta[0]) < (1.2+0.245*(abs(LepSel_pdgId[0])==11))) + (abs(LepSel_eta[1]) < (1.2+0.245*(abs(LepSel_pdgId[1])==11))) + (abs(LepSel_eta[0]) < (1.2+0.245*(abs(LepSel_pdgId[0])==11))) == 3" )
	selection.append( flav_cut )
	caption = """Trigger efficiency measurements in different data
      and MC samples in the in the region with three barrel leptons. Uncertainties in the efficiency
      measurements are statistical only. \WZ events are not normalized to the cross section to properly account
      for the full statistical power of the sample."""
	return " && ".join(selection), caption
