import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution, minimize
from scipy.interpolate import interp1d
import multiprocessing, time, os

T_MIN, T_MAX = 6, 60
RANDOM_SEED = 42
POP_SIZE = 25
MAX_ITER = 800
N_STARTS = 3
USE_EUCLIDEAN = False


def parametric_curve(t, theta_deg, M, X):
    th = np.deg2rad(theta_deg)
    exp_term = np.exp(np.clip(M * np.abs(t), -30, 30))
    sin_term = np.sin(0.3 * t)
    x = t * np.cos(th) - exp_term * sin_term * np.sin(th) + X
    y = 42 + t * np.sin(th) + exp_term * sin_term * np.cos(th)
    return x, y

def objective(params, t_vals, x_data, y_data):
    theta, M, X = params
    if not (0 <= theta <= 50 and -0.08 <= M <= 0.08 and 0 <= X <= 100):
        return np.inf
    x_pred, y_pred = parametric_curve(t_vals, theta, M, X)
    if not np.all(np.isfinite(x_pred)) or not np.all(np.isfinite(y_pred)):
        return np.inf
    idx = np.argsort(x_pred)
    x_sorted, y_sorted = x_pred[idx], y_pred[idx]
    try:
        interp = interp1d(x_sorted, y_sorted,
                          bounds_error=False,
                          fill_value=(y_sorted[0], y_sorted[-1]))
        y_interp = interp(x_data)
    except Exception:
        return np.inf
    dy = y_interp - y_data
    err = np.sum(np.abs(dy)) if not USE_EUCLIDEAN else np.sum(np.hypot(np.zeros_like(dy), dy))
    reg = ((M - 0.015) / 0.02) ** 2
    return err + 200 * reg


if __name__ == "__main__":
    multiprocessing.freeze_support()
    np.random.seed(RANDOM_SEED)
    os.makedirs("results", exist_ok=True)

    data = pd.read_csv("xy_data.csv")
    x_data, y_data = data["x"].to_numpy(), data["y"].to_numpy()
    N = len(x_data)
    t_vals = np.linspace(T_MIN, T_MAX, N)
    func = lambda p: objective(p, t_vals, x_data, y_data)
    bounds = [(0, 50), (-0.08, 0.08), (0, 100)]

    best = None
    global_snapshots = []


    for run in range(1, N_STARTS + 1):
        print(f"\n--- Global Run {run}/{N_STARTS} ---")
        progress, snapshots = [], []

        def log_progress(xk, conv):
            val = func(xk)
            progress.append(val)
            if len(progress) % 10 == 0:
                snapshots.append(xk.copy())
                print(f"  -> Iter {len(progress):4d}, best L1 = {val:.2f}")

        res = differential_evolution(
            func,
            bounds,
            seed=RANDOM_SEED + run * 3,
            popsize=POP_SIZE,
            maxiter=MAX_ITER,
            updating="deferred",
            workers=1,
            callback=log_progress,
            polish=False,
        )

        pd.DataFrame({"iteration": np.arange(1, len(progress)+1), "L1": progress}).to_csv(
            f"results/de_progress_run{run}.csv", index=False
        )
        global_snapshots.append(snapshots)
        print(f"  DE result: {res.fun:.2f} @ {res.x}")
        if best is None or res.fun < best.fun:
            best = res

    print("\nRunning local Nelder–Mead refinement...")
    loc = minimize(func, best.x, method="Nelder-Mead",
                   options={"maxiter": 2000, "xatol": 1e-9, "fatol": 1e-9})
    if loc.fun < best.fun:
        best = loc

    theta, M, X = best.x
    print("\n====================== FINAL RESULT ======================")
    print(f"Theta (deg) = {theta:.6f}")
    print(f"M = {M:.6f}")
    print(f"X = {X:.6f}")
    print(f"L1 distance = {best.fun:.4f}")


    th_r = np.deg2rad(theta)
    latex_x = f"t\\cos({th_r:.6f}) - e^{{{M:.6f}\\left|t\\right|}}\\sin(0.3t)\\sin({th_r:.6f}) + {X:.6f}"
    latex_y = f"42 + t\\sin({th_r:.6f}) + e^{{{M:.6f}\\left|t\\right|}}\\sin(0.3t)\\cos({th_r:.6f})"
    print("\nLaTeX:\n")
    print(f"\\left({latex_x}, {latex_y}\\right)")


    x_fit, y_fit = parametric_curve(t_vals, theta, M, X)
    residuals = np.hypot(x_fit - x_data, y_fit - y_data) 

    
    first_snapshot_params = global_snapshots[0][0]
    x_fit_initial, y_fit_initial = parametric_curve(t_vals, *first_snapshot_params)
    initial_l1 = func(first_snapshot_params)



    plt.ylabel("Y")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/fit_curve.png", dpi=300)


    plt.figure(figsize=(8, 6))
    plt.plot(x_fit, y_fit, "r-", lw=2, label="Final Fitted Curve")
    plt.legend()
    plt.title(f"Final Curve Only (Theta={theta:.2f}, M={M:.4f}, X={X:.2f})")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/final_curve_only.png", dpi=300)

    # 3️ Residuals vs t
    plt.figure(figsize=(10, 4))
    plt.plot(t_vals, residuals, lw=1)
    plt.title("Residuals vs t")
    plt.xlabel("t")
    plt.ylabel("Residual distance")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/residuals_vs_t.png", dpi=300)


    df = pd.read_csv("results/de_progress_run1.csv")
    plt.figure(figsize=(8, 4))
    plt.plot(df["iteration"], df["L1"], lw=1)
    plt.title("Differential Evolution Progress (Run 1)")
    plt.xlabel("Iteration")
    plt.ylabel("Best L1")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/de_progress.png", dpi=300)


    plt.figure(figsize=(8, 6))
    plt.scatter(x_data, y_data, s=10, alpha=0.4, label="Data", color="gray")
    plt.plot(x_fit_initial, y_fit_initial, "b-", lw=2, label=f"Initial Guess (L1={initial_l1:.2f})")
    plt.plot(x_fit, y_fit, "r-", lw=2.5, label=f"Final Fit (L1={best.fun:.2f})")
    plt.title("Fit Comparison (Start vs. Final)")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/fit_comparison.png", dpi=300)


    plt.figure(figsize=(8, 6))
    plt.plot(x_fit_initial, y_fit_initial, "b-", lw=2, label=f"Initial Guess (L1={initial_l1:.2f})")
    plt.plot(x_fit, y_fit, "r-", lw=2, label=f"Final Fit (L1={best.fun:.2f})")
    plt.title("Initial Guess vs. Final Fit (Curves Only)")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/initial_vs_final_curve_only.png", dpi=300)


    # 7️ Save parameters
    pd.DataFrame({"theta_deg": [theta], "M": [M], "X": [X], "L1": [best.fun]}).to_csv(
        "results/best_params.csv", index=False
    )

    print("\nSaved results in ./results/ :")
    print(" - fit_curve.png (Data + Final Fit)")
    print(" - final_curve_only.png (Just the Final Fit)")
    print(" - fit_comparison.png (Data + Start + Final)")
    print(" - initial_vs_final_curve_only.png (Start + Final Curves)")
    print(" - residuals_vs_t.png")
    print(" - de_progress.png")
    print(" - best_params.csv")
    print("==========================================================")