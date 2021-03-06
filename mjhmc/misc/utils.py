import numpy as np


# external code from stackoverflow: http://stackoverflow.com/questions/1167617/in-python-how-do-i-indicate-im-overriding-a-method
def overrides(interface_class):
    """
    override decorator. need to specify the super class, unfortunately
    """
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider


def min_idx(draws):
    """
    selects the argmin of the row wise minimum
    returns a list of rows where each input draw was min
    draws: a list of the various draws

    eg: draws = [fl_draws, f_draws] where fl_draws.shape = f_draws.shape = (1, N)
    returns fl_idx, f_idx where fl_idx (and the others) are
    arrays of shape (nbatch,) containing the indices of the rows where each variable was
    the minimum
    """
    cdraws = np.concatenate(draws, axis=0)
    transition_idx = np.argmin(cdraws, axis=0)
    return [np.where(transition_idx == i)[0] for i in xrange(len(draws))]


def draw_from(rates):
    """
    returns an array of draws from an exponential distribution with rate
    """
    assert rates.ndim == 1
    return np.array([np.random.exponential(scale=1./rate)
                     if rate != 0 else np.inf
                     for rate in rates]).reshape(1, len(rates))


def normalize_by_row(matrix):
    row_sums = matrix.sum(axis=1)
    # replaces 0 with 1 to avoid divide by 0
    np.place(row_sums, row_sums == 0, 1)
    norm_matrix = matrix / row_sums[:, np.newaxis]
    return norm_matrix
