# packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from AlphaVantage import *
import datetime
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import layers
import math as math
from statistics import mean

ticker = 'SPY'
investment = 10000

acount_value_list = []
market_change_list = []
trade_count_list = []
win_loss_ratio_list = []
win_to_all_list = []
win_average_list = []
loss_average_list = []


def plot():
    plt.figure(figsize=(15, 9))
    plt.title(ticker)
    plt.plot(dates_train, train_predictions)
    plt.plot(dates_train, y_train)
    plt.plot(dates_val, val_predictions)
    plt.plot(dates_val, y_val)
    plt.plot(dates_test, test_predictions)
    plt.plot(dates_test, y_test)
    plt.scatter(BuyPointx, BuyPointy, c='green', label='buy')
    plt.scatter(SellPointx, SellPointy, c='red', label='sell')
    plt.grid()
    plt.legend(['Training Predictions',
                'Training Observations',
                'Validation Predictions',
                'Validation Observations',
                'Testing Predictions',
                'Testing Observations'])
    plt.show()


def str_to_datetime(s):
    split = s.split('-')
    year, month, day = int(split[0]), int(split[1]), int(split[2])
    return datetime.datetime(year=year, month=month, day=day)


def df_to_windowed_df(dataframe, first_date_str, last_date_str, n=3):
    first_date = str_to_datetime(first_date_str)
    last_date = str_to_datetime(last_date_str)

    target_date = first_date

    dates = []
    X, Y = [], []

    last_time = False
    while True:
        df_subset = dataframe.loc[:target_date].tail(n + 1)

        if len(df_subset) != n + 1:
            print(f'Error: Window of size {n} is too large for date {target_date}')
            return

        values = df_subset['Close'].to_numpy()
        x, y = values[:-1], values[-1]

        dates.append(target_date)
        X.append(x)
        Y.append(y)

        next_week = dataframe.loc[target_date:target_date + datetime.timedelta(days=7)]
        next_datetime_str = str(next_week.head(2).tail(1).index.values[0])
        next_date_str = next_datetime_str.split('T')[0]
        year_month_day = next_date_str.split('-')
        year, month, day = year_month_day
        next_date = datetime.datetime(day=int(day), month=int(month), year=int(year))

        if last_time:
            break

        target_date = next_date

        if target_date == last_date:
            last_time = True

    ret_df = pd.DataFrame({})
    ret_df['Target Date'] = dates

    X = np.array(X)
    for i in range(0, n):
        X[:, i]
        ret_df[f'Target-{n - i}'] = X[:, i]

    ret_df['Target'] = Y

    return ret_df


def windowed_df_to_date_X_y(windowed_dataframe):
    df_as_np = windowed_dataframe.to_numpy()

    dates = df_as_np[:, 0]

    middle_matrix = df_as_np[:, 1:-1]
    X = middle_matrix.reshape((len(dates), middle_matrix.shape[1], 1))

    Y = df_as_np[:, -1]

    return dates, X.astype(np.float32), Y.astype(np.float32)


save_data_day(ticker, 'full')
data = load_data()
data = close_price_only(data)

windowed_df = df_to_windowed_df(data,
                                '2018-11-14',
                                '2022-11-14',
                                n=60)
dates, X, y = windowed_df_to_date_X_y(windowed_df)

# Testing
q_80 = int(len(dates) * .8)
q_90 = int(len(dates) * .9)

dates_train, X_train, y_train = dates[:q_80], X[:q_80], y[:q_80]

dates_val, X_val, y_val = dates[q_80:q_90], X[q_80:q_90], y[q_80:q_90]
dates_test, X_test, y_test = dates[q_90:], X[q_90:], y[q_90:]

model = Sequential([layers.Input((60, 1)),
                    layers.LSTM(64),
                    layers.Dense(32, activation='relu'),
                    layers.Dense(32, activation='relu'),
                    layers.Dense(32, activation='relu'),
                    layers.Dense(1)])

model.compile(loss='mse',
              optimizer=Adam(learning_rate=0.001),
              metrics=['mean_absolute_error'])

model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=32)

train_predictions = model.predict(X_train).flatten()
val_predictions = model.predict(X_val).flatten()
test_predictions = model.predict(X_test).flatten()


def buy_signal_test(i):
    result = False
    if test_predictions[i + 1] > test_predictions[i]:
        result = True

    return result


def sell_signal_test(i):
    result = False
    if (test_predictions[i + 1] < test_predictions[i]):
        result = True
    return result


def back_test_result(TradeCount, money):
    # print summary/stock
    print("\nTrade Count/交易次数: " + str(TradeCount))
    print("------")
    print("Final Account Value/最终账号价值: $" + str(round(money, 2)) + "(" + str(
        round((money / investment - 1) * 100, 2)) + "%)")
    print("------")


def backTest():
    money = investment
    prev_money = investment
    stock_volume = 0
    trade_count = 0
    price = 0
    position = False

    global BuyPointx, BuyPointy, SellPointx, SellPointy, trailing_stop_data, time, profit_percent
    BuyPointx = []
    BuyPointy = []
    SellPointx = []
    SellPointy = []
    profit_percent = []

    for i in range(len(dates_test) - 1):

        price = y_test[i]
        str_price = str(round(price, 2))

        if position == False:  # Signal to buy
            buy_signal = buy_signal_test(i)
            if (buy_signal == True):
                print(str(dates_test[i]))

                stock_volume = math.floor(money / price)  # Rendering stock volume
                money = money - stock_volume * price  # subtracting money
                BuyPointx.append(dates_test[i])
                BuyPointy.append(price)
                position = True
                print(" bought at: " + str_price)
        if position == True:  # Signal to sell
            sell_signal = sell_signal_test(i)
            if (sell_signal == True):
                print(str(dates_test[i]))
                money = money + stock_volume * price
                stock_volume = 0
                SellPointx.append(dates_test[i])
                SellPointy.append(price)
                profit_percent.append(round(((money - prev_money) / prev_money) * 100, 2))
                position = False
                print(" Sold at: " + str_price)
                print("Account value: " + str(round(money, 2)) + " (" + str(round(money - prev_money, 2))
                      + ") (" + str(round((money - prev_money) / prev_money * 100, 2)) + "%)\n\n")
                prev_money = money
                trade_count += 1

    money = money + stock_volume * price
    back_test_result(trade_count, money)


prediction_data = pd.Series(index=dates_test, data=test_predictions)
backTest()
plot()

print(data)
# print(windowed_df)
