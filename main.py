from lark import Lark, Transformer
import sympy as S
import re
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt

ω = S.symbols('ω')

class EETransformer(Transformer):
    def get_value(self, v, t):
        v = float(re.split("p|n|u|m|k|g|f|r|o|μ|Ω|l|c|h", v, flags=re.IGNORECASE)[0])
        if   t.startswith("PICO"): v *= 10**(-12)
        elif t.startswith("NANO"): v *= 10**(-9)
        elif t.startswith("MICRO"): v *= 10**(-6)
        elif t.startswith("MILLI"): v *= 10**(-3)
        elif t.startswith("KILO"): v *= 10**(3)
        elif t.startswith("MEGA"): v *= 10**(6)
        elif t.startswith("GIGA"): v *= 10**(9)

        if t.endswith("OHM"):     return v
        elif t.endswith("HENRY"): return S.I * ω * v
        else:                     return 1/(S.I * ω * v)

    def seriesexpression(self, s):
        total = 0
        for v in s: total += v
        return total

    def parallelexpression(self, s):
        total = 0
        for v in s: total += 1/v
        return 1/total

    def resistance(self, s):
        return self.get_value(s[0].value, s[0].type)

    def inductance(self, s):
        return self.get_value(s[0].value, s[0].type)

    def capacitance(self, s):
        return self.get_value(s[0].value, s[0].type)

parser = Lark.open("grammar.lark", start="start", parser="lalr", transformer=EETransformer())

while True:
    expression = input("Expression? ")
    if expression == "": break
    try:
        result = S.simplify(parser.parse(expression))
        imp = abs(result)
        pha = S.arg(result)*(180/S.pi)
        print(f"Impedance can be calculated as: Z={result}")
        b = [1.0, 1.5, 2.2, 3.3, 4.7, 6.8]
        freqs = []
        freqs.extend(np.array(b)/10)
        for i in range(1, 9): freqs.extend(np.array(b)*(10**i))
        data = [[f"{f:.2f}Hz", f"{imp.evalf(subs={ω:f}):.2f}Ω", f"{pha.evalf(subs={ω:f}):.2f}°"] for f in freqs]
        print(tabulate(data, headers=["Freq (Hz)", "Impedance (Ω)", "Phase shift (°)"]))
        doplt = input("Plot (y/[n])? ")
        if doplt == "y": 
            p1 = S.plot(imp, (ω, 0.001, 1e9), xscale='log', show=False, line_color='blue', title="Impedance", xlabel="Frequency (Hz)", ylabel="Impedance (Ω)", axis_center=(0.001, 0))
            p2 = S.plot(pha, (ω, 0.001, 1e9), xscale='log', show=False, line_color='red', title="Phase", xlabel="Frequency (Hz)", ylabel="Phase (°)", axis_center=(0.001, 0))
            plotgrid = S.plotting.PlotGrid(2, 1, p1, p2, show=False)
            plotgrid.show()
    except:
       print("Error while parsing expression.")

