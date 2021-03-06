'''
Script to find best hyper params from a set of output logs

Inputs == directory of outputs (string)
Outputs == numpy array with values of min_objective, epsilon, beta, M

'''

import re
import glob
import numpy as np
import json
import ipdb

searches = [
    ["control_mm_gauss", False],
    ["control_log_gauss", False],
    ["control_rw", False],
    ["MJHMC_mm_gauss", False],
    ["MJHMC_log_gauss", False],
    ["MJHMC_rw", False],
    ["LAHMC_mm_gauss", True]]


def find(directory, lahmc):
    #List files
    files = glob.glob(directory + '*')
    #Result array
    if lahmc:
        results = np.zeros((len(files),5),dtype='float32')
    else:
        results = np.zeros((len(files),4),dtype='float32')
    #Counter
    ii = 0
    for fname in files:
        for line in open(fname,'r'):
            if re.search('\'main\'',line):
                results[ii, 0] = np.float32(line.split(':')[1].split('}')[0])
            if re.search('epsilon',line):
                try:
                    results[ii, 1] = np.float32(line.split('\'epsilon\': array([')[1].split('])')[0])
                    results[ii, 2] = np.float32(line.split('\'beta\': array([')[1].split('])')[0])
                    results[ii, 3] = np.float32(line.split('\'num_leapfrog_steps\': array([')[1].split('])')[0])
                except:
                    ipdb.set_trace()
                if lahmc:
                    results[ii, 4] = np.float32(line.split('\'num_look_ahead_steps\': array([')[1].split('])')[0])
                ii = ii +1
    return results

def write_best(results, directory):
    # occurs when search is running sometimes
    results = results[results[:, -1] != 0]
    min_idx = np.argmin(results[:,0])
#    min_idx = np.argsort(results[:,0])[1]
    best_par = results[min_idx]
    params = {
        'epsilon' : float(best_par[1]),
        'beta' : float(best_par[2]),
        'num_leapfrog_steps' : int(best_par[3])
    }
    if len(best_par) == 5:
        params.update({'num_look_ahead_steps' : int(best_par[4])})
    with open("{}/params.json".format(directory), 'w') as d:
        json.dump(params, d)

def write_all():
    for directory, lahmc in searches:
        results = find("{}/output/".format(directory), lahmc)
        write_best(results, directory)

def make_standard(data):

    return smaller_mat
