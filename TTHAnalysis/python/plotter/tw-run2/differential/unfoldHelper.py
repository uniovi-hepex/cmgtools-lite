from copy import deepcopy
import ROOT as r
import warnings as wr
import os, sys, math, array, argparse
from multiprocessing import Pool

sys.path.append('{cmsswpath}/src/CMGTools/TTHAnalysis/python/plotter/tw-run2/differential/'.format(cmsswpath = os.environ['CMSSW_BASE']))
import beautifulUnfoldingPlots as bp
import errorPropagator as ep
#import getLaTeXtable as tex
import varList as vl
import goftests as gof

r.gROOT.SetBatch(True)
verbose = True
#===================================

class DataContainer:
    ''' Class to store all the needed inputs: response matrices and varied input distributions'''
    def __init__(self, var_, folderpath_, inputsfilename_ = "detectorsignal_bs.root", matricesfilename_ = "UnfoldingInfo.root", year_ = 2016):
        self.var              = var_
        self.year             = year_
        self.folderpath       = folderpath_
        self.fileName         = self.folderpath + "/" + inputsfilename_
        self.fileNameResponse = self.folderpath + "/" + matricesfilename_
        self.systListResp     = []
        self.listOfSysts      = []
        self.responseMatrices = {}
        self.unfoldingInputs  = {}
        self.covmatInput      = {}
        self.bkgs             = {}
        self.readAndStore()

    def readAndStore(self):
        # Getting inputs
        if not os.path.isfile(self.fileName):
            raise RuntimeError('The rootfile with the post signal extraction information of variable {var} does not exist.'.format(var = self.var))
        if not os.path.isfile(self.fileNameResponse):
            raise RuntimeError('The rootfile with the response matrices information of variable {var} does not exist.'.format(var = self.var))

        tfile = r.TFile.Open(self.fileName)
        for key in tfile.GetListOfKeys():
            if 'data_' in key.GetName():
                sysName = key.GetName().replace('data_', '')
                self.unfoldingInputs[sysName] = deepcopy(key.ReadObj())
                if sysName != '': self.listOfSysts.append(sysName)
            elif 'fitcovmat' in key.GetName():
                sysName = key.GetName().replace('fitcovmat_', '')
                self.covmatInput[sysName] = deepcopy(key.ReadObj())

        if '' not in self.unfoldingInputs:
            raise RuntimeError("Unfolding input for nominal sample is missing.")
        if '' not in self.covmatInput and "fit" in self.fileName:
            raise RuntimeError("Covariance input for nominal sample is missing")
        tfile.Close()
        
        # Getting uncertainties in the response matrix
        tfile = r.TFile.Open(self.fileNameResponse)
        for key in tfile.GetListOfKeys():
            #print key.GetName()
            if key.GetName()[0] != 'R': continue
            if vl.varList[self.var]['var_response'] not in key.GetName() and self.var not in key.GetName(): continue
            if key.GetName() == 'R' + vl.varList[self.var]['var_response'] + "_":
                self.responseMatrices[''] = deepcopy(key.ReadObj())
            elif 'R' + vl.varList[self.var]['var_response'] + '_' in key.GetName():
                #sysName = '_'.join(key.GetName().split('_')[1:])
                sysName = key.GetName().replace("R" + vl.varList[self.var]['var_response'] + '_', "")
                self.systListResp.append(sysName)
                self.responseMatrices[sysName] = deepcopy(key.ReadObj())

        # Getting background (events not passing the fiducial selection, but passing reco)
        thelumi = vl.TotalLumi if self.year == "run2" else vl.LumiDict[int(self.year)]
        scalevalone = thelumi
        if self.year == "run2":
            scalevalone = thelumi/3.
        for key in tfile.GetListOfKeys():
            if key.GetName()[0] != 'F': continue
            if vl.varList[self.var]['var_response'] not in key.GetName(): continue
            if key.GetName() == 'F' + vl.varList[self.var]['var_response'] + "_":
                self.bkgs[''] = deepcopy(key.ReadObj())
                #self.bkgs[''].Scale(scalevalone)
            elif "F" + vl.varList[self.var]['var_response'] + "_" in key.GetName():
                #sysName = '_'.join(key.GetName().split('_')[1:])
                sysName = key.GetName().replace("F" + vl.varList[self.var]['var_response'] + '_', "")
                self.bkgs[sysName] = deepcopy(key.ReadObj())
                #self.bkgs[sysName].Scale(scalevalone)
                
        tfile.Close()

        if '' not in self.responseMatrices:
            raise RuntimeError("The nominal response matrix is not present in the provided rootfile.")
        
        #if verbose: print "Printy thingy. listOfSysts:\n", self.listOfSysts, "\nsystListResp:\n", self.systListResp


        #print self.var, self.year
        #for i in range(1, self.unfoldingInputs[""].GetNbinsX() + 1):

            #print self.unfoldingInputs[""].GetBinContent(i), self.bkgs[''].GetBinContent(i)

        #for key in self.unfoldingInputs:
            #if key not in self.bkgs:
                #print key

        #print "==========="

        #for key in self.bkgs:
            #print key
        #sys.exit()
        return
    

    def getInputs(self, nuis):
        if verbose: print '\n> Getting inputs for nuisance', nuis

        retcovmat = None
        if nuis in self.covmatInput:
            retcovmat = self.covmatInput[nuis]

        if nuis not in self.responseMatrices:
            #raise RuntimeError("%s is not in the list of varied response matrices nor in the blacklist of systs. w/o associated response matrices."%nuis)
            wr.warn("WARNING: %s is not in the list of varied response matrices nor in the blacklist of systs. w/o associated response matrices. Nominal will be asigned"%nuis)
            return self.unfoldingInputs[nuis], self.responseMatrices[""], self.bkgs[""], retcovmat
        else:
            return self.unfoldingInputs[nuis], self.responseMatrices[nuis], self.bkgs[nuis], retcovmat


    def getResponse(self, nuis):
        if nuis not in self.systListResp:
            RuntimeError("%s is not in the list of varied response matrices nor in the blacklist of systs. w/o associated response matrices."%nuis)
        return self.responseMatrices[nuis]



class UnfolderHelper:
    ''' Performs unfolding for one specific nuisance'''
    def __init__(self, var, nuis):
        self.var        = var
        self.nuis       = nuis
        self.plotspath  = ''
        self.doArea     = False
        self.Init       = False
        self.wearedoingasimov = False
        self.tau        = 0

        self.tunfolder  = None
        self.unfInput   = None
        self.response   = None
        self.bkg        = None
        self.inputcovmat= None
    
    
    def makeUnfolderCore(self, unfInputNresponse):
        self.unfInput, self.response, self.bkg, self.inputcovmat = unfInputNresponse
        self.tunfolder = r.TUnfoldDensity(self.response,
                                          r.TUnfold.kHistMapOutputHoriz,
                                          r.TUnfold.kRegModeCurvature,
                                          r.TUnfold.kEConstraintArea if self.doArea else r.TUnfold.kEConstraintNone,
                                          r.TUnfoldDensity.kDensityModeNone)

        if self.inputcovmat:
            self.tunfolder.SetInput(self.unfInput, 0., 0., self.inputcovmat)
        else:
            self.tunfolder.SetInput(self.unfInput)

        self.tunfolder.SubtractBackground(self.bkg, "Events outside the fiducial region")
        return
    
    
    def doLCurveScan(self):
        if self.nuis != '':
            raise RuntimeError("Attempted to do naughty things like doing the scan with varied nuisances.")

        self.logTauX    = r.TSpline3()
        self.logTauY    = r.TSpline3()
        self.logTauCurv = r.TSpline3()
        self.lCurve     = r.TGraph(0)

        #self.themax = self.tunfolder.ScanLcurve(10000, 1e-10, 1e-4, self.lCurve, self.logTauX, self.logTauY, self.logTauCurv)
        self.themax = self.tunfolder.ScanLcurve(10000, r.Double(1e-30), r.Double(1e-4), self.lCurve, self.logTauX,  self.logTauY, self.logTauCurv)
        
        self.tau = self.tunfolder.GetTau()
        return
    
    
    def doTauScan(self):
        if self.nuis != '':
            raise RuntimeError("Attempted to do naughty things like doing the scan with varied nuisances.")

        self.logTauX = r.TSpline3()
        self.logTauY = r.TSpline3()
        self.scanRes = r.TSpline3()
        self.lCurve  = r.TGraph(0)
        
        # kEScanTauRhoAvg          average global correlation coefficient (from TUnfold::GetRhoI())
        # kEScanTauRhoMax          maximum global correlation coefficient (from TUnfold::GetRhoI())
        # kEScanTauRhoAvgSys       average global correlation coefficient (from TUnfoldSys::GetRhoItotal())
        # kEScanTauRhoMaxSys       maximum global correlation coefficient (from TUnfoldSys::GetRhoItotal())
        # kEScanTauRhoSquareAvg    average global correlation coefficient squared (from TUnfold::GetRhoI())
        # kEScanTauRhoSquareAvgSys average global correlation coefficient squared (from TUnfoldSys::GetRhoItotal())
        r.gInterpreter.LoadMacro('myScanner.C+')
        self.themax = r.myScanner(self.tunfolder, 1000, 1e-9, 1e-3, self.scanRes, r.TUnfoldDensity.kEScanTauRhoAvg,
                                  self.logTauX, self.logTauY)
        
        self.tau = self.tunfolder.GetTau()
        return
    
    
    def doScanPlots(self):
        # Plot the scan variable and the maximum
        t = r.Double(0)
        x = r.Double(0)
        y = r.Double(0)
        if not hasattr(self, 'logTauX'):
            self.doLCurveScan()
        
        # First: L-curve plot
        plot = bp.beautifulUnfPlot('{var}_asimov_LCurve'.format(var = self.var) if (self.wearedoingasimov) else '{var}_LCurve'.format(var = self.var), self.var)
        plot.isLCurve      = True
        plot.doPreliminary = vl.doPre
        plot.displayedLumi = vl.TotalLumi if self.year == "run2" else vl.LumiDict[int(self.year)]
        plot.plotspath     = self.plotspath

        if not hasattr(self, 'scanRes'):
            self.logTauX.GetKnot( self.themax, t, x)
            self.logTauY.GetKnot( self.themax, t, y)

            self.lCurve.SetLineWidth(2)
            self.lCurve.SetLineColor(r.kBlue)
            r.TGaxis.SetMaxDigits(3)
            self.lCurve.GetXaxis().SetNoExponent(True)
            self.lCurve.GetYaxis().SetNoExponent(True)
            self.lCurve.GetXaxis().SetTitle('log(#chi^{2}_{R})')
            self.lCurve.GetYaxis().SetTitle('log(#chi^{2}_{reg.})')
            plot.addHisto(self.lCurve,'ALnomin', '', 0)
        else:
            plot.addHisto(self.scanRes,'ALnomin','L curve',0)

        grph = r.TGraph(1, array.array('d', [r.Double(self.tunfolder.GetLcurveX())]), array.array('d', [r.Double(self.tunfolder.GetLcurveY())]))
        grph.SetMarkerColor(r.kRed)
        grph.SetMarkerSize(2)
        grph.SetMarkerStyle(29)
        #grph.Draw("P")
        plot.addTLatex(0.75, 0.9, "#tau = {taupar}".format(taupar = round(self.tau, 10)))
        #plot.addTLatex(0.75, 0.9, "#tau = {taupar}".format(taupar = self.tau))
        plot.saveCanvas('TR', leg = False)
        del plot, grph
        
        # Second: L-curve curvature plot
        plot = bp.beautifulUnfPlot('{var}_asimov_LogTauCurv'.format(var = self.var) if (self.wearedoingasimov) else '{var}_LogTauCurv'.format(var = self.var), self.var)
        plot.plotspath     = self.plotspath
        plot.displayedLumi = vl.TotalLumi if self.year == "run2" else vl.LumiDict[int(self.year)]
        plot.doPreliminary = vl.doPre
        plot.initCanvasAndAll()
        #plot.addHisto(self.lCurve, 'AL','',0)
        plot.canvas.cd()
        self.logTauCurv.Draw("AL")
        plot.saveCanvas('TR')
        del plot
        return
    
    
    def getConditionNumber(self, nuis = ''):
        prob = deepcopy( self.response.Clone(self.response.GetName() + '_' + nuis + '_probMatrix'))
        self.tunfolder.GetProbabilityMatrix(self.response.GetName() + '_' + nuis + '_probMatrix', '', r.TUnfold.kHistMapOutputHoriz)
        matrx = r.TMatrixD( prob.GetYaxis().GetNbins(), prob.GetXaxis().GetNbins()) # rows are y, x are columns
        for i in range(prob.GetXaxis().GetNbins()):
            for j in range(prob.GetYaxis().GetNbins()):
                matrx[j][i] = prob.GetBinContent( prob.GetBin(i+1,j+1) )
        
        if verbose: matrx.Print()
        decomp = r.TDecompSVD(matrx)
        condn  = decomp.Condition()
        del matrx, decomp, prob
        if verbose: print '> Matrix condition is', condn
        return condn



class Unfolder():
    def __init__(self, var, folderpath_, year = 2016, inputsfilename_ = "detectorsignal_bs.root", matricesfilename_ = "UnfoldingInfo.root"):
        self.var              = var
        self.folderpath       = folderpath_
        self.year             = year
        self.Data             = DataContainer(var, self.folderpath, inputsfilename_, matricesfilename_, year)
        self.systListResp     = self.Data.systListResp
        self.sysList          = self.Data.listOfSysts
        self.helpers          = { nuis : UnfolderHelper(self.var, nuis) for nuis in self.sysList }
        self.helpers['']      = UnfolderHelper(self.var, '')
        self.wearedoingasimov = (not vl.asimov and not 'asimov' in self.sysList)
        self.helpers[''].wearedoingasimov = self.wearedoingasimov    # ONLY IMPLEMENTED FOR NOMINAL ONES!!!!!
        self.plotspath        = ""
        self.doRegularisation = False
        self.usingFitInput    = False
        self.taulist          = { nuis : 0 for nuis in self.sysList } # Different taus for all the response matrices not implemented.
        self.taulist['']      = 0
        self.doAreaConstraint = False
        self.nomOutput        = None
        self.nomMatrix        = None


    def prepareAllHelpers(self, force = False):
        # maybe protect these boys so they dont get initialized several times
        self.prepareNominalHelper(force)

        for nuis in self.sysList:
            if nuis == '' or (not force and self.helpers[nuis].Init): continue
            self.helpers[nuis].doArea = self.doAreaConstraint
            self.helpers[nuis].makeUnfolderCore(self.Data.getInputs(nuis))
            self.helpers[nuis].Init   = True
        return


    def prepareNominalHelper(self, force = False):
        # maybe protect these boys so they dont get initialized several times
        if not force and self.helpers[''].Init: return
        self.helpers[''].doArea = self.doAreaConstraint
        self.helpers[''].makeUnfolderCore(self.Data.getInputs(''))
        self.helpers[''].Init   = True
        return


    def doLCurveScan(self):      # Different taus for all the response matrices not implemented.
        self.helpers[''].doLCurveScan()
        self.taulist[''] = self.helpers[''].tau
        return


    def doTauScan(self):
        self.helpers[''].doTauScan()
        self.taulist[''] = self.helpers[''].tau


    def doScanPlots(self):
        self.helpers[''].plotspath = self.plotspath
        self.helpers[''].doScanPlots()
        self.taulist[''] = self.helpers[''].tau


    def doClosure(self, tau = None):
        if tau:
            self.helpers[''].DoUnfold(tau)


    def doNominalPlot(self, tau = None):
        if tau:
            self.helpers[''].tunfolder.DoUnfold(tau)
        data = self.helpers[''].tunfolder.GetOutput('forPlot')

        print 'Unfolded distribution integral', data.Integral()
        plot = bp.beautifulUnfPlot(self.var)
        data.SetMarkerStyle(r.kFullCircle)
        data.GetXaxis().SetNdivisions(510,True)
        plot.plotspath       = self.plotspath
        plot.doPreliminary   = vl.doPre
        plot.doSupplementary = False
        plot.displayedLumi   = vl.TotalLumi if self.year == "run2" else vl.LumiDict[int(self.year)]
        
        if not os.path.isfile('temp/{var}_/ClosureTest_{var}.root'.format(var = self.var)):
            raise RuntimeError('The rootfile with the generated information does not exist')
        tmptfile = r.TFile.Open('temp/{var}_/ClosureTest_{var}.root'.format(var = self.var))
        tru = deepcopy(tmptfile.Get('tW'))
        tru.SetLineWidth(2)
        tru.SetLineColor(bp.colorMap[0])
        if not os.path.isfile('temp/{var}_/ClosureTest_aMCatNLO_{var}.root'.format(var = self.var)):
            raise RuntimeError('The rootfile with the generated information from an aMCatNLO sample does not exist')
        tmptfile2 = r.TFile.Open('temp/{var}_/ClosureTest_aMCatNLO_{var}.root'.format(var = self.var))
        aMCatNLO = deepcopy(tmptfile2.Get('tW'))
        aMCatNLO.SetLineWidth(2)
        aMCatNLO.SetLineColor(bp.colorMap[1])
        aMCatNLO.SetLineStyle(2)
        for bin in range(1, tru.GetNbinsX()):
            tru.SetBinError(bin, 0.)
            aMCatNLO.SetBinError(bin, 0.)
        plot.addHisto(tru,      'L,same', 'tW Powheg DR + Pythia8',   'L', 'mc')
        plot.addHisto(aMCatNLO, 'L,same', 'tW aMC@NLO DR + Pythia8',  'L', 'mc')
        plot.addHisto(data,     'P,E,same{s}'.format(s = ",X0" if "equalbinsunf" in vl.varList[self.var] else ""), vl.labellegend, 'PE')
        plot.saveCanvas('TR')
        tmptfile.Close()
        tmptfile2.Close()
        return


    def doRegularizationComparison(self):
        self.prepareNominalHelper()
        if self.taulist[''] == 0:
            self.doLCurveScan()  # Different taus for all the response matrices not implemented.

        self.helpers[''].tunfolder.DoUnfold(self.taulist[''])
        regularized = self.helpers[''].tunfolder.GetOutput('forPlot_regu')
        self.helpers[''].tunfolder.DoUnfold(0)
        unregularized = self.helpers[''].tunfolder.GetOutput('forPlot_nuregu')
        
        regularized  .SetLineWidth(2)
        unregularized.SetLineWidth(2)
        regularized  .SetLineColor( bp.colorMap[0])
        unregularized.SetLineColor( bp.colorMap[1])
        
        for bin in range(1, regularized.GetNbinsX()+1):
            regularized.SetBinContent(bin, regularized.GetBinContent(bin)/unregularized.GetBinContent(bin))
        
        plot = bp.beautifulUnfPlot(self.var + '_asimov_regcomp' if (self.wearedoingasimov) else self.var + '_regcomp', self.var)
        plot.displayedLumi = vl.TotalLumi if self.year == "run2" else vl.LumiDict[int(self.year)]
#        regularized.Draw()
        regularized.GetXaxis().SetTitle(vl.varList[self.var]['xaxis'])
        regularized.GetYaxis().SetTitle('Reg./Unreg.')
        #regularized.GetYaxis().SetRangeUser(0, 1.1*regularized.GetMaximum())
        plot.addHisto(regularized, 'hist', 'regcomp', 'L')
#        plot.addHisto(unregularized,'hist,same','UnRegularized','L')
        plot.plotspath = self.plotspath
        plot.doPreliminary = vl.doPre
        plot.saveCanvas('BR', '', False)
        return


    def doAreaConstraintComparison(self):
        if self.doRegularisation and self.taulist[''] == 0:
            self.doLCurveScan() # Different taus for all the response matrices not implemented.

        tauval = 0
        if self.doRegularisation:
            tauval = self.taulist[''] # Different taus for all the response matrices not implemented.

        self.prepareNominalHelper()
        self.helpers[''].tunfolder.SetConstraint(r.TUnfold.kEConstraintArea)
        self.helpers[''].tunfolder.DoUnfold(tauval)
        withareaconst    = self.helpers[''].tunfolder.GetOutput('forPlot_area')
        self.helpers[''].tunfolder.SetConstraint(r.TUnfold.kEConstraintNone)
        self.helpers[''].tunfolder.DoUnfold(tauval)
        withoutareaconst = self.helpers[''].tunfolder.GetOutput('forPlot_noarea')
        self.helpers[''].tunfolder.SetConstraint(r.TUnfold.kEConstraintArea)
        
        withareaconst   .SetLineWidth(2)
        withoutareaconst.SetLineWidth(2)
        withareaconst   .SetLineColor(bp.colorMap[0])
        withoutareaconst.SetLineColor(bp.colorMap[1])
        
        for bin in range(1, withareaconst.GetNbinsX()+1):
            if withoutareaconst.GetBinContent(bin) != 0:
                withareaconst.SetBinContent(bin, withareaconst.GetBinContent(bin)/withoutareaconst.GetBinContent(bin))
            else:
                withoutareaconst.SetBinContent(bin, 0)
        
        plot = bp.beautifulUnfPlot(self.var + '_asimov_areacomp' if (self.wearedoingasimov) else self.var + '_areacomp', self.var)
        plot.displayedLumi = vl.TotalLumi if self.year == "run2" else vl.LumiDict[int(self.year)]
        withareaconst.GetXaxis().SetTitle(vl.varList[self.var]['xaxis'])
        withareaconst.GetYaxis().SetTitle('Area/No area')
        plot.addHisto(withareaconst, 'hist', 'areacomp', 'L')
        plot.plotspath     = self.plotspath
        plot.doPreliminary = vl.doPre
        plot.saveCanvas('BR', '', False)
        return


    def saveFiducialCrossSection(self, val, inc):
        thef = open(self.folderpath + "/fiducialxsec.txt", "w")
        out = "Fiducial xsec = %f.4 +- %f.4"%(val, inc)
        thef.write(out)
        thef.close()
        return


    def doUnfoldingForAllNuis(self):
        thelumi = vl.TotalLumi if self.year == "run2" else vl.LumiDict[int(self.year)]

        allHistos = {}
        self.prepareAllHelpers()
        tauval = 0
        if self.doRegularisation:
            print "> Performing regularisation..."
            if self.tau == 0:
                print '   - Tau value not yet calculated! Extracting it with the L-curve method...'
                self.doLCurveScan()

            tauval = self.taulist['']


        if verbose: print '\n> Unfolding nominal distribution'
        self.helpers[''].tunfolder.DoUnfold(tauval)
        allHistos[""] = deepcopy(self.helpers[''].tunfolder.GetOutput(self.var))

        if "Fiducial" in self.var:
            print "\n"
            #wr.warn("WARNING: you are calculating the fiducial cross section for the Asimov dataset. For unknown reasons, the obtention of the full covariance matrix after the unfolding gives an error. As a by-pass of this situation, the statistical uncertainty that the nominal results will carry will be ONLY the ones introduced as input, NOT the ones related with the response matrix nor the signal efficiency / fiducial region efficiency detection. TAKE THIS INTO ACCOUNT.")
            
            mat    = self.helpers[''].response.GetBinContent(1, 1)
            incmat = self.helpers[''].response.GetBinError(1, 1)
            
            ns    = self.helpers[''].unfInput.GetBinContent(1)
            incns = self.helpers[''].unfInput.GetBinError(1)
            
            nf    = self.helpers[''].bkg.GetBinContent(1)
            incnf = self.helpers[''].bkg.GetBinError(1)
            
            valor = ( ns - nf ) / mat
            inc   = incns/mat + incnf/mat + (ns - nf)/mat**2 * incmat
            
            print "ns", ns, "nf", nf, "mat", mat, "ns-nf", ns-nf
            
            print "valor nom.", valor/thelumi/1000, "inc. nom.", inc/thelumi/1000, "\n"

            self.saveFiducialCrossSection(valor/thelumi/1000, inc/thelumi/1000)

            #sys.exit()
            
            allHistos[""].SetBinContent(1, valor);
            allHistos[""].SetBinError(1, inc);
            covnom = r.TH2F("CovMat", "", 1,                                         vl.varList[self.var]['bins_particle'][0],
                                          vl.varList[self.var]['bins_particle'][-1], 1,
                                          vl.varList[self.var]['bins_particle'][0],  vl.varList[self.var]['bins_particle'][-1])
            covnom.SetBinContent(1, 1, inc)
        else:
            if verbose: print '> Obtaining covariance matrix of all the statistical components that take part here.'
            covnom = deepcopy(self.helpers[''].tunfolder.GetEmatrixTotal("CovMat"))
            for bin in range(1, allHistos[""].GetNbinsX() + 1):
                allHistos[""].SetBinError(bin, math.sqrt(covnom.GetBinContent(bin, bin)))
        
        self.nomOutput = deepcopy(allHistos[""].Clone("nomOutput"))
        self.nomMatrix = deepcopy(covnom.Clone("nomMatrix"))

        for nuis in self.sysList:
            if nuis == "": continue
            if verbose: print '> Unfolding distribution of {sys} systematic'.format(sys = nuis)
            self.helpers[nuis].tunfolder.DoUnfold(tauval)
            allHistos[nuis] = self.helpers[nuis].tunfolder.GetOutput(self.var + '_' + nuis)
            if "Fiducial" in self.var:
                mat    = self.helpers[nuis].response.GetBinContent(1, 1)
                incmat = self.helpers[nuis].response.GetBinError(1, 1)
                
                ns    = self.helpers[nuis].unfInput.GetBinContent(1)
                incns = self.helpers[nuis].unfInput.GetBinError(1)
                
                nf    = self.helpers[nuis].bkg.GetBinContent(1)
                incnf = self.helpers[nuis].bkg.GetBinError(1)
                
                valor = ( ns - nf ) / mat
                inc   = incns/mat + incnf/mat + (ns-nf)/mat**2 * incmat
                
                allHistos[nuis].SetBinContent(1, 1, valor)
                allHistos[nuis].SetBinError(  1, 1, inc)
            else:
                tmpcov = deepcopy(self.helpers[nuis].tunfolder.GetEmatrixTotal("tmpcov"))
                for bin in range(1, allHistos[nuis].GetNbinsX() + 1):
                    allHistos[nuis].SetBinError(bin, math.sqrt(tmpcov.GetBinContent(bin, bin)))
                del tmpcov
                
        
        scaleval = 1/thelumi/1000 if vl.doxsec else 1
        for key in allHistos:
            allHistos[key].Scale(scaleval)
        

        if not self.wearedoingasimov:
            #if not os.path.isfile('temp/{var}_/ClosureTest_{var}.root'.format(var = self.var)):
                #raise RuntimeError('The rootfile with the generated information does not exist')
            #tmptfile = r.TFile.Open('temp/{var}_/ClosureTest_{var}.root'.format(var = self.var))
            ##tmptfile2 = r.TFile.Open('temp/{var}_/ClosureTest_recobinning_{var}.root'.format(var = self.var))
            #tru = deepcopy(tmptfile.Get('tW'))
            ##tru2 = deepcopy(tmptfile2.Get('tW'))
            ##tru2.Scale(thelumi*1000)
            #for bin in range(1, allHistos['asimov'].GetNbinsX() + 1):
                ##print "\nasimov:", allHistos['asimov'].GetBinContent(bin)
                ##print "verdad:", tru.GetBinContent(bin)
                #allHistos['asimov'].SetBinError(bin,   abs(allHistos['asimov'].GetBinContent(bin) - tru.GetBinContent(bin)))
                ##allHistos['asimov'].SetBinContent(bin, nominal.GetBinContent(bin))
                ##print "errorin:", allHistos['asimov'].GetBinError(bin)
                ##print "nominal:", nominal.GetBinContent(bin)
                ##print "relativo", round(allHistos['asimov'].GetBinError(bin)/allHistos['asimov'].GetBinContent(bin)*100, 1)
                ##print "ratio:", allHistos['asimov'].GetBinContent(bin)/tru.GetBinContent(bin)
            ##for bin in range(1, tru2.GetNbinsX() + 1):
                ##print "verdad2:", tru2.GetBinContent(bin)
            ##tmptfile2.Close()
            #tmptfile.Close()
            #del tru
        
            savetfile = r.TFile(self.folderpath + "/particleOutput.root", "recreate")
            for key in allHistos:
                allHistos[key].Write()

            covnom.Scale(scaleval**2)
            covnom.Write()
            #covitwo = deepcopy(self.helpers[''].tunfolder.GetEmatrixInput("CovMatInput"))
            #covitwo.Scale(scaleval**2)
            #covitwo.Write()
            #covithree = deepcopy(self.helpers[''].tunfolder.GetEmatrixSysUncorr("CovMatResponse"))
            #covithree.Scale(scaleval**2)
            #covithree.Write()
            savetfile.Close()
        

        if not self.wearedoingasimov: nominal_withErrors = ep.propagateHistoAsym(allHistos, vl.doSym)
        else:                         nominal_withErrors = ep.propagateHistoAsym(allHistos, vl.doSym)
        plot                 = bp.beautifulUnfPlot(self.var + "_asimov"  if self.wearedoingasimov else self.var, self.var)
        plot.doRatio         = True
        plot.doFit           = self.usingFitInput
        plot.doPreliminary   = vl.doPre
        plot.doSupplementary = False
        plot.plotspath       = self.plotspath
        plot.displayedLumi   = vl.TotalLumi if self.year == "run2" else vl.LumiDict[int(self.year)]
        
        allHistos[""].SetMarkerStyle(r.kFullCircle)
        allHistos[""].SetLineColor(r.kBlack)
        allHistos[""].SetMarkerSize(1)
        nominal_withErrors[0].SetFillColorAlpha(r.kBlue, 0.35)
        nominal_withErrors[0].SetLineColor(0)
        nominal_withErrors[0].SetFillStyle(1001)
        
        if "yaxisuplimitunf" in vl.varList[self.var]:
            plot.yaxisuplimit = vl.varList[self.var]["yaxisuplimitunf"]

        if not self.wearedoingasimov:
            savetfile2 = r.TFile(self.folderpath + "/particleOutput.root", "update")
            nom0 = deepcopy(nominal_withErrors[0].Clone("nom0"))
            nom1 = deepcopy(nominal_withErrors[1].Clone("nom1"))
            nom0.Write()
            nom1.Write()
            savetfile2.Close()
            del nom0,nom1
        
        #############################
        print "\nLOS RESULTAOS - {uno} - {dos}".format(uno = "ASIMOV" if self.wearedoingasimov else "DATOS", dos = self.var)
        for bin in range(1, nominal_withErrors[0].GetNbinsX() + 1):
            print "Bin", bin, "(abs.): (", round(allHistos[""].GetBinContent(bin), 4), "+", round(nominal_withErrors[0].GetBinError(bin), 4), "-", round(nominal_withErrors[1].GetBinError(bin), 4), ") pb"
            print "Bin", bin, "(rel.): (", round(allHistos[""].GetBinContent(bin), 4), "+", round(nominal_withErrors[0].GetBinError(bin)/allHistos[""].GetBinContent(bin)*100, 4), "-", round(nominal_withErrors[1].GetBinError(bin)/allHistos[""].GetBinContent(bin)*100, 4), ") pb\n"
        print "\n"
        #############################
        
        #if not self.wearedoingasimov and varName != "Fiducial":
            #tex.saveLaTeXfromhisto(allHistos[""], varName, path = vl.tablespath, errhisto = nominal_withErrors[0], ty = "unfolded")

        if   "legpos_particle"   in vl.varList[self.var] and not self.wearedoingasimov:
            legloc = vl.varList[self.var]["legpos_particle"]
        elif "legpos_particleas" in vl.varList[self.var] and     self.wearedoingasimov:
            legloc = vl.varList[self.var]["legpos_particleas"]
        else:
            legloc = "TR"
        
        if not os.path.isfile(self.folderpath + '/particle.root'):
            raise RuntimeError('The rootfile with the generated information does not exist.')
        tmptfile = r.TFile.Open(self.folderpath + '/particle.root')
        tru = deepcopy(tmptfile.Get('x_tw').Clone('tru'))
        tmptfile.Close()
        #tru.Scale(0.001)
        #if self.year == "run2":
            #tru.Scale(1./3.)
        tru.Scale(scaleval)
        tru.SetMarkerSize(0)
        tru.SetLineWidth(2)
        tru.SetLineColor(bp.colorMap[0])
        #if self.var == "Fiducial":
            #print "JEJE:", tru.GetBinContent(1)

        #for iB in range(1, allHistos[""].GetNbinsX() + 1):
            #print allHistos[""].GetBinContent(iB), tru.GetBinContent(iB),  (allHistos[""].GetBinContent(iB) - tru.GetBinContent(iB)) / tru.GetBinContent(iB) * 100

        #sys.exit()
        ##print "tW DR", tru.GetBinContent(1)

        #if not os.path.isfile('temp/{var}_/ClosureTest_aMCatNLO_{var}.root'.format(var = self.var)):
            #raise RuntimeError('The rootfile with the generated information from an aMCatNLO sample does not exist.')
        #tmptfile2 = r.TFile.Open('temp/{var}_/ClosureTest_aMCatNLO_{var}.root'.format(var = self.var))
        #aMCatNLO = deepcopy(tmptfile2.Get('tW').Clone('aMCatNLO'))
        #tmptfile2.Close()
        #aMCatNLO.SetLineWidth(2)
        #aMCatNLO.SetLineColor(r.kAzure)
        #aMCatNLO.SetLineStyle(2)

        ##print "tW aMCatNLO DR", aMCatNLO.GetBinContent(1)

        #if not os.path.isfile('temp/{var}_/ClosureTest_DS_{var}.root'.format(var = self.var)):
            #raise RuntimeError('The rootfile with the generated information with the DS variation does not exist.')
        #tmptfile3 = r.TFile.Open('temp/{var}_/ClosureTest_DS_{var}.root'.format(var = self.var))
        #hDS = deepcopy(tmptfile3.Get('tW').Clone('hDS'))
        #tmptfile3.Close()
        #hDS.SetLineWidth(2)
        #hDS.SetLineColor(r.kGreen)

        ##print "tW DS", hDS.GetBinContent(1)

        plot.addHisto(nominal_withErrors, 'E2',     'Uncertainty',            'F', 'unc')
        plot.addHisto(tru,                'L,same', 'tW Powheg DR + Pythia8', 'L', 'mc')
        #plot.addHisto(hDS,                'L,same', 'tW Powheg DS + Pythia8',   'L', 'mc')
        #plot.addHisto(aMCatNLO,           'L,same', 'tW aMC@NLO DR + Pythia8',  'L', 'mc')
        if self.wearedoingasimov:
            plot.addHisto(allHistos[""], 'P,same{s}'.format(s = ",X0" if "equalbinsunf" in vl.varList[self.var] else ""), "Asimov dataset", 'PE{s}'.format(s = "L" if not "equalbinsunf" in vl.varList[self.var] else ""), 'data')
        else:
            plot.addHisto(allHistos[""], 'P,same{s}'.format(s = ",X0" if "equalbinsunf" in vl.varList[self.var] else ""), vl.labellegend,   'PE{s}'.format(s = "L" if not "equalbinsunf" in vl.varList[self.var] else ""), 'data')
        plot.saveCanvas(legloc)

        del plot

        plot2 = bp.beautifulUnfPlot(self.var + 'uncs_asimov' if self.wearedoingasimov else self.var + 'uncs', self.var)
        plot2.displayedLumi   = vl.TotalLumi if self.year == "run2" else vl.LumiDict[int(self.year)]
        plot2.doFit           = self.usingFitInput
        plot2.plotspath       = self.plotspath
        plot2.doPreliminary   = vl.doPre
        plot2.doSupplementary = False

        yaxismax_detectorunc = 2
        if "yaxismax_detectorunc" in vl.varList[self.var]: yaxismax_detectorunc = vl.varList[self.var]["yaxismax_detectorunc"]

        uncListorig, hincstat, hincsyst, hincmax = ep.drawTheRelUncPlot(nominal_withErrors, allHistos, plot2, yaxismax_detectorunc, doFit = self.usingFitInput, doSym = vl.doSym)
        
        if   "legpos_particleunc"   in vl.varList[self.var] and not self.wearedoingasimov:
            unclegpos = vl.varList[self.var]["legpos_particleunc"]
        elif "legpos_particleuncas" in vl.varList[self.var]:
            unclegpos = vl.varList[self.var]["legpos_particleuncas"]
        else:
            unclegpos = "TR"
        
        plot2.saveCanvas(unclegpos)
        del plot2
        return


    def getConditionNumber(self, nuis):
        return self.helpers[nuis].getConditionNumber()


    def doBottomLineTest(self):
        if not self.nomOutput:
            raise RuntimeError("FATAL: tried to execute the bottom-line test, but unfolding for the nominal values has not been done yet!")
        response = self.helpers[""].response
        smeared  = deepcopy(self.helpers[""].unfInput.Clone("smeared"))

        tmptfile = r.TFile.Open(self.folderpath + '/particle.root')
        tru = deepcopy(tmptfile.Get('x_tw').Clone('tru'))
        tmptfile.Close()

        for iB in range(1, smeared.GetNbinsX() + 1):
            theval = 0
            for jB in range(1, tru.GetNbinsX() + 1):
                theval += tru.GetBinContent(iB) * response.GetBinContent(jB, iB)
            smeared.SetBinContent(iB, theval)

        theinput = deepcopy(self.helpers[""].unfInput.Clone("theinput"))
        theinput.Add(self.helpers[""].bkg, -1)

        thepvalue_detector = smeared.Chi2Test(theinput,   'WWCHI2/NDF')
        thepvalue_particle = tru.Chi2Test(self.nomOutput, 'WWCHI2/NDF')

        pv1, es1 = gof.Chi2TestForMultivarNormal(smeared, smeared, theinput,       theinput)
        pv2, es2 = gof.Chi2TestForMultivarNormal(tru,     tru,     self.nomOutput, self.nomMatrix)


        thef = open(self.folderpath + "/bottomlinetest.txt", "w")
        out  = "p-value at detector-level = %.7f\n"%(thepvalue_detector)
        out += "p-value at particle-level = %.7f"%(thepvalue_particle)
        out += "p-value at detector-level = %.7f %.7f\n"%(pv1,es1)
        out += "p-value at particle-level = %.7f %.7f"%(pv2,es2)
        thef.write(out)
        thef.close()
        return


def UnfoldVariable(tsk):
    inpath, iY, iV, signalextr = tsk
    pathtovariablefolder = inpath + "/" + iY + "/" + iV
    outplotspath         = inpath + "/" + iY + "/particleplots"
    a = Unfolder(iV, pathtovariablefolder, iY, "detectorsignal_" + signalextr + ".root")

    if not os.path.isdir(outplotspath):
        os.system("mkdir -p " + outplotspath)

    a.plotspath        = outplotspath
    a.doSanityCheck    = True
    if "fit" in signalextr:
        a.usingFitInput    = True
    #a.doRegularisation = vl.varList[iV]["doReg"]  if "doReg"  in vl.varList[iV] else vl.doReg
    #a.doAreaConstraint = vl.varList[iV]["doArea"] if "doArea" in vl.varList[iV] else vl.doArea
    a.doRegularisation = False
    a.doAreaConstraint = False

    a.doUnfoldingForAllNuis() # Unfolding

    if "Fiducial" not in iV:
        #a.doScanPlots()                # L-Curve and curvature plots
        #a.doRegularizationComparison() # Comparison plot between regularisation and not
        #a.doAreaConstraintComparison() # Comparison plot between area constraint and not
        a.doBottomLineTest()           # Bottom-line test

    del a
    return




if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage = "python nanoAOD_checker.py [options]", description = "Checker tool for the outputs of nanoAOD production (NOT postprocessing)", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--inpath',    '-i', metavar = 'inpath',     dest = "inpath",     required = False, default = "./temp/differential/")
    parser.add_argument('--year',      '-y', metavar = 'year',       dest = "year",       required = False, default = "all")
    parser.add_argument('--variable',  '-v', metavar = 'variable',   dest = "variable",   required = False, default = "all")
    parser.add_argument('--extraArgs', '-e', metavar = 'extra',      dest = "extra",      required = False, default = "")
    parser.add_argument('--nthreads',  '-j', metavar = 'nthreads',   dest = "nthreads",   required = False, default = 0, type = int)
    parser.add_argument('--pretend',   '-p', action  = "store_true", dest = "pretend",    required = False, default = False)
    parser.add_argument('--signalextr','-s', metavar = "signalextr", dest = "signalextr", required = False, default = "bs")

    args       = parser.parse_args()
    year       = args.year
    extra      = args.extra
    nthreads   = args.nthreads
    pretend    = args.pretend
    inpath     = args.inpath
    variable   = args.variable
    signalextr = args.signalextr

    vl.SetUpWarnings()

    tasks = []
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

    if year.lower() != "all" and year in presentyears:
        theyears = [ year ]
    elif year.lower() != "all":
        raise RuntimeError("FATAL: the year requested is not in the provided input folder.")

    for iY in theyears:
        thevars = next(os.walk(inpath + "/" + iY))[1]

        if variable.lower() != "all" and variable in thevars:
            thevars = [ variable ]
        elif variable.lower() != "all":
            raise RuntimeError("FATAL: the variable requested is not in the provided input folder.")

        for iV in thevars:
            if "plots" in iV: continue
            if "Fiducial" in iV: continue
            #if "Lep1_Pt" not in iV: continue
            #if "Lep1Lep2_DPhi" not in iV: continue
            #if iY not in ["2016", "2017"]: continue
            tasks.append( (inpath, iY, iV, signalextr) )


    #tasks = [ ("Lep1_Pt", inpath + "/" + "run2" + "/" + "Lep1_Pt", inpath + "/run2/particleplots") ]

    print "\n> Beginning unfolding...\n"

    if nthreads > 1:
        pool = Pool(nthreads)
        pool.map(UnfoldVariable, tasks)
        pool.close()
        pool.join()
    else:
        for tsk in tasks:
            UnfoldVariable(tsk)
