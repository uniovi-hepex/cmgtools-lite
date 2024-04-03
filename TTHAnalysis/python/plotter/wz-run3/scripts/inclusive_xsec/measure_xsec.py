""" Small script to compute the cross section for the WZ process """
from optparse import OptionParser
import os, sys, re
import ROOT as r
from copy import deepcopy 
import numpy as np
sys.path.append( os.path.join( os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3/"))
from cfgs.lumi import lumis

def get_histos(filename, return_variations = False):
  """ Function to retrieve histograms for computing the acceptance and its variations """
  f = r.TFile.Open( filename )
  
  # -- Nominal -- #
  nom = deepcopy( f.Get("tot_weight_prompt_WZ") )

  if return_variations:
    # -- Scales -- #
    scales = []; nscales = 6
    for iscale in range(nscales):
        hscale = deepcopy( f.Get(f"tot_weight_prompt_WZ_scale_{iscale}Up") )
        scales.append( hscale )
    
    # -- PDFs -- #
    pdfs = []; npdfs = 101
    for ipdf in range(1, npdfs):
        hpdf = deepcopy( f.Get(f"tot_weight_prompt_WZ_pdf_{ipdf}Up") )
        pdfs.append( hpdf )
        
    f.Close()
    return nom, scales, pdfs
  
  return nom

def get_acceptance( inpath, ch, rescale ):
  den_fileName = os.path.join( inpath, "denominator", f"{ch}", "plots_wz.root" ) 
  num_fileName = os.path.join( inpath, "numerator"  , f"{ch}", "plots_wz.root" ) 
  
  num, scales_num, pdfs_num = get_histos( num_fileName, return_variations = True )
  den, scales_den, pdfs_den = get_histos( den_fileName, return_variations = True )
  
  # 2. Compute the nominal acceptance
  rescale_fac = rescale.GetBinContent(1)/num.GetBinContent(1)
  print(rescale.GetBinContent(1), num.GetBinContent(1), rescale_fac)
  acc = rescale.GetBinContent(1) / den.GetBinContent(1)
  
  # 3. Compute the acceptance for each scale and PDF variation
  
  ## Scales: compute the envelop
  acc_scales = []
  for iscale in range( len(scales_num) ):
      acc_scales.append( scales_num[iscale].GetBinContent(1) / scales_den[iscale].GetBinContent(1) * rescale.GetBinContent(1)/num.GetBinContent(1) )
  acc_scale_unc_up   = abs( max(acc_scales) - acc )
  acc_scale_unc_down = abs( min(acc_scales) - acc )
  
  
  ## PDFs: rms
  # REMINDER: the last two variations account for alpha_s variations
  acc_pdfs = []
  for ipdf in range(1, len(pdfs_num) - 2 ): 
      acc_pdfs.append( pdfs_num[ipdf].GetBinContent(1) / pdfs_den[ipdf].GetBinContent(1) * rescale.GetBinContent(1)/num.GetBinContent(1) )
  
  
  acc_pdf_unc = np.sqrt( sum([(acc-pdf)**2 for pdf in acc_pdfs]) )
  return acc, acc_scale_unc_up, acc_scale_unc_down, acc_pdf_unc, num, den,rescale.GetBinContent(1)/num.GetBinContent(1)

def get_efficiency( inpath, ch ):
  den_fileName = os.path.join( inpath, "denominator", f"{ch}", "plots_wz.root" ) 
  num_fileName = os.path.join( inpath, "numerator"  , f"{ch}", "plots_wz.root" ) 
  
  num = get_histos( num_fileName )
  den = get_histos( den_fileName )
  
  
  # Now compute the TEfficiency
  eff_obj = r.TEfficiency()
  eff_obj.SetStatisticOption(r.TEfficiency.kFNormal)
  eff_obj.SetPassedHistogram( num, "f" )
  eff_obj.SetTotalHistogram( den, "f" )
  
  eff = eff_obj.GetEfficiency(1)
  efferr = np.sqrt(eff_obj.GetEfficiencyErrorLow(1)**2 + eff_obj.GetEfficiencyErrorUp(1)**2)
  return eff, efferr, num, den

def xsec_fid( Nsr, eff, L, Nsr_nonfid, Ntot ):
  return Nsr / (eff * L)# * (1 - Nsr_nonfid / Ntot)

def xsec_total( fid_xsec, acc ):
  return fid_xsec / (0.32 * 0.1 * acc)

if __name__ == "__main__":
    accpath = sys.argv[1]
    effpath = sys.argv[2]
    combinepath = sys.argv[3]
    year = sys.argv[4]

    # Perform these operations per channel: eee, eem, mme and mmm
    channels = ["eee", "eem", "mme", "mmm", "inclusive"]
        
    # 1. Collect the results per channel
    for ich, ch in enumerate(channels):
        # efficiency
        eff, efferr, num, den = get_efficiency( os.path.join(effpath, year) , ch )


        # acceptance
        acc, acc_scale_unc_up, acc_scale_unc_down, acc_pdf_unc, numacc, denacc, factor = get_acceptance( os.path.join(accpath, year), ch, den )

        # Fetch the fit results
        fitDiagnostics_path = os.path.join(os.path.join(combinepath, year, ch, "fitDiagnosticsTest.root"))
        fitD = r.TFile.Open( fitDiagnostics_path )

        # ---- Retrieve the signal strenght and its uncertainty 
        fitResult = fitD.Get("fit_s")
        r_prompt_WZ = 1
        r_prompt_WZ_errhigh = 0
        r_prompt_WZ_errlow = 0
        r_prompt_WZ_total = 0
        for par in fitResult.floatParsFinal():
          if "r_wz" in par.GetName():
            r_prompt_WZ         = par.getVal()
            r_prompt_WZ_errhigh = abs(par.getErrorHi())    
            r_prompt_WZ_errlow = abs(par.getErrorLo())
            r_prompt_WZ_total   = abs(par.getError())    

        # ---- Now get the number of events postfit
        dire = fitD.Get("shapes_prefit")
        if ch != "inclusive":
          direch = dire.Get( f"ch1" )
          nwz = direch.Get("prompt_WZ").GetBinContent( ich + 1 )
          nwz_nonfid = direch.Get("prompt_WZ_nonfiducial").GetBinContent( ich + 1 )
          ntotwz = direch.Get("total_signal").GetBinContent( ich + 1 )
          ntot = direch.Get("total").GetBinContent( ich + 1 )

        else:
          nwz = sum( [dire.Get( f"ch{ibin}" ).Get("prompt_WZ").GetBinContent(ibin) for ibin in range(1, 5) ] )
          nwz_nonfid = sum( [dire.Get( f"ch{ibin}" ).Get("prompt_WZ_nonfiducial").GetBinContent(ibin) for ibin in range(1, 5) ] )
          ntotwz = sum( [dire.Get( f"ch{ibin}" ).Get("total_signal").GetBinContent(ibin) for ibin in range(1, 5) ]  )
          ntot = sum( [dire.Get( f"ch{ibin}" ).Get("total").GetBinContent(ibin) for ibin in range(1, 5) ]  )
          

        fitD.Close()
        
      
        # fiducial cross section
        sigma_fid = xsec_fid( nwz + nwz_nonfid, eff, 20.6, nwz_nonfid, ntot) / factor 
        sigma_fid_err = xsec_fid( nwz + nwz_nonfid, eff , 20.6, nwz_nonfid, ntot) / factor * r_prompt_WZ_total        
        sigma_tot = xsec_total( sigma_fid, acc ) / 1000
        sigma_tot_err_fit = abs( xsec_total( sigma_fid + sigma_fid_err, acc ) / 1000 - sigma_tot )
        sigma_tot_err_acc_pdf = abs( xsec_total( sigma_fid, acc + acc_pdf_unc ) / 1000 - sigma_tot )
        sigma_tot_err_acc_scaleUp = abs( xsec_total( sigma_fid, acc + acc_scale_unc_up ) / 1000 - sigma_tot )
        sigma_tot_err_acc_scaleDn = abs( xsec_total( sigma_fid, acc - acc_scale_unc_down ) / 1000 - sigma_tot )

        print(f" ------- Compare things: {ch}")
        print(f" nwz = {nwz} (events passing offline)")
        print(f" nwznonfid = {nwz_nonfid} (events passing offline)")
        print(f" ntotwz = {ntotwz} (events passing offline)")
        print(f" ntot = {ntot} (events passing offline)")
        print(f" o Efficiency: {eff:3.3f} +/- {efferr:3.3f}")
        print(f" nwz = {num.GetBinContent(1)} (events passing offline + fiducial -- eff num)")
        print(f" nwz_fid = {den.GetBinContent(1)} (events passing fiducial -- eff den)")
        print(f" o Acceptance: A = {acc:3.4f}")
        print(f" nwz_acc_total = {denacc.GetBinContent(1)} (events passing total -- acc den)")
        print(f" nwz_acc_fiducial = {numacc.GetBinContent(1)} (events passing fiducial -- acc num)")
        print("")
        print("")
        #print(f" ---- Cross section results for channel: {ch} ----")
        #print(f" o Efficiency: {eff:3.3f} +/- {efferr:3.3f}")
        #print(f" o Acceptance: A = {acc:3.4f} +/- {acc_pdf_unc:3.4f} (PDF) + {acc_scale_unc_up:3.4f} (scale up) - {acc_scale_unc_down:3.4f} (scale dn)")
        #print(f" o Fid xsec: sigma = {sigma_fid:3.2f} +/- {sigma_fid_err:3.2f} fb")
        #print(f" o Total xsec: sigma = {sigma_tot:3.2f} +/- {sigma_tot_err_fit:3.2f} (total) +/- {sigma_tot_err_acc_pdf:3.2f} (PDF) {sigma_tot_err_acc_scaleUp:3.2f} (Scale Up) +/- {sigma_tot_err_acc_scaleDn:3.2f} (Scale Down) fb")
