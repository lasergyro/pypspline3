"""
1-D spline in float64 precision
"""

import warnings as _warnings

import numpy as _np

# to get the function value
ICT_FVAL = _np.array([1, 0, 0], dtype=_np.int32)
# 1st derivatives
ICT_F1 = _np.array([0, 1], dtype=_np.int32)
ICT_GRAD = _np.array([0, 1], dtype=_np.int32)
# generic derivatives
ICT_MAP = {
    0: _np.array([1, 0, 0], dtype=_np.int32),
    1: _np.array([0, 1, 0], dtype=_np.int32),
    2: _np.array([0, 0, 1], dtype=_np.int32),
}

from . import fpspline


class pspline:
    def __init__(self, x1, bcs1=None):
        """
        Constructor.

        x1: original grid array

        bcs1: boundary conditions. Use bcs1=1 to apply
        periodic boundary conditions (bcs1 defaults to None for
        not-a-knot boundary conditions, this should be fine in most cases.
        More general boundary conditions can be applied by setting
        bcs1=(bmin, bmax)

        where bmin/bmax can take values from 0 to 7, as described in
        http://w3.pppl.gov/NTCC/PSPLINE/.

        The boundary conditions (if inhomogeneous) must then be applied
        by setting the class members

        self.bcval1min and/or self.bcval1max
        explicitly *prior* to calling self.setup(f).

        1 -- match slope
        2 -- match 2nd derivative
        3 -- boundary condition is slope=0
        4 -- boundary condition is d2f/dx2=0
        5 -- match 1st derivative to 1st divided difference
        6 -- match 2nd derivative to 2nd divided difference
        7 -- match 3rd derivative to 3rd divided difference
        For example, if one wishes to apply df/dx = a on the left and
        d^2f/dx^2 = b
        on the right of x1, use
        bcs1=(1, 2)
        and set both
        self.bcval1min = a
        and
        self.bcval1max = b
        The returned value is a spline object.
        """

        self.__x1 = x1
        self.__n1 = len(x1)

        n1 = self.__n1

        # BC types
        # use these to set the boundary conditions,
        # e.g. ibctype1=(1,0) sets the 1st derivative to the left
        # but uses not-a-knot Bcs on the right. The value of the
        # derivative would eb set via bcval1min

        if bcs1:
            if bcs1 == 1:
                # periodic
                self.__ibctype1 = (-1, -1)
            else:
                # general
                self.__ibctype1 = (bcs1[0], bcs1[1])
        else:
            # not-a-knot BCs
            self.__ibctype1 = (0, 0)

        # BC values (see above)
        self.bcval1min = 0
        self.bcval1max = 0

        # Compact cubic coefficient arrays
        self.__fspl = _np.zeros((n1, 2))

        # storage
        self.__x1pkg = None

        # check flags
        self.__isReady = 0

        # will turn out to be 1 for nearly uniform mesh
        self.__ilin1 = 0

    def setup(self, f):
        """
        Set up (compute) cubic spline coefficients.
        See __init__ for comment about boundary conditions.
        Input is f[ix], a rank-1 array for the function values.
        """

        if _np.shape(f) != (self.__n1,):
            raise "pspline1_r4::setup shape error. Got shape(f)=%s should be %s" % (
                str(_np.shape(f)),
                str((self.__n1,)),
            )

        # default values for genxpg
        imsg = 0
        itol = 0  # range tolerance option
        ztol = 5.0e-7  # range tolerance, if itol is set
        ialg = -3  # algorithm selection code

        iper = 0
        if self.__ibctype1[0] == -1 or self.__ibctype1[1] == -1:
            iper = 1
        self.__x1pkg, ifail = fpspline.genxpkg(self.__x1, iper)
        if ifail != 0:
            raise "pspline1_r4::setup failed to compute x1pkg"

        self.__isReady = 0

        self.__fspl[:, 0] = f

        self.__ilin1, ifail = fpspline.mkspline(
            self.__x1,
            self.__fspl.flat,
            self.__ibctype1[0],
            self.bcval1min,
            self.__ibctype1[1],
            self.bcval1max,
        )

        if ifail != 0:
            raise "pspline1_r4::setup mkspline error"

        self.__isReady = 1

    def interp_point(self, p1):
        """
        Point interpolation at p1.
        """

        iwarn = 0
        fi, ier = fpspline.evspline(
            p1, self.__x1, self.__ilin1, self.__fspl.flat, ICT_FVAL
        )
        return fi, ier, iwarn

    def interp_cloud(self, p1):
        """
        Cloud interpolation for all p1[:].
        In 1-D, this is the same as interp_array.
        Return the interpolated function, an error flag  (=0 if ok) and a warning flag (=0 if ok).
        """

        fi, iwarn, ier = fpspline.vecspline(
            ICT_FVAL, p1, self.__x1pkg, self.__fspl.flat
        )
        return fi, ier, iwarn

    def interp_array(self, p1):
        """
        Array interpolation for all p1[i1], i1=0:len( p1 ).
        In 1-D, this is the same as interp_cloud.
        Return the interpolated function, an error flag  (=0 if ok) and a warning flag (=0 if ok).
        """

        fi, iwarn, ier = fpspline.vecspline(
            ICT_FVAL, p1, self.__x1pkg, self.__fspl.flat
        )

        return fi, ier, iwarn

    def interp(self, p1, meth=None):
        """
        Interpolatate onto p1, the coordinate which can either be a single point
        (point interpolation) or an array  (cloud/array interpolation).
        The returned value is a single float for point interpolation,
        it is a rank-1 array of length len(p1) for cloud/array interpolation.
        The meth argument has no effect, its purpose is to provide compatibility
        with higher order spline methods.
        With checks enabled.
        """

        if self.__isReady != 1:
            raise "pspline1_r4::interp: spline coefficients were not set up!"

        if type(p1) == _np.float64:
            fi, ier, iwarn = self.interp_point(p1)
        else:
            fi, ier, iwarn = self.interp_cloud(p1)

        if ier:
            raise "pspline1_r4::interp error ier=%d" % ier
        if iwarn:
            _warnings.warn("pspline1_r4::interp abscissae are out of bound!")

        return fi

    def derivative_point(self, i1, p1):
        """
        Compute a single point derivative d^i1 f/dx1^i1 at p1.
        Must have i1>=0 and i1<=2.
        Return the interpolated function, an error flag  (=0 if ok) and a warning flag (=0 if ok).
        """

        iwarn = 0
        fi, ier = fpspline.evspline(
            p1, self.__x1, self.__ilin1, self.__fspl.flat, ICT_MAP[i1]
        )
        return fi, ier, iwarn

    def derivative_cloud(self, i1, p1):
        """
        Compute the derivative d^i1 f/dx1^i1 for a cloud p1.
        Must have i1>=0 and i1<=2.
        Return the interpolated function, an error flag  (=0 if ok) and a warning flag (=0 if ok).
        """

        fi, iwarn, ier = fpspline.vecspline(
            ICT_MAP[i1], p1, self.__x1pkg, self.__fspl.flat
        )
        return fi, ier, iwarn

    def derivative_array(self, i1, p1):
        """
        Compute the derivative d^i1 f/dx1^i1 for a grid-array p1. Must have
        i1>=0 and i1<=2. Same as derivative_cloud in 1-D.
        Return the interpolated function, an error flag  (=0 if ok) and a warning flag (=0 if ok).
        """

        fi, iwarn, ier = fpspline.vecspline(
            ICT_MAP[i1], p1, self.__x1pkg, self.__fspl.flat
        )
        return fi, ier, iwarn

    def derivative(self, i1, p1, meth=None):
        """
        Compute the derivative d^i1 f/dx1^i1 at p1. Must have
        i1>=0 and i1<=2. See interp method for a list of possible p1 shapes.

        The meth argument has no effect, its purpose is to provide compatibility
        with higher order spline methods.

        With checks enabled.
        """

        if self.__isReady != 1:
            raise "pspline1_r4::derivative: spline coefficients were not set up!"

        if type(p1) == _np.float64:
            fi, ier, iwarn = self.derivative_point(i1, p1)
        else:
            fi, ier, iwarn = self.derivative_cloud(i1, p1)

        if ier:
            raise "pspline1_r4::derivative error"
        if iwarn:
            _warnings.warn("pspline1_r4::derivative abscissae are out of bound!")

        return fi
