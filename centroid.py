import math


def mostatil(l,h):
    x = l/2
    y = h/2
    return x , y
def mosalas(h):
    x = 0
    y = h / 3
    return x, y
def nimdaiere(r):
    x = 0
    y = 4*r/3*math.pi
    return x , y
def robdaire(r):
    x = 4*r/3*math.pi
    y = 4*r/3*math.pi
    return x , y 
def nimbeiezi(a,b):
    x = 0
    y = 4 * b / 3 * math.pi
    return x , y
def robbeizi(a,b):
    x = 4 * a / 3 * math.pi
    y = 4 * b / 3 * math.pi
    return x , y
def sahmavi(a,h):
    x = 0
    y = 3 * h / 5
    return x , y
def robsahamavi(a,h):
    x = 3 * a / 8
    y = 3 * h / 5
    return x , y
def spandrol(a, h, n):
    x = (n + 1) / (n + 2) * a
    y = (n + 1) / (4 * (n + 2)) * h
    return x, y


if __name__ == "__main__":
    print("=== Centroid Calculator ===")
    print("1. Rectangle       (l, h)")
    print("2. Triangle        (h)")
    print("3. Quarter circle  (r)")
    print("4. Semi circle     (r)")
    print("5. Quarter ellipse (a, b)")
    print("6. Semi ellipse    (a, b)")
    print("7. Parabola        (a, h)")
    print("8. Half parabola   (a, h)")
    print("9. General spandrel(a, h, n)")

    choice = int(input("Pick a shape (1-9): "))

    if choice == 1:
        l = float(input("l = "))
        h = float(input("h = "))
        x, y = mostatil(l, h)
    elif choice == 2:
        h = float(input("h = "))
        x, y = mosalas(h)
    elif choice == 3:
        r = float(input("r = "))
        x, y = robdaire(r)
    elif choice == 4:
        r = float(input("r = "))
        x, y = nimdaiere(r)
    elif choice == 5:
        a = float(input("a = "))
        b = float(input("b = "))
        x, y = robbeizi(a, b)
    elif choice == 6:
        a = float(input("a = "))
        b = float(input("b = "))
        x, y = nimbeiezi(a, b)
    elif choice == 7:
        a = float(input("a = "))
        h = float(input("h = "))
        x, y = sahmavi(a, h)
    elif choice == 8:
        a = float(input("a = "))
        h = float(input("h = "))
        x, y = robsahamavi(a, h)
    elif choice == 9:
        a = float(input("a = "))
        h = float(input("h = "))
        n = float(input("n = "))
        x, y = spandrol(a, h, n)
    else:
        x, y = None, None
        print("Invalid choice")

    if x is not None:
        print(f"Centroid: x = {x:.6f}, y = {y:.6f}")