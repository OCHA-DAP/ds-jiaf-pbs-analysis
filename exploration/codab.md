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

# CODAB

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
from src.datasources import codab
```

```python
codab.download_codab_to_blob()
```

```python
adm = codab.load_codab_from_blob()
```

```python
adm.plot()
```
