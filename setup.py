from numpy.distutils.core import setup, Extension
from numpy import get_include
import numpy.version
from distutils.version import StrictVersion

import generatePyCamb
import os.path
import os
import sys
from subprocess import call
if '--nonstop' in sys.argv:
    sys.argv.remove('--nonstop')
    from nonstopf2py import f2py
else:
    from numpy import f2py

# Look in sys.argv for a url to get CAMB from (we can't use the url here
# because of licensing).
url = os.getenv('CAMBURL', None)
print "*****", url
if url is not None:
    fname = url.split("/")[-1]
    # Get CAMB from http://camb.info, untar and copy *.[fF]90 to src/
    # this is done by the script extract_camb.sh
    call(["wget", url])
    call(["tar", "-xzvf", fname])
    call(["rm", fname])

#sys.exit()
# List of all sources that must be there
cambsources = ['CAMB-March2013/%s' % f for f in [
    'constants.f90',
    'utils.F90',
    'subroutines.f90',
    'inifile.f90',
    'power_tilt.f90',
    'recfast.f90',
    'reionization.f90',
    'modules.f90',
    'bessels.f90',
    'equations.f90',
    'halofit.f90',
    'lensing.f90',
    'SeparableBispectrum.F90',
    'cmbmain.f90',
    'camb.f90',
]]

# Check if all sources are in fact there
for f in cambsources:
    if not os.path.exists(f):
        raise Exception("At least one of CAMB code file: '%s' is not found. Download and extract to camb/" % f)

# Make folder "src" unless already made
try: os.mkdir('src')
except: pass
generatePyCamb.main()

# Generate .pyf wrappers
f2py.run_main(['-m', '_pycamb', '-h', '--overwrite-signature', 'src/py_camb_wrap.pyf',
         'src/py_camb_wrap.f90', 'skip:', 'makeparameters', ':'])

# Newer versions of f2py (from numpy >= 1.6.2) use specific f90 compile args
if StrictVersion(numpy.version.version) > StrictVersion('1.6.1'):
    pycamb_ext = Extension("pycamb._pycamb",
                           ['src/py_camb_wrap.pyf'] + cambsources + ['src/py_camb_wrap.f90'],
                           extra_f90_compile_args=['-ffree-line-length-none','-O0', '-g', '-Dintp=npy_intp', '-fopenmp'],
                           libraries=['gomp'],
                           include_dirs=[get_include()],
                           )
else:
    Extension("pycamb._pycamb",
             ['src/py_camb_wrap.pyf'] + cambsources + ['src/py_camb_wrap.f90'],
             extra_compile_args=['-O0', '-g', '-Dintp=npy_intp'],
             include_dirs=[get_include()],
             )

# Perform setup
setup(name="pycamb", version="0.3",
      author="Joe Zuntz",
      author_email="joezuntz@googlemail.com",
      description="python binding of camb, you need sign agreement and obtain camb source code to build this. Thus we can not GPL this code.",
      url="http://github.com/joezuntz/pycamb",
      zip_safe=False,
      install_requires=['numpy'],
      requires=['numpy'],
      packages=[ 'pycamb' ],
      package_dir={'pycamb': 'src'},
      data_files=[('pycamb/camb', ['CAMB-March2013/HighLExtrapTemplate_lenspotentialCls.dat'])],
      scripts=[],
      ext_modules=[pycamb_ext]
    )
