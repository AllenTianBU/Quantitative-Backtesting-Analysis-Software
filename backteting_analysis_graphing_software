# packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math as math
from statistics import mean
from datetime import timedelta
from AlphaVantage import *

# User input
investment = 25000 #初始投资
ticker_list = ['SPY'] #股票ticker
interval = '1min'  # 1min, 5min, 15min, 30min, 60min
month = 5 #x月的数据

emaON = True #EMA是否
smaON = True #SMA是否
trailing_stop_on = True #追踪止损开启
emaDays = 14 #EMA period
smaDays = 200 #SMA period
trailing_stop_value = 0.9925 #追踪止损

all_time = False #全天交易
start_time = "10:30:00" #开始交易时间
end_time = "15:00:00" #停止交易时间





# Summary Values
acount_value_list = []
market_change_list = []
trade_count_list = []
win_loss_ratio_list = []
win_to_all_list = []
win_average_list = []
loss_average_list = []

# Trailing_stop variable
trailingx = []
trailingy = []
trailing_stop_data = 100000

end_of_day = "14:58:00"
stop_buy_time = "14:30:00"
stop_loss_on = False
# Creates and present the graph
def plot():
    plt.figure(figsize=(15, 9))
    plt.title(ticker_list[0] + ' ' + str(month) + " Month, " + interval)
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.plot(data['Close'], lw=1, label='Close Price')
    plt.scatter(BuyPointx, BuyPointy, c='green', label='buy')
    plt.scatter(SellPointx, SellPointy, c='red', label='sell')
    plt.plot(trailingx, trailingy, lw=1, c="purple")
    plt.plot(EMAdata, 'r', lw=1, label='EMA')
    plt.plot(SMAdata, 'b', lw=1, label='SMA')
    plt.legend()
    plt.grid()
    plt.show()


def EMA(emaDays):
    global EMAdata
    EMAdata = pd.Series(data['Close'].ewm(span=emaDays, min_periods=emaDays - 1).mean())
    # plt.plot(EMAdata, 'r', lw=1, label='EMA')


def SMA(ndays):
    global SMAdata
    SMAdata = pd.Series(data['Close'].rolling(ndays).mean(), name='SMA')


def buy_signal_test(i):
    result = False
    price = data['Close'][i]
    if emaON and smaON:
        if (EMAdata[i] != None and EMAdata[i - 1] != None):
            if ((EMAdata[i] - EMAdata[i - 1] > 0 and price > EMAdata[i])
                    and SMAdata[i] - SMAdata[i - 1] > 0 and price > SMAdata[i]):
                result = True
                global high_price
                high_price = price
    '''
        if emaON:
            if (EMAdata[i] != None and EMAdata[i-1] != None):
                if(EMAdata[i]-EMAdata[i-1] > 0 and price > EMAdata[i]):
                    ema_result = True
                    global high_price
        '''
    return result


def sell_signal_test(i):
    ema_result = False

    global high_price, trailing_stop_data
    price = data['Close'][i]

    # Sell at end of day
    if time == end_of_day:
        print("Sold at end of day at:" + time)
        return True

    # Stop Loss
    if stop_loss_on:
        if price >= BuyPointy[-1] * stop_loss_value:
            print("Stopp Loss Activated")
            return True

    # Trailing Stop
    if trailing_stop_on:
        # print("Price" + str(price))
        # print("High Price" + str(high_price))
        if price >= high_price and price >= data['Close'][i - 1]:
            high_price = price
            trailing_stop_data = price * trailing_stop_value
            trailingx.append(data.index[i])
            trailingy.append(trailing_stop_data)
        else:
            trailing_stop_data = trailing_stop_data
            trailingx.append(data.index[i])
            trailingy.append(trailing_stop_data)

        if price <= trailing_stop_data:
            print(" Trailng Stop Activated")
            return True

    # Ema
    if emaON:
        if EMAdata[i] != None and EMAdata[i - 1] != None:
            if EMAdata[i] - EMAdata[i - 1] < 0:
                ema_result = True
    else:
        ema_result = True

    return ema_result


def win_percent_seprate():
    list = []
    for i in range(len(profit_percent)):
        if profit_percent[i] > 0:
            list.append(profit_percent[i])
    return list


def loss_percent_seprate():
    list = []
    for i in range(len(profit_percent)):
        if profit_percent[i] < 0:
            list.append(profit_percent[i])
    return list


def find_day_index():
    start_day = data.index[0]
    for i in range(len(data2.index)):
        if str(data2.index[i])[0:10] == str(start_day - timedelta(days=1))[0:10]:
            return (i)

    for i in range(len(data2.index)):
        if str(data2.index[i])[0:10] == str(start_day - timedelta(days=2))[0:10]:
            return (i)

    for i in range(len(data2.index)):
        if str(data2.index[i])[0:10] == str(start_day - timedelta(days=3))[0:10]:
            return (i)


def back_test_result(TradeCount, money):
    profit_percent.sort()
    win_percent_list = win_percent_seprate()
    loss_percent_list = loss_percent_seprate()
    # index = find_day_index()

    # prior_closing_price = data2['Close'][index]

    # print(data['Close'][-1])
    # print(prior_closing_price)

    # percent_change = ((data['Close'][-1]-prior_closing_price)/prior_closing_price)*100

    acount_value_list.append(round((money / investment - 1) * 100, 1))
    # market_change_list.append(round(percent_change,1))
    trade_count_list.append(int(TradeCount))
    win_loss_ratio_list.append(round(len(win_percent_list) / len(loss_percent_list), 2))
    win_to_all_list.append(round(len(win_percent_list) / TradeCount, 2))
    win_average_list.append(round(sum(win_percent_list) / len(win_percent_list), 2))
    loss_average_list.append(round(sum(loss_percent_list) / len(loss_percent_list), 2))

    # print summary/stock
    print("\nTrade Count/交易次数: " + str(TradeCount))
    print("------")
    print("Final Account Value/最终账号价值: $" + str(round(money, 2)) + "(" + str(
        round((money / investment - 1) * 100, 2)) + "%)")
    print("------")


def show_average():
    ticker_list.append(' ')
    acount_value_list.append(mean(acount_value_list))
    # market_change_list.append(mean(market_change_list))
    trade_count_list.append(mean(trade_count_list))
    win_loss_ratio_list.append(mean(win_loss_ratio_list))
    win_to_all_list.append(mean(win_to_all_list))
    win_average_list.append(mean(win_average_list))
    loss_average_list.append(mean(loss_average_list))

    # Add the %
    for i in range(len(acount_value_list)):
        acount_value_list[i] = str(round(acount_value_list[i], 1)) + "%"
        # market_change_list[i] =  str(round(market_change_list[i],1)) + "%"


def summary():
    # In a table. Table on left. Change%, trade count,
    show_average()
    data_table = pd.DataFrame(list(
        zip(acount_value_list, trade_count_list, win_loss_ratio_list, win_to_all_list, win_average_list,
            loss_average_list)),
        index=ticker_list,
        columns=['account change%', 'Trade Count', 'Win Loss Ratio', "Win percent", "Win Average",
                 "Loss Average"])
    print("Trailing stop: " + str(trailing_stop_on))
    print("\n")
    print(data_table.to_string())


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

    for i in range(len(data.index)):
        time = str(data.index[i])[11:19]
        if all_time or (time >= start_time and time <= end_time):
            price = data['Close'][i]
            str_price = str(round(price, 2))
            if position == False and time <= stop_buy_time:  # Signal to buy
                buy_signal = buy_signal_test(i)
                if (buy_signal == True):
                    print(str(data.index[i])[0:19])
                    trailing_stop_data = price * trailing_stop_value
                    trailingx.append(data.index[i])
                    trailingy.append(trailing_stop_data)

                    stock_volume = math.floor(money / price)  # Rendering stock volume
                    money = money - stock_volume * price  # subtracting money
                    BuyPointx.append(data.index[i])
                    BuyPointy.append(price)
                    position = True
                    print(" Short at: " + str_price)
            if position:  # Signal to sell
                sell_signal = sell_signal_test(i)
                if sell_signal == True:
                    print(str(data.index[i])[0:19])
                    money = money + stock_volume * price
                    stock_volume = 0
                    SellPointx.append(data.index[i])
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


# Download Data
for i in range(len(ticker_list)):
    save_data_intra(ticker_list[i], month, interval)
    data = load_data()
    if emaON:
        EMA(emaDays)  # Creates EMAdata, a series containing EMA data
    if smaON:
        SMA(smaDays)
    backTest()
summary()
plot()
print("\nFinished")
