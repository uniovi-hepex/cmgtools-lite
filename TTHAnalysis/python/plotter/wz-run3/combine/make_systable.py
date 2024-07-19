""" Read scan and give postfit systematic table """
import ROOT as r
import sys, os, re
import math
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3"))
from scripts.make_latex_table import dict_to_latex_table
from optparse import OptionParser
from copy import deepcopy 
import json

def parse_file(file_path):
    data_dict = {}
    
    jsonpath = "table_groupings.json"
    with open(jsonpath, "rb") as input_json:
        data = json.load(input_json)
    

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(' : ')
            key = parts[0]
            if key == "val":
                continue
            values = list(map(float, parts[1:]))
            average = sum(values) / len(values) * 100

            name = data["systsGroup"][ key.replace("inc_", "") ]["inTable"] if key != "inc_stat" else "Statistical Uncertainty"
            data_dict[name] = average
    
    return data_dict



# Example usage
result     = parse_file('fit-results_approval-v2/total/inclusive/uncertainty-table/outputfit.txt')
result_eee = parse_file('fit-results_approval-v2/total/eee/uncertainty-table/outputfit.txt')
result_eem = parse_file('fit-results_approval-v2/total/eem/uncertainty-table/outputfit.txt')
result_mme = parse_file('fit-results_approval-v2/total/mme/uncertainty-table/outputfit.txt')
result_mmm = parse_file('fit-results_approval-v2/total/mmm/uncertainty-table/outputfit.txt')

#table = {
#    "Source"   : list(result.keys()),
#    "Inclusive"  : [ "%3.1f"%result[source] if result[source] > 0.01 else "-" for source in list(result.keys())  ],
#    "\\eee"      : [ "%3.1f"%result_eee[source] if result[source] > 0.01 else "-" for source in list(result_eee.keys())],
#    "\\eem"      : [ "%3.1f"%result_eem[source] if result[source] > 0.01 else "-" for source in list(result_eem.keys())],
#    "\\mme"      : [ "%3.1f"%result_mme[source] if result[source] > 0.01 else "-" for source in list(result_mme.keys())],
#    "\\mmm"      : [ "%3.1f"%result_mmm[source] if result[source] > 0.01 else "-" for source in list(result_mmm.keys())],
#}

table = {
    "Source"   : list(result.keys()),
    "Inclusive"  : [ "%3.1f"%result[source] if result[source] > 0.01 else "-" for source in list(result.keys())  ],
    "\\eee"      : [ "%3.1f"%result_eee[source] if float(result_eee[source]) > 0.01 else "-" for source in list(result_eee.keys())],
    "\\eem"      : [ "%3.1f"%result_eem[source] if float(result_eem[source]) > 0.01 else "-" for source in list(result_eem.keys())],
    "\\mme"      : [ "%3.1f"%result_mme[source] if float(result_mme[source]) > 0.01 else "-" for source in list(result_mme.keys())],
    "\\mmm"      : [ "%3.1f"%result_mmm[source] if float(result_mmm[source]) > 0.01 else "-" for source in list(result_mmm.keys())],
}

# Create the latex table
caption = """ Breakdown of different sources of systematic and their relative impact in each channel, as well as in the combined measurement. """
table = dict_to_latex_table(table, caption, "tab:table_syst")
print(table)

