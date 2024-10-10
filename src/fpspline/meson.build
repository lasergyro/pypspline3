# project('fpspline', 'c',
#   version : '0.1',
#   license: 'BSD-3',
#   meson_version: '>=0.64.0',
#   default_options : ['warning_level=2'],
# )

add_languages('fortran')

incdir_numpy = run_command(py,
  ['-c', 'import os; os.chdir(".."); import numpy; print(numpy.get_include())'],
  check : true
).stdout().strip()

incdir_f2py = run_command(py,
    ['-c', 'import os; os.chdir(".."); import numpy.f2py; print(numpy.f2py.get_include())'],
    check : true
).stdout().strip()

inc_np = include_directories(incdir_numpy, incdir_f2py)


fpspline_sources = files(
    'cspline.f90',
    'evbicub.f90',
    'evspline.f90',
    'evtricub.f90',
    'genxpkg.f90',
    'gridbicub.f90',
    'gridtricub.f90',
    'herm1ev.f90',
    'herm2ev.f90',
    'herm3ev.f90',
    'ibc_ck.f90',
    'mkbicub.f90',
    'mkspline.f90',
    'mktricub.f90',
    'splinck.f90',
    'vecbicub.f90',
    'vecspline.f90',
    'vectricub.f90',
    'v_spline.f90',
    'xlookup.f90',
    'zonfind.f90',
)

module_source = custom_target('fpsplinemodule.c',
  input : ['fpspline.pyf'],
  output : ['fpsplinemodule.c'],
  command : ['run_f2py_simple.py', '@INPUT@','@OUTPUT@']
)


py.extension_module('fpspline',
  fpspline_sources+module_source,
  incdir_f2py / 'fortranobject.c',
  include_directories: inc_np,
  dependencies : py_dep,
  install : true,
  subdir: 'pypspline3',
)
