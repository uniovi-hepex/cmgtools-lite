import matplotlib.pyplot as plt
import sys

def read_txt_to_data(filename):
    # Read the txt file
    with open(filename, 'r') as f:
        lines = f.readlines()

    names = []
    values = []

    for line in lines:
        # Splitting by ':' and taking the last value (the float value)
        parts = line.split(':')
        if len(parts) < 3:  # Ignoring lines that don't match the pattern
            continue
        names.append(parts[2].strip())
        values.append(float(parts[3].strip()))

    return names, values

def plot_histogram(names, values, what, outname):
    plt.barh(names, values, color='skyblue')
    plt.xlabel('Relative importance')
    plt.ylabel('Variable Name')
    plt.title('TMVA feature importance ranking')
    plt.gca().invert_yaxis()  # To have the 1st entry at the top
    plt.tight_layout()
    plt.savefig("%s/%s_ranking.png"%(outname, what))
if __name__ == '__main__':
    what=sys.argv[1]
    outname=sys.argv[2]
    names, values = read_txt_to_data('ranking_tables/%s_table.txt'%(what))
    plot_histogram(names, values, what, outname)







