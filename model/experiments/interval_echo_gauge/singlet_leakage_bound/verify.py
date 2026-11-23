"""Check the finite colour transport enclosure without an optimizer."""
import argparse
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import subprocess
import zipfile

from flint import acb, acb_mat, arb, ctx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REVISION = '912d25da4efbdae9344e4198e75ac8ad93125a88'
ORDER = 40
ctx.prec = 192


def require(ok, message):
    if not ok:
        raise ValueError(message)


def adj(m):
    return m.transpose().conjugate()


def eye(n):
    return acb_mat([[int(i == j) for j in range(n)] for i in range(n)])


def npy(data):
    """Read only integer NPY arrays. No NumPy code is used."""
    f = io.BytesIO(data)
    require(f.read(6) == b'\x93NUMPY', 'NPY magic')
    version = f.read(2)
    length = struct.unpack('<H' if version[0] == 1 else '<I', f.read(2 if version[0] == 1 else 4))[0]
    import ast
    header = ast.literal_eval(f.read(length).decode('latin1'))
    require(not header['fortran_order'], 'NPY order')
    dtype = header['descr']
    require(dtype in ('<i8', '<i4', '|i8', '|i4'), 'NPY integer type')
    values = list(struct.unpack('<' + ('q' if dtype.endswith('8') else 'i') * math.prod(header['shape']), f.read()))
    shape = header['shape']
    return values if len(shape) == 1 else [values[i:i + shape[1]] for i in range(0, len(values), shape[1])]


# Elements of Q(sqrt(5)) use exact pairs of rational numbers.
def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul(a, b):
    return (a[0]*b[0] + 5*a[1]*b[1], a[0]*b[1] + a[1]*b[0])


def exact_product(a, b):
    return [[sum_pairs(mul(a[i][k], b[k][j]) for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def sum_pairs(xs):
    out = (F(0), F(0))
    for x in xs:
        out = add(out, x)
    return out


def projector(internal):
    a = [[int([min(i,j), max(i,j)] in internal) for j in range(12)] for i in range(12)]
    distances = [[0 if i == j else 1 if a[i][j] else 99 for j in range(12)] for i in range(12)]
    for k in range(12):
        for i in range(12):
            for j in range(12):
                distances[i][j] = min(distances[i][j], distances[i][k] + distances[k][j])
    anti = []
    for row in distances:
        far = [i for i, d in enumerate(row) if d == 3]
        require(len(far) == 1, 'unique antipode')
        anti.append(far[0])
    p = [[(F(int(i == j) - int(anti[i] == j),4), F(a[i][j] - a[anti[i]][j],20)) for j in range(12)] for i in range(12)]
    require(exact_product(p,p) == p, 'projector idempotence')
    require(sum_pairs(p[i][i] for i in range(12)) == (3,0), 'projector rank')
    require(all(p[i][j] == p[j][i] for i in range(12) for j in range(12)), 'projector symmetry')
    aq = [[(F(x),F(0)) for x in row] for row in a]
    require(exact_product(aq,p) == [[mul((0,1),x) for x in row] for row in p], 'intended positive sqrt(5) band')
    require(all(p[i][i] == (F(1,4),0) for i in range(12)), 'sharp-port calibration')
    return p


def native_restriction(edges):
    """Check the native write invariant exactly, then assemble all one-load entries."""
    src = [(a,b) for a in range(3) for b in range(3)]
    labels = [(c,d) for c in (0,1) for d in range(-2,3)]
    w = [[0]*9 for _ in range(90)]
    for j,(a,b) in enumerate(src):
        for c in (0,1):
            s = a+b
            y = (s//2+c*(s%2),s//2+(1-c)*(s%2))
            w[9*labels.index((c,a-b))+src.index(y)][j] += 1
    require(all(sum(w[k][i]*w[k][j] for k in range(90)) == 2*int(i==j) for i in range(9) for j in range(9)), 'native write isometry')
    h2 = [[int(i==j)-int(src[i] == src[j][::-1])+16*(src[i][0]-src[i][1])**2*int(i==j) for j in range(9)] for i in range(9)]
    for k,(c,d) in enumerate(labels):
        reverse = labels.index((c,-d))
        for load in range(9):
            for j in range(9):
                left = (1+16*d*d)*w[9*k+load][j]-w[9*reverse+load][j]
                right = sum(w[9*k+load][i]*h2[i][j] for i in range(9))
                require(left == right, 'native memory invariant')
    require([[h2[i][j] for j in (3,1)] for i in (3,1)] == [[17,-1],[-1,17]], 'native seam restriction')
    degree = [0]*240
    native = [[F(0) for _ in range(240)] for _ in range(240)]
    for a,b in edges:
        degree[a] += 1
        degree[b] += 1
        native[a][a] += F(17,2)
        native[b][b] += F(17,2)
        native[a][b] -= F(1,2)
        native[b][a] -= F(1,2)
    for i in range(240):
        native[i][i] += 8*(6-degree[i])-51  # 48 native phase, then 3.
    lap = [[F(degree[i],2)-3 if i == j else F(-1,2) if native[i][j] else F(0) for j in range(240)] for i in range(240)]
    require(native == lap, 'full native restriction')
    require(max(abs(lap[i][i])+sum(abs(lap[i][j]) for j in range(240) if j != i) for i in range(240)) <= 3, 'generator norm')
    return lap, degree


def bind(data):
    require(data['revision'] == REVISION and data['time'] == '1' and data['budget'] == '1/1000', 'fixed question')
    expected = {
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
    }
    require(set(data['source_sha256']) == expected, 'complete source manifest')
    for path, digest in data['source_sha256'].items():
        pinned = subprocess.run(['git','show',REVISION+':'+path],cwd=ROOT,check=True,capture_output=True).stdout
        require(hashlib.sha256(pinned).hexdigest() == digest, 'pinned source hash: '+path)
        require(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, 'source hash: '+path)
    with zipfile.ZipFile(ROOT/'model/executable_model/carriers/FEDERATION_LEVEL0.npz') as z:
        edges = sorted(sorted(e) for e in npy(z.read('edges.npy')))
        stored_degree = npy(z.read('degree.npy'))
    require(data['edges'] == edges, 'carrier edge binding')
    require(len(edges) == 630 and len({tuple(e) for e in edges}) == 630, 'carrier seam count')
    require(all(0 <= a < b < 240 for a,b in edges), 'carrier endpoints')
    internal = [[a,b] for a,b in edges if b < 12]
    require(len(internal) == 30, 'complete source cell')
    for c in range(20):
        require([[a-12*c,b-12*c] for a,b in edges if a//12 == b//12 == c] == internal, 'complete cell')
    external = [(a,b) for a,b in edges if a//12 != b//12]
    endpoints = [p for e in external for p in e]
    require(len(external) == 30 and len(set(endpoints)) == 60, 'all bridges')
    require(all(sum(p//12 == c for p in endpoints) == 3 for c in range(20)), 'gateway count')
    p = projector(internal)
    encoded = [[[str(x),str(y)] for x,y in row] for row in p]
    require(data['projector'] == encoded, 'projector binding')
    h,degree = native_restriction(edges)
    require(degree == stored_degree, 'stored degree binding')
    return h,p


def ball_pair(x):
    return arb(str(x[0])) + arb(str(x[1]))*arb(5).sqrt()


def ldl(m):
    """Sufficient strict Hermitian PSD test using outward-rounded Schur complements."""
    n = m.nrows()
    require(all((m[i,j]-m[j,i].conjugate()).contains(0) for i in range(n) for j in range(n)), 'Hermitian enclosure')
    l = acb_mat(n,n)
    pivots = []
    for i in range(n):
        d = (m[i,i]-sum((l[i,k]*l[i,k].conjugate()*pivots[k] for k in range(i)),acb(0))).real
        require(d > 0, 'strict LDL pivot '+str(i))
        pivots.append(d)
        l[i,i] = 1
        for j in range(i+1,n):
            l[j,i] = (m[j,i]-sum((l[j,k]*l[i,k].conjugate()*pivots[k] for k in range(i)),acb(0)))/d
    return pivots


def matrices(h,p,columns,closed=False):
    require(len(columns) == 9 and len(set(columns)) == 9 and all(0 <= x < 12 for x in columns), 'source basis columns')
    b = [[int(i==j)-ball_pair(p[i][j]) for j in range(12)] for i in range(12)]
    s = acb_mat([[b[i][j] if i < 12 else 0 for j in columns] for i in range(240)])
    w = adj(s)*s
    ldl(w)  # Nine independent columns span the rank-nine complement.
    hh = acb_mat([[arb(str(h[i][j])) if not closed or i//12 == j//12 else 0 for j in range(240)] for i in range(240)])
    terms = [s]
    for k in range(1,ORDER+1):
        terms.append((hh*terms[-1])*acb(0,-1)/k)
    u = sum(terms, acb_mat(240,9))
    outside = acb_mat([[u[i,j] if i >= 12 else 0 for j in range(9)] for i in range(240)])
    arrival = adj(outside)*outside
    qterms = []
    pp = acb_mat([[ball_pair(x) for x in row] for row in p])
    for term in terms:
        blocks = []
        for c in range(20):
            blocks.extend((pp*acb_mat([[term[12*c+i,j] for j in range(9)] for i in range(12)])).tolist())
        qterms.append(acb_mat(blocks))
    g = acb_mat(9,9)
    for i in range(ORDER+1):
        for j in range(i,ORDER+1):
            z = adj(terms[i])*qterms[j]/(i+j+1)
            g += z if i == j else z+adj(z)
    triplet = adj(outside)*acb_mat([[sum((pp[i%12,k]*outside[12*(i//12)+k,j] for k in range(12)),acb(0)) for j in range(9)] for i in range(240)])
    eps = arb(3)**(ORDER+1)/math.factorial(ORDER+1)/(1-arb(3)/(ORDER+2))
    eta = 2*eps+eps*eps
    return w,arrival,g,triplet,eta


def vector(coords):
    return acb_mat([[acb(arb(x),arb(y))] for x,y in coords])


def quadratic(v,m):
    return (adj(v)*m*v)[0,0].real


def enclosed(v,w,m,eta):
    norm = quadratic(v,w)
    require(norm > 0, 'nonzero source')
    error = eta*quadratic(v,eye(v.nrows()))/norm
    return quadratic(v,m)/norm + arb(0,error.upper())


def check_certificate(c,w,a,g,eta):
    mu,lam = arb(c['mu']),arb(c['lambda'])
    require(mu >= 0, 'nonnegative dual multiplier')
    ldl(lam*w+mu*g-a-eye(9)*((1+mu)*eta))
    require(lam+mu/1000 <= arb(c['upper']), 'claimed dual upper bound')
    v = vector(c['witness'])
    leakage = enclosed(v,w,g,eta)
    arrival = enclosed(v,w,a,eta)
    require(leakage <= arb('1/1000'), 'feasible preparation')
    require(arrival >= arb(c['lower']), 'claimed primal lower bound')
    require(arb(c['upper'])-arb(c['lower']) <= arb('1/1000'), 'bracket width')
    return v,arrival,leakage


def bounds(x):
    # Decimal strings carry Arb's outward interval, never an unlabelled midpoint.
    return str(x)


def rejected(name,fn):
    try:
        fn()
    except ValueError as e:
        return {'control':name,'rejected':True,'reason':str(e)}
    raise ValueError('control accepted: '+name)


def run(all_controls=False):
    data = json.loads((HERE/'certificate.json').read_text())
    h,p = bind(data)
    w,a,g,t,eta = matrices(h,p,data['columns'])
    v,arrival,leakage = check_certificate(data,w,a,g,eta)
    triplet = enclosed(v,w,t,eta)
    out = {'status':'independently checked numerical enclosure', 'revision':REVISION,
           'bracket':[data['lower'],data['upper']], 'arrival':bounds(arrival),
           'integrated_triplet':bounds(leakage), 'outside_triplet':bounds(triplet),
           'outside_complement':bounds(arrival-triplet), 'home':bounds(1-arrival),
           'preparation':{'supplied_pure_state_probability':1,'refused_probability':0,'failed_probability':0},
           'taylor_state_error':bounds(eta/2), 'matrix_error_bound':bounds(eta),
           'dual_pivots':[bounds(x) for x in ldl(arb(data['lambda'])*w+arb(data['mu'])*g-a-eye(9)*((1+arb(data['mu']))*eta))]}
    require(arrival > 0, 'nonzero arrival source')
    if all_controls:
        controls = []
        bad = deepcopy(data)
        bad['edges'][0][1] += 1
        controls.append(rejected('changed carrier edge',lambda:bind(bad)))
        badp = deepcopy(data)
        badp['projector'][0][0][0] = '0'
        controls.append(rejected('changed projector',lambda:bind(badp)))
        badb = deepcopy(data)
        badb['upper'] = str(F(data['lower'])-F(1,10000))
        controls.append(rejected('tightened upper bound',lambda:check_certificate(badb,w,a,g,eta)))
        badd = deepcopy(data)
        badd['lambda'] = str(F(data['lambda'])-F(1,100))
        controls.append(rejected('invalid dual matrix',lambda:check_certificate(badd,w,a,g,eta)))
        badv = deepcopy(data)
        badv['witness'] = [['0','0']]*9
        controls.append(rejected('zero preparation',lambda:check_certificate(badv,w,a,g,eta)))
        cw,ca,cg,ct,ce = matrices(h,p,data['columns'],closed=True)
        closed_arrival = enclosed(v,cw,ca,ce)
        require(closed_arrival.contains(0) and closed_arrival < arb('1e-20'), 'closed bridge arrival')
        closed_triplet = enclosed(v,cw,ct,ce)
        controls.append({'control':'closed bridges, diagonal retained','arrival':bounds(closed_arrival),
                         'outside_triplet':bounds(closed_triplet),'outside_complement':bounds(closed_arrival-closed_triplet),
                         'home':bounds(1-closed_arrival),'integrated_triplet':bounds(enclosed(v,cw,cg,ce)),
                         'refused_probability':0,'failed_probability':0})
        out['controls'] = controls
    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all-controls',action='store_true')
    args = parser.parse_args()
    print(json.dumps(run(args.all_controls),indent=2))
