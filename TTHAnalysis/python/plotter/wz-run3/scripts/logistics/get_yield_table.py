import re
import math
import sys
from make_latex_table import dict_to_latex_table

def process_line(line):
    # Extract numerical values from the line
    values = [float(match.group()) for match in re.finditer(r'\d+\.\d+', line)]
    return values

def process_table(file_path):
    data = {'Process': [], 'eee': [], 'eem': [], 'mme': [], 'mmm': [], 'Inclusive': []}

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:
            if line[0] in ["-", "#"]: continue
            if "DATA" in line: continue
            process = line.split(" ")[0] if "Fakes" not in line else line.split(" ")[0]+" "+line.split(" ")[1]
            remove_empty = line.replace(process, "").replace(" ", "").replace("\n", "")
            separate_bins = remove_empty.split("(syst)")[:-1]
            print(process, separate_bins)
            data["Process"].append(process)
            tot = 0
            tot_unc = 0 
            for ibin, col in zip(separate_bins, ["eee", "eem", "mme", "mmm"]):
                value = float(ibin.split("+/-")[0])
                stat = float(ibin.split("+/-")[1].replace("(stat)", ""))
                syst = float(ibin.split("+/-")[2]) 
                total = math.sqrt(stat*stat + syst*syst) 
                
                data[col].append("%3.2f +/- %3.2f"%(value, total)) 
                tot += value
                tot_unc += total*total

            data["Inclusive"].append("%3.2f +/- %3.2f"%(tot, math.sqrt(tot_unc)))
                #data['Process'].append(process_name)
                #data['Column1'].append(values[0])
                #data['Column2'].append(values[1])
                #data['Column3'].append(values[2])
                #data['Column4'].append(values[3])
                #data['Sum'].append(sum(values))

    return data

if __name__ == "__main__":
    file_path = sys.argv[1] 
    table_data = process_table(file_path)

    # Print the processed data
    caption="""Expected (pre-fit) yields (by flavor channel) for the relevant processes in the signal 
    region of the analysis. All analysis uncertainties but the $(\mu_r, \mu_F)$ and PDFs are included."""
    
    table = dict_to_latex_table(table_data, caption, "yields_prefit2022PostEE")
    print(table)
