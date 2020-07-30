import pandas as pd
from pandas_datareader import data
import datetime
from datetime import date

df = data.DataReader(name='aapl',data_source="yahoo",start=0,end=date.today())

print(df)
