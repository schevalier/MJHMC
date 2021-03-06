import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import json

from LAHMC import LAHMC

from mjhmc.samplers.markov_jump_hmc import MarkovJumpHMC, ControlHMC
from mjhmc.misc.autocor import calculate_autocorrelation, autocorrelation
from mjhmc.misc.nutshell import sample_nuts_to_df

# green blue palette
sns.set_palette("cubehelix", n_colors=4)
sns.set_context("talk")
sns.set_style("whitegrid")

# interactive mode for ipython
plt.ion()

std_param1 = {'epsilon': 1, 'beta': 0.1, 'num_leapfrog_steps': 10}
std_param2 = {'epsilon': 1, 'beta': .8, 'num_leapfrog_steps': 10}

def plot_ac(distribution, control_params, mjhmc_params, lahmc_params, max_steps=3000,
            sample_steps=1, truncate=False, truncate_at=0.0):
    """
    distribution is an instantiated distribution object
    runs the sampler for max steps and then truncates the output to autocorrelation 0.5
    throws an error if ac 0.5 is not reached
    """
    # control_params = {'beta': 0.5, 'epsilon': 1, "num_leapfrog_steps": 1}
#    control_params = {'beta': 0.999, 'epsilon': 1.01, "num_leapfrog_steps": 2}
    # mjhmc_params = {'beta': 0.5, 'epsilon': 1, "num_leapfrog_steps": 1}
#    mjhmc_params = {'beta': 0.999, 'epsilon': 1.01, "num_leapfrog_steps": 2}
    plt.clf()
    control_ac = calculate_autocorrelation(ControlHMC, distribution,
                                           num_steps=max_steps,
                                           sample_steps=sample_steps,
                                           half_window=True,
                                           **control_params)
    mjhmc_ac = calculate_autocorrelation(MarkovJumpHMC, distribution,
                                         num_steps=max_steps,
                                         sample_steps=sample_steps,
                                         half_window=True,
                                         **mjhmc_params)
    # lahmc_ac = calculate_autocorrelation(LAHMC, distribution,
    #                                      num_steps=max_steps,
    #                                      sample_steps=sample_steps,
    #                                      half_window=True,
    #                                      **lahmc_params)
    nuts_df = sample_nuts_to_df(distribution, 100000, n_burn_in=10000)
    nuts_ac = autocorrelation(nuts_df, half_window=True)

   # find idx with autocorrelation closest to truncate_at
    if truncate:
        control_trunc = control_ac.loc[:, 'autocorrelation'] < truncate_at
        mjhmc_trunc = mjhmc_ac.loc[:, 'autocorrelation'] < truncate_at
        nuts_trunc = nuts_ac.loc[:, 'autocorrelation'] < truncate_at
#        lahmc_trunc = lahmc_ac.loc[:, 'autocorrelation'] < truncate_at
        # error if we haven't hit autocorrelation truncate_at
#        assert len(control_trunc[control_trunc]) != 0
#        assert len(mjhmc_trunc[mjhmc_trunc]) != 0
  #      assert len(mjhmc_trunc[nuts_trunc]) != 0
#        assert len(lahmc_trunc[lahmc_trunc]) != 0
        trunc_idx = max(control_trunc[control_trunc].index[0],
                        mjhmc_trunc[mjhmc_trunc].index[0])
                        # nuts_trunc[nuts_trunc].index[0])
#                        lahmc_trunc[lahmc_trunc].index[0])
        control_ac = control_ac.loc[:trunc_idx]
        mjhmc_ac = mjhmc_ac.loc[:trunc_idx]
        nuts_ac = nuts_ac.loc[:trunc_idx]
#        lahmc_ac = lahmc_ac.loc[:trunc_idx]

    control_ac.index = control_ac['num grad']
    mjhmc_ac.index = control_ac['num grad']
    nuts_ac.index = nuts_ac['num grad']
#    lahmc_ac.index = lahmc_ac['num grad']
    control_ac['autocorrelation'].plot(label='Control HMC')
    mjhmc_ac['autocorrelation'].plot(label='Markov Jump HMC')
    nuts_ac['autocorrelation'].plot(label='NUTS')
 #   lahmc_ac['autocorrelation'].plot(label="LAHMC")
    plt.xlabel("Gradient Evaluations")
    plt.ylabel("Autocorrelation")
    plt.title("{}D {}".format(distribution.ndims, type(distribution).__name__))
    plt.legend()
    plt.show()
    plt.savefig("{}_ac.pdf".format(type(distribution).__name__))
    plt.show()

def load_params(distribution):
    dist_to_extension = {
        'RoughWell' : "rw",
        'Gaussian' : 'log_gauss',
        'MultimodalGaussian' : 'mm_gauss'
    }
    file_name = "params.json"
    extension = dist_to_extension[type(distribution).__name__]
    with open("../search/control_{}/{}".format(extension, file_name), 'r') as control:
        control_params = json.load(control)
    with open("../search/MJHMC_{}/{}".format(extension, file_name), 'r') as mjhmc:
        mjhmc_params = json.load(mjhmc)
#    with open("../search/LAHMC_{}/{}".format(extension, file_name), 'r') as lahmc:
 #       lahmc_params = json.load(lahmc)
    lahmc_params = None
    return control_params, mjhmc_params, lahmc_params

def plot_best(distribution, num_steps=100000):
    """
    plot ac with the best parameters for control and mjhmc and compare to nuts
    nbatch must be 1 for nuts comparison
    """
#    assert distribution.nbatch == 1
    control_params, mjhmc_params, lahmc_params = load_params(distribution)
    plot_ac(distribution, control_params, mjhmc_params, lahmc_params, num_steps, truncate=True, truncate_at=0.1)

def plot_std(distribution):
    # change this!!!
    steps = int(1E4)
    plt.clf()
    c_ac_1 = calculate_autocorrelation(ControlHMC, distribution,
                                       num_steps=steps,
                                       sample_steps=1,
                                       half_window=True,
                                       **std_param1)
    m_ac_1 = calculate_autocorrelation(MarkovJumpHMC, distribution,
                                       num_steps=steps,
                                       sample_steps=1,
                                       half_window=True,
                                       **std_param1)
    c_ac_2 = calculate_autocorrelation(ControlHMC, distribution,
                                       num_steps=steps,
                                       sample_steps=1,
                                       half_window=True,
                                       **std_param2)
    m_ac_2 = calculate_autocorrelation(MarkovJumpHMC, distribution,
                                       num_steps=steps,
                                       sample_steps=1,
                                       half_window=True,
                                       **std_param2)
    # c1_trunc = c_ac_1.loc[:, 'autocorrelation'] < 0.0
    # c2_trunc = c_ac_2.loc[:, 'autocorrelation'] < 0.0
    # m1_trunc = m_ac_1.loc[:, 'autocorrelation'] < 0.0
    # m2_trunc = c_ac_2.loc[:, 'autocorrelation'] < 0.0
    # trunc_idx = max(c1_trunc[c1_trunc].index[0],
    #                 c2_trunc[c2_trunc].index[0],
    #                 m1_trunc[m1_trunc].index[0],
    #                 m2_trunc[m2_trunc].index[0])
    # c_ac_1 = c_ac_1.loc[:trunc_idx]
    # c_ac_2 = c_ac_2.loc[:trunc_idx]
    # m_ac_1 = m_ac_1.loc[:trunc_idx]
    # m_ac_2 = m_ac_2.loc[:trunc_idx]
    c_ac_1.index = c_ac_1['num grad']
    c_ac_2.index = c_ac_1['num grad']
    m_ac_1.index = c_ac_1['num grad']
    m_ac_2.index = c_ac_1['num grad']
    c_ac_1.autocorrelation.plot(label=r"Control HMC $\beta = 0.1$")
    m_ac_1.autocorrelation.plot(label=r"Markov Jump HMC $\beta = 0.1$")
    c_ac_2.autocorrelation.plot(label=r"Control HMC $\beta = 0.8$")
    m_ac_2.autocorrelation.plot(label=r"Markov Jump HMC $\beta = 0.8$")
    plt.xlabel("Gradient Evaluations")
    plt.ylabel("Autocorrelation")
    plt.title("{}D {}".format(distribution.ndims, type(distribution).__name__))
    plt.legend()
    plt.savefig("{}_std.pdf".format(type(distribution).__name__))