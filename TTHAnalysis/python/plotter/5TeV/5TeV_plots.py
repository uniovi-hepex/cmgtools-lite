#!/usr/bin/env python
import sys
import re
import os

ODIR=sys.argv[1]
dowhat=sys.argv[2]

#lumi = 0.296 #/pb
lumi = 0.30432  #/pb

submit = '{command}' 
#dowhat = "plots" 
#dowhat = "dumps" 
#dowhat = "yields" 
#dowhat = "ntuple" # syntax: python ttH-multilepton/ttH_plots.py no 2lss_SR_extr outfile_{cname}.root --sP var1,var2,...

P0="/eos/cms/store/group/phys_muon/folguera/5TeV_Mar23/"
nCores = 12

TREESALL      = " --FMCs {P}/0_jmeUnc_v1 --FDs {P}/0_jmeUncData_v1 --FMCs {P}/0_weights_v1 --Fs {P}/1_recleaner_v2 --Fs {P}/2_eventVars_v4 --FMCs {P}/3_leptonSF_v2/"
TREESONLYSKIM = "-P "+P0

def base(selection):
    THETREES = TREESALL

    CORE=' '.join([THETREES,TREESONLYSKIM])
    CORE+=" -f -j %d -l %s -L 5TeV/functions5TeV.cc --tree NanoAOD --mcc 5TeV/lepchoice-FO.txt  --split-factor=-1 "%(nCores, lumi)
    RATIO= " --maxRatioRange 0.6  1.99 --ratioYNDiv 505 "
    RATIO2=" --showRatio --attachRatioPanel --fixRatioRange "
    LEGEND=" --legendColumns 3 --legendWidth 0.35 "
    LEGEND2=" --legendFontSize 0.042 "
    SPAM=" --noCms --topSpamSize 1.1 --lspam '#scale[1.1]{#bf{CMS}} #scale[0.9]{#it{Preliminary}}' --rspam '%(lumi) (5.02 TeV)' "
    if dowhat == "plots": CORE+=RATIO+RATIO2+LEGEND+LEGEND2+SPAM+"  --showMCError --rebin 4 "

    if selection=='wz3l':
        GO="%s 5TeV/mca-wz-3l-mc.txt 5TeV/wz_3l.txt "%CORE
        GO="%s -W '(PrefireWeight*puWeight*leptonSF_3l_sr)'"%GO
        if dowhat in ["plots","ntuple"]: GO+=" 5TeV/wz_2lss_3l_plots.txt --xP '^2l_.*' "
        if dowhat == "plots": GO=GO.replace(LEGEND, " --legendColumns 3 --legendWidth 0.42 ")
        GO += " --binname 3l "
    elif selection=='wz2lss':
        GO="%s 5TeV/mca-wz-2lss-mc.txt 5TeV/wz_2lss.txt "%CORE
        GO="%s -W 'PrefireWeight*puWeight*leptonSF_2l_sr'"%GO
        if dowhat in ["plots","ntuple"]: GO+=" 5TeV/wz_2lss_3l_plots.txt --xP '^lep(3|W|Z1|Z2)_.*' --xP '^3l_.*' " 
        if dowhat == "plots": GO=GO.replace(LEGEND, " --legendColumns 3 --legendWidth 0.42 ")
        GO += " --binname 2lss "
    elif selection=='zz4l':
        GO="%s 5TeV/mca-zz-4l-mc.txt 5TeV/zz_4l.txt "%CORE
        GO="%s -W 'PrefireWeight*puWeight'"%GO
        if dowhat in ["plots","ntuple"]: GO+=" 5TeV/wz_2lss_3l_plots.txt --xP '^lep(W|Z1|Z2)_.*' --xP '^3l_.*' --xP '^2l_.*' " 
        if dowhat == "plots": GO=GO.replace(LEGEND, " --legendColumns 3 --legendWidth 0.42 ")
        GO += " --binname 4l "        
    elif selection=='zz2l2nu':
        GO="%s 5TeV/mca-zz-2l2nu-mc.txt 5TeV/zz_2l2nu.txt "%CORE
        GO="%s -W 'PrefireWeight*puWeight*leptonSF_2l_sr'"%GO
        if dowhat in ["plots","ntuple"]: GO+=" 5TeV/wz_2lss_3l_plots.txt --xP '^lep(W|Z1|Z2)_.*' --xP '^3l_.*' " 
        if dowhat == "plots": GO=GO.replace(LEGEND, " --legendColumns 3 --legendWidth 0.42 ")
        GO += " --binname 2l2nu "        
    elif selection=='ww':
        GO="%s 5TeV/mca-ww-mc.txt 5TeV/ww_dilepton.txt "%CORE
        GO="%s -W 'PrefireWeight*puWeight*leptonSF_2l_sr'"%GO
        if dowhat in ["plots","ntuple"]: GO+=" 5TeV/ww_plots.txt  " 
        if dowhat == "plots": GO=GO.replace(LEGEND, " --legendColumns 3 --legendWidth 0.42 ")
        GO += " --binname ww "
    elif selection=='ttbar':
        GO="%s 5TeV/mca-ttbar-mc.txt 5TeV/ttbar_dilepton.txt "%CORE
        GO="%s -W 'PrefireWeight*puWeight*leptonSF_2l_sr'"%GO
        if dowhat in ["plots","ntuple"]: GO+=" 5TeV/ttbar_plots.txt  " 
        if dowhat == "plots": GO=GO.replace(LEGEND, " --legendColumns 3 --legendWidth 0.42 ")
        GO=GO.replace("--Fs {P}/2_eventVars_v2"," ")
        GO += " --binname ttbar "        
    else:
        raise RuntimeError, 'Unknown selection'

    return GO

def promptsub(x):
    procs = [ '' ]
    if dowhat == "cards": procs += ['_FRe_norm_Up','_FRe_norm_Dn','_FRe_pt_Up','_FRe_pt_Dn','_FRe_be_Up','_FRe_be_Dn','_FRm_norm_Up','_FRm_norm_Dn','_FRm_pt_Up','_FRm_pt_Dn','_FRm_be_Up','_FRm_be_Dn']
    return x + ' '.join(["--plotgroup data_fakes%s+='.*sub%s'"%(x,x) for x in procs])+" --neglist '.*sub.*' "
def procs(GO,mylist):
    return GO+' '+" ".join([ '-p %s'%l for l in mylist ])
def sigprocs(GO,mylist):
    return procs(GO,mylist)+' --showIndivSigs --noStackSig'
def runIt(GO,name,plots=[],noplots=[]):
    print ''
    if dowhat == "plots":  
        if not ('forcePlotChoice' in sys.argv[4:]): print submit.format(command=' '.join(['python mcPlots.py',"--pdir %s/%s"%(ODIR,name),GO,' '.join(['--sP %r'%p for p in plots]),' '.join(['--xP %r'%p for p in noplots]),' '.join(sys.argv[4:])]))
        else: print 'python mcPlots.py',"--pdir %s/%s"%(ODIR,name),GO,' '.join([x for x in sys.argv[4:] if x!='forcePlotChoice'])
    elif dowhat == "yields": print 'echo %s; python mcAnalysis.py'%name,GO,' '.join(sys.argv[4:])
    elif dowhat == "dumps":  print 'echo %s; python mcDump.py'%name,GO,' '.join(sys.argv[4:])
    elif dowhat == "ntuple": print 'echo %s; python mcNtuple.py'%name,GO,' '.join(sys.argv[4:])


def add(GO,opt):
    return '%s %s'%(GO,opt)
def setwide(x):
    x2 = add(x,'--wide')
    x2 = x2.replace('--legendWidth 0.35','--legendWidth 0.20')
    return x2

if __name__ == '__main__':

    torun = sys.argv[3]

    if 'wz_3l_' in torun and not('cr') in torun:
        torun = torun.replace("wz_","wz/")
        x = base('wz3l')
        if '_norebin' in torun: x = x.replace('--rebin 4','')
        if '_appl' in torun: x = add(x,'-I ^TT ')
        if '_br' in torun: 
            x = add(x,'-U ^Zmass ')
            x = x.replace('leptonSF_3l_sr','leptonSF_3l_br')
        if '_relax' in torun: x = add(x,'-X ^TT ')
        if '_unc' in torun: x = add(x, '--unc 5TeV/systsUnc.txt')
        if '_noskim' in torun: x = x.replace('5TeV_Mar23','5TeV_Apr14_noSkim') 
        
        if '_fid' in torun: 
            x = x.replace('mca-wz-3l-mc.txt','mca-includes/mca-wz-3l-sig-uncertainties.txt')
            x = x.replace('wz_3l.txt','wz_3l_fiducial.txt')
            x = x.replace('5TeV_Mar23','5TeV_Apr14_noSkim') 
            x = x.replace('-l %s' %lumi, '-l 1')
            x = add(x,'--sP .*tot_weight.* --unweight-forced') 
        
        if '_data' in torun: 
            x = x.replace('mca-wz-3l-mc.txt','mca-wz-3l-mcdata.txt')
            if '_frmc'  in torun: 
                x = promptsub(x)
                x = x.replace('mcdata.txt','mcdata-frmc.txt')
##            if '_frdata' in torun: 
##                x = promptsub(x)
##                x = x.replace('mcdata.txt','mcdata-frdata.txt')
        
        if '_closure' in torun: 
            x = x.replace('mca-wz-3l-mc.txt','mca-3l-mc-closuretest.txt')
            x = add(x,"--AP --plotmode nostack --sP met --sP lep1_pt --sP lep2_pt --sP nJet25")
            if '_dyjets' in torun: 
                x = add(x,"-p DYJETS_FR_TT -p DYJETS_fake --ratioDen DYJETS_FR_TT --ratioNums DYJETS_fake,DYJETS_FR_TT --errors ")                
                torun = torun.replace("_dyjets","/dyjets")
            else : 
                x = add(x,"-p TT_FR_TT -p TT_fake --ratioDen TT_FR_TT --ratioNums TT_fake,TT_FR_TT --errors ")
            x = x.replace('--showMCError','')
            x = x.replace('--legendWidth 0.42','--legendWidth 0.60')
            x = x.replace('--maxRatioRange 0.6  1.99','--maxRatioRange 0.001 2.99')
            if '_norm' in torun:
                x = x.replace("--plotmode nostack","--plotmode norm")
                torun = torun.replace("_norm","/norm")                                
                if 'dyjets' in torun: 
                    x = x.replace("--ratioNums DYJETS_fake,DYJETS_FR_TT","--ratioNums DYJETS_fake")
                else :
                    x = x.replace("--ratioNums TT_fake,TT_FR_TT","--ratioNums TT_fake")
                x = add(x,"--fitRatio 1")

            if '_mufake' in torun: 
                x = add(x,"-A alwaystrue mufake '(abs(LepGood1_pdgId)==13 && LepGood1_mcMatchId==0) || (abs(LepGood2_pdgId)==13 && LepGood2_mcMatchId==0) || (abs(LepGood3_pdgId)==13 && LepGood3_mcMatchId==0)'")
                torun = torun.replace("_mufake","/mufake")
            if '_elfake' in torun: 
                x = add(x,"-A alwaystrue elfake '(abs(LepGood1_pdgId)==11 && (LepGood1_mcMatchId==0 && LepGood1_mcPromptGamma==0)) || (abs(LepGood2_pdgId)==11 && (LepGood2_mcMatchId==0 && LepGood2_mcPromptGamma==0)) || (abs(LepGood3_pdgId)==11 && (LepGood3_mcMatchId==0 && LepGood3_mcPromptGamma==0))'")
                torun = torun.replace("_elfake","/elfake")
            
        runIt(x,'%s'%torun)
    elif 'wz_2lss' in torun and not('cr') in torun:
        torun = torun.replace("wz_","wz/")
        x = base('wz2lss')
        if '_norebin' in torun: x = x.replace('--rebin 4','')
        if '_appl' in torun: x = add(x,'-I ^TT ')
        if '_relax' in torun: x = add(x,'-X ^TT ')
        if '_unc' in torun: x = add(x, '--unc 5TeV/systsUnc.txt')
        if '_noskim' in torun: x = x.replace('5TeV_Mar23','5TeV_Apr14_noSkim') 
        if '_fid' in torun: 
            x = x.replace('mca-wz-2lss-mc.txt','mca-includes/mca-wz-2lss-sig-uncertainties.txt')
            x = x.replace('wz_2lss.txt','wz_2lss_fiducial.txt')
            x = x.replace('5TeV_Mar23','5TeV_Apr14_noSkim') 
            x = add(x,'--sP .*tot_weight.* --unweight-forced') 
        if '_data' in torun: 
            x = x.replace('mca-wz-2lss-mc.txt','mca-wz-2lss-mcdata.txt')
            if '_frmc' in torun: 
                x = promptsub(x)
                x = x.replace('mca-wz-2lss-mcdata.txt','mca-wz-2lss-mcdata-frmc.txt')                
            if '_frdata' in torun: 
                x = promptsub(x)
                x = x.replace('mca-wz-2lss-mcdata.txt','mca-wz-2lss-mcdata-frdata.txt')

        if '_closure' in torun: 
            x = x.replace('mca-wz-2lss-mc.txt','mca-2l-mc-closuretest.txt')
            x = add(x,"--AP --plotmode nostack --sP met --sP lep1_pt --sP lep2_pt --sP nJet25")
            if '_wjets' in torun: 
                x = add(x,"-p WJETS_FR_TT -p WJETS_fake --ratioDen WJETS_FR_TT --ratioNums WJETS_fake,WJETS_FR_TT --errors ")                
                torun = torun.replace("_wjets","/wjets")
            else: 
                x = add(x,"-p TT_FR_TT -p TT_fake --ratioDen TT_FR_TT --ratioNums TT_fake,TT_FR_TT --errors ")
            x = x.replace('--showMCError','')
            x = x.replace('--legendWidth 0.42','--legendWidth 0.60')
            x = x.replace('--maxRatioRange 0.6  1.99','--maxRatioRange 0.001 2.99')
            if '_norm' in torun:
                torun = torun.replace("_norm","/norm")
                x = x.replace("--plotmode nostack","--plotmode norm")
                if 'wjets' in torun: 
                    x = x.replace("--ratioNums WJETS_fake,WJETS_FR_TT","--ratioNums WJETS_fake")                    
                else: 
                    x = x.replace("--ratioNums TT_fake,TT_FR_TT","--ratioNums TT_fake")
                x = add(x,"--fitRatio 1")

            if '_mufake' in torun: 
                x = add(x,"-A alwaystrue mufake '(abs(LepGood1_pdgId)==13 && LepGood1_mcMatchId==0) || (abs(LepGood2_pdgId)==13 && LepGood2_mcMatchId==0)'")
                torun = torun.replace("_mufake","/mufake")
            if '_elfake' in torun: 
                x = add(x,"-A alwaystrue elfake '(abs(LepGood1_pdgId)==11 && (LepGood1_mcMatchId==0 && LepGood1_mcPromptGamma==0)) || (abs(LepGood2_pdgId)==11 && (LepGood2_mcMatchId==0 && LepGood2_mcPromptGamma==0))'")
                torun = torun.replace("_elfake","/elfake")
                
        runIt(x,'%s'%torun)
    elif 'wz_convscr' in torun: 
        x = base('wz3l')
        x = add(x,'-I ^Zmass -X ^m3l -X ^lWpt20 -E ^cr_convs -X ^TT ')
        if '_norebin' in torun: x = x.replace('--rebin 4','')
        if '_data' in torun: x = x.replace('mca-wz-3l-mc.txt','mca-wz-3l-mcdata.txt')
        runIt(x,'%s'%torun)
    elif 'zz_4l' in torun: 
        x = base('zz4l')
        torun = torun.replace("zz_","zz/")
        if '_norebin' in torun: x = x.replace('--rebin 4','')        
        if '_data' in torun: x = x.replace('mca-zz-4l-mc.txt','mca-zz-4l-mcdata.txt')
        runIt(x,'%s'%torun)        
    elif 'zz_2l2nu' in torun: 
        x = base('zz2l2nu')
        if '_norebin' in torun: x = x.replace('--rebin 4','')        
        if '_data' in torun: 
            x = x.replace('mca-zz-2l2nu-mc.txt','mca-zz-2l2nu-mcdata.txt')
            if '_frmc' in torun: 
                x = promptsub(x)
                x = x.replace('mcdata','mcdata-frmc')           
        runIt(x,'%s'%torun)        
    elif 'wz_dycr' in torun: 
        x = base('wz3l')
        x = add(x,'-X ^TT -X ^m3l -X ^lWpt20  -E ^cr_mTlW30')
        if '_norebin' in torun: x = x.replace('--rebin 4','')        
        if '_data' in torun: x = x.replace('mca-wz-3l-mc.txt','mca-wz-3l-mcdata.txt')
        runIt(x,'%s'%torun)
    elif 'wz_wjetscr' in torun:
        x = base('wz2lss')
        x = add(x,'-I ^TT -E ^crwjets')
        if '_norebin' in torun: x = x.replace('--rebin 4','')        
        if '_data' in torun: x = x.replace('mca-wz-2lss-mc.txt','mca-wz-2lss-mcdata.txt')
        runIt(x,'%s'%torun)
    elif 'ww_2l' in torun:
        torun = torun.replace("ww_","ww/")
        x = base('ww')
        if '_norebin' in torun: x = x.replace('--rebin 4','')
        if '_appl' in torun: x = add(x,'-I ^TT ')
        if '_relax' in torun: x = add(x,'-X ^TT ')
        if '_sscr' in torun: x=add(x,'-I ^os ')
        if '_ttcr' in torun: x=add(x,'-I ^0jet ')
        if '_dycr' in torun: x=add(x,'-I ^em ')
        if '_unc' in torun: x = add(x, '--unc 5TeV/systsUnc.txt ')
        if '_noskim' in torun: x = x.replace('5TeV_Mar23','5TeV_Apr14_noSkim') 
        if '_fid' in torun: 
            x = x.replace('mca-ww-mc.txt','mca-includes/mca-ww-sig-uncertainties.txt')
            x = x.replace('ww_dilepton.txt','ww_dilepton_fiducial.txt')
            x = x.replace('--FMCs {P}/3_leptonSF_v2/', '')
            x = x.replace('5TeV_Mar23','5TeV_Apr14_noSkim') 
            x = add(x,'--sP .*tot_weight.* -u -p WW') 
        if '_data' in torun: 
            x = x.replace('mca-ww-mc.txt','mca-ww-mcdata.txt')
            if '_frmc' in torun: 
                x = promptsub(x)
                x = x.replace('mca-ww-mcdata.txt','mca-ww-mcdata-frmc.txt')
            if '_frdata' in torun: 
                x = promptsub(x)
                x = x.replace('mca-ww-mcdata.txt','mca-ww-mcdata-frdata.txt')

        if '_closure' in torun: 
            x = x.replace('mca-ww-mc.txt','mca-2l-mc-closuretest.txt')
            x = add(x,"--AP --plotmode nostack --sP met --sP lep1_pt --sP lep2_pt --sP nJet25")
            if '_wjets' in torun: 
                x = add(x,"-p WJETS_FR_TT -p WJETS_fake --ratioDen WJETS_FR_TT --ratioNums WJETS_fake,WJETS_FR_TT --errors ")                
                torun = torun.replace("_wjets","/wjets")
            else: 
                x = add(x,"-p TT_FR_TT -p TT_fake --ratioDen TT_FR_TT --ratioNums TT_fake,TT_FR_TT --errors ")

            x = x.replace('--showMCError','')
            x = x.replace('--legendWidth 0.42','--legendWidth 0.60')
            x = x.replace('--maxRatioRange 0.6  1.99','--maxRatioRange 0.001 2.99')
            if '_norm' in torun:
                torun = torun.replace("_norm","/norm")                
                x = x.replace("--plotmode nostack","--plotmode norm")
                if "wjets" in torun: 
                    x = x.replace("--ratioNums WJETS_fake,WJETS_FR_TT","--ratioNums WJETS_fake")
                else: 
                    x = x.replace("--ratioNums TT_fake,TT_FR_TT","--ratioNums TT_fake")
                
                x = add(x,"--fitRatio 1")
            if '_mufake' in torun: 
                x = add(x,"-A alwaystrue mufake '(abs(LepGood1_pdgId)==13 && LepGood1_mcMatchId==0) || (abs(LepGood2_pdgId)==13 && LepGood2_mcMatchId==0)'")
                torun = torun.replace("_mufake","/mufake")
            if '_elfake' in torun: 
                x = add(x,"-A alwaystrue elfake '(abs(LepGood1_pdgId)==11 && (LepGood1_mcMatchId==0 && LepGood1_mcPromptGamma==0)) || (abs(LepGood2_pdgId)==11 && (LepGood2_mcMatchId==0 && LepGood2_mcPromptGamma==0))'")
                torun = torun.replace("_elfake","/elfake")

        runIt(x,'%s'%torun)
    elif 'ttbar' in torun:
        x = base('ttbar')
        if '_norebin' in torun: x = x.replace('--rebin 4','')
        if '_appl' in torun: x = add(x,'-I ^TT ')
        if '_relax' in torun: x = add(x,'-X ^TT ')
        if '_ss' in torun: x = add(x, '-I ^os')
        if '_dycr' in torun: 
            x=add(x, '-E ^sf -X ^ZVeto -E ^onZ') 
            if '_nojet' in torun: x=add(x, ' -X ^2jets') 
            if '_nomet' in torun: x=add(x, ' -X ^MET') 
        if '_tight' in torun: 
            x=x.replace('1_recleaner','1_recleanerTight')
        if '_em' in torun: 
            x = add(x, '-E ^em')
            torun = torun.replace('_em','/em')
        if '_mm' in torun: 
            x = add(x, '-E ^mm')
            torun = torun.replace('_mm','/mm')            
        if '_ee' in torun: 
            x = add(x, '-E ^ee')
            torun = torun.replace('_ee','/ee')                    
        if '_noskim' in torun: x = x.replace('5TeV_Mar23','5TeV_Apr14_noSkim') 
        if '_fid' in torun: 
            x = x.replace('mca-ttbar-mc.txt','mca-includes/mca-ttbar-sig-uncertainties.txt')
            x = x.replace('ttbar_dilepton.txt','ttbar_dilepton_fiducial.txt')
            x = x.replace('--FMCs {P}/3_leptonSF_v2/', '')
            x = x.replace('5TeV_Mar23','5TeV_Apr14_noSkim') 
            x = add(x,'--sP .*tot_weight.* -u')         
        if '_data' in torun: x = x.replace('mca-ttbar-mc.txt','mca-ttbar-mcdata.txt')
        runIt(x,'%s'%torun)

        
        



       
        
