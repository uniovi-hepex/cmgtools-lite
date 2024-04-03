import os
import sys
import re
from optparse import OptionParser

# -- Define functions -- #
def add_parsing_opts():
    ''' Function with base parsing arguments used by any script '''
    parser = OptionParser(usage = "python wz-run.py [options]", 
                                    description = "Main options for running WZ analysis") 

    # -- Input and outputs
    parser.add_option("--mode", dest = "mode", default = "friend",
                help = "Option for merging friend trees or postprocessor output.")
    parser.add_option("--inpath", dest = "inpath", 
                help = "Inpath with the trees to merge.")
    return parser
if __name__ == "__main__":
    opts, args = add_parsing_opts().parse_args()
    
    mode = opts.mode
    inpath = opts.inpath
    
    if mode == "friend":
        # This is the skeleton for the merging script
        header = """#!/bin/bash
cd %s 
what=%s
""" 
        cmd = """
if [[ "$1" != "" ]]; then what=$1; fi
for F in $(ls ${what}_Friend.chunk*.root | sed 's/\.chunk[0-9]\+//' | sort | uniq); do
    if test -f $F; then echo "Merged file $F already exists. skipping."; continue; fi
    FILES=$(ls ${F/.root/.chunk*.root} | \\
            perl -npe 's/\.chunk(\d+)\./sprintf(".%06d.",$1)/e' | \\
            sort -n | \\
            perl -npe 's/\.(\d+)\.root$/sprintf(".chunk%d.root",$1)/e' );
    echo -e "\\nWill merge into $F:\\n$FILES"; 
    hadd -ff $F $FILES
done

              """#\n mkdir -p chunks\n mv {name}_*chunk*root chunks/"""
            
        # Get a list of all the files and filter repetitions. 
        # This way you can know which output files you will have to create
        processes = [ re.match("(.*)_Friend(.*)chunk(.*)root", p).groups()[0] for p in os.listdir(opts.inpath) if (".root" in p) and ("chunk" in p) ]
        AllFiles = [ p for p in os.listdir(opts.inpath) if ".root" in p ]

        main_names = list( dict.fromkeys(processes) )
        
        # Now you need to iterate over the files and associate them to a main name
        dict_to_merge = dict.fromkeys(main_names)
        
        if not os.path.exists("%s/logs/"%inpath):
            os.system("mkdir -p %s/logs/"%inpath)
            os.system("mv %s/log*.* %s/logs"%(inpath, inpath))
        if not os.path.exists("%s/chunks/"%inpath):
            os.system("mkdir -p %s/chunks/"%inpath)
        
        for pname in dict_to_merge.keys():
           
            # Create the script
            script = header%(inpath, pname) + cmd
            #.format(name = inpath + "/%s"%pname, files = " ".join(files))
            f = open("mergefriend_%s.sh"%pname, "w")
            f.write(script)
            f.close()
            
            # Make it executable
            os.system("chmod +x mergefriend_%s.sh"%pname)
            
            # Execute
            os.system('sbatch -J merge -e {inpath}/logs/log{pname}.%j.%x.err -o {inpath}/logs/log{pname}.%j.%x.out --wrap "./mergefriend_{pname}.sh" '.format(pname = pname, inpath = inpath))
            
            # Now remove the script
            #os.system("rm mergefriend_%s.sh"%pname)
            print(" --- ")
    elif mode == "postproc":
        cmd = """#!/bin/bash \ncd $1 \nhaddChunks.py -n -c --max-size 15 . """
        f = open("mergepostproc.sh", "w")
        f.write(cmd)
        f.close()
        os.system("chmod +x mergepostproc.sh ")
        os.system("sbatch -J wzchunk --wrap './mergepostproc.sh %s'"%inpath)            
        
