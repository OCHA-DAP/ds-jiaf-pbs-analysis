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
dfs = []

for pcode, group in df.groupby("ADM2_PCODE"):
    # method 2
    max_sector = (
        group[group["severity"] >= 3]
        .groupby("sector")["pop_count"]
        .sum()
        .idxmax()
    )
    df_out = group[group["sector"] == max_sector][
        ["ADM2_PCODE", "severity", "pop_count"]
    ]
    df_out["method"] = "2:\ndist. of sector\nwith max. PiN"
    dfs.append(df_out)

    # method 3
    df_out = group.groupby("severity")["pop_count"].max().reset_index()
    df_out["ADM2_PCODE"] = pcode
    df_out["method"] = "3:\nmax. of each\nsev. level"
    dfs.append(df_out)

    # method 4a (mean, no zeros)
    df_out = (
        group[group["pop_count"] > 0]
        .groupby("severity")["pop_count"]
        .mean()
        .reset_index()
    )
    df_out["ADM2_PCODE"] = pcode
    df_out["method"] = "4a:\nmean by sev. level\n(with zeros)"
    dfs.append(df_out)

    # method 4b (mean, with zeros)
    df_out = group.groupby("severity")["pop_count"].mean().reset_index()
    df_out["ADM2_PCODE"] = pcode
    df_out["method"] = "4b:\nmean by sev. level\n(without zeros)"
    dfs.append(df_out)

    # method 4c (median)
    df_out = group.groupby("severity")["pop_count"].median().reset_index()
    df_out["ADM2_PCODE"] = pcode
    df_out["method"] = "4b:\nmedian by sev. level"
    dfs.append(df_out)


df_compare = pd.concat(dfs, ignore_index=True)
display(df_compare)
```

```python
df_compare_adm0 = (
    df_compare.groupby(["severity", "method"])["pop_count"].sum().reset_index()
)
```

```python
colors = {5: "crimson", 4: "darkorange", 3: "gold"}
```

```python
df_pivot = df_compare_adm0[df_compare_adm0["severity"] >= 3].pivot_table(
    index="method", columns="severity", values="pop_count", aggfunc="sum"
)

fig, ax = plt.subplots(dpi=200, figsize=(10, 6))

df_pivot.plot(
    kind="bar",
    stacked=True,
    color=[colors[severity] for severity in df_pivot.columns],
    ax=ax,
)

formatter = FuncFormatter(lambda x, pos: f"{int(x):,}")
ax.yaxis.set_major_formatter(formatter)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlabel("Method")
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

ax.set_ylabel("Population Count")
ax.set_title("Stacked Bar Chart of Population Count by Severity and Method")
```

```python
df_pivot
```
