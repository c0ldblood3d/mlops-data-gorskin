from __future__ import annotations
import hashlib, sys
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
IRIS_COLS = ["sepal length (cm)", "sepal width (cm)",
             "petal length (cm)", "petal width (cm)", "target"]
WINE_ROWS, IRIS_ROWS = 178, 150

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def describe(p: Path) -> dict:
    df = pd.read_csv(p)
    return {"path": str(p.relative_to(Path.cwd())),
            "sha256": sha256_file(p), "rows": len(df),
            "columns": len(df.columns),
            "names": list(df.columns),
            "missing": int(df.isna().sum().sum())}

def assert_no_index(df: pd.DataFrame, name: str) -> None:
    for c in df.columns:
        if str(c).startswith("Unnamed") or c == "" or str(c).lower() == "index":
            raise SystemExit(f"{name}: безымянный столбец индекса: {c!r}")

def check_iris(p: Path) -> None:
    df = pd.read_csv(p)
    assert_no_index(df, p.name)
    if len(df) != IRIS_ROWS:
        raise SystemExit(f"{p.name}: строк {len(df)}, ожидалось {IRIS_ROWS}")
    if not set(IRIS_COLS).issubset(df.columns):
        raise SystemExit(f"{p.name}: потеряны исходные столбцы")
    if "sepal_area" in df.columns:
        if not (df["sepal_area"] == df["sepal length (cm)"] * df["sepal width (cm)"]).all():
            raise SystemExit(f"{p.name}: неверный sepal_area")
    if "petal_area" in df.columns:
        if not (df["petal_area"] == df["petal length (cm)"] * df["petal width (cm)"]).all():
            raise SystemExit(f"{p.name}: неверный petal_area")

def check_wine(p: Path) -> None:
    df = pd.read_csv(p)
    assert_no_index(df, p.name)
    if len(df) != WINE_ROWS:
        raise SystemExit(f"{p.name}: строк {len(df)}, ожидалось {WINE_ROWS}")

def main() -> None:
    iris, wine = DATA_DIR / "iris.csv", DATA_DIR / "wine.csv"
    if not iris.exists():
        raise SystemExit(f"нет {iris}")
    check_iris(iris)
    if wine.exists():
        check_wine(wine)
    rows = [describe(iris)] + ([describe(wine)] if wine.exists() else [])
    print(pd.DataFrame(rows).to_string(index=False))

if __name__ == "__main__":
    main()