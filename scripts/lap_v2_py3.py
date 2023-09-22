"""
lap

A python module that provides methods for calculating projections
and predictivity based on a set of basis samples.

"""

import numpy as np
import scipy.stats as sps

#%% #############################
def check_type_data(data, data_type=np.ndarray, dim=2):
    """ Some basic type checking on data """
    
    # Code assumes that we have a matrix, so force it for single samples
    if len(data.shape)==1:
        data = data.reshape((data.size,1))
    
    if type(data) != data_type:
        raise TypeError('data is not a numpy array!')
    if len(data.shape) != dim:
        raise TypeError('basis is not a numpy array of dimension 2!')
        
    return data
        
#%% #############################
def check_type_basis(basis, basis_type=np.ndarray, dim=2):
    """ Some basic type checking on basis """
    if type(basis) != basis_type:
        raise TypeError('basis is not a numpy array!')
    if len(basis.shape) != dim:
        raise TypeError('basis is not a numpy array of dimension 2!')

#%% #############################
def lap(basis, data, full_output=False):
    """
    Calculates projections of data onto basis. Always returns projections,
    optionally can also return correlation matrix of basis and predictivity
    of basis.
    
    Inputs:
    basis = (N,p_b) array with p_b basis samples and N observations
    data = (N,p_d) array with p_d samples and N observations or
            (N,) array for single sample
    full_output =   False only returns projections (a)
                    True returns projections (a), correlation of basis (A),
                       and predictivity of basis (eta) 

    Outputs:
    output = projections and optionally correlations and predictivity
                of basis
    
    """    
    
    check_type_basis(basis)
    N_basis, p_basis = basis.shape

    data = check_type_data(data)
    N_data, p_data = data.shape

    # check if basis and data have the same number of observations
    if N_basis != N_data:
        raise ValueError('basis and data do not have the same number of observations!')

    # check if full_output is a boolean
    if type(full_output) != bool:
        raise TypeError('full_output is not a boolean!')

    A = np.dot(basis.T, basis) / N_basis
    eta = np.linalg.solve(A, basis.T) / N_basis
    a = np.dot(eta, data)

    if full_output:
        output = [a, A, eta]
    else:
        output = a

    return output

#%% #############################
def rank_norm(data, dist='normal', norm=None):
    """ 
    Calculates rank norm of data. Each column is assumed to be an 
    independent sample while each row is an observation. Each column
    is ranked amongst itself and then the ranked data gets adjusted
    by dist and norm.
    
    Inputs:
    data = (N,p) array with p samples and N observations or
            (N,) array for single sample
    dist = distribution that each sample will match. Options include
            normal, uniform, or None
    norm = Can further adjust each sample to fix its L2 norm. Options 
            include an integer, float, or None

    Outputs:
    output_data = N by p array that has been ranked, 
                    and potentially fit to a distribution and a given norm

    """
    if dist not in ['normal', 'uniform',None]:
        raise TypeError('dist can be either normal or uniform!')
    if type(norm) not in [int,float,type(None)]:
        raise TypeError('norm must be None, integer, or float!')

    data = check_type_data(data)
    N, p = data.shape
    
    # Calculate rank for each sample
    rank_data = np.zeros((N,p))
    for i in range(p):
        # by default, ties method is average
        rank_data[:,i] = sps.rankdata(data[:,i]) 

    # Forces the ranked data to fit a certain distribution
    if dist == 'normal':
        # Converts rank_data to percentile, then normal
        output_data = sps.norm.ppf(rank_data / (N+1))
    elif dist == 'uniform':
        # Scales each sample to 0,1 inclusive
        output_data = (rank_data-1) / (N-1)
    elif dist is None:
        output_data = rank_data

    # Adjusts the L2 norm
    if norm is not None:
        current_norm = np.sum(output_data**2,axis=0)        
        output_data = output_data * np.sqrt(norm/current_norm)        

    return output_data

#%% #############################
if __name__ == '__main__':
    a = np.random.rand(3, 2)
    b = np.random.rand(3, 2)
    print(lap(a, b))
