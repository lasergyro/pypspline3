#!/usr/bin/env python
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

if __name__=="__main__":
    with TemporaryDirectory() as tmpdir:
        pin,pout=Path(sys.argv[-2]),Path(sys.argv[-1])
        tmp=Path(tmpdir)
        p2=tmp/'input.pyf'
        shutil.copy(pin,p2)
        shutil.copy(Path(__file__).parent/'.f2py_f2cmap',tmp)
        subprocess.run(f"python -m numpy.f2py input.pyf",shell=True,check=True,cwd=tmp)
        for p in tmp.iterdir():
            if p!=p2 and p.suffix=='.c':
                break
        else:
            raise ValueError
        shutil.copy(p,pout)