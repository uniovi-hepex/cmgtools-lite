import json
from copy import deepcopy
import numpy as np

jsonpath = "table_groupings.json"
with open(jsonpath, "r") as input_json:
    data = json.load(input_json)

def sort_list(rows):
    order = []
    avgs = []
    for index,row in enumerate(rows.keys()):
        avgs.append(rows[row])
    avgs_copy = deepcopy(avgs)
    avgs_copy = np.sort(avgs_copy)

    for avg in avgs_copy[::-1]:
        order.append(avgs.index(avg))
    return order


def systs_for_table(filename, sg):
    systsGroup = data["systsGroup"]
    
    val = 0
    stat = 0
    syst = 0
    # Get the values
    f = open(filename, "r")
    rows = {}
    total_up = 0
    total_down = 0
    avgs = {} # for sorting rows
    for syst in f.readlines():  
        info = syst.split(":")
        name = str(info[0]).strip().replace("inc_", "")
        if name == 'val': 
            val = float(info[1].split("\n")[0])
            continue
    
        up = float(info[1])
        down = float(info[2].split("\n")[0])
        avg = (up + down)/2
        if name == 'stat': 
            stat = avg
            continue
        if systsGroup[name]["SuperGroup"] != sg:
            continue
        avgs[name] = avg

        total_up += up*up
        total_down +=  down*down
        
        
        rows[name] =  "\t \t %s & %3.1f \\\ \n"%(systsGroup[name]["inTable"], avg/val*100)

    f.close() 
    return rows, avgs, val, stat, total_up, total_down

def latex_table(data, filename):
    supergroups = data["SuperGroups"]
    r = "\t\t\multicolumn{2}{c}{$r_{\\text{t}\\bar{\\text{t}}\\text{W}}$ = %2.3f $\pm$ %2.3f (stat) $\pm$ %2.3f (syst)}\\\ \n"
    latex_table = '''
    \usepackage{tabular}
    \\begin{table}
        \\centering
        \\resizebox{\\textwidth}{!}{
            \\begin{tabular}{p{12cm}m{3cm}}
                    \\hline
    '''
    latex_table += "\t \t %s & %s \\\\  \n"%("Source", "Avg. Unc (\%)")
    total_up = 0
    total_down = 0
    for sg in supergroups:
        rows, avgs, val, stat, syst_up, syst_down = systs_for_table(filename, sg)
        total_up   += syst_up
        total_down += syst_down
        names = rows.keys()
        # sort rows
        order = sort_list(avgs)

        if sg != "None": latex_table += "\t\t \hline\hline \multicolumn{2}{c}{%s}  \\\ \hline\hline\n"%sg  
        else: latex_table +=  "\t\t \hline  \n "  
        for index in order:
            name = names[index]
            latex_table += rows[name]

    total_up = np.sqrt(total_up)
    total_down = np.sqrt(total_down)
    syst  = (total_up+total_down)/2

    # Add the statistic uncertainty 
    latex_table +='''           \t \hline  \n'''
    latex_table += r%(val, stat, syst) 
    latex_table +='''            \t \\hline       
        \\end{tabular}
    }
    \\end{table}'''
    # End table
    print(latex_table)
    return

latex_table(data, "fits/all/inclusive/outputfit.txt")
