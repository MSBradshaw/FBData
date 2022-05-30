import pandas as pd
import sys

"""
1. slip score file with a column labeled "baseline"
2. hotspot score file with no baseline column
3. where to save a new version of the hotspot score with a new baseline
"""

df1 = pd.read_csv(sys.argv[1])
df2 = pd.read_csv(sys.argv[2])

df2['baseline'] = df1['baseline']

df2.to_csv(sys.argv[3])