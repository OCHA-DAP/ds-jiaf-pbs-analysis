---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.1
  kernelspec:
    display_name: ds-jiaf-pbs-analysis
    language: python
    name: ds-jiaf-pbs-analysis
---

# CAF JIAF

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from src.datasources import jiaf
```

```python
df = jiaf.load_jiaf_sectoral_severity()
df
```

```python
group
```

```python
dfs = []

for pcode, group in df.groupby("ADM2_PCODE"):
    # method 2
    max_sector = (
        group[group["severity"] >= 3]
        .groupby("sector")["pop_count"]
        .sum()
        .idxmax()
    )
    df_out = group[group["sector"] == max_sector].copy()
    df_out["method"] = "2"
    dfs.append(df_out)

    # method 3
    def get_max_severity(group):
        group_out = group.loc[group["pop_count"].idxmax()].copy()
        if group_out["pop_count"] == 0:
            group_out["sector"] = ""
        return group_out

    df_out = (
        group.groupby("severity")
        .apply(get_max_severity, include_groups=False)
        .reset_index()
    )

    df_out["ADM2_PCODE"] = pcode
    df_out["method"] = "3"
    dfs.append(df_out)

    # method 4a (mean, with zeros)
    df_out = group.groupby("severity")["pop_count"].mean().reset_index()
    df_out["ADM2_PCODE"] = pcode
    df_out["method"] = "4a"
    dfs.append(df_out)

    # method 4b (mean, without zeros)
    df_out = (
        group[group["pop_count"] > 0]
        .groupby("severity")["pop_count"]
        .mean()
        .reset_index()
    )
    df_out["ADM2_PCODE"] = pcode
    df_out["method"] = "4b"
    dfs.append(df_out)

    # method 4c (median, with zeros)
    df_out = group.groupby("severity")["pop_count"].median().reset_index()
    df_out["ADM2_PCODE"] = pcode
    df_out["method"] = "4c"
    dfs.append(df_out)

    # method 4d (median, without zeros)
    df_out = (
        group[group["pop_count"] > 0]
        .groupby("severity")["pop_count"]
        .median()
        .reset_index()
    )
    df_out["ADM2_PCODE"] = pcode
    df_out["method"] = "4d"
    dfs.append(df_out)


df_compare = pd.concat(dfs, ignore_index=True)
```

```python
df_compare_adm0 = (
    df_compare.groupby(["severity", "method"])["pop_count"].sum().reset_index()
)
```

```python
df_compare_adm0
```

```python
total_pin = df_compare_adm0[
    (df_compare_adm0["method"] == "2") & (df_compare_adm0["severity"] >= 3)
]["pop_count"].sum()
```

```python
total_pin
```

```python
colors = {5: "crimson", 4: "darkorange", 3: "gold", "adj": "silver"}
```

```python
method_names = {
    "2": "2:\ndist. of sector\nwith max. PiN",
    "3": "3:\nmax. of each\nsev. level",
    "4a": "4a:\nmean by sev. level\n(with zeros)",
    "4b": "4b:\nmean by sev. level\n(without zeros)",
    "4c": "4c:\nmedian by sev. level\n(with zeros)",
    "4d": "4d:\nmedian by sev. level\n(without zeros)",
}
```

```python
df_pivot = df_compare_adm0[df_compare_adm0["severity"] >= 3].pivot_table(
    index="method", columns="severity", values="pop_count", aggfunc="sum"
)

df_pivot.index = [method_names[x] for x in df_pivot.index]

fig, ax = plt.subplots(dpi=200, figsize=(12, 6))

df_pivot.plot(
    kind="bar",
    stacked=True,
    color=[colors[severity] for severity in df_pivot.columns],
    ax=ax,
)

ax.axhline(total_pin, color="grey", linewidth=1, linestyle="--")
ax.annotate(
    "Total PiN ",
    (-0.5, total_pin),
    va="center",
    ha="right",
    fontstyle="italic",
    color="grey",
)

formatter = FuncFormatter(lambda x, pos: f"{int(x):,}")
ax.yaxis.set_major_formatter(formatter)

ax.legend(title="Severity")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlabel("Method")
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

ax.set_ylabel("Population Count")
ax.set_title(
    "CAR Total PiN by Severity\n"
    "ignoring total PiN constraint, calculating severity for 3, 4, and 5 directly"
)
```

```python
df_pivot = df_compare_adm0[df_compare_adm0["severity"] >= 3].pivot_table(
    index="method", columns="severity", values="pop_count", aggfunc="sum"
)

df_pivot["adj"] = df_pivot.apply(lambda row: total_pin - row.sum(), axis=1)
df_pivot[3] = df_pivot[3] + df_pivot["adj"].apply(lambda x: min(x, 0))
df_pivot = df_pivot[["adj", 3, 4, 5]]

df_pivot.index = [method_names[x] for x in df_pivot.index]

fig, ax = plt.subplots(dpi=200, figsize=(12, 6))

df_pivot.plot(
    kind="bar",
    stacked=True,
    color=[colors[severity] for severity in df_pivot.columns],
    ax=ax,
)

ax.axhline(total_pin, color="grey", linewidth=1, linestyle="--")
ax.annotate(
    "Total PiN ",
    (-0.5, total_pin),
    va="center",
    ha="right",
    fontstyle="italic",
    color="grey",
)

ax.axhline(0, color="k", linewidth=0.5)

formatter = FuncFormatter(lambda x, pos: f"{int(x):,}")
ax.yaxis.set_major_formatter(formatter)

ax.legend(
    title="Severity",
    bbox_to_anchor=(1, 0.8),
    loc="center left",
    borderaxespad=0.0,
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.set_xlabel("Method")
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

ax.set_ylabel("Population Count")
ax.set_title(
    "CAR Total PiN by Severity\n" "with adjustment for total PiN constraint"
)
```

```python
df_compare[
    (df_compare["method"] == "3")
    & (df_compare["severity"] >= 3)
    & (df_compare["sector"] == "Nutrition")
]
```

```python
df_sector_counts = (
    df_compare[
        (df_compare["method"].isin(["2", "3"])) & (df_compare["severity"] >= 3)
    ]
    .groupby(["sector", "method"])
    .size()
    .rename("count")
    .reset_index()
)
```

```python
df_compare["sector"].unique()
```

```python
df_sector_counts
```

```python
df["ADM2_PCODE"].nunique() * 3
```

```python
df_pivot = df_sector_counts.pivot(
    index="method", values="count", columns="sector"
)
df_pivot.index = [method_names[x] for x in df_pivot.index]

fig, ax = plt.subplots(dpi=200, figsize=(3, 6))

df_pivot.plot(
    kind="bar",
    stacked=True,
    ax=ax,
)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.set_xlabel("Method")
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

ax.legend(
    title="Sector",
    bbox_to_anchor=(1, 0.7),
    loc="center left",
    borderaxespad=0.0,
)

ax.set_ylabel("Admin2-Severity contributions")
ax.set_title("Number of contributions to overall PiN by severity")
```

```python
df_sector_sums = (
    df.groupby(["sector", "severity"])["pop_count"].sum().reset_index()
)
```

```python
df_pivot = df_sector_sums[df_sector_sums["severity"] >= 3].pivot(
    index="sector", columns="severity", values="pop_count"
)

fig, ax = plt.subplots(dpi=200, figsize=(4, 6))

df_pivot.plot(
    kind="bar",
    stacked=True,
    color=[colors[severity] for severity in df_pivot.columns],
    ax=ax,
)

formatter = FuncFormatter(lambda x, pos: f"{int(x):,}")
ax.yaxis.set_major_formatter(formatter)

ax.legend(title="Severity")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlabel("Sector")

ax.set_ylabel("Population Count")
ax.set_title("Total population in severity by sector")
```

```python

```
