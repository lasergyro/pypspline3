#!/usr/local/env python

# $Id: test_bound1_r8.py,v 1.1 2004/03/30 16:33:19 pletzer Exp $

import numpy as np
from pypspline.pspline_1d import pspline
EPS = 1.e-6

import pytest

def periodic1():
    n1 = 11
    x1 = np.linspace(0., 2*np.pi, n1)
    ff = np.cos(x1)
    spl = pspline(x1, bcs1=1)
    spl.setup(ff)
    x1 = np.linspace(0., 2*np.pi, n1-1)
    ff = np.cos(x1)
    ffi, ier, iwarn = spl.interp_array(x1)
    return np.sqrt(np.sum(np.sum(np.sum( (ff-ffi)**2 )))/float(len(ff)))

def slope1():
    n1 = 11
    x1 = np.linspace(0., 2*np.pi, n1)
    ff = np.cos(x1)
    spl = pspline(x1, bcs1=(1,1))
    spl.bcval1min = 0.
    spl.bcval1max = 0.
    spl.setup(ff)
    x1 = np.linspace(0., 2*np.pi, n1-1)
    ff = np.cos(x1)
    ffi, ier, iwarn = spl.interp_array(x1)
    return np.sqrt(np.sum( (ff-ffi)**2 )/float(len(ff)))

def secondDer1():
    n1 = 11
    x1 = np.linspace(0., 2*np.pi, n1)
    ff = np.cos(x1)
    spl = pspline(x1, bcs1=(2,2))
    spl.bcval1min = 0.
    spl.bcval1max = 0.
    spl.setup(ff)
    x1 = np.linspace(0., 2*np.pi, n1-1)
    ff = np.cos(x1)
    ffi, ier, iwarn = spl.interp_array(x1)
    return np.sqrt(np.sum( (ff-ffi)**2 )/float(len(ff)))

##################################################################

def test_periodic1():
    error = periodic1()
    assert error < 2.5e-4
    print('error = %g'%error)

def test_slope1():
    error = slope1()
    assert error < 2.5e-4
    print('error = %g'%error)

def test_secondDer1():
    error = secondDer1()
    assert error < 1.5e-3
    print('error = %g'%error)

if __name__ == "__main__":
    test_periodic1()
    test_slope1()
    test_secondDer1()
