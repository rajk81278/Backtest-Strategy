import yfinance as yf
import pandas as pd
import pandas_ta as ta
import logging
import datetime
import time

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

logging.basicConfig(level=logging.INFO, filename=f'sma200_{datetime.date.today()}', filemode='w', format="%(asctime)s - %(message)s")


# Define the stock ticker and the time period
start_date = '2020-08-01'
end_date = '2024-08-31'
interval = '1d'

# Fetch the historical data
stock=input("Enter a stock ticker symbol: ")
# stock= 'TCS.NS'

df = yf.download(stock, start=start_date, end=end_date, interval=interval)
print(df)

# Calculate EMAs
emasUsed=[3,5,8,10,12,15,30,35,40,45,50,60]
for x in emasUsed:
	ema=x
	df["Ema_"+str(ema)]=round(df.iloc[:,4].ewm(span=ema, adjust=False).mean(),2)


df=df.iloc[60:]

print(df)

for i in df.index:
	cmin=min(df["Ema_3"][i],df["Ema_5"][i],df["Ema_8"][i],df["Ema_10"][i],df["Ema_12"][i],df["Ema_15"][i],)
	cmax=max(df["Ema_30"][i],df["Ema_35"][i],df["Ema_40"][i],df["Ema_45"][i],df["Ema_50"][i],df["Ema_60"][i],)

	close=df["Adj Close"][i]

print(cmin)
print(cmax)

for i in df.index:
	cmin=min(df["Ema_3"][i],df["Ema_5"][i],df["Ema_8"][i],df["Ema_10"][i],df["Ema_12"][i],df["Ema_15"][i],)
	cmax=max(df["Ema_30"][i],df["Ema_35"][i],df["Ema_40"][i],df["Ema_45"][i],df["Ema_50"][i],df["Ema_60"][i],)


def calculate_emas(df, emas_used):
    for ema in emas_used:
        # Make sure to refer to the correct column and add the EMA columns
        df[f"Ema_{ema}"] = df.iloc[:, 4].ewm(span=ema, adjust=False).mean().round(2)
    return df

# Function to calculate cmin (minimum of small EMAs)
def calculate_cmin(df, emas_list):
    cmin_list = []
    for i in df.index:
        # Use list comprehension to gather EMA values and calculate min
        try:
            cmin = min(df[f"Ema_{ema}"][i] for ema in emas_list)
        except KeyError as e:
            print(f"KeyError: {e}, check if EMA columns exist.")
            return None
        cmin_list.append(cmin)
    return cmin_list

# Function to calculate cmax (maximum of large EMAs)
def calculate_cmax(df, emas_list):
    cmax_list = []
    for i in df.index:
        try:
            cmax = max(df[f"Ema_{ema}"][i] for ema in emas_list)
        except KeyError as e:
            print(f"KeyError: {e}, check if EMA columns exist.")
            return None
        cmax_list.append(cmax)
    return cmax_list

# Example usage
emas_used = [3, 5, 8, 10, 12, 15, 30, 35, 40, 45, 50, 60]

# First, calculate the EMAs
df = calculate_emas(df, emas_used)

# List of small EMAs for cmin and large EMAs for cmax
small_emas = [3, 5, 8, 10, 12, 15]
large_emas = [30, 35, 40, 45, 50, 60]

# Now, calculate cmin and cmax
df['cmin'] = calculate_cmin(df, small_emas)
df['cmax'] = calculate_cmax(df, large_emas)

print(df[['cmin', 'cmax']])
print(df)

def same_ind1(df,name):
     return df[name]
def same_ind2(df,name):
     return df[name]

class SmaCross(Strategy):
    logging.info('inside strategy')
    

    def init(self):
        close = self.data.Close.s
        self.cmin=self.I(same_ind1,self.data.df,'cmin')
        self.cmax=self.I(same_ind2,self.data.df,'cmax')

    def next(self):

        if crossover(self.cmin,self.cmax):
             self.position.close()
             self.buy()
        elif crossover(self.cmax,self.cmin):
             self.position.close()


bt = Backtest(df, SmaCross,
              cash=100000, commission=.002,
              exclusive_orders=True)

output = bt.run()
print(output)
bt.plot()


