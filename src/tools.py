# Usefully functions
from math import sqrt

def Vsum(v1, v2):
    v = []
    for i in range(min(len(v1), len(v2))):
        v.append(v1[i] + v2[i])
    return v

def Vmult(v, factor):
    res = []
    for i in range(len(v)):
        res.append(v[i] * factor)
    return res

def Vsum_mult(v1, v2, factor):
    return Vmult(Vsum(v1, v2), factor)

def Vmult_sum(v1, factor_1, v2, factor_2=1):
    return Vsum(Vmult(v1, factor_1), Vmult(v2, factor_2))

def VectMult(v1, v2):
    v = []
    for i in range(min(len(v1), len(v2))):
        v.append(v1[i] * v2[i])
    return v

def Vselfsum(v, multiplicator=1, power=1):
    tot = 0
    for i in range(len(v)):
        tot += v[i] ** power
    return tot * multiplicator

def norm(v):
    return sqrt(Vselfsum(v, power=2))

def s(number):
    return -1 if number < 0 else 1

def VisEqual(v1, v2):
    if len(v1) != len(v2):
        return False
    else:
        for i in range(len(v1)):
            if v1[i] != v2[i]:
                return False
    return True

def VerifyVbounds(v, bounds):
    for i in range(len(v)):
        low, up = bounds[i]
        if not low <= v[i] <= up:
            return False
    return True

def roundVect(v, r=2):
    res = []
    for coord in v:
        res.append(round(coord, r))
    return res

def inv(nb):
    if nb == 0:
        return 1e-12
    else:
        return 1/nb

def controlVect(v, bounds):
    for i in range(len(v)):
        low, up = bounds[i]
        if v[i] < low:
            v[i] = low
        if v[i] > up:
            v[i] = up
    return v

def isLowerThanALL(value, liste):
    for elt in liste:
        if value > elt:
            return False
    return True

def isHigherThanALL(value, liste):
    for elt in liste:
        if value < elt:
            return False
    return True
