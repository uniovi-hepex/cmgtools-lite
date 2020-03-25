#!/usr/bin/env python
import sys
import re
import os

ODIR=sys.argv[1]
YEAR=sys.argv[2]

lumi = 0.296

submit = '{command}' 
dowhat = "plots" 
#dowhat = "dumps" 
#dowhat = "yields" 
#dowhat = "ntuple" # syntax: python ttH-multilepton/ttH_plots.py no 2lss_SR_extr outfile_{cname}.root --sP var1,var2,...

P0="/eos/cms/store/group/phys_muon/folguera/5TeV_Mar23/"
nCores = 12
if 'fanae' in os.environ['HOSTNAME']:
    nCores = 32
    submit = 'sbatch -c %d -p short  --wrap "{command}"'%nCores
    P0     = "/pool/ciencias/HeppyTrees/EdgeZ/TTH/"
if 'gae' in os.environ['HOSTNAME']: 
    P0     = "/pool/ciencias/HeppyTrees/EdgeZ/TTH/"

TREESALL      = " --FMCs {P}/0_jmeUnc_v1 --Fs {P}/1_recleaner_v1 --Fs {P}/2_eventVars_v2 "
TREESONLYSKIM = "-P "+P0

def base(selection):
    THETREES = TREESALL

    CORE=' '.join([THETREES,TREESONLYSKIM])
    CORE+=" -f -j %d -l %s -L WZ-5TeV/functionsWZ.cc --tree NanoAOD --mcc WZ-5TeV/lepchoice-WZ-FO.txt  --split-factor=-1 %s"%(nCores, lumi)
    RATIO= " --maxRatioRange 0.6  1.99 --ratioYNDiv 505 "
    RATIO2=" --showRatio --attachRatioPanel --fixRatioRange "
    LEGEND=" --legendColumns 3 --legendWidth 0.35 "
    LEGEND2=" --legendFontSize 0.042 "
    SPAM=" --noCms --topSpamSize 1.1 --lspam '#scale[1.1]{#bf{CMS}} #scale[0.9]{#it{Preliminary}}' "
    if dowhat == "plots": CORE+=RATIO+RATIO2+LEGEND+LEGEND2+SPAM+"  --showMCError --rebin 4 "

    if selection=='3l':
        GO="%s WZ-5TeV/mca-3l-mc.txt WZ-5TeV/3l.txt "%CORE
#        GO="%s -W 'L1PreFiringWeight_Nom*puWeight*btagSF_shape*leptonSF_3l*triggerSF_ttH(LepGood1_pdgId, LepGood1_conePt, LepGood2_pdgId, LepGood2_conePt, 3, year)'"%GO
        if dowhat in ["plots","ntuple"]: GO+=" WZ-5TeV/2lss_3l_plots.txt "
        if dowhat == "plots": GO=GO.replace(LEGEND, " --legendColumns 3 --legendWidth 0.42 ")
        GO += " --binname 3l "
    else:
        raise RuntimeError, 'Unknown selection'

    return GO

def promptsub(x):
    procs = [ '' ]
    if dowhat == "cards": procs += ['_FRe_norm_Up','_FRe_norm_Dn','_FRe_pt_Up','_FRe_pt_Dn','_FRe_be_Up','_FRe_be_Dn','_FRm_norm_Up','_FRm_norm_Dn','_FRm_pt_Up','_FRm_pt_Dn','_FRm_be_Up','_FRm_be_Dn']
    return x + ' '.join(["--plotgroup data_fakes%s+='.*_promptsub%s'"%(x,x) for x in procs])+" --neglist '.*_promptsub.*' "
def procs(GO,mylist):
    return GO+' '+" ".join([ '-p %s'%l for l in mylist ])
def sigprocs(GO,mylist):
    return procs(GO,mylist)+' --showIndivSigs --noStackSig'
def runIt(GO,name,plots=[],noplots=[]):
    if '_74vs76' in name: GO = prep74vs76(GO)
    if dowhat == "plots":  
        if not ('forcePlotChoice' in sys.argv[4:]): print submit.format(command=' '.join(['python mcPlots.py',"--pdir %s/%s/%s"%(ODIR,YEAR,name),GO,' '.join(['--sP %r'%p for p in plots]),' '.join(['--xP %r'%p for p in noplots]),' '.join(sys.argv[4:])]))
        else: print 'python mcPlots.py',"--pdir %s/%s/%s"%(ODIR,YEAR,name),GO,' '.join([x for x in sys.argv[4:] if x!='forcePlotChoice'])
    elif dowhat == "yields": print 'echo %s; python mcAnalysis.py'%name,GO,' '.join(sys.argv[4:])
    elif dowhat == "dumps":  print 'echo %s; python mcDump.py'%name,GO,' '.join(sys.argv[4:])
    elif dowhat == "ntuple": print 'echo %s; python mcNtuple.py'%name,GO,' '.join(sys.argv[4:])
def add(GO,opt):
    return '%s %s'%(GO,opt)
def setwide(x):
    x2 = add(x,'--wide')
    x2 = x2.replace('--legendWidth 0.35','--legendWidth 0.20')
    return x2
def fulltrees(x):
    return x.replace(TREESONLYSKIM,TREESONLYFULL)

allow_unblinding = True

if __name__ == '__main__':

    torun = sys.argv[3]

    if (not allow_unblinding) and '_data' in torun and (not any([re.match(x.strip()+'$',torun) for x in ['.*_appl.*','cr_.*','3l.*_Zpeak.*']])): raise RuntimeError, 'You are trying to unblind!'

    if '3l_' in torun and not('cr') in torun:
        x = base('3l')
        if '_norebin' in torun: x = x.replace('--rebin 4','')
        if '_appl' in torun: x = add(x,'-I ^TT ')
        if '_br' in torun: x = add(x,'-U ^Zmass ')
        if '_relax' in torun: x = add(x,'-X ^TT ')
        if '_data' in torun: x = x.replace('mca-3l-mc.txt','mca-3l-mcdata.txt')

        runIt(x,'%s'%torun)


       
        
