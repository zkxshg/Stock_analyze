# 计算沪深个股的日线和周线多项指标，合并保存为 股票代码.csv
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
    return MIN_21, MAX_21, smaArray


def calculateDB2(DB1, M1, M2, smaArray=[]):
    length = len(DB1)
    if not smaArray:
        # 首日EMA記為當日收盤價
        smaArray.append(DB1[0])
        for i in range(1, length):
            ema = (M2 * DB1[i] + (M1 - M2) * smaArray[-1]) / M1
            smaArray.append(ema)
    return smaArray


# 输入文件路径
path = "沪深A股.xls"

# 输入要读取的工作表 / sheet 数，默认读取第一张
# sheets = [3]
sheets = [0, 1, 2, 3]

# 输入储存文件路径
savePath = "./data/stock"

# 设置计算 ADX、PDI 和 MDI 的周期，默认为14 (M)
period = 14

# 设置计算 SMA 的周期 N
N = 13
N2 = 8
weight = 1

# 设置起始时间，两个要保持一致
start_time = '2019-06-05'
start_time2 = '20190605'

# df1 = ts.pro_bar("600000.SH", adj='qfq', start_date='2017-01-01')
# df1.to_csv("./data/demo.csv")

for sheet in sheets:
    print("正在读取第", end='')
    print(sheet, end='')
    print("张工作表")

    # 读入单张工作表
    sheet_i = pd.read_excel(path, sheet_name=sheet)
    # 读入股票代码列
    stockCode = sheet_i["代码"]

    # 根据股票代码读取日指数并保存
    for SC in stockCode:
        code = str(SC)

        # 补零到六位代码
        while len(code) < 6:
            code = "0" + code

        # 补全复权代码
        if code[0] == '0':
            code = code + '.SZ'
        else:
            code = code + '.SH'

        # 读入前复权日指数
        df1 = ts.pro_bar(code, adj='qfq', start_date=start_time2)
        df = df1.sort_values('trade_date', ascending=True)
        df.index = df1.index

        # 如果数据为空
        if df is None:
            print("股票代码", end='')
            print(code, end='')
            print("的查询结果为空")
            continue

        # 数据量小于21
        if len(df) < 21:
            print("股票代码", end='')
            print(code, end='')
            print("的记录数量小于21，不予计算 DB2")
            continue

        # 计算 DB1 和 DB2
        df['MIN_21'], df['MAX_21'], df['DB1'] = calculateDB1(df.high, df.low, df.close, N, N2, [])
        df['DB2'] = calculateDB2(df['DB1'], N, N2, [])

        # 计算其他指标
        df['RSI'] = talib.RSI(df.open, timeperiod=12)
        df["DMI"] = talib.DX(df.high, df.low, df.close, timeperiod=14)
        df["MACD_macd"], df["MACD_macdsignal"], df["MACD_macdhist"] = talib.MACD(df.close, fastperiod=12, slowperiod=26,
                                                                                 signalperiod=9)
        df['OBV'] = talib.OBV(df.close, df.vol)
        df['DMA'] = talib.DEMA(df.close, timeperiod=30)
        df['EXPMA'] = talib.EMA(df.close, timeperiod=30)
        df['TRIX'] = talib.TRIX(df.close, timeperiod=30)
        df["SAR"] = talib.SAR(df.high, df.low, acceleration=0, maximum=0)
        df["CCI"] = talib.CCI(df.high, df.low, df.close, timeperiod=14)
        df["ROC"] = talib.ROC(df.close, timeperiod=10)

        # ==================== 周线 ===========================
        dfw1 = ts.pro_bar(ts_code=code, freq='W', adj='qfq', start_date=start_time2)
        dfw = dfw1.sort_values('trade_date', ascending=True)
        dfw.index = dfw1.index

        # 如果数据为空
        if dfw is None:
            print("股票代码", end='')
            print(code, end='')
            print("的周线数据查询结果为空")
            continue

        # 数据量小于21
        if len(dfw) < 21:
            print("股票代码", end='')
            print(code, end='')
            print("的周线数据记录数量小于21，不予计算 DB2")
            continue

        # 计算 DB1 和 DB2
        dfw['MIN_21'], dfw['MAX_21'], dfw['DB1'] = \
            calculateDB1(dfw.high, dfw.low, dfw.close, N, N2, [])
        dfw['DB2'] = calculateDB2(dfw['DB1'], N, N2, [])

        # 计算其他指标
        dfw['RSI'] = talib.RSI(dfw.open, timeperiod=12)
        dfw["DMI"] = talib.DX(dfw.high, dfw.low, dfw.close, timeperiod=14)
        dfw["MACD_macd"], dfw["MACD_macdsignal"], dfw["MACD_macdhist"] = \
            talib.MACD(dfw.close, fastperiod=12, slowperiod=26, signalperiod=9)
        dfw['OBV'] = talib.OBV(dfw.close, dfw.vol)
        dfw['DMA'] = talib.DEMA(dfw.close, timeperiod=30)
        dfw['EXPMA'] = talib.EMA(dfw.close, timeperiod=30)
        dfw['TRIX'] = talib.TRIX(dfw.close, timeperiod=30)
        dfw["SAR"] = talib.SAR(dfw.high, dfw.low, acceleration=0, maximum=0)
        dfw["CCI"] = talib.CCI(dfw.high, dfw.low, dfw.close, timeperiod=14)
        dfw["ROC"] = talib.ROC(dfw.close, timeperiod=10)

        pos_day = 0
        pos_week = 0
        
        # 合并日线和周线指标
        while pos_day < len(df) and pos_week < len(dfw):
            if dfw['trade_date'][pos_week] < df['trade_date'][pos_day]:
                dfw.loc[pos_week, 'trade_date'] = str(dfw['trade_date'][pos_week]) + '_week'
                above = df.loc[:pos_day - 1]
                below = df.loc[pos_day:]
                df = above.append(dfw.loc[pos_week], ignore_index=False).append(below, ignore_index=False)
                pos_week += 1
            else:
                pos_day += 1

        # 保存为 csv 文件
        saveFile = savePath + "/" + code + ".csv"
        df.to_csv(saveFile, encoding='gbk', float_format='%.3f')
        print("已将股票代码", end='')
        print(code, end='')
        print("的结果保存在路径", end='')
        print(saveFile)

print("程序结束")
