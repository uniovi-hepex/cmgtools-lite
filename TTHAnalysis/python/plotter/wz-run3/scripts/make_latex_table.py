""" 
Script to make latex table with a dictionary as input.
-----------------------------------------------
Keys are column headers.
Values are lists representing the rows under each 
column header. 

For multirows and multicolumns:
-----------------------------------------------
Multirows: We can denote a multirow using a tuple where the first item 
           is the content and the second item is the number of rows it spans.
           For example, ('content', 3) would span 3 rows.

Multicolumns: This can be represented as nested dictionaries. 
              The outer dictionary key represents the main column title that 
              spans multiple columns. The inner dictionary keys are the 
              sub-column titles, and the values are the corresponding rows.
"""

def dict_to_latex_table(data, caption, label):
    """Convert dictionary to LaTeX table format."""

    # Define a helper function for multirow
    def multirow_format(item):
        if isinstance(item, tuple):
            return f"\\multirow{{{item[1]}}}{{*}}{{{item[0]}}}"
        else:
            return item

    # Identify if there are multicolumns and calculate column count
    column_count = 0
    for key, value in data.items():
        if isinstance(value, dict):
            column_count += len(value)
        else:
            column_count += 1

    # Begin table format
    latex_str = "\\begin{table}\n" 
    latex_str += "\caption{\label{%s} %s}\n"%(label, caption)
    latex_str += "  \\centering\n"
    latex_str += "  \\resizebox{\\textwidth}{!}{\n"
    latex_str += "  \\begin{tabular}{" + "c" * column_count + "}\n"

    # Header
    for key, value in data.items():
        if isinstance(value, dict):
            latex_str += f" \\multicolumn{{{len(value)}}}{{|c|}}{{{key}}} & "
        else:
            latex_str += key + " & "

    latex_str = latex_str.rstrip(" & ") + "\\\\\n"
    latex_str += "  \\hline\n"

    # Subheaders for multicolumns
    has_subheaders = any(isinstance(value, dict) for value in data.values())
    if has_subheaders:
        for key, value in data.items():
            if isinstance(value, dict):
                for sub_key in value.keys():
                    latex_str += sub_key + " & "
            else:
                latex_str += "& "
        latex_str = latex_str.rstrip(" & ") + "\\\\\n"

    # Rows
    row_count = max(len(value) if not isinstance(value, dict) else max(len(sub_value) for sub_value in value.values()) for value in data.values())
    for i in range(row_count):
        for key, value in data.items():
            if isinstance(value, dict):
                for sub_key in value.keys():
                    if i < len(value[sub_key]):
                        latex_str += "  " + multirow_format(value[sub_key][i]) + " & "
                    else:
                        latex_str += "& "
            else:
                if i < len(value):
                    latex_str += "  " + multirow_format(value[i]) + " & "
                else:
                    latex_str += "& "
                    
        latex_str = latex_str.rstrip(" & ") + "\\\\\n"
    # End table format
    latex_str += "  \\end{tabular}}\n"
    latex_str += "\\end{table}\n"

    return latex_str

if __name__ == "__main__":
    # Example usage:
    data = {
        "Name": ["John", "Doe", ('Jack', 2), "Alice"],
        "Scores": {
            "Math": ["85", "90", "78", "95"],
            "Physics": ["80", "89", "88", "92"]
        }
    }
    print(dict_to_latex_table(data))

    
