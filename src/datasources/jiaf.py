import pandas as pd

from src.utils import blob_utils


def load_jiaf_sectoral_severity():
    blob_name = (
        f"{blob_utils.PROJECT_PREFIX}/raw/jiaf/"
        f"CAR PiN and Severity Worksheet .xlsx"
    )
    df = blob_utils.load_excel_from_blob(
        blob_name,
        sheet_name="3.3 PiN par gravité",
        header=[0, 1],
        skiprows=[0, 1, 4],
    )

    # set ADM2_PCODE as index
    df = df.set_index(("Unnamed: 4_level_0", "Unnamed: 4_level_1"))
    df.index.name = "ADM2_PCODE"
    df = df[~df.index.isnull()]
    df = df.iloc[:, 5:]

    # assign sector column names
    last_sector = "WASH"
    tuples = []
    previous_header = ""
    for l1, l2 in zip(
        df.columns.get_level_values(0), df.columns.get_level_values(1)
    ):
        if "Unnamed" not in l1:
            previous_header = l1
        tuples.append((previous_header, l2))
        if previous_header == last_sector and l2 == "PiN":
            break
    df = df.iloc[:, : len(tuples)]
    df.columns = pd.MultiIndex.from_tuples(tuples)

    # melt
    df = (
        df.melt(ignore_index=False)
        .reset_index()
        .rename(
            columns={
                "variable_0": "sector",
                "variable_1": "severity",
                "value": "pop_count",
            }
        )
    )
    df = df.dropna()
    df = df[df["severity"].isin([str(x) for x in range(1, 6)])]
    df["severity"] = df["severity"].astype(int)
    return df
