"""Find a candidate primal and dual. Floating values are proposals for verify.py."""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import eigh, qr
from scipy.optimize import brentq
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0,str(ROOT))
from model.executable_model import cell, federation
from model.candidate_laws.contrast_memory_spherical_v1 import candidate as contrast

REVISION = '912d25da4efbdae9344e4198e75ac8ad93125a88'
SOURCES = [
    'model/executable_model/__init__.py',
    'model/executable_model/carrier.py',
    'model/executable_model/carriers/FEDERATION_LEVEL0.npz',
    'model/candidate_laws/contrast_memory_spherical_v1/candidate.py',
    'model/candidate_laws/contrast_memory_spherical_v1/law.py',
    'model/candidate_laws/interval_echo/candidate.py',
    'model/candidate_laws/interval_echo/currents.py',
    'model/experiments/interval_echo_gauge/singlet_flight/measure.py',
    'model/experiments/interval_echo_gauge/singlet_flight/PROTOCOL.md',
    'model/experiments/interval_echo_gauge/singlet_flight/README.md',
]


def run():
    from fractions import Fraction as F
    board, local = federation(0), cell()
    adjacency = local.adjacency().toarray().astype(int)
    distances = np.where(adjacency,1,99)
    np.fill_diagonal(distances,0)
    for k in range(12):
        distances = np.minimum(distances,distances[:,k,None]+distances[None,k,:])
    anti = distances.argmax(axis=1)
    p = (np.eye(12)-np.eye(12)[anti])@(np.eye(12)+adjacency/np.sqrt(5))/4
    b = np.eye(12)-p
    _,_,pivot = qr(b,pivoting=True)
    columns = sorted(map(int,pivot[:9]))
    s = np.zeros((240,9))
    s[:12] = b[:,columns]
    w = s.T@s
    h = board.laplacian().toarray()/2-3*np.eye(240)
    native = contrast.generator(board,8).toarray()-51*np.eye(240)
    if not np.array_equal(h,native):
        raise ValueError('native generator differs')
    ev,z = eigh(h)
    zs = z.T@s
    q = np.kron(np.eye(20),p)
    u = z@(np.exp(-1j*ev)[:,None]*zs)
    a = u[12:].conj().T@u[12:]
    g = np.zeros((9,9),complex)
    nodes,weights = leggauss(48)
    for t,weight in zip((nodes+1)/2,weights/2):
        x = z@(np.exp(-1j*t*ev)[:,None]*zs)
        g += weight*x.conj().T@q@x
    def top(mu):
        values,vecs = eigh(a-mu*g,w)
        v = vecs[:,-1]
        return values[-1],v,float((v.conj()@g@v).real)
    # Leave a strict feasibility margin so decimal serialization cannot sit on equality.
    target = 0.001-1e-9
    hi = 1.
    while top(hi)[2] > target:
        hi *= 2
    mu = brentq(lambda m:top(m)[2]-target,0,hi,xtol=1e-13)
    lam,v,leakage = top(mu)
    arrival = float((v.conj()@a@v).real)
    v *= np.exp(-1j*np.angle(v[np.argmax(abs(v))]))
    encoded = [[[str(F(int(i==j)-int(anti[i]==j),4)),str(F(int(adjacency[i,j])-int(adjacency[anti[i],j]),20))] for j in range(12)] for i in range(12)]
    # Slack is part of the proposed certificate and is checked by interval LDL.
    mu_text = format(mu,'.12f')
    lambda_text = format(lam+1e-7,'.12f')
    lower = format(arrival-1e-7,'.12f')
    upper = str(F(lambda_text)+F(mu_text)/1000+F(1,10**10))
    data = {'revision':REVISION,'time':'1','budget':'1/1000',
            'source_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES},
            'edges':[list(e) for e in board.seams], 'projector':encoded,'columns':columns,
            'mu':mu_text,'lambda':lambda_text,'lower':lower,'upper':upper,
            'witness':[[format(x.real,'.16f'),format(x.imag,'.16f')] for x in v]}
    (HERE/'certificate.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({'candidate_arrival':arrival,'candidate_leakage':leakage,'mu':mu,'lambda':lam,'lower':lower,'upper':upper,'columns':columns},indent=2))


if __name__ == '__main__':
    run()
