""" Small piece of code to run card commands """
import argparse
import os 

# Define a dictionary with card configs
variable_configs = {
    "flavor3l" : {
        "srwz"   : ( "(abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2", "4,-0.5,3.5" ),
        "crzz"   : ( "(abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2", "4,-0.5,3.5" ),
        "crtt"   : ( "(abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2", "4,-0.5,3.5" ),
        "crconv" : ( "(abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2", "4,-0.5,3.5" )
    },
    "lepZ1_pt" : {
        "srwz"   : ( "min(max(LepZ1_pt, 25), 224)", "20,25,225" ),
        "crzz"   : ( "min(max(LepZ1_pt, 25), 224)", "20,25,225" ),
        "crtt"   : ( "min(max(LepZ1_pt, 25), 224)", "20,25,225" ),
        "crconv" : ( "min(max(LepZ1_pt, 25), 124)", "10,25,125" )
    },
    "lepZ2_pt" : {        
        "srwz"   : ( "min(max(LepZ2_pt, 15), 224)", "10,15,165" ),
        "crzz"   : ( "min(max(LepZ2_pt, 15), 224)", "10,15,165" ),
        "crtt"   : ( "min(max(LepZ2_pt, 15), 224)", "10,15,165" ),
        "crconv" : ( "min(max(LepZ2_pt, 15), 124)", "4,15,75" )
    },

    "lepW_pt" : {
        "srwz"   : ( "min(max(LepW_pt, 25), 224)", "20,25,225" ),
        "crzz"   : ( "min(max(LepW_pt, 25), 224)", "20,25,225" ),
        "crtt"   : ( "min(max(LepW_pt, 25), 224)", "20,25,225" ),
        "crconv" : ( "min(max(LepW_pt, 25), 124)", "10,25,125" )
    },
    "lepZ1_eta" : {
        "srwz"   : ( "min(max(LepZ1_eta, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crzz"   : ( "min(max(LepZ1_eta, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crtt"   : ( "min(max(LepZ1_eta, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crconv" : ( "min(max(LepZ1_eta, -2.5), 2.4)", "10,-2.5,2.5" )
    },
    "lepZ2_eta" : {
        "srwz"   : ( "min(max(LepZ2_eta, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crzz"   : ( "min(max(LepZ2_eta, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crtt"   : ( "min(max(LepZ2_eta, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crconv" : ( "min(max(LepZ2_eta, -2.5), 2.4)", "10,-2.5,2.5" )
    },
    "lepW_eta" : {
        "srwz"   : ( "min(max(LepW_eta, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crzz"   : ( "min(max(LepW_eta, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crtt"   : ( "min(max(LepW_eta, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crconv" : ( "min(max(LepW_eta, -2.5), 2.4)", "10,-2.5,2.5" )
    },
    "lepZ1_phi" : {
        "srwz"   : ( "min(max(LepZ1_phi, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crzz"   : ( "min(max(LepZ1_phi, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crtt"   : ( "min(max(LepZ1_phi, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crconv" : ( "min(max(LepZ1_phi, -2.5), 2.4)", "10,-2.5,2.5" )
    },
    "lepZ2_phi" : {
        "srwz"   : ( "min(max(LepZ2_phi, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crzz"   : ( "min(max(LepZ2_phi, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crtt"   : ( "min(max(LepZ2_phi, -2.5), 2.4)", "10,-2.5,2.5" ),
        "crconv" : ( "min(max(LepZ2_phi, -2.5), 2.4)", "10,-2.5,2.5" )
    },
    "lepW_phi" : {
        "srwz"   : ( "min(max(LepW_phi, -3.15), 3.13)", "10,-2.5,2.5" ),
        "crzz"   : ( "min(max(LepW_phi, -3.15), 3.13)", "10,-2.5,2.5" ),
        "crtt"   : ( "min(max(LepW_phi, -3.15), 3.13)", "10,-2.5,2.5" ),
        "crconv" : ( "min(max(LepW_phi, -3.15), 3.13)", "10,-2.5,2.5" )
    },
    "nJets" : {
        "srwz"   : ("min(max(nJet25_Mini,0), 4)", "[-0.5,0.5,1.5,2.5,3.5,4.5,5.5]"),
        "crzz"   : ("min(max(nJet25_Mini,0), 4)", "[-0.5,0.5,1.5,2.5,3.5,4.5,5.5]"),
        "crtt"   : ("min(max(nJet25_Mini,0), 4)", "[-0.5,0.5,1.5,2.5,3.5,4.5,5.5]"),
        "crconv" : ("min(max(nJet25_Mini,0), 4)", "[-0.5,0.5,1.5,2.5,3.5,4.5,5.5]"),
    },
    "m3l" : {
        "srwz"   : ("min(max(m3L, 100), 299)", "10,100,300"),
        "crzz"   : ("min(max(m3L, 100), 299)", "10,100,300"),
        "crtt"   : ("min(max(m3L, 100), 299)", "10,100,300"),
        "crconv" : ("min(max(m3L, 100), 299)", "10,100,300"),
    },
    "mll_3l" : {
        "srwz"   : ("min(max(mll_3l, 75), 114)", "20,75,115"),
        "crzz"   : ("min(max(mll_3l, 75), 114)", "20,75,115"),
        "crtt"   : ("min(max(mll_3l, 75), 114)", "20,75,115"),
        "crconv" : ("min(max(mll_3l, 75), 114)", "20,75,115"),
    },
    "mll_3l_ee" : {
        "srwz"   : ("min(if3((abs(LepZ1_pdgId)+abs(LepZ2_pdgId)) == 22, mll_3l, -99), 104)", "25,80,105"),
        "crzz"   : ("min(if3((abs(LepZ1_pdgId)+abs(LepZ2_pdgId)) == 22, mll_3l, -99), 104)", "25,85,95"),
        "crtt"   : ("min(if3((abs(LepZ1_pdgId)+abs(LepZ2_pdgId)) == 22, mll_3l, -99), 104)", "20,85,105"),
        "crconv" : ("min(if3((abs(LepZ1_pdgId)+abs(LepZ2_pdgId)) == 22, mll_3l, -99), 104)", "20,85,105"),
    },
    "mll_3l_mm" : {
        "srwz"   : ("min(if3((abs(LepZ1_pdgId)+abs(LepZ2_pdgId)) == 26, mll_3l, -99), 104)", "25,80,105"),
        "crzz"   : ("min(if3((abs(LepZ1_pdgId)+abs(LepZ2_pdgId)) == 26, mll_3l, -99), 104)", "30,85,100"),
        "crtt"   : ("min(if3((abs(LepZ1_pdgId)+abs(LepZ2_pdgId)) == 26, mll_3l, -99), 104)", "20,85,105"),
        "crconv" : ("min(if3((abs(LepZ1_pdgId)+abs(LepZ2_pdgId)) == 26, mll_3l, -99), 104)", "20,85,105"),
    },
    "met" : {
        "srwz"   : ("min(max(MET_pt_central, 35), 174)", "20,35,175"),
        "crzz"   : ("min(max(MET_pt_central, 35), 174)", "20,35,175"),
        "crtt"   : ("min(max(MET_pt_central, 35), 174)", "20,35,175"),
        "crconv" : ("min(max(MET_pt_central, 35), 174)", "20,35,175"),
    },
    "charge" : {
        "srwz"   : ("if3(LepZ1_pdgId>0,-1,1)+if3(LepZ2_pdgId>0,-1,1)+if3(LepW_pdgId>0,-1,1)", "2,-1.5,1.5"),
        "crzz"   : ("if3(LepZ1_pdgId>0,-1,1)+if3(LepZ2_pdgId>0,-1,1)+if3(LepW_pdgId>0,-1,1)", "2,-1.5,1.5"),
        "crtt"   : ("if3(LepZ1_pdgId>0,-1,1)+if3(LepZ2_pdgId>0,-1,1)+if3(LepW_pdgId>0,-1,1)", "2,-1.5,1.5"),
        "crconv" : ("if3(LepZ1_pdgId>0,-1,1)+if3(LepZ2_pdgId>0,-1,1)+if3(LepW_pdgId>0,-1,1)", "2,-1.5,1.5"),
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

def add_parsing_options():
    parser = argparse.ArgumentParser()

    parser.add_argument('--variables', '-v', 
    	dest = "variables", 
    	default = "flavor3l", 
    	help = "Variable to make card. Comma separated"
    )

    parser.add_argument('--mode', '-m', 
    	dest = "mode", 
    	default = "total", 
    	help = "Produce cards for fiducial or total fit (only theoretical uncertainties change)"
    )

    parser.add_argument('--regions', '-r', 
    	dest = "regions", 
    	default = "srwz,crzz,crtt,crconv",
    	help = "Run card only for this region. Comma separated"
    )

    parser.add_argument('--submit', '-s', 
        dest = "submit", 
        action = "store_true",
        help = "Submit jobs."
    )


    return parser.parse_args()


if __name__ == "__main__":
    binname_template = "{0}.input{1}{2}" # 0 -> region, 1-> year/era, 2->variable (omit if flavor3l)

    opts = add_parsing_options()
    variables = opts.variables.split(",")
    mode = opts.mode
    regions = opts.regions.split(",")
    submit = opts.submit

    systfile = f"wz-run3/common/systs-wz-{mode}.txt"
    outfolder = f"wz-run3/combine/cards/inclusive/approval-04thJuly2024/{mode}"

    for variable in variables:
        color_msg( f"Making cards for variable {variable}", "green")
        varconfig = variable_configs[variable]

        for region in regions:
            for year in ["2022", "2022EE"]:
                color_msg( f"region: {region} -- {year}", "blue", indentlevel = 1 )


                binname = binname_template.format( region, year, "."+variable if variable != "flavor3l" else "")
                cutfile = f"wz-run3/common/cuts-{region}.txt"

                var = varconfig[region][0]
                binning = varconfig[region][1]
                
 
                cmd = f"python3 wz-run3/wz-run.py card --uncfile {systfile} --outname {outfolder}/{variable}/{region} --binname {binname}   --cutfile {cutfile} --ncores 24 --year {year} --var \'{var}\' --binning \"{binning}\" "

                if submit:
                    cmd += " --do-submit"
                os.system( cmd )




	

