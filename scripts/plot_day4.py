import csv
import matplotlib.pyplot as plt

designs = {
    "Sturdy": "results/day4/sweep_robust_seed9_t2.5.csv",
    "Quiet": "results/day4/sweep_lownoise_seed5_t2.5.csv",
}

for name, path in designs.items():
    ks, rates = [], []
    for row in csv.DictReader(open(path)):
        if float(row["dep"]) != 0.02:
            continue                      # keep only 2% deposition error
        if row["k"] != "0" and float(row["meas"]) != 0.0:
            continue                      # keep only perfect measurement
        ks.append(int(row["k"]))
        rates.append(float(row["pass_rate"]))
    plt.plot(ks, rates, marker="o", label=name)

plt.xlabel("Top layers re-optimized (k)")
plt.ylabel("Pass rate")
plt.title("2% thickness error, perfect measurement")
plt.ylim(0, 1.05)
plt.legend()
plt.grid(alpha=0.3)
plt.savefig("results/day4/pass_vs_k.png", dpi=150)
plt.show()
