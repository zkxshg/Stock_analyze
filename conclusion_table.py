import pandas as pd
import xlrd
import tushare as ts
import numpy as np
import os
import talib

token = ""
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


# ========== Initialize ==========
# 输入文件路径
path = "沪深A股.xls"

# 输入要读取的工作表 / sheet 数，默认读取第一张
# sheets = [5]
sheets = [0, 1, 2, 3, 4]

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

# ========== 创建汇总表模板 ==========
# 1 日前复权数据 DB2
demo1 = ts.pro_bar('600000.SH', adj='qfq', start_date=start_time2)
demo = demo1.sort_values('trade_date', ascending=True)  # sort
demo.index = demo1.index

demoT = demo['trade_date'].T  # get column names
demoT = demoT[-5:]  # slice
dateName = demoT.tolist()  # df -> list
dateName = ['DB2_day_' + i for i in dateName]  # add index label

# 2 周前复权数据 DB2
demo_week1 = ts.pro_bar('600000.SH', freq='W', adj='qfq', start_date=start_time2)
demo_week = demo_week1.sort_values('trade_date', ascending=True)
demo_week.index = demo_week1.index

demo_weekT = demo_week['trade_date'].T
demo_weekT = demo_weekT[-5:]
weekName = demo_weekT.tolist()
weekName = ['DB2_week_' + i for i in weekName]

# 3 MACD_hist
macdName = demoT.tolist()  # df -> list
macdName = ['MACD_' + i for i in macdName]  # add index label

# 4 RSI
RSIName = demoT.tolist()  # df -> list
RSIName = ['RSI_' + i for i in RSIName]  # add index label

# 5 CCI
CCIName = demoT.tolist()  # df -> list
CCIName = ['CCI_' + i for i in CCIName]  # add index label

# 6 KDJ
KtName = demoT.tolist()  # df -> list
KtName = ['Kt_' + i for i in KtName]  # add index label
DtName = demoT.tolist()  # df -> list
DtName = ['Dt_' + i for i in DtName]  # add index label
JtName = demoT.tolist()  # df -> list
JtName = ['Jt_' + i for i in JtName]  # add index label

# 7 企业基本数据
empl = ts.get_stock_basics()
emplName = empl.columns.tolist()
# demo_empl = empl.loc['600000']

colsName = dateName + weekName + macdName + RSIName + CCIName + KtName + DtName + JtName + emplName
conclude = pd.DataFrame(columns=colsName)
print(conclude)

# ========== 续写汇总表文件 ==========
# 检测汇总表文件是否存在
saveFile = savePath + "/conclusion_weighted.csv"
if os.path.exists(saveFile):
    print("文件", saveFile, "已存在，开始续写。")
else:
    conclude.to_csv(saveFile, encoding="utf_8_sig", float_format='%.2f')

# 记录已汇总股票指数
conc = pd.read_csv(saveFile)
tlist = np.array(conc.iloc[:, 0].values).tolist()
# print(tlist)

for sheet in sheets:
    # ========== 读入工作表 ==========
    # 0-1 读入单张工作表
    print("正在读取第", sheet, "张工作表")
    try:
        sheet_i = pd.read_excel(path, sheet_name=sheet)
    except:
        print("无法找到工作表: ", sheet, "，已跳过")
        continue

    # 0-2 读入股票代码列
    stockCode = sheet_i["代码"]

    # ========== 0-3 根据股票代码读取日指数后计算指标并保存 ==========
    for SC in stockCode:
        code = str(SC)

        # 1 补零到六位代码
        while len(code) < 6:
            code = "0" + code

        # 2 读入企业信息
        try:
            df_basics = empl.loc[code]
        except:
            print("无法找到企业代码: ", code, " 的信息")
            continue

        # 3 补全复权代码
        if code[0] == '6':
            code = code + '.SH'
        else:
            code = code + '.SZ'

        # 3-2 跳过已汇总代码
        if code in tlist:
            print("代码", code, "已在表中，跳过读取。")
            continue

        # 4 读入日复权指数
        df1 = ts.pro_bar(code, adj='qfq', start_date='2017-01-01')
        
        # ========== 处理 outlier ==========
        # 4-1 如果数据为空
        if df1 is None:
            print("股票代码", end='')
            print(code, end='')
            print("的查询结果为空")
            continue

        # 4-2 数据量小于21
        if len(df1) < 21:
            print("股票代码", end='')
            print(code, end='')
            print("的记录数量小于21，不予计算 DB2")
            continue
        
        # ========== 计算技术指数 ==========
        
        # 5-1 计算 DB1 和 DB2
        df = df1.sort_values('trade_date', ascending=True)
        df.index = df1.index
        try:
            df['MIN_21'], df['MAX_21'], df['DB1'] = calculateDB1(df.high, df.low, df.close, N, N2, [])
            df['DB2'] = calculateDB2(df['DB1'], N, N2, [])
        except:
            print("Error code is: ", code)
            continue

        # 5-2 计算 MACD
        try:
         df["MACD_DIFF"], df["MACD_DEA"], df["MACD_macdhist"] = \
             talib.MACD(df.close, fastperiod=12, slowperiod=26,signalperiod=9)
        except:
            print("MACD Error code is: ", code)
            continue

        # 5-3 计算 RSI
        try:
            df['RSI'] = talib.RSI(df.open, timeperiod=12)
        except:
            print("RSI Error code is: ", code)
            continue

        # 5-4 计算 CCI
        try:
            df["CCI"] = talib.CCI(df.high, df.low, df.close, timeperiod=14)
        except:
            print("CCI Error code is: ", code)
            continue

        # 5-5 计算 KDJ
        try:
            df['Kt'], df['Dt'] = talib.STOCH(df.high, df.low, df.close, fastk_period=9,
                                             slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
            df['Jt'] = list(map(lambda x, y: 3 * x - 2 * y, df['Kt'], df['Dt']))
        except:
            print("KDJ Error code is: ", code)
            continue

        # ========== 5-6 取出五天内数据作为 series 并修改 index ==========
        df.index = df['trade_date']

        newRow = df['DB2'][-5:]
        newRow.index = df['trade_date'][-5:].map(lambda x: "DB2_day_" + str(x)).tolist()

        MACD_Row = df["MACD_macdhist"][-5:]
        MACD_Row.index = df['trade_date'][-5:].map(lambda x: "MACD_" + str(x)).tolist()

        RSI_Row = df['RSI'][-5:]
        RSI_Row.index = df['trade_date'][-5:].map(lambda x: "RSI_" + str(x)).tolist()

        CCI_Row = df['CCI'][-5:]
        CCI_Row.index = df['trade_date'][-5:].map(lambda x: "CCI_" + str(x)).tolist()

        Kt_Row = df['Kt'][-5:]
        Kt_Row.index = df['trade_date'][-5:].map(lambda x: "Kt_" + str(x)).tolist()

        Dt_Row = df['Dt'][-5:]
        Dt_Row.index = df['trade_date'][-5:].map(lambda x: "Dt_" + str(x)).tolist()

        Jt_Row = df['Jt'][-5:]
        Jt_Row.index = df['trade_date'][-5:].map(lambda x: "Jt_" + str(x)).tolist()

        # ========== 6 读入周复权指数 ==========
        df_week = pro.weekly(ts_code=code, start_date=start_time2)

        # 6-1 如果数据为空
        if df_week is None:
            print("股票代码", end='')
            print(code, end='')
            print("的周数据查询结果为空")
            continue

        # 6-2 数据量小于21
        if len(df_week) < 21:
            print("股票代码", end='')
            print(code, end='')
            print("的周数据记录数量小于21，不予计算 DB2")
            continue

        # 6-3 计算 DB1 和 DB2
        df_week['MIN_21'], df_week['MAX_21'], df_week['DB1'] = \
            calculateDB1(df_week.high, df_week.low, df_week.close, N, N2, [])
        df_week['DB2'] = calculateDB2(df_week['DB1'], N, N2, [])

        # 6-4 取出 DB2 作为 series 并取出五天内数据
        newRow_week = df_week[-5:]['DB2']
        newRow_week.index = weekName

        # ========== 7 将数据加入汇总表 ==========
        # 7-1 合并各指数
        allRows = pd.concat([newRow, newRow_week, MACD_Row, RSI_Row,
                             CCI_Row,  Kt_Row, Dt_Row,  Jt_Row, df_basics])
        allRows.name = code

        # 7-2 与汇总表 index 对接
        newRows = conclude.append(allRows)

        # 7-3 写入 csv 文件
        newRows.to_csv(saveFile, mode='a', header=False, encoding="utf_8_sig", float_format='%.2f')
        print("代码", code, "已记录")

# conclude.to_csv(saveFile, encoding="utf_8_sig", float_format='%.2f')
print("已将汇总表的结果保存在路径: ", saveFile)
