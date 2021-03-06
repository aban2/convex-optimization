from math import sqrt
import numpy as np


# 二分法
def bisect(a0, b0, acc, fn, grad_fn):
    l, r, num_iters = a0, b0, 0
    while r-l >= acc:
        num_iters += 1
        mid = (l+r) / 2
        gradient = grad_fn(mid)
        if gradient == 0: return mid, num_iters
        elif gradient < 0: l = mid
        else: r = mid
    return (l+r)/2, num_iters


# 黄金分割法
def golden_section(a0, b0, acc, fn, grad_fn):
    # 选取初始点
    l, r, t = a0, b0, (sqrt(5)-1)/2
    m, n = l+(1-t)*(r-l), l+t*(r-l)
    num_iters = 0

    while r-l >= acc:
        num_iters += 1
        if fn(m) > fn(n):
            l = m
            m = n
            n = r - (m-l)
        else:
            r = n
            n = m
            m = l + (r-n)
    return (l+r)/2, num_iters


# 斐波那契搜索
def fibonacci(a0, b0, acc, fn, grad_fn):
    fibs = [0, 1, 1, 2]
    l, r, num_iters = a0, b0, 0

    while r-l >= acc:
        num_iters += 1
        fibs.append(fibs[-1]+fibs[-2])
        m, n = l + (r - l) * (fibs[-3] / fibs[-1]), l + (r - l) * (fibs[-2] / fibs[-1])
        if fn(m) > fn(n): l = m
        else: r = n

    return (l+r)/2, num_iters


def dichotomous(a0, b0, acc, fn, grad_fn):
    l, r, num_iters = a0, b0, 0
    float_judge = 1e-3

    while r-l >= acc:
        num_iters += 1
        mid = (l+r) / 2
        m, n = mid-acc, mid+acc
        if abs(m-l) < float_judge and abs(n-r) < float_judge: break
        if(fn(m) > fn(n)): l = m
        else: r = n

    return (l+r)/2, num_iters


def gold_stein(step_size, fn, grad_fn):
    rou, alpha, beta, num_iters = 0.08, 1.5, 0.5, 0

    grad0, f0 = grad_fn(0), fn(0)
    while True:
        num_iters += 1
        # 选取的d的方向和梯度方向相反，所以此处用梯度上升
        upper_bound = rou * grad0 * step_size
        lower_bound = (1 - rou) * grad0 * step_size
        diff = fn(step_size) - f0

        if diff < lower_bound: step_size *= alpha
        elif diff > upper_bound: step_size *= beta
        else: return step_size, num_iters


def wolfe_powell(step_size, fn, grad_fn):
    rou, sigma, alpha, beta, num_iters = 0.08, 0.5, 1.5, 0.5, 0

    grad0, f0 = grad_fn(0), fn(0)
    while True:
        num_iters += 1
        # 选取的d的方向和梯度方向相反，所以此处用梯度上升
        upper_bound = rou * grad0 * step_size
        diff = fn(step_size) - f0
        new_grad = grad_fn(step_size)

        if diff > upper_bound: step_size *= beta
        elif new_grad < sigma*grad0: step_size *= alpha
        else: return step_size, num_iters


def DFP(x0, h, eps, fn, grad_fn):
    x = np.array(x0, dtype=np.float64)
    num_iters = 0
    while True:
        grad = grad_fn(x)
        if np.linalg.norm(grad) < eps: return x, num_iters
        num_iters += 1
        d = -np.dot(h, grad)
        step_size, _ = bisect(0, 1, 0.001, \
                              lambda a: fn(a*d[:,0]+x),\
                              lambda a: grad_fn(a*d[:,0]+x).T.dot(d))
        s = d*step_size
        x += s[:,0]
        y = grad_fn(x) - grad
        delta_h = np.dot(s, s.T)/np.dot(s.T, y) - \
                  h.dot(y).dot(y.T).dot(h)/y.T.dot(h).dot(y)
        h += delta_h


def BFGS(x0, b, eps, fn, grad_fn):
    x = np.array(x0, dtype=np.float64)
    num_iters = 0
    while True:
        grad = grad_fn(x)
        if np.linalg.norm(grad) < eps: return x, num_iters
        num_iters += 1
        d = -np.dot(np.linalg.inv(b), grad)
        step_size, _ = bisect(0, 1, eps, \
                              lambda a: fn(a*d[:,0]+x),\
                              lambda a: grad_fn(a*d[:,0]+x).T.dot(d))
        s = d*step_size
        x += s[:,0]
        y = grad_fn(x) - grad
        delta_b = np.dot(y, y.T)/np.dot(y.T, s) - \
                  b.dot(s).dot(s.T).dot(b)/s.T.dot(b).dot(s)
        b += delta_b


def flecher_reeves(x0, eps, fn, grad_fn):
    x0 = np.array(x0, dtype=np.float64)
    x = np.array(x0, dtype=np.float64)
    d = -grad_fn(x)
    num_iters = 0
    while True:
        num_iters += 1
        if np.linalg.norm(d) < eps: return x, num_iters
        step_size, _ = bisect(0, 1, eps,
                              lambda a: fn(a*d[:,0]+x),
                              lambda a: grad_fn(a*d[:,0]+x).T.dot(d))
        grad = grad_fn(x)
        x += step_size*d[:,0]
        if step_size % 2 == 0:
            d = -grad_fn(x0)
        else:
            new_grad = grad_fn(x)
            beta = new_grad.T.dot(new_grad)/grad.T.dot(grad)
            d = beta*d - new_grad


def momentum(x0, eps, fn, grad_fn):
    beta = 0.9
    x = np.array(x0, dtype=np.float64)
    v = np.zeros(2)
    num_iters = 0
    while True:
        num_iters += 1
        grad = grad_fn(x)[:,0]
        if np.linalg.norm(grad) < eps: return x, num_iters
        v = beta*v+(1-beta)*grad
        step_size, _ = bisect(0, 1, eps,
                              lambda a: fn(-a * v + x),
                              lambda a: -grad_fn(-a * v + x).T.dot(v))
        step_size = 1e-3
        x -= v*step_size


def RMSprop(x0, acc, fn, grad_fn):
    beta, eps = 0.999, 1e-8
    x = np.array(x0, dtype=np.float64)
    s = np.zeros(2)
    num_iters = 0
    step_size = 0.1
    while True:
        num_iters += 1
        grad = grad_fn(x)[:,0]
        if np.linalg.norm(grad) < acc: return x, num_iters
        s = beta*s+(1-beta)*grad**2
        x -= step_size*grad/(np.linalg.norm(s)+eps)
