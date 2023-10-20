import pandas as pd
import datetime
import yfinance as yf
import numpy as np

import quarters

def get_all_returns_between_years(start_year:int, end_year:int) -> pd.DataFrame:
    companies_to_eliminate = get_throughout(start_year)[1]
    quarter_dates = quarters.get_dates_between_years(start_year, end_year)
    quarter_names = quarters.get_names_between_years(start_year, end_year)

    companies = pd.read_csv('./constituents.csv').set_index('Symbol').drop(labels=companies_to_eliminate).index
    quarterly_returns_df = pd.DataFrame(0, index=quarter_names, columns=companies)
    for company in companies:
        start_date = datetime.datetime(year=start_year, month=1, day=1)
        hist = yf.Ticker(company).history(start=start_date)
        year = start_year
        valid = True
        while year < end_year and valid:
            for quarter in quarter_dates[year]:
                quarter_start_date = quarter_dates[year][quarter]['start']
                quarter_end_date = quarter_dates[year][quarter]['end']
                try:
                    nearest_start_trading_date_index = np.where(np.min(abs(hist.index-quarter_start_date)) == abs(hist.index-quarter_start_date))[0][0]
                    nearest_start_trading_date = hist.index[nearest_start_trading_date_index]
        
                    nearest_end_trading_date_index = np.where(np.min(abs(hist.index-quarter_end_date)) == abs(hist.index-quarter_end_date))[0][0]
                    nearest_end_trading_date = hist.index[nearest_end_trading_date_index]
        
                    start_price = float(hist['Close'][nearest_start_trading_date])
                    end_price = float(hist['Close'][nearest_end_trading_date])
                    if start_price == 0 or end_price == 0:
                        valid = False
                        break
                    
                    growth = (end_price - start_price)/start_price
                    quarterly_returns_df[company][f'{year}-{quarter}'] = growth
                except:
                    print(f'{year}-{quarter}', company)
                    valid = False
                    break
            year += 1
        if not valid:
            print(company, year)
            
        if quarterly_returns_df[company].iloc[0] == 0 and quarterly_returns_df[company].iloc[1] == 0:
            quarterly_returns_df = quarterly_returns_df.drop(company, axis=1)
            print('invalid', company)
    quarterly_returns_df.to_csv(f'./data/returns/returns_{start_year}-{end_year}.csv')
    return quarterly_returns_df

def get_throughout(start_year:int) -> tuple:
    companies_throughout = []
    companies_to_eliminate = []
    df = pd.read_csv('./constituents.csv')
    start_date = datetime.datetime(year=start_year, month=1, day=1)
    for i in range(len(df['Symbol'])):
        row = df.iloc[i]
        try:
            added_date = datetime.datetime.strptime(row['Date added'], "%Y-%m-%d")
            if added_date > start_date:
                companies_to_eliminate += [row['Symbol']]
            else:
                #print(added_date)
                companies_throughout += [row['Symbol']]
        except Exception as e:
            companies_to_eliminate += [row['Symbol']]
            continue
    return (companies_throughout, companies_to_eliminate)

