import os, sys
nCores=32
submit = '{command}' 
#submit = '''sbatch -c %d -p batch  --wrap '{command}' '''%nCores

ORIGIN="/eos/cms/store/group/phys_muon/folguera/5TeV_Mar23/"

if len(sys.argv) < 3: 
    print 'Sytaxis is %s [outputdir] [region] [other]'%sys.argv[0]
    raise RuntimeError 
OUTNAME=sys.argv[1]
REGION=sys.argv[2]
OTHER=sys.argv[3:] if len(sys.argv) > 3 else ''

LUMI=".30432"

OPTIONS=" --tree NanoAOD --s2v -j {J} -l {LUMI} -f  --split-factor=-1 ".format(LUMI=LUMI,J=nCores)
os.system("test -d cards/{OUTNAME} || mkdir -p cards/{OUTNAME}".format(OUTNAME=OUTNAME))
OPTIONS="{OPTIONS} --od cards/{OUTNAME} ".format(OPTIONS=OPTIONS, OUTNAME=OUTNAME)

T2L="-P {ORIGIN} --FMCs {{P}}/0_jmeUnc_v1  --FDs {{P}}/0_jmeUncData_v1 --FMCs {{P}}/0_weights_v1 --Fs {{P}}/1_recleaner_v2 --Fs {{P}}/2_eventVars_v4 --FMCs {{P}}/3_leptonSF_v2/".format(ORIGIN=ORIGIN)
T3L=T2L
T4L=T2L

SYSTS="--unc 5TeV/systsUnc.txt --amc "
MCAOPTION=""
ASIMOV="--asimov signal"
#ASIMOV="" 
SCRIPT= "makeShapeCardsNew.py"
PROMPTSUB="--plotgroup data_fakes+=.*sub"

if 'unblind' in OTHER:
    ASIMOV=""

print "We are using the asimov dataset"
OPTIONS="{OPTIONS} -L 5TeV/functions5TeV.cc --mcc 5TeV/lepchoice-FO.txt  {PROMPTSUB} --neg  --threshold 0.01 {ASIMOV} ".format(OPTIONS=OPTIONS,PROMPTSUB=PROMPTSUB,ASIMOV=ASIMOV) # neg necessary for subsequent rebin #  
OPTIONS_3L="{OPTIONS} -L 5TeV/functions5TeV.cc --mcc 5TeV/lepchoice-FO.txt --neg  --threshold 0.01 {ASIMOV} ".format(OPTIONS=OPTIONS,ASIMOV=ASIMOV) # neg necessary for subsequent rebin #  
CATPOSTFIX="--categorize 'getChannel2l(LepGood1_pdgId,LepGood2_pdgId)' [0.5,1.5,2.5,3.5] ee,em,mm"

ONEBIN="1 1,0.5,1.5"
MLL='''"mZ1" 20,70,110 '''

MCASUFFIX="mcdata-frmc"

DOFILE = ""


if REGION == "wz_2lss":
    OPT_2L='{T2L} {OPTIONS} -W "PrefireWeight*puWeight*leptonSF_2l_sr"'.format(T2L=T2L, OPTIONS=OPTIONS)
    TORUN='''python {SCRIPT} {DOFILE} 5TeV/mca-wz-2lss-{MCASUFFIX}.txt 5TeV/wz_2lss.txt {FUNCTION_SVA_2L} {SYSTS} {OPT_2L} --binname wz_2lss;'''.format(SCRIPT=SCRIPT, DOFILE=DOFILE, MCASUFFIX=MCASUFFIX, FUNCTION_SVA_2L=ONEBIN, SYSTS=SYSTS, OPT_2L=OPT_2L)
    print submit.format(command=TORUN)
    
if REGION == "wz_3l":
    OPT_3L='{T3L} {OPTIONS} -W "PrefireWeight*puWeight*leptonSF_3l_sr"'.format(T3L=T3L, OPTIONS=OPTIONS_3L)
    TORUN = 'python {SCRIPT} {DOFILE} 5TeV/mca-wz-3l-{MCASUFFIX}.txt 5TeV/wz_3l.txt {FUNCTION_3L} {SYSTS} {OPT_3L} --binname wz_3l  '.format(SCRIPT=SCRIPT, DOFILE=DOFILE,MCASUFFIX=MCASUFFIX,FUNCTION_3L=ONEBIN, SYSTS=SYSTS, OPT_3L=OPT_3L)
    print submit.format(command=TORUN)


if REGION == "ww_2l":
    OPT_2L='{T2L} {OPTIONS} -W "PrefireWeight*puWeight*leptonSF_2l_sr"'.format(T2L=T2L, OPTIONS=OPTIONS)
    TORUN='''python {SCRIPT} {DOFILE} 5TeV/mca-ww-{MCASUFFIX}.txt 5TeV/ww_dilepton.txt {FUNCTION_SVA_2L} {SYSTS} {OPT_2L} --binname ww;'''.format(SCRIPT=SCRIPT, DOFILE=DOFILE, MCASUFFIX=MCASUFFIX,  FUNCTION_SVA_2L=ONEBIN, SYSTS=SYSTS, OPT_2L=OPT_2L)
    print submit.format(command=TORUN)

if REGION == "ww_ttcr":
    OPT_2L='{T2L} {OPTIONS} -W "PrefireWeight*puWeight*leptonSF_2l_sr"'.format(T2L=T2L, OPTIONS=OPTIONS)
    TORUN='''python {SCRIPT} {DOFILE} 5TeV/mca-ww-{MCASUFFIX}.txt 5TeV/ww_dilepton.txt {FUNCTION_SVA_2L} {SYSTS} {OPT_2L} --binname ww_tt -I ^0jet;'''.format(SCRIPT=SCRIPT, DOFILE=DOFILE, MCASUFFIX=MCASUFFIX,  FUNCTION_SVA_2L=ONEBIN, SYSTS=SYSTS, OPT_2L=OPT_2L)
    print submit.format(command=TORUN)

if REGION == "ww_dycr":
    OPT_2L='{T2L} {OPTIONS} -W "PrefireWeight*puWeight*leptonSF_2l_sr"'.format(T2L=T2L, OPTIONS=OPTIONS)
    TORUN='''python {SCRIPT} {DOFILE} 5TeV/mca-ww-{MCASUFFIX}.txt 5TeV/ww_dilepton.txt {FUNCTION_SVA_2L} {SYSTS} {OPT_2L} --binname ww_dy -I ^em;'''.format(SCRIPT=SCRIPT, DOFILE=DOFILE, MCASUFFIX=MCASUFFIX,  FUNCTION_SVA_2L=ONEBIN, SYSTS=SYSTS, OPT_2L=OPT_2L)
    print submit.format(command=TORUN)


if REGION == "ww_sscr":
    OPT_2L='{T2L} {OPTIONS} -W "PrefireWeight*puWeight*leptonSF_2l_sr"'.format(T2L=T2L, OPTIONS=OPTIONS)
    TORUN='''python {SCRIPT} {DOFILE} 5TeV/mca-ww-{MCASUFFIX}.txt 5TeV/ww_dilepton.txt {FUNCTION_SVA_2L} {SYSTS} {OPT_2L} --binname ww_ss -I ^os;'''.format(SCRIPT=SCRIPT, DOFILE=DOFILE, MCASUFFIX=MCASUFFIX,  FUNCTION_SVA_2L=ONEBIN, SYSTS=SYSTS, OPT_2L=OPT_2L)
    print submit.format(command=TORUN)


MCASUFFIX="mcdata" 
if REGION == "zz_4l":
    OPT_4L='{T4L} {OPTIONS} -W "PrefireWeight*puWeight*leptonSF_3l_br"'.format(T4L=T4L, OPTIONS=OPTIONS_3L)
    TORUN = 'python {SCRIPT} {DOFILE} 5TeV/mca-zz-4l-{MCASUFFIX}.txt 5TeV/zz_4l.txt {FUNCTION_4L} {SYSTS} {OPT_4L} --binname zz_4l  '.format(SCRIPT=SCRIPT, DOFILE=DOFILE,MCASUFFIX=MCASUFFIX,FUNCTION_4L=ONEBIN, SYSTS=SYSTS, OPT_4L=OPT_4L)
    print submit.format(command=TORUN)

if REGION == "zz_2l2nu":
    OPT_2L='{T2L} {OPTIONS} -W "PrefireWeight*puWeight*leptonSF_2l_sr"'.format(T2L=T2L, OPTIONS=OPTIONS_3L)
    TORUN = 'python {SCRIPT} {DOFILE} 5TeV/mca-zz-2l2nu-{MCASUFFIX}.txt 5TeV/zz_2l2nu.txt {FUNCTION_2L} {SYSTS} {OPT_2L} --binname zz_2l2nu '.format(SCRIPT=SCRIPT, DOFILE=DOFILE,MCASUFFIX=MCASUFFIX,FUNCTION_2L=ONEBIN, SYSTS=SYSTS, OPT_2L=OPT_2L)
    print submit.format(command=TORUN)


SYSTS_TT="--unc 5TeV/systs_ttbar.txt --amc "
if REGION == "ttbar_2l":
    OPT_2L='{T2L} {OPTIONS} -W "PrefireWeight*puWeight*leptonSF_2l_sr"'.format(T2L=T2L, OPTIONS=OPTIONS)
    TORUN='''python {SCRIPT} {DOFILE} 5TeV/mca-ttbar-{MCASUFFIX}.txt 5TeV/ttbar_dilepton.txt {FUNCTION_SVA_2L} {SYSTS} {OPT_2L} --binname ttbar {CAT};'''.format(SCRIPT=SCRIPT, DOFILE=DOFILE, MCASUFFIX=MCASUFFIX,  FUNCTION_SVA_2L=ONEBIN, SYSTS=SYSTS_TT, OPT_2L=OPT_2L,CAT=CATPOSTFIX)
    print submit.format(command=TORUN)

if REGION == "ttbar_dycr":
    CUTS='-E ^sf -X ^ZVeto -E ^onZ -X ^MET'
    OPT_2L='{T2L} {OPTIONS} -W "PrefireWeight*puWeight*leptonSF_2l_sr" {EXTRA}'.format(T2L=T2L, OPTIONS=OPTIONS, EXTRA=CUTS)
    TORUN='''python {SCRIPT} {DOFILE} 5TeV/mca-ttbar-{MCASUFFIX}.txt 5TeV/ttbar_dilepton.txt {FUNCTION_SVA_2L} {SYSTS} {OPT_2L} --binname ttbar_dycr {CAT};'''.format(SCRIPT=SCRIPT, DOFILE=DOFILE, MCASUFFIX=MCASUFFIX,  FUNCTION_SVA_2L=MLL, SYSTS=SYSTS_TT, OPT_2L=OPT_2L,CAT=CATPOSTFIX)
    print submit.format(command=TORUN)
