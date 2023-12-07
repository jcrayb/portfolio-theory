import pandas as pd
import yfinance_cache as yfc
import datetime

def compare_to_benchmark(weights, companies, start_date, benchmark='SPY'):
    dates = yfc.Ticker('AAPL').history(period='10y').reset_index()['Date']
    index = dates.loc[dates>=start_date]
    total = pd.DataFrame(0, index=index, columns=['benchmark'])
    x = 1
    for weight in weights:
        markowitz = pd.DataFrame(0, index=index, columns = companies)
    
        for i in range(len(companies)):
            company = companies[i]
            w = weight[i]
            history = yfc.Ticker(company).history(period='10y')['Close']
            history = history.loc[history.index>=start_date]
            try:
                adjusted = history/history.iloc[0]*w
            except:
                continue
            markowitz[company] = adjusted
        
        total[f'portfolio_{x}'] = markowitz.sum(axis=1)
        x+=1
    benchmark_hist = yfc.Ticker(benchmark).history(period='10y')['Close']
    benchmark_hist = benchmark_hist.loc[benchmark_hist.index>=start_date]
    total['benchmark'] = benchmark_hist/benchmark_hist.iloc[0]
    return total
    
        