from pathlib import Path

import pandas as pd

df = pd.read_csv(Path(__file__).parent / "resources" / "test.csv")
