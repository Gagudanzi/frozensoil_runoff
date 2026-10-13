from pathlib import Path
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
import numpy as np


here = Path(__file__).resolve().parent
figures_dir = here / "figures"
figures_dir.mkdir(parents=True, exist_ok=True)
output_file = figures_dir / "Fig5_hydraulic_relationships.svg"

colors = {
    "omega0": "#C0D6EA",
    "omega2": "#86B7DB",
    "omega4": "#6E8FB2",
    "omega6": "#4B7DB2",
    "text": "#4D4D4D",
}

for font_file in (Path(sys.prefix) / "fonts").glob("arial*.ttf"):
    font_manager.fontManager.addfont(font_file)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Liberation Sans"],
    "mathtext.fontset": "custom",
    "mathtext.rm": "Arial",
    "mathtext.it": "Arial:italic",
    "mathtext.bf": "Arial:bold",
    "mathtext.cal": "Arial",
    "mathtext.sf": "Arial",
    "mathtext.tt": "Arial",
    "svg.fonttype": "none",
    "font.size": 8,
    "axes.labelsize": 8.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.2,
    "axes.edgecolor": colors["text"],
    "axes.labelcolor": colors["text"],
    "xtick.color": colors["text"],
    "ytick.color": colors["text"],
    "text.color": colors["text"],
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


# Parameter values used in Figure 5.
theta_sat = 0.45
theta_total = 0.80 * theta_sat
k_sat = 1.0e-3
psi_sat = -300.0
b = 5.0
omega_values = (0, 2, 4, 6)

liquid_fraction = np.linspace(0.2, 0.8, 241)
theta_liquid = liquid_fraction * theta_total
theta_ice = theta_total - theta_liquid
ice_fraction = theta_ice / theta_sat
effective_porosity = np.maximum(theta_sat - theta_ice, 1.0e-12)

# Default / Revised hydraulic relationships.

saturation_default = np.clip(theta_liquid / theta_sat, 1.0e-12, 1.0)
saturation_revised = np.clip(
    theta_liquid / effective_porosity, 1.0e-12, 1.0
)

conductivity_default = {}
conductivity_revised = {}
for omega in omega_values:
    ice_impedance = 10.0 ** (-omega * ice_fraction)
    conductivity_default[omega] = (
        ice_impedance * k_sat * saturation_default ** (2.0 * b + 3.0)
    )
    conductivity_revised[omega] = (
        ice_impedance * k_sat * saturation_revised ** (2.0 * b + 3.0)
    )

potential_default = psi_sat * saturation_default ** (-b)
potential_revised = psi_sat * saturation_revised ** (-b)


figure, (conductivity_axis, potential_axis) = plt.subplots(
    1, 2, figsize=(7.0, 2.75), constrained_layout=True
)

for omega in omega_values:
    curve_color = colors[f"omega{omega}"]
    conductivity_axis.plot(
        liquid_fraction,
        np.log10(conductivity_default[omega]),
        color=curve_color,
        linestyle="--",
        linewidth=1.45,
        zorder=2,
    )
    conductivity_axis.plot(
        liquid_fraction,
        np.log10(conductivity_revised[omega]),
        color=curve_color,
        linestyle="-",
        linewidth=1.45,
        zorder=3,
    )

conductivity_axis.set_xlabel("Liquid water fraction")
conductivity_axis.set_ylabel(r"$\log_{10} k$ (mm s$^{-1}$)")
conductivity_axis.set_xticks([0.2, 0.4, 0.6, 0.8])
conductivity_axis.set_xlim(0.17, 0.83)
conductivity_axis.spines["top"].set_visible(False)
conductivity_axis.spines["right"].set_visible(False)

omega_handles = [
    Line2D(
        [0], [0], color=colors[f"omega{omega}"], linewidth=1.5,
        label=rf"{omega}",
    )
    for omega in omega_values
]
conductivity_axis.legend(
    handles=omega_handles,
    title=r"$\Omega$",
    title_fontsize=7.2,
    loc="lower right",
    ncol=1,
    frameon=False,
    borderpad=0.1,
    handlelength=1.5,
    handletextpad=0.35,
    labelspacing=0.3,
)

formula_handles = [
    Line2D(
        [0], [0], color=colors["omega6"], linewidth=1.45,
        linestyle="--", label="Default",
    ),
    Line2D(
        [0], [0], color=colors["omega6"], linewidth=1.45,
        linestyle="-", label="Revised",
    ),
]
potential_axis.plot(
    liquid_fraction,
    np.log10(np.abs(potential_default)),
    color=colors["omega6"],
    linestyle="--",
    linewidth=1.45,
    label="Default",
)
potential_axis.plot(
    liquid_fraction,
    np.log10(np.abs(potential_revised)),
    color=colors["omega6"],
    linestyle="-",
    linewidth=1.45,
    label="Revised",
)

potential_axis.set_xlabel("Liquid water fraction")
potential_axis.set_ylabel(r"$\log_{10}|\psi|$ (mm)")
potential_axis.set_xticks([0.2, 0.4, 0.6, 0.8])
potential_axis.set_xlim(0.17, 0.83)
potential_axis.spines["top"].set_visible(False)
potential_axis.spines["right"].set_visible(False)
potential_axis.legend(
    handles=formula_handles,
    loc="upper right",
    frameon=False,
    borderpad=0.1,
    handlelength=2.1,
    labelspacing=0.35,
)


figure.savefig(output_file, format="svg", bbox_inches="tight")
plt.close(figure)

print(f"Saved: {output_file}")
