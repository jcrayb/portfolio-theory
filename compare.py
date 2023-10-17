import pandas as pd
import yfinance as yf
import datetime

def compare_to_benchmark(weights, companies, start_year, benchmark='SPY'):
    start_date_local = datetime.datetime(year=start_year, month=1, day=1)
    index = yf.Ticker('AAPL').history(start=start_date_local).index
    markowitz = pd.DataFrame(0, index=index, columns = companies)

    for i in range(len(companies)):
        company = companies[i]
        weight = weights[i]
        history = yf.Ticker(company).history(start=start_date_local)['Close']
        try:
            adjusted = history/history.iloc[0]*weight
        except:
            continue
        markowitz[company] = adjusted
    total = pd.DataFrame(0, index=index, columns=['portfolio', 'benchmark'])
    total['portfolio'] = markowitz.sum(axis=1)
    benchmark_hist = yf.Ticker(benchmark).history(start=start_date_local)['Close']
    total['benchmark'] = benchmark_hist/benchmark_hist.iloc[0]
    return total
    
        