from optparse import OptionParser
from copy import deepcopy
import os 
import re
import sys
import json 


region_configs = {
    "srwz"   : { 
        "poi" : "r_wz",  
        "procmatch" : ".*prompt_WZ",
        "channels" : [
            "srwz_eee_2022",
            "srwz_eem_2022",
            "srwz_mme_2022",
            "srwz_mmm_2022",
            "srwz_eee_2022EE",
            "srwz_eem_2022EE",
            "srwz_mme_2022EE",
            "srwz_mmm_2022EE" 
        ]
    },
    "crzz"   : { 
        "poi" : "r_zz",  
        "procmatch" : ".*prompt_.*ZZ",
        "channels" : [
            "crzz_eee_2022",
            "crzz_eem_2022",
            "crzz_mme_2022",
            "crzz_mmm_2022",
            "crzz_eee_2022EE",
            "crzz_eem_2022EE",
            "crzz_mme_2022EE",
            "crzz_mmm_2022EE" 
        ]
    },
    "crtt"   : { 
        "poi" : "r_ttz", 
        "procmatch" : ".*prompt_TTX",
        "channels" : [
            "crtt_eee_2022",
            "crtt_eem_2022",
            "crtt_mme_2022",
            "crtt_mmm_2022",
            "crtt_eee_2022EE",
            "crtt_eem_2022EE",
            "crtt_mme_2022EE",
            "crtt_mmm_2022EE" 
        ]
    },
    "crconv" : { 
        "poi" : "r_xg",  
        "procmatch" : ".*conv",
        "channels" : [
            "crconv_eee_2022",
            "crconv_eem_2022",
            "crconv_mme_2022",
            "crconv_mmm_2022",
            "crconv_eee_2022EE",
            "crconv_eem_2022EE",
            "crconv_mme_2022EE",
            "crconv_mmm_2022EE" 
        ]
    },
}

def color_msg(msg, color = "none", indentlevel=0):
    """ Prints a message with ANSI coding so it can be printout with colors """
    codes = {
        "none" : "0m",
        "green" : "1;32m",
        "red" : "1;31m",
        "blue" : "1;34m",
        "yellow" : "1;35m"
    }

    if indentlevel == 0: indentSymbol=">> "
    if indentlevel == 1: indentSymbol="+ "
    if indentlevel == 2: indentSymbol="* "

    indent = indentlevel*" " + indentSymbol
    print("\033[%s%s%s \033[0m"%(codes[color], indent, msg))
    return

def add_parsing_opts():
    ''' Function with base parsing arguments used by any script '''
    parser = OptionParser(usage = "python wz-run.py [options]",  description = "Main options for running WZ analysis fits") 

    # -- Input and outputs
    parser.add_option("--mode",              dest = "mode", default = "combinecards", help = "Mode to run")
    parser.add_option("--inpath",     "-i",  dest = "inpath",  help = "Path to the card folders. ")
    parser.add_option("--cluster",    "-c",  dest = "cluster", action = "store_true", default = False, help = "Submit in cluster")
    parser.add_option("--output",     "-o",  dest = "output_folder", default = "inclusiveFlavorFit", help = "Main output folder")



    parser.add_option("--fit-for",    "-r",  dest = "fitFor", default = "srwz", help = "Do the fit only to a certain region.")
    parser.add_option("--mask",       "-m",  dest = "mask", default = "", 
                      help = "Mask channels that match expressions (i.e. select what to fit). The ones that are parsed will be used for the fit." )
    parser.add_option("--fitDiagnostics",  dest = "fitDiagnostics", default = "../fitDiagnosticsTest.root", help = "Path to fitDiagnostics. Used for making postfit observables.")
    parser.add_option("--workspace",  dest = "workspace", default = "workspace_wz.root", 
                      help = "Path to workspace. If it already exists, it takes the full path so it can be used for other combine methods.")
    parser.add_option("--jsonpath", "-j",  dest = "jsonpath", default = "table_groupings.json", help = "A JSON file containing information about how to split scan. Only used in scan_groups mode.")
    parser.add_option("--year",       "-y",  dest = "year", default = "all", 
                      help = "Use cards only satisfying this year in the name" )
    
    
    parser.add_option("--blind-sr",          dest = "blind_sr", default = False, action="store_true", help = "Blind SR")
    parser.add_option("--blind-all",         dest = "blind_all", default = False, action="store_true", help = "Blind everything")


    parser.add_option("--submit",            dest = "submit", default = False, action="store_true", help = "Submit job.")
    return parser

def create_outpath(out):
    """ Function to make sure output path exists """
    if not os.path.exists( out ):
        os.system("mkdir -p %s"%out)
    return

def apply_mask( mask ):
    """ Add any channel masking if needed """
    if mask == "": return ""
    
    all_channels = []
    for region, config in region_configs.items():
        all_channels.extend( config["channels"] )

    masks = []
    for ch in all_channels:
        match_mask = re.compile( f"{mask}" )
        if not match_mask.match( ch ) : 
            masks.append( f"mask_{ch}=1" )
    
    mask_text = " --setParameters " + ",".join( masks ) 
    return mask_text

def combine_cards( inpath, year_match = "all" ):
    """ Function to combine cards using fancy naming so they can be tracked in the impacts """
    match_cards = re.compile( "(srwz|crzz|crtt|crconv).*input(.*)_(.*).txt")
    maincmd="combineCards.py {cardtext} > combinedCard.dat"
    
    # Get a list of cards
    cards = []

    # Check if the path that it's given as input is directly the one with the cards
    for root, folders, files in os.walk( inpath ):
        cards_channel = [ file_ for file_ in files if "txt" in file_ ]
        for card in cards_channel:
            region, year, channel =  match_cards.match( card ).groups() 

            if year_match != "all" and year.split(".")[0] != year_match: continue
            realpath = os.path.realpath( os.path.join(root, card ) ) # Absolute path to the card
            cards.append( "%s_%s_%s=%s"%(region, channel, year.replace(".", "_"), realpath) )            

    # Join the text together           
    card_text = " ".join(cards)
    return [ maincmd.format(cardtext = card_text) ]

def workspace( wsname, combineModel ):
    """ Function to create workspace """

    # Build the mappings
    maps = []
    for region, config in region_configs.items():
        procmatch = config["procmatch"]
        poiname   = config["poi"]
        maps.append( " 'map=.*/%s:%s[1, 0, 6]'"%(procmatch, poiname)) # Float between 0 and 6 -- hardcoded

    maps = " --PO".join(maps)
    cmd = f"text2workspace.py combinedCard.dat -o {wsname} -P {combineModel} --PO verbose --PO {maps} --channel-masks"

    return [cmd]

def impacts(blind_signal, blind_all, wsname, fitFor = "srwz", cluster = False, mask = ""):
    """ Function to run impacts """ 
    # Check for channel masking
    extra = apply_mask( mask )
    outjson = "impacts.json"
    if blind_signal and not blind_all:
        extra = f" {extra} --expectSignal 1 --setParameters %s=1 -n .blindSignal "%(region_configs[fitFor]["poi"])
        outjson = "impacts-blindSignal.json"
    elif blind_all:
        extra = f" {extra} -t -1 --setParameters %s=1 -n .blindAll "%(region_configs[fitFor]["poi"])
        outjson = "impacts-blindAll.json"

    # Get the parameter to fit
    signalPOI = region_configs[fitFor]["poi"]
    if fitFor != "srwz": # This is a fit to a CR, so we have to fix other POIs
      poilist = ",".join( [ region_configs[reg]["poi"] for reg in region_configs.keys() if reg != fitFor] )
      extra = f" {extra} --freezeParameters {poilist}"

    # Always do the initial fit on local
    initialFit = f"combineTool.py -M Impacts -m 125 -d {wsname} --doInitialFit  --redefineSignalPOI {signalPOI} {extra} " 
    doFits = initialFit.replace("doInitialFit", "doFits --parallel 12 ")
    collectImpacts = initialFit.replace("--doInitialFit", "-o {outjson}".format(outjson = outjson) )
    plotImpacts = "plotImpacts.py -i {outjson} -o {outpdf}".format(outjson = outjson, outpdf = outjson.replace(".json", ""))

    if cluster:
        doFits += "  --job-mode slurm --sub-opts='-p batch'"   

    return [initialFit, doFits]#, collectImpacts, plotImpacts]

def scan(blind_signal, blind_all, wsname, fitFor = "srwz", cluster = False, freeze = "allConstrainedNuisances", name_freeze = "stat", mask = ""):
    """ Function to run likelihood scan commands """
    points = 200
    extra = apply_mask( mask )

    # Check for blinding 
    if blind_signal and not blind_all:
        extra = f" {extra} --expectSignal 1 --setParameters %s=1 -n .blindSignal "%(region_configs[fitFor]["poi"])
    elif blind_all:
        extra = f" {extra} -t -1 --setParameters %s=1 -n .blindAll "%(region_configs[fitFor]["poi"])
    
    # Get the parameter to fit
    signalPOI = region_configs[fitFor]["poi"]

    # First scan: always in local
    initialScan = f"combineTool.py -M MultiDimFit --algo grid --points {points} --rMin 0 --rMax 6 -m 125 -d {wsname} --redefineSignalPOI {signalPOI} -n .nominal {extra} --split-points 12"
    initialScan += " --task-name %s_%s "%("nom", region_configs[fitFor]["poi"])
    
    # Save snapshot
    snapshot = initialScan.replace("grid --points %d"%points, "none ").replace("nominal", "bestfit")
    snapshot += " --saveWorkspace"
    if cluster:
        initialScan += "  --job-mode slurm --sub-opts='-p batch'"
    
    # Freeze scan: allow for batch submission
    ScanFreeze = initialScan.replace( wsname, "higgsCombine.bestfit.MultiDimFit.mH125.root")
    ScanFreeze = ScanFreeze.replace("nominal", f"{name_freeze}").replace("--saveWorkspace", "")
    ScanFreeze += f" --snapshotName MultiDimFit --freezeParameters {freeze}"
    ScanFreeze += " --task-name %s_%s "%(name_freeze, region_configs[fitFor]["poi"] )
    if cluster:
        ScanFreeze += " --split-points 12 --job-mode slurm --sub-opts='-p batch'"

    return [initialScan, snapshot, ScanFreeze]

def fitDiagnostics(blind_signal, blind_all, wsname, fitFor, cluster = False, mask = ""):
    """ Function to run fitDiagnostics tool """
    
    extra = apply_mask( mask )
    if blind_signal and not blind_all:
        extra = f" {extra} --expectSignal 1 --setParameters %s=1 -n .blindSignal "%(region_configs[fitFor]["poi"])
    elif blind_all:
        extra = f" {extra} -t -1 --setParameters %s=1 -n .blindAll "%(region_configs[fitFor]["poi"])
    
    cmd = F"combine -M FitDiagnostics {wsname} -m 125 --plots --saveShapes --saveWithUncertainties  --numToysForShapes 200 --skipBOnlyFit -v 3 {extra}"

    if cluster:
        cmd = f"sbatch --wrap '{cmd}'"
    return [cmd]

def multigof(wsname, fitFor, cluster = False, mask = ""):
    """ Function to run Goodness Of Fit tests """
    extra = apply_mask( mask )

    points = 4000
    jobs = 40
    pointsperjob = points//jobs
    
    # For GOF, make sure you freeze WZ so the signal POI is not interfering in a weird way (for the bkg only fits, it does not have an effect, because we use channel masking)
    basecmd = f"combineTool.py -M GoodnessOfFit --expectSignal 1 {wsname} --freezeParameters r_wz  --algo=saturated  --toysFreq {extra}"
    if cluster: 
        basecmd += " --job-mode slurm"


    cmds = [basecmd]
    for ijob in range(jobs):
        icmd = deepcopy(basecmd)
        icmd += f" -n _{fitFor}_gof_job{ijob} -t {pointsperjob} -s {ijob}"
        cmds.append( icmd )

    return cmds 

def make_postfit(out, wsname, cluster = False, fitDiagnostics_path = "../fitDiagnostics/fitDiagnosticsTest.root" ):
    """ Function PostFitShapesFromWorkspace script to make any postfit distribution """

    cmd = f"PostFitShapesFromWorkspace -w {wsname} -d combinedCard.dat -o wz_OUT.root -f {fitDiagnostics_path}:fit_s --postfit --sampling --print --total-shapes ".format(
        workspace = wsname,
        out = out,
    )

    if cluster:
        cmd = f"sbatch -p batch --wrap '{cmd}'"
        
    return [cmd] 

#def scan(blind_signal, blind_all, wsname, fitFor = "srwz", cluster = False, freeze = "allConstrainedNuisances", name_freeze = "stat", mask = ""):

def scan_groups(blind_signal, blind_all, wsname, jsonpath, cluster = False, mask = ""):
    """ Run multiple scans at once to compute table of systematics """

    with open(jsonpath, "rb") as input_json:
        data = json.load(input_json)

    groupList = data["groupList"]

    cmds = []
    cumulative = []
    
    
    nom = scan( blind_signal, blind_all, wsname, fitFor = "srwz", cluster = cluster, mask = mask)[0]
    bestfit = scan( blind_signal, blind_all, wsname, fitFor = "srwz", cluster = False, mask = mask)[1] # Always do the bestfit in local

    cmds.append( nom )
    cmds.append( bestfit )
    
    ## Now one by one freezing groups
    for group in groupList:
        cumulative += data["systsGroup"][group]["systs"]

        if data["systsGroup"][group]["systs"][0] == "allConstrainedNuisances":
            freeze_cmd = scan( blind_signal, blind_all, wsname, fitFor = "srwz", cluster = cluster, freeze = "allConstrainedNuisances", name_freeze = group, mask = mask )[2] # Keep only the freezing command
        else:
            freeze_cmd = scan( blind_signal, blind_all, wsname, fitFor = "srwz", cluster = cluster, freeze = ",".join(cumulative), name_freeze = group, mask = mask )[2] # Keep only the freezing command

        cmds.append(freeze_cmd)
        
    return cmds

def sys_table(fitFor, jsonpath):
    """ Build the table of systematics from the output of scan_groups """

    signalPOI = region_configs[fitFor]["poi"]
    with open(jsonpath, "r") as input_json:
        data = json.load(input_json)
    groupList = data["groupList"]

    
    cmds = []

    # First merge all the outputs
    outfile =  "higgsCombine.nominal.MultiDimFit.mH125.root"
    
    if not os.path.isfile(outfile): 
        infile = "higgsCombine.nominal.POINTS.*.MultiDimFit.mH125.root"
        hadd = f"hadd {outfile} {infile}"
        cmds.append( hadd )

    for gr in groupList:
        outfile_gr =  "higgsCombine.%s.MultiDimFit.mH125.root"%(gr+'_'+signalPOI)
        if os.path.isfile(outfile_gr): continue
        infile_gr = "higgsCombine.%s.POINTS.*.MultiDimFit.mH125.root"%(gr)
        hadd_gr = f"hadd {outfile_gr} {infile_gr}"
        cmds.append( hadd_gr )

    # Now the plot1Dscan
    cmd_freeze = "'higgsCombine.%s.MultiDimFit.mH125.root:%s:%d'"
    cmd_scan = "plot1DScan.py higgsCombine.nominal.MultiDimFit.mH125.root --others "

    fileList = []
    for gr in groupList:
        fileList.append(cmd_freeze%(gr+'_'+signalPOI, gr,groupList.index(gr)+2))

    cmd_scan += " ".join( fileList )
    cmd_scan += " --breakdown "
    cmd_scan += ','.join(groupList)
    cmd_scan += ',stat'
    cmd_scan += " --POI %s "%signalPOI

    mv_pdf = 'mv scan.pdf scan_%s.pdf'%(signalPOI)
    mv_png = 'mv scan.png scan_%s.png'%(signalPOI)

    cmds.append(cmd_scan)
    cmds.append(mv_pdf)
    cmds.append(mv_png)
    
    return cmds




if __name__ == "__main__":
    opts, args = add_parsing_opts().parse_args()

    mode    = opts.mode
    inpath  = opts.inpath
    cluster = opts.cluster
    output  = opts.output_folder

    fitFor = opts.fitFor
    mask = opts.mask
    wsname = os.path.realpath( opts.workspace ) if os.path.isfile( opts.workspace ) else opts.workspace 
    fitD = os.path.realpath(opts.fitDiagnostics)
    jsonpath = opts.jsonpath
    year = opts.year

    submit  = opts.submit
    blind_sr   = opts.blind_sr
    blind_all   = opts.blind_all
        

    # For the moment this is hardcoded for the inclusive measurement
    combineModel = "HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel"


    # Call the correct function
    cmds = None
 
    # --- Card combination
    if mode == "combinecards":   
        cmds = combine_cards( 
            inpath = inpath,
            year_match = year
        )

    # --- Workspace creation
    elif mode == "workspace":
        cmds = workspace( 
            wsname = wsname, 
            combineModel = combineModel 
        )

    # --- Run impacts
    elif mode == "impacts":
        cmds = impacts( 
            blind_signal = blind_sr, 
            blind_all = blind_all, 
            wsname = wsname, 
            fitFor = fitFor, 
            cluster = cluster,
            mask = mask
        )

    # --- Run scan
    elif mode == "scan":
        cmds = scan( 
            blind_signal = blind_sr, 
            blind_all = blind_all,
            wsname = wsname, 
            fitFor = fitFor, 
            cluster = cluster, 
            mask = mask 
        )
 
    # --- Run fitDiagnostics
    elif mode == "fitDiagnostics":
        cmds = fitDiagnostics( 
            blind_signal = blind_sr, 
            blind_all = blind_all,
            wsname = wsname,
            fitFor = fitFor,
            cluster = cluster,
            mask = mask
        )

    # --- Run GOF
    elif mode == "multigof":
        cmds = multigof( 
            wsname = wsname,
            fitFor = fitFor,
            cluster = cluster, 
            mask = mask
        )

    elif mode == "make_postfit":
        cmds = make_postfit( 
            out = output,
            wsname = wsname,
            cluster = cluster,
            fitDiagnostics_path = fitD
        )

    
    elif mode == "scan_groups":    
        cmds = scan_groups( 
            blind_signal = blind_sr, 
            blind_all = blind_all,
            wsname = wsname,
            jsonpath = jsonpath,
            cluster = cluster, 
            mask = mask 
        )
    
    elif mode == "sys_table":      
        cmds = sys_table( 
            fitFor = fitFor,
            jsonpath = jsonpath,
        )
    

    # make sure the output exists
    if opts.submit:
        create_outpath( output )


    for icmd, cmd in enumerate(cmds):
        color_msg("Command %d:"%icmd, "green")
    
        cmd = "cd %s; %s; cd -"%(output, cmd)
        print(cmd) 
        if opts.submit:
            os.system(cmd)

