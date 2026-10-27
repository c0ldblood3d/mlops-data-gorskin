from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from sklearn.datasets import load_iris, load_wine

DATA_DIR = Path(__file__).resolve().parent / "data"

IRIS_BASE_COLUMNS = [
    "sepal length (cm)", "sepal width (cm)",
    "petal length (cm)", "petal width (cm)", "target",
]
WINE_BASE_COLUMNS = [
    "alcohol", "malic_acid", "ash", "alcalinity_of_ash", "magnesium",
    "total_phenols", "flavanoids", "nonflavanoid_phenols", "proanthocyanins",
    "color_intensity", "hue", "od280/od315_of_diluted_wines", "proline", "target",
]

def save_frame(frame: pd.DataFrame, path: Path, columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = (
        frame.sort_values(columns, kind="mergesort")
             .reset_index(drop=True)[columns]
    )
    ordered.to_csv(path, index=False, lineterminator="\n", float_format="%.10g")

def mode_base() -> None:
    save_frame(load_iris(as_frame=True).frame,
               DATA_DIR / "iris.csv", IRIS_BASE_COLUMNS)

def mode_wine() -> None:
    save_frame(load_wine(as_frame=True).frame,
               DATA_DIR / "wine.csv", WINE_BASE_COLUMNS)

def mode_iris_features() -> None:
    iris = (load_iris(as_frame=True).frame
            .sort_values(IRIS_BASE_COLUMNS, kind="mergesort")
            .reset_index(drop=True))
    iris["sepal_area"] = iris["sepal length (cm)"] * iris["sepal width (cm)"]
    iris["petal_area"] = iris["petal length (cm)"] * iris["petal width (cm)"]
    cols = IRIS_BASE_COLUMNS + ["sepal_area", "petal_area"]
    iris[cols].to_csv(DATA_DIR / "iris.csv", index=False,
                      lineterminator="\n", float_format="%.10g")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["base", "wine", "iris_features"])
    a = p.parse_args()
    {"base": mode_base, "wine": mode_wine,
     "iris_features": mode_iris_features}[a.mode]()