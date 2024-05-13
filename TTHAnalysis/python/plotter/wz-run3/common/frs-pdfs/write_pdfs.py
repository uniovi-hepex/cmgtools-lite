import os

pdfs_indices = range(104)
template = "LHEPdfWeight[{idx}]"

txt = """weight : Alt$(LHEPdfWeight[{idx}], 1)
alt-norm : Alt$(LHEPdfSumw[{idx}]/LHEPdfSumw[4],1)
"""
 
filename_template = "fr-pdf_{idx}.txt"
for pdfindex in pdfs_indices:
    f = open(filename_template.format(idx = pdfindex), "w")
    f.write(txt.format(idx = pdfindex))
    f.close()
