import os
import subprocess

if __name__ == '__main__':
    min_freqs = [0.05, 0.1, 0.2, 0.3, 0.4]
    max_freqs = [0.2, 0.3, 0.4, 0.5, 0.6]
    for minim in min_freqs:
        for maxim in max_freqs:
           r = os.system("python ExtractData.py --index arxiv_abs --minfreq " + str(minim) + " --maxfreq " + str(maxim))