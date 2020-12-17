import os, sys, argparse, shutil
import ROOT as r
import warnings as wr
from multiprocessing import Pool
from array import array
from copy import deepcopy

sys.path.append('{cmsswpath}/src/CMGTools/TTHAnalysis/python/plotter/tw-run2/differential/'.format(cmsswpath = os.environ['CMSSW_BASE']))
import varList as vl
import CMS_lumi, tdrstyle

r.gROOT.SetBatch(True)
CMS_lumi.writeExtraText = 1
vl.SetUpWarnings()

markersize  = 0.8


def GetAndPlotResponseMatrix(var, key, theresponseh, theparticleh, thepath):
    #print "\n[GetAndPlotResponseMatrix]"
    particlebins = vl.varList[var]["bins_particle"]
    detectorbins = vl.varList[var]["bins_detector"]
    nparticlebins = len(particlebins) - 1
    ndetectorbins = len(detectorbins) - 1
    particlebins = array("d", particlebins)
    detectorbins = array("d", detectorbins)

    hGen  = r.TH2D('hGen', '', nparticlebins, particlebins, ndetectorbins, detectorbins)

    htemp = deepcopy(theresponseh.Clone("response"))

    for i in range(0, nparticlebins + 2):
        for j in range(0, ndetectorbins + 2):
            hGen.SetBinContent(i, j, theparticleh.GetBinContent(i))
            hGen.SetBinError(i, j, theparticleh.GetBinError(i))

    overlap = None
    htemp.Divide(hGen); del hGen;

    if var == "Fiducial":
        overlap = htemp.GetBinContent(1, 1)

    # Fixing the over and underflow bins to one.
    for i in range(1, nparticlebins+1):
        tmpsum = 0.
        for j in range(1, ndetectorbins+1):
            tmpsum += htemp.GetBinContent(i, j)
        #print tmpsum
        htemp.SetBinContent(i, 0, 0.)
        htemp.SetBinContent(i, ndetectorbins + 1, 1 - tmpsum)
        #htemp.SetBinContent(i, ndetectorbins + 1, 0)
    for j in range(0, ndetectorbins+2):
        htemp.SetBinContent(0, j, 0.)
        htemp.SetBinContent(nparticlebins + 1, j, 0.)

    #print "htemp 00", htemp.GetBinContent(0, 0)
    #print "htemp 20", htemp.GetBinContent(nparticlebins + 1, 0)
    #print "htemp 02", htemp.GetBinContent(0, ndetectorbins + 1)
    #print "htemp 11", htemp.GetBinContent(1, 1)
    #print "htemp 12", htemp.GetBinContent(1, 2)
    #print "htemp 21", htemp.GetBinContent(2, 1)
    #print "htemp 11", htemp.GetBinContent(nparticlebins + 1, ndetectorbins + 1)

    htemp.SetXTitle(vl.varList[var]['xaxis'] + " [particle level]")
    htemp.SetYTitle(vl.varList[var]['xaxis'] + " [detector level]")
    htemp.SetName("R" + var + "_" + key)

    tdrstyle.setTDRStyle()
    htemp.SetStats(False)
    r.gStyle.SetLabelFont(43, "XYZ")
    r.gStyle.SetLabelSize(22, "XYZ")
    htemp.GetYaxis().SetTitleOffset(1.4)
    htemp.GetXaxis().SetTitleOffset(1.2)
    htemp.GetXaxis().SetTitleFont(43)
    htemp.GetXaxis().SetTitleSize(22)
    htemp.GetXaxis().SetLabelFont(43)
    htemp.GetXaxis().SetLabelSize(22)
    htemp.GetYaxis().SetTitleFont(43)
    htemp.GetYaxis().SetTitleSize(22)
    htemp.GetYaxis().SetLabelFont(43)
    htemp.GetYaxis().SetLabelSize(22)
    #c = r.TCanvas('c', "", 700, 500)
    c = r.TCanvas('c', "", 600, 600)
    plot = c.GetPad(0);
    #plot.SetPad(0.0, 0.23, 1.0, 1.0);
    plot.SetTopMargin(0.0475); plot.SetRightMargin(0.1); plot.SetLeftMargin(0.12); plot.SetBottomMargin(0.1)
    if 'resptxtsize' in vl.varList[var]: htemp.SetMarkerSize(vl.varList[var]['resptxtsize'])
    else:                                  htemp.SetMarkerSize(markersize)
    htemp.SetMarkerColor(r.kRed)
    #print htemp.GetBinContent(2, 2)
    htemptodraw = deepcopy(htemp.Clone("htemptodraw"))
    htemptodraw.Scale(100.)
    #print htemp.GetBinContent(2, 2)
    htemptodraw.Draw("colz text e")
    r.gStyle.SetPaintTextFormat("4.3f")
    CMS_lumi.lumi_13TeV = ""
    #CMS_lumi.extraText  = 'Simulation Supplementary'
    CMS_lumi.extraText  = 'Simulation Preliminary'
    CMS_lumi.lumi_sqrtS = ''
    #CMS_lumi.cmsTextSize += 0.1
    CMS_lumi.CMS_lumi(r.gPad, 0, 0, 0.05)
    r.gStyle.SetLabelFont(43, "XYZ")
    r.gStyle.SetLabelSize(22, "XYZ")
    r.gPad.Update()
    c.SaveAs(thepath + "/R_" + var + "_" + key + ".png")
    c.SaveAs(thepath + "/R_" + var + "_" + key + ".eps")
    c.SaveAs(thepath + "/R_" + var + "_" + key + ".pdf")
    c.SaveAs(thepath + "/R_" + var + "_" + key + ".root")
    c.Close(); del c, plot


    c = r.TCanvas('c', "", 600, 600)
    plot = c.GetPad(0);
    plot.SetTopMargin(0.0475); plot.SetRightMargin(0.1); plot.SetLeftMargin(0.12); plot.SetBottomMargin(0.1)
    htemp.Draw("colz")
    CMS_lumi.CMS_lumi(r.gPad, 0, 0, 0.05)
    r.gStyle.SetLabelFont(43, "XYZ")
    r.gStyle.SetLabelSize(22, "XYZ")
    r.gPad.Update()
    c.SaveAs(thepath + "/Rnonumb_" + var + "_" + key + ".png")
    c.SaveAs(thepath + "/Rnonumb_" + var + "_" + key + ".eps")
    c.SaveAs(thepath + "/Rnonumb_" + var + "_" + key + ".pdf")
    c.SaveAs(thepath + "/Rnonumb_" + var + "_" + key + ".root")
    c.Close(); del c, plot
    return htemp, overlap


def GetAndPlotPuritiesAndStabilities(var, theresponseh, theparticleh, thedetectorparticleh, thedetectorh, thepath):
    #print "\n[PuritiesAndStabilities]"
    purities          = []
    stabilities       = []
    stabilities_woeff = []

    particlebins  = vl.varList[var]["bins_particle"]
    detectorbins  = vl.varList[var]["bins_detector"]
    nparticlebins = len(particlebins) - 1
    ndetectorbins = len(detectorbins) - 1
    particlebins  = array("d", particlebins)
    detectorbins  = array("d", detectorbins)

    #print " > Calculating stabilities..."
    for i in range(1, nparticlebins + 1):
        sumstab = 0
        for j in range(1, ndetectorbins + 1):
            sumstab += theresponseh.GetBinContent(i, j)

        ## CON EFICIENCIA DE RECONSTRUCCION
        try:
            stabilities.append(sumstab / theparticleh.GetBinContent(i))
        except ZeroDivisionError:
            stabilities.append(0)

        ## SIN EFICIENCIA DE RECONSTRUCCION
        try:
            stabilities_woeff.append(sumstab / thedetectorparticleh.GetBinContent(i))
        except ZeroDivisionError:
            stabilities_woeff.append(0)

    #print " > Calculating purities..."
    for j in range(1, ndetectorbins + 1):
        sumpur = 0
        for i in range(1, nparticlebins + 1):
            sumpur += theresponseh.GetBinContent(i, j)

        try:
            purities.append(sumpur / thedetectorh.GetBinContent(j))
        except ZeroDivisionError:
            purities.append(0)


    #print " > Fixing values of histograms..."
    #print nparticlebins, particlebins, ndetectorbins, detectorbins
    hStab       = r.TH1D('hStab',       '', nparticlebins, particlebins)
    hStab_woeff = r.TH1D('hStab_woeff', '', nparticlebins, particlebins)
    hPur        = r.TH1D('hPur',        '', ndetectorbins, detectorbins)
    for i in range(1, hStab.GetNbinsX() + 1):
        hStab.SetBinContent(i, stabilities[i - 1])
        hStab_woeff.SetBinContent(i, stabilities_woeff[i - 1])

    for j in range(1, hPur.GetNbinsX() + 1):
        hPur.SetBinContent(j, purities[j - 1])

    #print " > Plotting first purities and stabilities plot..."
    c = r.TCanvas('c', "Purities and stabilities of " + var)
    plot = c.GetPad(0);
    #plot.SetPad(0.0, 0.23, 1.0, 1.0);
    plot.SetTopMargin(0.06); plot.SetRightMargin(0.05); plot.SetLeftMargin(0.1); plot.SetBottomMargin(0.12)

    hPur.SetXTitle(vl.varList[var]['xaxis'])
    hPur.SetStats(False)
    hPur.SetYTitle("Purities and stabilities")
    hStab.SetLineColor(r.kBlue)
    hPur.SetLineColor(r.kRed)
    hPur.SetMaximum(1.)
    hPur.SetMinimum(0.)
    #hPur.SetMinimum(0.6)
    hPur.GetXaxis().SetTitleFont(43)
    hPur.GetXaxis().SetTitleSize(22)
    hPur.GetXaxis().SetLabelFont(43)
    hPur.GetXaxis().SetLabelSize(22)
    hPur.GetXaxis().SetLabelOffset(0.007)
    hPur.GetXaxis().SetTitleOffset(1.2)
    hPur.GetYaxis().SetTitleFont(43)
    hPur.GetYaxis().SetTitleSize(22)
    hPur.GetYaxis().SetLabelFont(43)
    hPur.GetYaxis().SetLabelSize(22)
    hPur.GetYaxis().SetLabelOffset(0.007)
    hPur.GetYaxis().SetTitleOffset(1.2)
    hPur.Draw('')
    hStab.Draw('same')
    r.gPad.Update()

    textSize      = 0.035
    (x1,y1,x2,y2) = (.75, .45, .85, .65)
    l             = r.TLegend(x1, y1, x2, y2);
    l.AddEntry(hStab, 'Stability')
    l.AddEntry(hPur,  'Purity')
    l.SetTextFont(42)
    l.SetTextSize(textSize)
    l.SetBorderSize(0)
    l.SetFillColor(10)
    l.Draw()
    r.gPad.Update()

    c.SaveAs(thepath + "/PurStab_" + var + ".png")
    c.SaveAs(thepath + "/PurStab_" + var + ".pdf")
    c.SaveAs(thepath + "/PurStab_" + var + ".root")
    c.Close(); del c, hStab, plot


    #print " > Plotting second purities and stabilities plot..."
    c = r.TCanvas('c', "Purities and stabilities of " + var)
    plot = c.GetPad(0);
    #plot.SetPad(0.0, 0.23, 1.0, 1.0);
    plot.SetTopMargin(0.06); plot.SetRightMargin(0.05); plot.SetLeftMargin(0.1); plot.SetBottomMargin(0.12)

    hStab_woeff.SetLineColor(r.kBlue)
    hPur.Draw('')
    hStab_woeff.Draw('same')
    r.gPad.Update()

    textSize      = 0.035
    (x1,y1,x2,y2) = (.75, .45, .85, .65)
    l             = r.TLegend(x1, y1, x2, y2);
    l.AddEntry(hStab_woeff, 'Stability (w/o rec. eff.)')
    l.AddEntry(hPur,  'Purity')
    l.SetTextFont(42)
    l.SetTextSize(textSize)
    l.SetBorderSize(0)
    l.SetFillColor(10)
    l.Draw()
    r.gPad.Update()

    c.SaveAs(thepath + "/PurStabwoeff_" + var + ".png")
    c.SaveAs(thepath + "/PurStabwoeff_" + var + ".pdf")
    c.SaveAs(thepath + "/PurStabwoeff_" + var + ".root")
    c.Close(); del c, hStab_woeff, plot
    return


def GetConditionNumber(thehisto):
    #print "\n[GetConditionNumber]"
    matrx = r.TMatrixD( thehisto.GetYaxis().GetNbins(), thehisto.GetXaxis().GetNbins()) # rows are y, x are columns
    for i in range(thehisto.GetXaxis().GetNbins()):
        for j in range(thehisto.GetYaxis().GetNbins()):
            matrx[j][i] = thehisto.GetBinContent( thehisto.GetBin(i+1, j+1) )

    decomp = r.TDecompSVD(matrx)
    condn  = decomp.Condition()
    del matrx, decomp
    return condn


def GetAndPlotNonFiducialHisto(var, theunc, thefiducialh, thepath):
    #print "\n[GetAndPlotNonFiducialHisto]"
    '''This function obtains the non fiducial histograms.'''
    hNonFid = deepcopy(thefiducialh.Clone("F" + var + "_" + theunc))
    hNonFid.SetXTitle("var")
    hNonFid.SetYTitle("Events not passing the fiducial sel.")

    c = r.TCanvas('c', "Fiducial histogram - " + var + "_" + theunc, 600, 600)
    hNonFid.Draw()
    r.gStyle.SetPaintTextFormat("4.1f")
    r.gPad.Update()
    c.SaveAs(thepath + "/F_" + var + "_" + theunc + ".png")
    c.SaveAs(thepath + "/F_" + var + "_" + theunc + ".pdf")
    c.SaveAs(thepath + "/F_" + var + "_" + theunc + ".root")
    c.Close(); del c
    return hNonFid


def SaveOverlap(theoverlap, thepath):
    #print "\n[SaveOverlap]"
    fcn = open(thepath + "/overlaps.txt", "w")
    out = '(detector & particle) / particle\n'
    out += str(round(theoverlap, 4)) + '\n'
    fcn.write(out)
    fcn.close
    return


def SaveAllConditionNumbers(thedict, thepath):
    #print "\n[SaveAllConditionNumbers]"
    fcn = open(thepath + "/condnums.txt", "w")
    out = 'Variation        Value\n'
    for key in thedict:
        out += ("Nominal" if key == "" else key) + ":\t" + str(round(thedict[key], 4)) + '\n'
    fcn.write(out)
    fcn.close
    return


def CalculateAndPlotResponseMatrices(tsk):
    inpath, iY, iV = tsk
    # 0) Preliminary.
    print "\n> Creando matrices de respuesta en", inpath, "para el anyo", iY, "y la variable", iV

    fParticle = r.TFile(inpath + "/" + iY + "/" + iV + "/particle.root", "READ")
    hParticle = deepcopy(fParticle.Get("x_tw").Clone("hParticle_" + iV))
    fParticle.Close(); del fParticle

    unclist = []
    fDetector         = r.TFile(inpath + "/" + iY + "/" + iV + "/detector.root", "READ")
    fDetectorParticle = r.TFile(inpath + "/" + iY + "/" + iV + "/detectorparticle.root", "READ")
    fResponse         = r.TFile(inpath + "/" + iY + "/" + iV + "/detectorparticleResponse.root", "READ")
    fDetectorParticleButDetector  = r.TFile(inpath + "/" + iY + "/" + iV + "/detectorparticlebutdetector.root", "READ")
    fNonFiducial      = r.TFile(inpath + "/" + iY + "/" + iV + "/nonfiducial.root", "READ")

    detectordict = {}; detectorparticledict = {}; detectorparticlebutdetectordict = {};
    responsedict = {}; nonfiducialdict = {};
    condnumdict = {}
    for key in fDetector.GetListOfKeys():
        tmpnam = key.GetName()
        #print "\ntmpnam:", tmpnam

        #if "mistagging" in tmpnam: continue #### ?????????????????????????????????????????????????????????????????????????


        if "data" in tmpnam: continue

        if "Up" not in tmpnam and "Down" not in tmpnam: # It is the nominal value!
            print tmpnam
            detectordict[""]         = deepcopy(fDetector.Get(tmpnam).Clone(""))
            detectorparticledict[""] = deepcopy(fDetectorParticle.Get(tmpnam).Clone(""))
            detectorparticlebutdetectordict[""] = deepcopy(fDetectorParticleButDetector.Get(tmpnam).Clone(""))
            responsedict[""]         = deepcopy(fResponse.Get(tmpnam).Clone(""))
            nonfiducialdict[""]      = deepcopy(fNonFiducial.Get(tmpnam).Clone(""))
        else:
            tmpunc  = tmpnam.replace("x_tw_", "")
            #print "tmpunc", tmpunc

            if tmpunc not in detectordict:
                detectordict[tmpunc]         = {}
                responsedict[tmpunc]         = {}
            #print tmpunc
            detectordict[tmpunc]         = deepcopy(fDetector.Get(tmpnam).Clone(tmpunc))
            responsedict[tmpunc]         = deepcopy(fResponse.Get(tmpnam).Clone(tmpunc))
            nonfiducialdict[tmpunc]      = deepcopy(fNonFiducial.Get(tmpnam).Clone(tmpunc))


    fDetector.Close();         del fDetector
    fDetectorParticle.Close(); del fDetectorParticle
    fResponse.Close();         del fResponse
    fNonFiducial.Close();      del fNonFiducial
    fDetectorParticleButDetector.Close(); del fDetectorParticleButDetector

    #print detectordict, detectorparticledict, responsedict, nonfiducialdict

    tmpoutpath = inpath + "/" + iY + "/" + iV + "/responseplots"

    if not os.path.isdir(tmpoutpath):
        os.system("mkdir -p " + tmpoutpath)

    foutput = r.TFile(inpath + "/" + iY + "/" + iV + "/UnfoldingInfo.root", "recreate")
    for key in detectordict:
        if key == "":
            GetAndPlotPuritiesAndStabilities(iV, responsedict[key], hParticle, detectorparticledict[key], detectordict[key], tmpoutpath)

        hResponse, theoverlap = GetAndPlotResponseMatrix(iV, key, responsedict[key], hParticle, tmpoutpath)

        if theoverlap != None:
            SaveOverlap(theoverlap, tmpoutpath)

        condnumdict[key] = GetConditionNumber(hResponse)
        hNonFiducial     = GetAndPlotNonFiducialHisto(iV, key, nonfiducialdict[key], tmpoutpath)

        hResponse.Write()
        hNonFiducial.Write()
    foutput.Close()

    SaveAllConditionNumbers(condnumdict, tmpoutpath)
    return



if __name__=="__main__":
    parser = argparse.ArgumentParser(usage = "python nanoAOD_checker.py [options]", description = "Checker tool for the outputs of nanoAOD production (NOT postprocessing)", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--inpath',    '-i', metavar = 'inpath',     dest = "inpath",   required = False, default = "./temp/differential/cards")
    parser.add_argument('--year',      '-y', metavar = 'year',       dest = "year",     required = False, default = "all")
    parser.add_argument('--variable',  '-v', metavar = 'variable',   dest = "variable", required = False, default = "all")
    parser.add_argument('--extraArgs', '-e', metavar = 'extra',      dest = "extra",    required = False, default = "")
    parser.add_argument('--nthreads',  '-j', metavar = 'nthreads',   dest = "nthreads", required = False, default = 0, type = int)
    parser.add_argument('--pretend',   '-p', action  = "store_true", dest = "pretend",  required = False, default = False)


    args     = parser.parse_args()
    year     = args.year
    extra    = args.extra
    nthreads = args.nthreads
    pretend  = args.pretend
    inpath   = args.inpath
    variable = args.variable

    print("\n===== Unfolding procedures: Response matrices & ROOT files production =====")
    print("> Setting binning, paths, and other details...")

    print "\n> Drawing matrices and writing ROOT file (old one will be overwritten!)."


    #### First, find the tasks
    tasks = []
    if year == "all":
        if variable == "all":
            theyears = []
            presentyears = next(os.walk(inpath))[1]

            if "2016" in presentyears:
                theyears.append("2016")
            if "2017" in presentyears:
                theyears.append("2017")
            if "2018" in presentyears:
                theyears.append("2018")
            if "run2" in presentyears:
                theyears.append("run2")

            for iY in theyears:
                thevars = next(os.walk(inpath + "/" + iY))[1]

                for iV in thevars:
                    if "plots" in iV:
                        continue

                    tasks.append( (inpath, iY, iV) )

    if nthreads > 1:
        pool = Pool(nthreads)
        pool.map(CalculateAndPlotResponseMatrices, tasks)
        pool.close()
        pool.join()
    else:
        for tsk in tasks:
            CalculateAndPlotResponseMatrices(tsk)
