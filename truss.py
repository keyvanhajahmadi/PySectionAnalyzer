import math


def solve_truss(nodes, members, supports, loads):
    n = len(nodes)
    m = len(members)

    reactions = []
    for idx, rtype in supports:
        if rtype in ("pinned", "fixed", "cable"):
            reactions.append((idx, 0))
            reactions.append((idx, 1))
        elif rtype == "roller":
            reactions.append((idx, 1))
        elif rtype == "roller_x":
            reactions.append((idx, 0))

    r = len(reactions)
    neq = 2 * n

    A = [[0.0] * (m + r) for _ in range(neq)]
    b = [0.0] * neq

    for k, (i, j) in enumerate(members):
        xi, yi = nodes[i]
        xj, yj = nodes[j]
        dx, dy = xj - xi, yj - yi
        L = math.hypot(dx, dy)
        if L < 1e-12:
            continue
        cx, cy = dx / L, dy / L
        A[2 * i][k] = cx
        A[2 * i + 1][k] = cy
        A[2 * j][k] = -cx
        A[2 * j + 1][k] = -cy

    for k, (idx, d) in enumerate(reactions):
        A[2 * idx + d][m + k] = 1.0

    for idx, fx, fy in loads:
        b[2 * idx] = -fx
        b[2 * idx + 1] = -fy

    At = _transpose(A)
    AtA = _mat_mul(At, A)
    Atb = _mat_vec_mul(At, b)
    f = _gauss(AtA, Atb)

    return f[:m], f[m:]


def _transpose(A):
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def _mat_mul(A, B):
    m = len(A)
    n = len(B)
    p = len(B[0]) if B else 0
    return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(p)] for i in range(m)]


def _mat_vec_mul(A, v):
    return [sum(A[i][j] * v[j] for j in range(len(v))) for i in range(len(A))]


def _gauss(A, b):
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) < 1e-14:
            continue
        M[col], M[pivot] = M[pivot], M[col]
        for row in range(col + 1, n):
            f = M[row][col] / M[col][col]
            for j in range(col, n + 1):
                M[row][j] -= f * M[col][j]

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        if abs(M[i][i]) < 1e-14:
            x[i] = 0.0
        else:
            M[i][n] -= sum(M[i][j] * x[j] for j in range(i + 1, n))
            x[i] = M[i][n] / M[i][i]

    return x
