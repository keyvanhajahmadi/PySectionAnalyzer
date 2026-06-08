import centroid
import math
import sys


def centroid_spandrel_integral(a, h, n):
    """محاسبه مرکز سطح اسپاندرول با انتگرال عددی.
    منحنی: y = h * (x/a)^(1/n) ، از x=0 تا x=a
    """
    if a <= 0 or h <= 0 or n <= 0:
        raise ValueError("a, h, n must be positive")

    try:
        from scipy import integrate
    except ImportError:
        raise ImportError("برای محاسبه اسپاندرول باید scipy نصب باشه: pip install scipy")

    def y(x):
        return h * (x / a) ** (1.0 / n)

    area, _ = integrate.quad(y, 0, a)
    mx, _ = integrate.quad(lambda x: x * y(x), 0, a)
    my, _ = integrate.quad(lambda x: 0.5 * y(x) ** 2, 0, a)

    return mx / area, my / area


def run_cli():
    print("╔════════════════════════════════════════════════╗")
    print("║       محاسبه‌گر مرکز سطح مرکب                 ║")
    print("║   ساخته شده توسط کیوان حاج احمدی              ║")
    print("╚════════════════════════════════════════════════╝")
    print()
    k = int(input('تعداد اجزای شکل را مشخص کنید: '))


    i = 1

    x1 = 0
    y1 = 0
    a1 = 0
    parts = []

    while i <= k:
        i += 1
        ajza = int(input('نوع شکل: 1.مستطیل  2.مثلث  3.ربع دایره  4.نیم دایره  5.نیم بیضی  6.ربع بیضی  7.سهموی  8.نیم سهموی  9.اسپاندرول: '))
        noe = int(input('1.پر   2.خالی: '))
        sign = 1 if noe == 1 else -1
        kind = "پر" if sign == 1 else "خالی"
        cx = cy = a = 0.0
        shape_name = ""
        params_str = ""

        if ajza == 1:
            l = float(input('طول (l): '))
            h = float(input('ارتفاع (h): '))
            cx, cy = centroid.mostatil(l, h)
            a = l * h
            shape_name = "مستطیل"
            params_str = f"l={l:g}, h={h:g}"
        elif ajza == 2:
            h = float(input('ارتفاع (h): '))
            b = float(input('قاعده (b): '))
            cx, cy = centroid.mosalas(h)
            a = b * h / 2
            shape_name = "مثلث"
            params_str = f"h={h:g}, b={b:g}"
        elif ajza == 3:
            r = float(input('شعاع (r): '))
            a = math.pi * r ** 2 / 4
            cx, cy = centroid.robdaire(r)
            shape_name = "ربع دایره"
            params_str = f"r={r:g}"
        elif ajza == 4:
            r = float(input('شعاع (r): '))
            a = math.pi * r ** 2 / 2
            cx, cy = centroid.nimdaiere(r)
            shape_name = "نیم دایره"
            params_str = f"r={r:g}"
        elif ajza == 5:
            s = float(input('a: '))
            b = float(input('b: '))
            a = math.pi * b * s / 2
            cx, cy = centroid.nimbeiezi(s, b)
            shape_name = "نیم بیضی"
            params_str = f"a={s:g}, b={b:g}"
        elif ajza == 6:
            s = float(input('a: '))
            b = float(input('b: '))
            a = math.pi * b * s / 4
            cx, cy = centroid.robbeizi(s, b)
            shape_name = "ربع بیضی"
            params_str = f"a={s:g}, b={b:g}"
        elif ajza == 7:
            s = float(input('a: '))
            b = float(input('h: '))
            a = 2 * s * b / 3
            cx, cy = centroid.sahmavi(s, b)
            shape_name = "سهموی"
            params_str = f"a={s:g}, h={b:g}"
        elif ajza == 8:
            n = float(input('توان (n): '))
            h = float(input('ارتفاع (h): '))
            a_in = float(input('a: '))
            a = a_in * h * n / (n + 1)
            cx, cy = centroid_spandrel_integral(a_in, h, n)
            shape_name = "اسپاندرول"
            params_str = f"a={a_in:g}, h={h:g}, n={n:g}"

        x1 += sign * a * cx
        y1 += sign * a * cy
        a1 += sign * a
        parts.append((shape_name, params_str, cx, cy, a, kind))


    print("\n" + "=" * 70)
    print(f"{'#':<3} {'شکل':<12} {'پارامترها':<22} {'x̄':>10} {'ȳ':>10} {'مساحت':>10}")
    print("-" * 70)
    for i, (name, par, cx, cy, ar, kd) in enumerate(parts, 1):
        print(f"{i:<3} {name:<12} {par:<22} {cx:>10.4f} {cy:>10.4f} {ar:>10.4f}  {kd}")
    print("=" * 70)

    if a1 == 0:
        print('خطا: مساحت خالص صفر است.')
    else:
        x_c = x1 / a1
        y_c = y1 / a1
        print(f"{'مرکز سطح مرکب':.<28} x̄ = {x_c:.4f}    ȳ = {y_c:.4f}    (مساحت خالص = {a1:.4f})")


def run_gui():
    import tkinter as tk
    from tkinter import ttk
    import gui
    import truss_gui

    root = tk.Tk()
    root.title("محاسبه‌گر سازه‌ای")
    root.state("zoomed")
    root.resizable(True, True)
    root.minsize(960, 680)
    root.configure(bg="#1e1e2e")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    centroid_frame = tk.Frame(notebook, bg="#1e1e2e")
    truss_frame = tk.Frame(notebook, bg="#1e1e2e")

    notebook.add(centroid_frame, text="📐  مرکز سطح")
    notebook.add(truss_frame, text="🏗️  خرپا")

    gui.CentroidGUI(root, parent=centroid_frame)
    truss_gui.TrussGUI(truss_frame)

    root.mainloop()


if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        run_gui()
