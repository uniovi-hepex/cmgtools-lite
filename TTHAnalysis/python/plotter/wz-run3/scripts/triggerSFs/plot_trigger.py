import os
import sys
import json
import numpy as np
import matplotlib.pyplot as plt

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def plot_efficiency_comparison_perMeasurement(data_folder, mode, years):
    channels = ['inclusive', 'lowpt', 'highpt', 'barrel0', 'barrel1', 'barrel2', 'barrel3']
    x_values = range(len(channels))


    for idx, year in enumerate(years):

        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 8), sharex='col', gridspec_kw={'height_ratios': [7, 3]})
        data_efficiencies = {channel: {'eff': 0, 'eff_errup': 0, 'eff_errdn': 0} for channel in channels}
        mc_efficiencies = {channel: {'eff': 0, 'eff_errup': 0, 'eff_errdn': 0} for channel in channels}

        # Read data_results.json
        for channel in channels:
            data_file_path = os.path.join(data_folder, year, "inclusive", channel, 'data_results.json')
            if os.path.exists(data_file_path):
                data_json = read_json_file(data_file_path)
                data_efficiencies[channel]['pass_num'] = data_json['pass_num']
                data_efficiencies[channel]['pass_den'] = data_json['pass_den']
                data_efficiencies[channel]['eff'] = data_json['eff']
                data_efficiencies[channel]['eff_errup'] = data_json['eff_errup']
                data_efficiencies[channel]['eff_errdn'] = data_json['eff_errdn']

        # Read mc_results.json
        for channel in channels:
            mc_file_path = os.path.join(data_folder, year, "inclusive", channel, 'mc_results.json')
            if os.path.exists(mc_file_path):
                mc_json = read_json_file(mc_file_path)
                mc_efficiencies[channel]['pass_num'] = mc_json['pass_num']
                mc_efficiencies[channel]['pass_den'] = mc_json['pass_den']
                mc_efficiencies[channel]['eff'] = mc_json['eff']
                mc_efficiencies[channel]['eff_errup'] = mc_json['eff_errup']
                mc_efficiencies[channel]['eff_errdn'] = mc_json['eff_errdn']        

        # Calculate ratios
        data_ratios = {channel: data_efficiencies[channel]['eff'] / mc_efficiencies[channel]['eff'] for channel in channels}

        # Plot data and MC for each channel
        first = True
        for channel, x in zip(channels, x_values):
            # Upper subplot: Efficiency comparison
            axes[0].errorbar(x, data_efficiencies[channel]['eff'], yerr=[[data_efficiencies[channel]['eff_errdn']], [data_efficiencies[channel]['eff_errup']]], fmt='ro', label='Data' if channel == 'inclusive' else '')
            axes[0].errorbar(x, mc_efficiencies[channel]['eff'], yerr=[[mc_efficiencies[channel]['eff_errdn']], [mc_efficiencies[channel]['eff_errup']]], fmt='ko', label='MC' if channel == 'inclusive' else '')

            # Lower subplot: Ratio
            axes[1].plot(x, data_ratios[channel], 'bo' if idx == 0 else 'bo')

# Add labels below each point
            #axes[0, idx].text(x+0.05, data_efficiencies[channel]['eff'] - 0.15, f"Data: {data_efficiencies[channel]['pass_num']}/{data_efficiencies[channel]['pass_den']:.2f}", ha='left', fontsize=8)
            #axes[0, idx].text(x+0.05, data_efficiencies[channel]['eff'] - 0.17, f"MC: {mc_efficiencies[channel]['pass_num']}/{mc_efficiencies[channel]['pass_den']:.2f}", ha='left', fontsize=8)


        axes[0].set_xticks(x_values)
        axes[0].set_xticklabels(channels)
        axes[0].set_title(f'{year}')
        axes[0].set_ylabel('Efficiency')
        axes[0].set_ylim(0.8, 1.05)  # Set y-axis range
        axes[0].legend()
        axes[0].grid(True)

        # Lower subplot settings
        if year == "PreEE":
          ylimvals_ratio = 0.975, 1.025
          window = 0.003
        elif year == "PostEE":
          ylimvals_ratio = 0.975, 1.025
          window = 0.01
        axes[1].set_xticks(x_values)
        axes[1].set_xticklabels(channels)
        axes[1].set_ylabel('Data/MC')
        axes[1].fill_between(x_values, 1-window, 1+window, where=[0.9 <= ratio <= 1.1 for ratio in data_ratios.values()], color='gray', alpha=0.2)
        axes[1].set_ylim(ylimvals_ratio[0], ylimvals_ratio[1])  # Set y-axis range
        axes[1].grid(True)

        plt.tight_layout()
        fig.savefig("%s-perMeasurement-%s.png"%(mode, year))

def plot_efficiency_comparison(data_folder, mode, years):
    channels = ['eee', 'eem', 'mme', 'mmm', 'inclusive']
    x_values = range(len(channels))

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 8), sharex='col', gridspec_kw={'height_ratios': [7, 3]})

    for idx, year in enumerate(years):
        data_efficiencies = {channel: {'eff': 0, 'eff_errup': 0, 'eff_errdn': 0} for channel in channels}
        mc_efficiencies = {channel: {'eff': 0, 'eff_errup': 0, 'eff_errdn': 0} for channel in channels}

        # Read data_results.json
        for channel in channels:
            data_file_path = os.path.join(data_folder, year, channel, mode, 'data_results.json')
            if os.path.exists(data_file_path):
                data_json = read_json_file(data_file_path)
                data_efficiencies[channel]['pass_num'] = data_json['pass_num']
                data_efficiencies[channel]['pass_den'] = data_json['pass_den']
                data_efficiencies[channel]['eff'] = data_json['eff']
                data_efficiencies[channel]['eff_errup'] = data_json['eff_errup']
                data_efficiencies[channel]['eff_errdn'] = data_json['eff_errdn']

        # Read mc_results.json
        for channel in channels:
            mc_file_path = os.path.join(data_folder, year, channel, mode, 'mc_results.json')
            if os.path.exists(mc_file_path):
                mc_json = read_json_file(mc_file_path)
                mc_efficiencies[channel]['pass_num'] = mc_json['pass_num']
                mc_efficiencies[channel]['pass_den'] = mc_json['pass_den']
                mc_efficiencies[channel]['eff'] = mc_json['eff']
                mc_efficiencies[channel]['eff_errup'] = mc_json['eff_errup']
                mc_efficiencies[channel]['eff_errdn'] = mc_json['eff_errdn']

        # Calculate ratios
        data_ratios = {channel: data_efficiencies[channel]['eff'] / mc_efficiencies[channel]['eff'] for channel in channels}

        # Plot data and MC for each channel
        first = True
        for channel, x in zip(channels, x_values):
            # Upper subplot: Efficiency comparison
            axes[0, idx].errorbar(x, data_efficiencies[channel]['eff'], yerr=[[data_efficiencies[channel]['eff_errdn']], [data_efficiencies[channel]['eff_errup']]], fmt='ro', label='Data' if channel == 'eee' else '')
            axes[0, idx].errorbar(x, mc_efficiencies[channel]['eff'], yerr=[[mc_efficiencies[channel]['eff_errdn']], [mc_efficiencies[channel]['eff_errup']]], fmt='ko', label='MC' if channel == 'eee' else '')

            # Lower subplot: Ratio
            axes[1, idx].plot(x, data_ratios[channel], 'bo' if idx == 0 else 'bo')

# Add labels below each point
            #axes[0, idx].text(x+0.05, data_efficiencies[channel]['eff'] - 0.15, f"Data: {data_efficiencies[channel]['pass_num']}/{data_efficiencies[channel]['pass_den']:.2f}", ha='center', fontsize=8)
            #axes[0, idx].text(x+0.05, data_efficiencies[channel]['eff'] - 0.20, f"MC: {mc_efficiencies[channel]['pass_num']}/{mc_efficiencies[channel]['pass_den']:.2f}", ha='center', fontsize=8)

        axes[0, idx].set_xticks(x_values)
        axes[0, idx].set_xticklabels(channels)
        axes[0, idx].set_title(f'Efficiency Comparison for Data Taking Year {year}')
        axes[0, idx].set_xlabel('Channel')
        axes[0, idx].set_ylabel('Efficiency')
        axes[0, idx].set_ylim(0.8, 1.05)  # Set y-axis range
        if idx == 0:
            axes[0, idx].legend()
        axes[0, idx].grid(True)

        # Lower subplot settings
        axes[1, idx].set_xticks(x_values)
        axes[1, idx].set_xticklabels(channels)
        axes[1, idx].set_title(f'Data/MC Ratio for Data Taking Year {year}')
        axes[1, idx].set_xlabel('Channel')
        axes[1, idx].set_ylabel('Ratio')
        axes[1, idx].fill_between(x_values, 0.98, 1.02, where=[0.9 <= ratio <= 1.1 for ratio in data_ratios.values()], color='gray', alpha=0.2)
        axes[1, idx].set_ylim(0.97, 1.03)  # Set y-axis range
        axes[1, idx].grid(True)

    plt.tight_layout()
    fig.savefig("%s-perFlavor.png"%mode)

# Example usage
data_folder = 'results'
years = ['PreEE', 'PostEE']

plot_efficiency_comparison_perMeasurement(data_folder, "inclusive", years)
for mode in ["inclusive", "lowpt", "highpt", "barrel0", "barrel1", "barrel2", "barrel3"]:
    plot_efficiency_comparison(data_folder, mode, years)

