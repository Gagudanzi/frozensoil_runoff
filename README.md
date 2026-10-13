# Source data and plotting code

- `Yao_et_al_Source_Data.xlsx` contains source data for Figures 1–4. Worksheet names correspond to the figure panels.
- `plot_figure_1_2_3_4.py` produces Figures 1–4 from the source data.
- `plot_figure_5.py` produces Figure 5 from the hydraulic equations and parameters specified in the code.

Requirements: Python with NumPy, pandas, Matplotlib, and Cartopy. Cartopy may download map backgrounds on the first run.

Keep the source data and scripts in the same directory and run:

```bash
python plot_figure_1_2_3_4.py
python plot_figure_5.py
```

The five figures are saved as SVG files in the `figures` subdirectory.
