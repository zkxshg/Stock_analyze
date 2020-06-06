import pandas as pd
import xlrd
import tushare as ts
import numpy as np
import talib


def calculateDB1(HIGH, LOW, CLOSE, M1, M2, smaArray=[]):
    MIN_21 = []
    MAX_21 = []
    for i in range(0, 21):
        MIN_21.append(LOW[:i + 1].min())
        MAX_21.append(HIGH[:i + 1].max())
    for i in range(21, len(LOW)):
        MIN_21.append(LOW[i - 20:i + 1].min())
        MAX_21.append(HIGH[i - 20:i + 1].max())
    MIN_21 = np.array(MIN_21)
    MAX_21 = np.array(MAX_21)
    # DB1赋值: (收盘价 - 21日内最低价的最低值) / (21日内最高价的最高值-21日内最低价的最低值) * 100
    smaArray = (CLOSE - MIN_21) / (MAX_21 - MIN_21) * 100
    return smaArray


def calculateDB2(DB1, M1, M2, smaArray=[]):
    length = len(DB1)
    if not smaArray:
        # 首日EMA記為當日收盤價
        smaArray.append(DB1[0])
        for i in range(1, length):
            ema = (M2 * DB1[i] + (M1 - M2) * smaArray[-1]) / M1
            smaArray.append(ema)
    return smaArray


# 计算SMA
def calculateSMA(PDI, MDI, ADX, N2, weight, smaArray=[]):
    length = len(PDI)
    X = (MDI - PDI) / (MDI + PDI) * 100
    # 首日SMA記為當日ADX
    smaArray.append(ADX[0])
    # SMA(加权移动平均数)＝[ X ×  M ＋ Y ×  (N－M) ] ／ N 
    # 输出SMA
    for i in range(1, length):
        sma = (weight * X[i] + (N2 - weight) * ADX[i - 1]) / (N2 + 1)
        smaArray.append(sma)
    # X ＝（MDI－PDI)／(MDI＋PDI) ×100; M为权重，这里是1; Y为前一日ADX值
    return np.array(smaArray)


# 输入文件路径
path = "沪深A股.xls"
# 输入要读取的工作表 / sheet 数，默认读取第一张
sheets = [3]
# sheets = [0, 1, 2, 3]
# 输入储存文件路径
savePath = "./data"
# 设置计算 ADX、PDI 和 MDI 的周期，默认为14 (M)
period = 14
# 设置计算 SMA 的周期 N
N = 13
N2 = 8
weight = 1

df = ts.pro_bar('600000.SH', adj='hfq', start_date='2020-01-01', end_date='2020-05-29')
df = df.sort_index(ascending=True)
df['PDI'] = talib.PLUS_DI(df.high, df.low, df.close, timeperiod=period)
df['MDI'] = talib.MINUS_DI(df.high, df.low, df.close, timeperiod=period)
df['ADX'] = talib.ADX(df.high, df.low, df.close, timeperiod=period)
df['SMA'] = calculateSMA(df['PDI'], df['MDI'], df['ADX'], N, 1, [])
df['DB1'] = calculateDB1(df.high, df.low, df.close, N, N2, [])
df['DB2'] = calculateDB2(df['DB1'], N, N2, [])
saveFile = savePath + "/600000.csv"
df.to_csv(saveFile)
