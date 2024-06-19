""" Small piece of code to run card commands """
import argparse
import os 

# Define a dictionary with card configs
variable_configs = {
    "flavor3l" : {
    	"variable" : "(abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2",
        "binning" : {
           "srwz"   : "4,-0.5,3.5",
           "crzz"   : "4,-0.5,3.5",
           "crtt"   : "4,-0.5,3.5",
           "crconv" : "4,-0.5,3.5",
        }
    },
    "counts" : {
    	"variable" : "1",
    	"binning" : {
           "srwz"   : "1,0.5,1.5",
           "crzz"   : "1,0.5,1.5",
           "crtt"   : "1,0.5,1.5",
           "crconv" : "1,0.5,1.5",
        }
    },
    "lepZ1_pt" : {
        "variable" : "LepZ1_pt",
        "binning" : {
           "srwz"   : "20,20,200",
           "crzz"   : "20,20,200",
           "crtt"   : "20,20,200",
           "crconv" : "10,20,100",
        }
    },
    "lepZ2_pt" : {
        "variable" : "LepZ2_pt",
        "binning" : {
           "srwz"   : "10,15,150",
           "crzz"   : "10,15,150",
           "crtt"   : "10,15,150",
           "crconv" : "4,15,60",
        }
    },
    "lepW_pt" : {
        "variable" : "LepW_pt",
        "binning" : {
           "srwz"   : "20,20,200",
           "crzz"   : "20,20,200",
           "crtt"   : "20,20,200",
           "crconv" : "10,20,100",
        }
    },
    "lepZ1_eta" : {
        "variable" : "LepZ1_eta",
        "binning" : {
           "srwz"   : "10,-2.5,2.5",
           "crzz"   : "5,-2.5,2.5",
           "crtt"   : "5,-2.5,2.5",
           "crconv" : "5,-2.5,2.5",
        }
    },
    "lepZ2_eta" : {
        "variable" : "LepZ2_eta",
        "binning" : {
           "srwz"   : "10,-2.5,2.5",
           "crzz"   : "5,-2.5,2.5",
           "crtt"   : "5,-2.5,2.5",
           "crconv" : "5,-2.5,2.5",
        }
    },
    "lepW_eta" : {
        "variable" : "LepW_eta",
        "binning" : {
           "srwz"   : "10,-2.5,2.5",
           "crzz"   : "5,-2.5,2.5",
           "crtt"   : "5,-2.5,2.5",
           "crconv" : "5,-2.5,2.5",
        }
    },
    "nJets" : {
        "variable" : "nJet25_Mini",
        "binning" : {
           "srwz"   : "[-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5]",
           "crzz"   : "[-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5]",
           "crtt"   : "[-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5]",
           "crconv" : "[-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5]",
        }
    }

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
    regions = opts.regions.split(",")
    submit = opts.submit

    systfile = "wz-run3/common/systs-wz.txt"
    outfolder = "wz-run3/combine/cards/inclusive/unblinded-fitFlavorForTTZ-groupFakes/"

    for variable in variables:
        color_msg( f"Making cards for variable {variable}", "green")
        varconfig = variable_configs[variable]

        for region in regions:
            for year in ["2022", "2022EE"]:
                color_msg( f"region: {region} -- {year}", "blue", indentlevel = 1 )


                binname = binname_template.format( region, year, "."+variable if variable != "flavor3l" else "")
                cutfile = f"wz-run3/common/cuts-{region}.txt"
                cmd = f"python3 wz-run3/wz-run.py card --uncfile {systfile} --outname {outfolder}/{variable}/{region} --binname {binname}   --cutfile {cutfile} --ncores 16 --year {year} --var \'{varconfig['variable']}\' --binning \"{varconfig['binning'][region]}\" "

                if submit:
                    cmd += " --do-submit"
                os.system( cmd )




	

