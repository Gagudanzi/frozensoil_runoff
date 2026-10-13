from pathlib import Path
import sys
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
from cartopy.util import add_cyclic_point
from matplotlib import font_manager
from matplotlib.colorbar import ColorbarBase


here = Path(__file__).resolve().parent
workbook = here / "Yao_et_al_Source_Data.xlsx"
figures_dir = here / "figures"
figures_dir.mkdir(parents=True, exist_ok=True)

plot_sheets = [
    "Fig1b", "Fig2a", "Fig2bcd", "Fig3d", "Fig4a", "Fig4bc",
    "Fig1a_Fig3abc",
]
source_data = pd.read_excel(workbook, sheet_name=plot_sheets)
map_table = source_data["Fig1a_Fig3abc"]
latitudes = np.sort(map_table["lat"].unique())
longitudes = np.sort(map_table["lon"].unique())


def map_array(column):
    return (
        map_table.pivot(index="lat", columns="lon", values=column)
        .reindex(index=latitudes, columns=longitudes)
        .to_numpy()
    )


river_index = map_array("basin_id")
bfi_maps = {name: map_array(name) for name in ("GSCD", "CON", "SEN")}


for font_file in (Path(sys.prefix) / "fonts").glob("arial*.ttf"):
    font_manager.fontManager.addfont(font_file)

basins = np.arange(1, 22)
amip_models = [
    "ACCESS-ESM1-5", "CESM2", "CanESM5", "E3SM-2-1", "MIROC6",
    "MPI-ESM1-2-LR", "MRI-ESM2-0",
]
colors = {
    "LORA": "#E19D49", "GSCD": "#D0D08A", "GRACE": "#ACA1BE",
    "CON": "#78B7D0", "SEN": "#D9756C", "text": "#4D4D4D",
    "zero": "#A8A8A8", "land": "#E6E6E6",
    "ACCESS-ESM1-5": "#9F8DB8", "CESM2": "#808080",
    "CanESM5": "#D0D08A", "E3SM-2-1": "#AABCD8",
    "MIROC6": "#C16E71", "MPI-ESM1-2-LR": "#D59EBE",
    "MRI-ESM2-0": "#6E8FB2",
}
markers = {
    "LORA": "o", "GRACE": "o", "CON": "s", "SEN": "^",
    "ACCESS-ESM1-5": "o", "CESM2": "s", "CanESM5": "^",
    "E3SM-2-1": "D", "MIROC6": "v", "MPI-ESM1-2-LR": "P",
    "MRI-ESM2-0": "X",
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Liberation Sans"],
    "mathtext.fontset": "custom",
    "mathtext.rm": "Arial",
    "mathtext.it": "Arial:italic",
    "mathtext.bf": "Arial:bold",
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 9.5,
    "axes.labelsize": 10.0,
    "xtick.labelsize": 9.0,
    "ytick.labelsize": 9.0,
    "legend.fontsize": 9.0,
    "axes.edgecolor": colors["text"],
    "axes.labelcolor": colors["text"],
    "xtick.color": colors["text"],
    "ytick.color": colors["text"],
    "text.color": colors["text"],
    "axes.linewidth": 0.85,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.major.size": 3.5,
    "ytick.major.size": 3.5,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.dpi": 300,
})


def clean_axis(axis):
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.grid(False)


def save_svg(figure, filename, description=""):
    figure.savefig(
        figures_dir / filename, format="svg", dpi=300, bbox_inches="tight",
        facecolor="white",
        metadata={"Title": filename.removesuffix(".svg"),
                  "Description": description,
                  "Creator": Path(__file__).name},
    )
    plt.close(figure)


def plot_seasonal(axis, table, names, ylabel, shading=True):
    for name in names:
        rows = table.loc[table.source == name].sort_values("month")
        x = rows.month.to_numpy()
        mean = rows["mean"].to_numpy()
        if shading:
            standard_deviation = rows.interannual_sd.to_numpy()
            axis.fill_between(
                x, mean - standard_deviation, mean + standard_deviation,
                color=colors[name], alpha=0.14, linewidth=0, zorder=1,
            )
        is_amip = name in amip_models
        axis.plot(
            x, mean, color=colors[name], linewidth=2.2,
            marker=markers[name], markersize=4.2,
            markerfacecolor="white" if is_amip else colors[name],
            markeredgecolor=colors[name],
            markeredgewidth=0.8 if is_amip else 0,
            label=name, zorder=3,
        )
    axis.set_xlim(1, 12)
    axis.set_xticks(
        np.arange(1, 13),
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    )
    axis.set_xlabel("Month", fontsize=11.0)
    axis.set_ylabel(ylabel, fontsize=11.0)
    axis.tick_params(axis="both", which="major", labelsize=10.5)
    axis.axhline(0, color=colors["zero"], linewidth=0.65, zorder=0)
    clean_axis(axis)


def draw_metric_values(axis, table, metric, positions=(1.0, 2.0)):
    random = np.random.default_rng(42)
    for position, name in zip(positions, ("CON", "SEN")):
        values = table.loc[table.simulation == name, metric].to_numpy(float)
        values = values[np.isfinite(values)]
        violin = axis.violinplot(
            [values], positions=[position], widths=0.72,
            showmeans=False, showmedians=False, showextrema=False,
        )
        body = violin["bodies"][0]
        body.set_facecolor(colors[name])
        body.set_edgecolor(colors[name])
        body.set_linewidth(0.9)
        body.set_alpha(0.30)
        axis.boxplot(
            [values], positions=[position], widths=0.24,
            patch_artist=True, showfliers=False,
            boxprops={"facecolor": "white", "edgecolor": colors[name],
                      "linewidth": 0.9},
            whiskerprops={"color": colors[name], "linewidth": 0.9},
            capprops={"color": colors[name], "linewidth": 0.9},
            medianprops={"color": colors["text"], "linewidth": 1.1},
        )
        axis.scatter(
            position + random.uniform(-0.10, 0.10, values.size), values,
            s=10, color=colors[name], edgecolors="white", linewidths=0.3,
            alpha=0.85, zorder=3,
        )
    axis.set_xlim(positions[0] - 0.55, positions[-1] + 0.55)
    clean_axis(axis)


def draw_metric_panel(axis, table, metric, show_labels, positions=(1.0, 2.0)):
    draw_metric_values(axis, table, metric, positions)
    axis.axhline(0, color=colors["zero"], linewidth=0.70, zorder=0)
    axis.set_ylabel(
        "KGE" if metric == "KGE_2012" else metric, fontsize=10.5
    )
    axis.tick_params(axis="y", which="major", labelsize=10.5)
    axis.set_xticks(positions)
    if show_labels:
        axis.set_xticklabels(["CON", "SEN"])
        axis.tick_params(axis="x", which="major", labelsize=10.5)
    else:
        axis.set_xticklabels([])
        axis.tick_params(axis="x", which="both", bottom=False)


def draw_broken_nse(axis_main, axis_extreme, table):
    for axis in (axis_main, axis_extreme):
        draw_metric_values(axis, table, "NSE")
    axis_main.set_ylim(-1.2, 1.0)
    axis_main.set_yticks(np.arange(-1.0, 1.01, 0.5))
    axis_main.axhline(0, color=colors["zero"], linewidth=0.70, zorder=0)
    axis_main.set_ylabel("NSE", fontsize=10.5)
    axis_main.tick_params(axis="y", which="major", labelsize=10.5)
    axis_main.spines["bottom"].set_visible(False)
    axis_main.tick_params(axis="x", which="both", bottom=False,
                          labelbottom=False)
    axis_extreme.set_ylim(-36.5, -1.5)
    axis_extreme.set_yticks([-35, -25, -15, -5])
    axis_extreme.spines["top"].set_visible(False)
    axis_extreme.set_xticks([1, 2])
    axis_extreme.set_xticklabels(["CON", "SEN"])
    axis_extreme.tick_params(axis="both", which="major", labelsize=10.5)
    diagonal = 0.025
    for axis, y_values in (
            (axis_main, (-diagonal, diagonal)),
            (axis_extreme, (1 - diagonal, 1 + diagonal))):
        style = dict(color=colors["text"], clip_on=False, linewidth=0.85,
                     transform=axis.transAxes)
        axis.plot((-diagonal, diagonal), y_values, **style)
        axis.plot((1 - diagonal, 1 + diagonal), y_values, **style)


def basin_label_position(basin_id):
    interior_overrides = {
        2: (117.75, 69.25),
        19: (-79.25, 44.75),
    }
    if basin_id in interior_overrides:
        return interior_overrides[basin_id]
    lon2d, lat2d = np.meshgrid(longitudes, latitudes)
    selected = river_index == basin_id
    basin_lon = lon2d[selected]
    basin_lat = lat2d[selected]
    radians = np.deg2rad(basin_lon)
    center_lon = np.rad2deg(np.arctan2(np.sin(radians).mean(),
                                      np.cos(radians).mean()))
    center_lat = basin_lat.mean()
    lon_distance = np.rad2deg(np.angle(
        np.exp(1j * np.deg2rad(basin_lon - center_lon))
    ))
    nearest = np.argmin(lon_distance ** 2 + (basin_lat - center_lat) ** 2)
    return basin_lon[nearest], basin_lat[nearest]


def draw_basin_map(axis):
    values, longitude = add_cyclic_point(
        river_index, coord=longitudes
    )
    projection = ccrs.PlateCarree()
    axis.set_extent([-180, 180, 35, 90], crs=projection)
    axis.add_feature(cfeature.LAND.with_scale("50m"), facecolor=colors["land"],
                     edgecolor="none", zorder=0)
    axis.contourf(
        longitude, latitudes, np.isin(values, basins).astype(float),
        levels=[0.5, 1.5], colors=["#9AC4DB"], transform=projection, zorder=1,
    )
    axis.add_feature(cfeature.BORDERS.with_scale("50m"), edgecolor="#B0B0B0",
                     linewidth=0.4, zorder=2)
    axis.add_feature(cfeature.COASTLINE.with_scale("50m"), edgecolor="#7A7A7A",
                     linewidth=0.6, zorder=2)
    for basin_id in basins:
        axis.contour(
            longitude, latitudes, (values == basin_id).astype(float),
            levels=[0.5], colors=["#6E6E6E"], linewidths=0.8,
            transform=projection, zorder=3,
        )
        x_text, y_text = basin_label_position(basin_id)
        axis.text(x_text, y_text, str(basin_id), transform=projection,
                  ha="center", va="center", fontsize=7.5, zorder=4)
    axis.set_xticks([-120, -60, 0, 60, 120], crs=projection)
    axis.set_yticks([40, 60, 80], crs=projection)
    axis.xaxis.set_major_formatter(LongitudeFormatter())
    axis.yaxis.set_major_formatter(LatitudeFormatter())
    axis.tick_params(pad=1.5)
    axis.spines["geo"].set_edgecolor("#808080")
    axis.spines["geo"].set_linewidth(0.85)


# Figure 1
fig1_table = source_data["Fig1b"]
fig1 = plt.figure(figsize=(7.1, 5.6))
grid1 = fig1.add_gridspec(
    2, 1, height_ratios=[1.15, 2.15], left=0.065, right=0.99,
    bottom=0.09, top=0.975, hspace=0.24,
)
map_axis1 = fig1.add_subplot(grid1[0], projection=ccrs.PlateCarree())
draw_basin_map(map_axis1)
axis1 = fig1.add_subplot(grid1[1])
plot_seasonal(axis1, fig1_table, ["LORA"] + amip_models,
              r"Runoff (mm day$^{-1}$)", shading=False)
axis1.legend(
    frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=4,
    fontsize=9.0, handlelength=2.0, handletextpad=0.4, columnspacing=0.75,
)
save_svg(fig1, "Fig1_AMIP_runoff.svg",)


# Figure 3
fig3_basin = source_data["Fig3d"]
levels = np.linspace(0.0, 1.0, 11)
cmap = mcolors.ListedColormap([
    "#F7FBFF", "#E1EEF8", "#C6DBEF", "#9ECAE1", "#6BAED6",
    "#4292C6", "#2171B5", "#145A9C", "#084081", "#062B5C",
])
cmap.set_bad((0, 0, 0, 0))
norm = mcolors.BoundaryNorm(levels, cmap.N, clip=False)


def draw_bfi_map(axis, data, show_longitudes):
    field, longitude = add_cyclic_point(data, coord=longitudes)
    river, _ = add_cyclic_point(river_index, coord=longitudes)
    projection = ccrs.PlateCarree()
    axis.set_extent([-180, 180, 35, 90], crs=projection)
    axis.add_feature(cfeature.LAND.with_scale("50m"), facecolor=colors["land"],
                     edgecolor="none", zorder=0)
    axis.contourf(longitude, latitudes, np.clip(field, 0, 1), levels=levels,
                  cmap=cmap, norm=norm, transform=projection, zorder=1)
    axis.add_feature(cfeature.BORDERS.with_scale("50m"), edgecolor="#B0B0B0",
                     linewidth=0.4, zorder=2)
    axis.add_feature(cfeature.COASTLINE.with_scale("50m"), edgecolor="#7A7A7A",
                     linewidth=0.6, zorder=2)
    for basin_id in basins:
        axis.contour(
            longitude, latitudes, (river == basin_id).astype(float),
            levels=[0.5], colors=[colors["text"]], linewidths=0.8,
            transform=projection, zorder=3,
        )
    axis.set_xticks([-120, -60, 0, 60, 120], crs=projection)
    axis.set_yticks([40, 60, 80], crs=projection)
    axis.xaxis.set_major_formatter(LongitudeFormatter())
    axis.yaxis.set_major_formatter(LatitudeFormatter())
    axis.tick_params(pad=1.5, axis="x", bottom=show_longitudes,
                     labelbottom=show_longitudes)
    axis.tick_params(pad=1.5, axis="y")
    axis.spines["geo"].set_edgecolor("#808080")
    axis.spines["geo"].set_linewidth(0.85)


fig3 = plt.figure(figsize=(7.1, 6.8))
map_axes = [fig3.add_axes([0.075, y, 0.91, 0.145], projection=ccrs.PlateCarree())
            for y in (0.825, 0.665, 0.505)]
for axis, name, longitude_labels in zip(
        map_axes, ("GSCD", "CON", "SEN"), (False, False, True)):
    draw_bfi_map(axis, bfi_maps[name], longitude_labels)
colorbar_axis = fig3.add_axes([0.105, 0.445, 0.82, 0.010])
colorbar = ColorbarBase(colorbar_axis, cmap=cmap, norm=norm,
                        boundaries=levels, ticks=levels,
                        orientation="horizontal")
colorbar.set_label("BFI", labelpad=2)
colorbar.outline.set_edgecolor("#808080")
colorbar.outline.set_linewidth(0.85)
colorbar.ax.tick_params(length=3.5, width=0.8, pad=1.5)
bar_axis = fig3.add_axes([0.075, 0.075, 0.91, 0.295])
x = np.arange(1, 22)
for offset, name in zip((-0.24, 0, 0.24), ("GSCD", "CON", "SEN")):
    bar_axis.bar(x + offset, fig3_basin[name], width=0.23,
                 color=colors[name], edgecolor="none", label=name, zorder=3)
bar_axis.set(xlim=(0.4, 21.6), ylim=(0, 1), xticks=x,
             yticks=np.arange(0, 1.01, 0.2), xlabel="Basin ID", ylabel="BFI")
clean_axis(bar_axis)
bar_axis.legend(
    frameon=False, ncol=1, loc="upper right", bbox_to_anchor=(0.995, 1.035),
    handlelength=1.0, handletextpad=0.3, labelspacing=0.25,
)
save_svg(fig3, "Fig3_BFI.svg",)


# Figure 2
fig4_table = source_data["Fig2a"]
fig4_metrics = source_data["Fig2bcd"]
fig4 = plt.figure(figsize=(10.8, 5.35))
grid4 = fig4.add_gridspec(
    3, 2, width_ratios=[3.6, 1.0], height_ratios=[1.0, 1.0, 1.35],
    left=0.065, right=0.99, bottom=0.09, top=0.975,
    wspace=0.24, hspace=0.42,
)
axis4 = fig4.add_subplot(grid4[:, 0])
plot_seasonal(axis4, fig4_table, ["LORA", "CON", "SEN"],
              r"Runoff (mm day$^{-1}$)")
axis4.legend(frameon=False, loc="upper right", ncol=3,
             fontsize=10.5, handlelength=2.2, handletextpad=0.45,
             columnspacing=0.9)
axis4.set_ylim(-0.1, 2.5)
axis4.set_yticks(np.arange(0.0, 2.51, 0.5))
kge_axis = fig4.add_subplot(grid4[0, 1])
r_axis = fig4.add_subplot(grid4[1, 1])
draw_metric_panel(kge_axis, fig4_metrics, "KGE_2012", False)
draw_metric_panel(r_axis, fig4_metrics, "R", False)
kge_axis.set_ylim(-1.2, 1.0)
kge_axis.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])
r_axis.set_ylim(-0.05, 1.0)
r_axis.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
nse_grid = grid4[2, 1].subgridspec(2, 1, height_ratios=[3, 1], hspace=0.08)
nse_main = fig4.add_subplot(nse_grid[0, 0])
nse_extreme = fig4.add_subplot(nse_grid[1, 0], sharex=nse_main)
draw_broken_nse(nse_main, nse_extreme, fig4_metrics)
save_svg(fig4, "Fig2_runoff.svg",)


# Figure 4
fig5_table = source_data["Fig4a"]
fig5_metrics = source_data["Fig4bc"]
fig5 = plt.figure(figsize=(10.8, 5.35))
grid5 = fig5.add_gridspec(
    2, 2, width_ratios=[3.6, 1.0], height_ratios=[1, 1],
    left=0.065, right=0.99, bottom=0.09, top=0.975,
    wspace=0.24, hspace=0.42,
)
axis5 = fig5.add_subplot(grid5[:, 0])
plot_seasonal(axis5, fig5_table, ["GRACE", "CON", "SEN"], "TWSA (mm)")
axis5.legend(frameon=False, loc="upper right", ncol=3,
             fontsize=10.5, handlelength=2.2, handletextpad=0.45,
             columnspacing=0.9)
positions = (1.0, 2.0)
twsa_r_axis = fig5.add_subplot(grid5[0, 1])
draw_metric_panel(twsa_r_axis, fig5_metrics, "R", False, positions)
nse_axis = fig5.add_subplot(grid5[1, 1])
draw_metric_panel(nse_axis, fig5_metrics, "NSE", True, positions)
nse_axis.set_ylim(-1.25, 1.0)
nse_axis.set_yticks(np.arange(-1.0, 1.01, 0.5))
save_svg(fig5, "Fig4_TWSA.svg",)
