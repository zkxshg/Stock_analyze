import pandas as pd
import xlrd
import tushare as ts
import numpy as np


token = " "
ts.set_token(token)
pro = ts.pro_api()


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
sheets = [1, 3]
# sheets = [0, 1, 2, 3]
# 输入储存文件路径
savePath = "./data"
# 设置计算 ADX、PDI 和 MDI 的周期，默认为14
period = 14
# 设置计算 SMA 的周期 N
N = 13
N2 = 8
weight = 1
# 设置起始时间，两个要保持一致
start_time = '2019-06-05'
start_time2 = '20190605'

# 创建汇总表模板
# demo = ts.get_hist_data('600000', start='2019-06-05')
demo1 = ts.pro_bar('600000.SH', adj='qfq', start_date=start_time)
demo = demo1.sort_values('trade_date', ascending=True)
demo.index = demo1.index
demoT = demo['trade_date'].T
dateName = demoT.tolist()
# dateName.insert(0, "code")
conclude = pd.DataFrame(columns=dateName)
# print(conclude)

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
        # 读入日指数
        # df = ts.get_hist_data(code, start='2017-01-01')
        # 读入复权指数
        df1 = ts.pro_bar(code, adj='hfq', start_date='2017-01-01')
        # 如果数据为空
        if df1 is None:
            print("股票代码", end='')
            print(code, end='')
            print("的查询结果为空")
            continue
        # 数据量小于21
        if len(df1) < 21:
            print("股票代码", end='')
            print(code, end='')
            print("的记录数量小于21，不予计算 DB2")
            continue
        # 计算 DB1 和 DB2
        df = df1.sort_values('trade_date', ascending=True)
        df.index = df1.index
        try:
            df['MIN_21'], df['MAX_21'], df['DB1'] = calculateDB1(df.high, df.low, df.close, N, N2, [])
            df['DB2'] = calculateDB2(df['DB1'], N, N2, [])
        except:
            print("Error code is: ", code)
        # 将数据加入汇总表
        df.index = df['trade_date']
        newRow = df['DB2']
        newRow = newRow[start_time2:]
        newRow.name = code
        conclude = conclude.append(newRow)
        # print("代码", code, "已记录")

print(conclude)
saveFile = savePath + "/conclusion_weighted.csv"
conclude.to_csv(saveFile)
print("已将汇总表的结果保存在路径: ", saveFile)
