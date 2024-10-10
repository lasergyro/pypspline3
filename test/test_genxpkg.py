
import numpy as np

from pypspline3 import fpspline as m


def test_genxpkg():
    n=10    
    x=(np.arange(n)*.5).astype(np.float32)
    v,err=m.genxpkg(x,1.)
    assert err==0
    assert np.allclose(v,np.array([ 0.00e+00,  5.00e-01,  1.00e+00,  1.50e+00,  2.00e+00,  2.50e+00,
        3.00e+00,  3.50e+00,  4.00e+00,  4.50e+00,  5.00e-01,  5.00e-01,
        5.00e-01,  5.00e-01,  5.00e-01,  5.00e-01,  5.00e-01,  5.00e-01,
        5.00e-01,  5.00e-01,  2.00e+00,  2.00e+00,  2.00e+00,  2.00e+00,
        2.00e+00,  2.00e+00,  2.00e+00,  2.00e+00,  2.00e+00,  2.00e+00,
       -2.25e-06,  1.00e+00,  0.00e+00,  1.00e+00,  0.00e+00,  0.00e+00,
        0.00e+00,  0.00e+00,  0.00e+00,  0.00e+00]))
