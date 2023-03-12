from pathlib import Path

import pandas as pd

dataframe = pd.read_csv(Path(__file__).parent / "resources" / "test.csv")
