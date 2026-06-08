import numpy as np
from scipy import integrate


def quad_integral(f, a, b):
    result, error = integrate.quad(f, a, b)
    return result, error


def trapezoid_integral(f, a, b, n=10000):
    x = np.linspace(a, b, n + 1)
    y = f(x)
    return integrate.trapezoid(y, x)


def simpson_integral(f, a, b, n=10000):
    x = np.linspace(a, b, n + 1)
    y = f(x)
    return integrate.simpson(y, x=x)


if __name__ == "__main__":
    print("=== Integral Calculator (scipy) ===")
    print("Enter function f(x) using 'x' as variable.")
    print("You can use: +, -, *, /, **, sin, cos, tan, exp, log, sqrt, pi, e")
    print("Example: x**2 + sin(x)")
    print()

    func_str = input("f(x) = ")
    a = float(input("Lower bound (a) = "))
    b = float(input("Upper bound (b) = "))

    safe_dict = {
        "x": 0,
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan,
        "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
        "exp": np.exp, "log": np.log, "log10": np.log10,
        "sqrt": np.sqrt, "abs": np.abs,
        "floor": np.floor, "ceil": np.ceil,
        "pi": np.pi, "e": np.e,
    }

    f = lambda x: eval(func_str, {"__builtins__": {}}, {**safe_dict, "x": x})

    q, err = quad_integral(f, a, b)
    t = trapezoid_integral(f, a, b)
    s = simpson_integral(f, a, b)

    print()
    print(f"scipy.integrate.quad  : {q:.12f}  (est. error: {err:.2e})")
    print(f"Trapezoid (scipy)     : {t:.12f}")
    print(f"Simpson (scipy)       : {s:.12f}")
