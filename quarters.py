import pandas as pd
import datetime
import yfinance as yf
from dateutil.relativedelta import relativedelta
import os

from utils import tz

gdp_data = pd.read_csv('./data/us_gdp_growth_1995.csv').set_index('quarter')

def get_names_between_years(start_year:int, end_year:int) -> list:
    date = datetime.datetime(year=start_year, month=1, day=1, tzinfo = tz)
    quarters = []
    year = start_year
    while year < end_year:
        for i in range(4):
            quarters += [f'{year}-Q{i+1}']
        year += 1
        date += relativedelta(years=1)
    return quarters

def get_dates_between_years(start_year:int, end_year:int) -> dict:
    date = datetime.datetime(year=start_year, month=1, day=1, tzinfo = tz)
    quarters = {}
    year = start_year
    while year < end_year:
        quarters[year] = {} 
        for i in range(4):
            quarters[year][f'Q{i+1}'] = {}
            quarters[year][f'Q{i+1}']['start'] = date+relativedelta(months=3*(i))
            quarters[year][f'Q{i+1}']['end']  = date+relativedelta(months=3*(i+1))-datetime.timedelta(days=1)
        year += 1
        date += relativedelta(years=1)
    return quarters

def get_mean_rfr_between_years(start_year:int, end_year:int)-> pd.DataFrame:
    if os.path.exists(f'./cached/mean_rfr-{start_year}-{end_year}.csv'):
        quarterly_rfr_df = pd.read_csv(f'./cached/mean_rfr-{start_year}-{end_year}.csv').set_index('Unnamed: 0')
        return quarterly_rfr_df
    start_date = datetime.datetime(year=start_year, month=1, day=1)
    IRX_hist = yf.Ticker('^IRX').history(start=start_date)['Close'].reset_index()

    quarter_names = get_names_between_years(start_year, end_year)
    quarters = get_dates_between_years(start_year, end_year)
    
    quarterly_rfr_df = pd.DataFrame(columns=['avg_rfr'], index=quarter_names)
    
    for year in quarters:
        for quarter in quarters[year]:
            quarter_start_date = quarters[year][quarter]['start']
            quarter_end_date = quarters[year][quarter]['end']
            mask = (IRX_hist['Date'] >= quarter_start_date) & (IRX_hist['Date'] < quarter_end_date)
            quarter_rfr = IRX_hist.loc[mask]['Close'].mean()
            
            quarterly_rfr_df['avg_rfr'][f'{year}-{quarter}'] = quarter_rfr/100
    quarterly_rfr_df.to_csv(f'./cached/mean_rfr-{start_year}-{end_year}.csv')
    return quarterly_rfr_df

def get_gdp_growth(quarter: str) -> float:
    try:
        return gdp_data['growth_%'][quarter]/100
    except KeyError:
        return None

def get_gdp_growth_between_years(start_year:int, end_year:int) -> pd.DataFrame:
    quarters= get_names_between_years(start_year, end_year)
    growth_df = pd.DataFrame(0, index=quarters, columns=['growth'])
    for quarter in quarters:
        growth_df['growth'][quarter] = gdp_data['growth_%'][quarter]/100
    return growth_df

def get_inflation_between_years(start_year:int, end_year:int) -> pd.DataFrame:
    quarters = get_names_between_years(start_year, end_year)
    q_dates = get_dates_between_years(start_year, end_year)

    inflation_df = pd.read_csv('./data/cpi_qoq_change.csv').set_index('DATE')
    
    df = pd.DataFrame(0, index=quarters, columns=['inflation'])
    for quarter in quarters:
        split = quarter.split('-')
        year = int(split[0])
        name = split[1]
        
        date = q_dates[year][name]['start'].strftime('%Y-%m-%d')
        
        inflation = inflation_df['inflation'][date]
        df['inflation'][quarter] = inflation
    return df/100

def get_unemployment_between_years(start_year:int, end_year:int) -> pd.DataFrame:
    quarters = get_names_between_years(start_year, end_year)
    q_dates = get_dates_between_years(start_year, end_year)

    unem_df = pd.read_csv('./data/unemployment_rate.csv').set_index('DATE')
    
    df = pd.DataFrame(0, index=quarters, columns=['unemployment'])
    for quarter in quarters:
        split = quarter.split('-')
        year = int(split[0])
        name = split[1]
        
        date = q_dates[year][name]['start'].strftime('%Y-%m-%d')
        
        unem = unem_df['UNRATE'][date]
        df['unemployment'][quarter] = unem
    return df/100