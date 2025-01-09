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

from src.datasources import jiaf
```

```python
df = jiaf.load_jiaf_sectoral_severity()
df
```

```python
df = df.dropna()
```

```python
df[df["severity"].isin([str(x) for x in range(1, 6)])]
```

```python

```
