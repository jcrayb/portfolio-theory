import datetime
import yfinance as yf
import numpy as np

def nearest_trading_date(date, type_='nearest'):
    date = date.replace(tzinfo=datetime.timezone.utc)
    if type_ == 'nearest':
        start = date-datetime.timedelta(days=7)
        end = date+datetime.timedelta(days=7)
    elif type_ == 'upper':
        start = date
        end = date+datetime.timedelta(days=7)
    elif type_ == 'lower':
        start = date-datetime.timedelta(days=7)
        end = date
        
    hist = yf.Ticker('AAPL').history(start=start, end=end)

    nearest_trading_date_index = np.where(np.min(abs(hist.index-date)) == abs(hist.index-date))[0][0]
    nearest_trading_date = hist.index[nearest_trading_date_index]
    
    return nearest_trading_date