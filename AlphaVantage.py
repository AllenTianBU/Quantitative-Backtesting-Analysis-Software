import csv
import requests
import numpy as np
import pandas as pf
import pandas as pd
from pandas import to_numeric
from datetime import datetime

'''
ticker = 'TQQQ'
month = 5
interval = '60min'
'''


def return_data_intra(ticker, month, interval):
    data_index = []
    datalist = []
    my_list = []

    for i in range(month):
        i += 1
        print("Month: " + str(i))
        CSV_URL = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED" \
                  "&symbol=" + ticker + \
                  '&interval=' + interval + \
                  '&slice=year1month' + str(i) + \
                  '&apikey=Y7MBTIEO3VUZFU3F'
        with requests.Session() as s:
            download = s.get(CSV_URL)
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            lists = list(cr)
            for row in lists:
                my_list.append(row)

    # Creating a clean list
    print("Cleaning Data")
    my_list.remove(['time', 'open', 'high', 'low', 'close', 'volume'])

    for row in my_list:
        time = row[0][11:19]
        if '09:30:00' <= time <= '16:00:00':
            data_index.append(str_to_datetime(row[0]))
            datalist.append(row[1:6])

    # Creating the dataframe
    print("Creating dataframe")
    data_index.reverse()
    datalist.reverse()
    # Changing to dataframe
    data = pd.DataFrame(data=datalist, index=data_index, columns=['Open', 'High', 'Low', 'Close', 'Volume'])
    data['Close'] = data['Close'].apply(pd.to_numeric)

    # print(data.to_string())
    return data


def return_data_day(ticker, length):
    data_index = []
    datalist = []
    my_list = []

    print("Downlaoding data")
    CSV_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED' \
              '&symbol=' + ticker + \
              '&outputsize=' + length + \
              '&apikey=Y7MBTIEO3VUZFU3F' \
              '&datatype=csv'
    with requests.Session() as s:
        download = s.get(CSV_URL)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        lists = list(cr)
        for row in lists:
            my_list.append(row)
    my_list.pop(0)

    for row in my_list:
        split = row[0].split('-')
        year, month, day = int(split[0]), int(split[1]), int(split[2])
        date = datetime(year=year, month=month, day=day)
        data_index.append(date)
        datalist.append(row[1:7])

    print("Creating dataframe")
    data_index.reverse()
    datalist.reverse()
    # Changing to dataframe
    data = pd.DataFrame(data=datalist, index=data_index, columns=['Open', 'High', 'Low', 'close', 'Close', 'Volume'])
    data.drop(columns=['close'], axis=1, inplace=True)
    # data['Close'] = data['Close'].apply(pd.to_numeric)
    data[0:6] = data[0:6].apply(pd.to_numeric)

    return data


def close_price_only(data):
    data = pd.DataFrame(index=data.index, data=data['Close'], columns=['Close'])
    return data


def save_data_intra(ticker, month, interval):
    data = return_data_intra(ticker, month, interval)
    data.to_pickle("./downloads.pkl")


def save_data_day(ticker, length):
    data = return_data_day(ticker, length)
    data.to_pickle("./downloads.pkl")


def load_data():
    data = pd.read_pickle("./downloads.pkl")
    return data


def str_to_datetime(s):
    split1 = s[0:10].split('-')
    split2 = s[11:16].split(':')
    split = split1 + split2
    year, month, day, hour, minute = int(split[0]), int(split[1]), int(split[2]), int(split[3]), int(split[4])
    return datetime(year=year, month=month, day=day, hour=hour, minute=minute)
