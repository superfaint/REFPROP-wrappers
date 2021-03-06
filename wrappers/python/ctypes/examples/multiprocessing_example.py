"""
An example of the use of the multiprocessing library in concert with the 
ctREFPROP wrapper to evaluate many thermodynamic state points

By Ian Bell, NIST, 2018 (ian.bell@nist.gov)
"""

# Python standard library
import os, timeit, itertools
from multiprocessing import Pool

# Pip installable packages
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary

# Conda packages
import numpy as np

def parallel_evaluate(mixture):
    """ 
    Fully encapsulated for multiprocessing support 
    Fresh copy of REFPROP will be loaded into each instance, for parallelism
    """
    root = os.environ['RPPREFIX']
    R = REFPROPFunctionLibrary(root)
    R.SETPATHdll(root)
    components, compositions = mixture
    names = '*'.join([f+'.FLD' for f in components])
    r = R.REFPROPdll(names, 'TP', 'D', R.MOLAR_BASE_SI,0,0,300,10e3,compositions)
    if r.ierr == 0:
        return [r.Output[0]]
    else:
        return r.herr
    return out 
            
if __name__=='__main__':
    
    # Build the inputs
    inputs = []
    pairs = [['METHANE','ETHANE'],['PROPANE','DECANE']]
    for pair in pairs:
        for z0 in np.linspace(0,1,30):
            inputs.append((pair, np.array([z0,1-z0])))

    # Serial evaluation
    tic = timeit.default_timer()
    outserial = list(map(parallel_evaluate, inputs))
    toc = timeit.default_timer()
    print(toc-tic, 's for serial evaluation')

    # Parallel evaluation
    p = Pool(2)
    tic = timeit.default_timer()
    outparallel = p.map(parallel_evaluate, inputs)
    toc = timeit.default_timer()
    print(toc-tic, 's for parallel evaluation')

    # Unravel the nested lists
    serial = np.array(list(itertools.chain.from_iterable(outserial)))
    parallel = np.array(list(itertools.chain.from_iterable(outparallel)))
    err = 100*(serial/parallel-1)

    print('error: ', err, '%')