import numpy as np
import pandas as pd
import yfinance as yf
from fredapi import Fred

import requests

fred = Fred(api_key='f137a7f2802f84117668a8931892dab9')

start_date = '2000-01-01'

series_ids = ['GDPC1',    # Real Gross Domestic Product
            'DRCCLACBS',  # Delinquency Rate on Credit Card Loans, All Commercial Banks
              'CPIAUCSL',   # Consumer Price Index for All Urban Consumers: All Items in U.S. City Average
              'CPILFESL',    # Consumer Price Index for All Urban Consumers: All Items Less Food and Energy in U.S. City Average
              'UNRATE',     # Unemployment Rate
              'RPI',        # Real Personal Income
              'PCESC96',    # Real Personal Consumption Expenditures: Services
              'DGDSRX1',    # Real Personal Consumption Expenditures: Goods
              'PSAVERT',    # Personal Saving Rate
              'TERMCBCCALLNS', # Commercial Bank Interest Rate on Credit Card Plans, All Accounts
              'CORCCACBS',  # Charge-Off Rate on Credit Card Loans, All Commercial Banks
              'RCCCBACTIVEUTILPCT75', #Large Bank Consumer Credit Card Balances: Utilization: Active Accounts Only: 75th Percentile
              'FEDFUNDS',   # Federal Funds Effective Rate
              'TDSP',       # Household Debt Service Payments as a Percent of Disposable Personal Income
              'RCCCONUMACT', # Large Bank Consumer Credit Card Originations: Number of New Accounts
              'RCCCBSCOREPCT50', # Large Bank Consumer Credit Card Balances: Current Credit Score: 50th Percentile
              'RCCCBSCOREPCT25', #Large Bank Consumer Credit Card Balances: Current Credit Score: 25th Percentile
              'RCCCOSCOREPCT10', # Large Bank Consumer Credit Card Originations: Original Credit Score: 10th Percentile
              'UMCSENT',         # University of Michigan: Consumer Sentiment
              ]

def fetch_fred_data(series_ids, start_date):
    data_dict = {}
    for series_id in series_ids:
        try:
            data = fred.get_series(series_id, start_date=start_date)
            print(f"Successfully fetched FRED data for: {series_id}")
            data_dict[f'{series_id}'] = data
        except Exception as e:
            print(f"Error fetching data for series_id: {series_id}. Error: {e}")
    return data_dict

print("Fetching FRED data...")
fred_data_dict = fetch_fred_data(series_ids, start_date)
fred_data = pd.DataFrame(fred_data_dict)

# Filter data to start from start_date
fred_data = fred_data[start_date:]

quarterly_metrics = [
    'GDPC1',
    'DRCCLACBS',
    'TERMCBCCALLNS',                # double check logic here to make sure it's correct
    'CORCCACBS',
    'RCCCBACTIVEUTILPCT75',        # adjust logic here so it's correct, alsp provide similar logic to TDSP
    'TDSP',                         # adjust
    'RCCCONUMACT',                  # adjust
]

for i in quarterly_metrics:
    # Get the last non-NaN date for quarterly metrics
    last_actual_date = fred_data[i].last_valid_index()
    last_quarter = pd.Timestamp(last_actual_date).quarter
    last_year = pd.Timestamp(last_actual_date).year

    # Create a mask for dates up to the end of the current quarter
    last_quarter_end = pd.Timestamp(f"{last_year}-{last_quarter * 3:02d}-01") + pd.offsets.MonthEnd(3)

    # Forward fill up to the end of the current quarter
    fred_data.loc[:last_quarter_end, i] = fred_data.loc[:last_quarter_end, i].ffill()

    # Set all values after the current year to NaN
    next_year_start = pd.Timestamp(f"{last_year + 1}-01-01")
    fred_data.loc[next_year_start:, i] = np.nan

monthly_metrics_yoy_change = ['CPIAUCSL','CPILFESL','RPI','PCESC96','DGDSRX1',
                              'RCCCBACTIVEUTILPCT75','GDPC1','RCCCONUMACT','UMCSENT']
for i in monthly_metrics_yoy_change:
    fred_data[i] = (fred_data[i] - fred_data[i].shift(12)) / fred_data[i].shift(12) * 100


print("\nResulting DataFrame:")
print(fred_data)

# Print the most recent months to verify the NaN handling
print("\nMost recent months of data:")
print(fred_data.tail(13))