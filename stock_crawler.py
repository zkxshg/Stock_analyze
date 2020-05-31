import pandas as pd
import xlrd
import tushare as ts

# 输入文件路径
path = "沪深A股.xls"
# 输入要读取的工作表 / sheet 数，默认读取第一张
# sheets = [3]
sheets = [0, 1, 2, 3]
# 输入储存文件路径
savePath = "./data"

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
        # 读入日指数
        df = ts.get_hist_data(code, start='2017-01-01', end='2020-05-29')
        # 如果数据为空
        if df is None:
            print("股票代码", end='')
            print(code, end='')
            print("的查询结果为空")
            continue
        # 保存为 csv 文件
        saveFile = savePath + "/" + code + ".csv"
        df.to_csv(saveFile)
        print("已将股票代码", end='')
        print(code, end='')
        print("的结果保存在路径", end='')
        print(saveFile)


# df = ts.get_hist_data('000002', start='2017-01-01', end='2020-05-29')  # 一次性获取全部日k线数据
# print(df)
# df.to_csv('data.csv')


# 歷史行情
# df = ts.get_hist_data('600848')  # 一次性获取全部日k线数据
'''
ts.get_hist_data('600848', ktype='W') #获取周k线数据
ts.get_hist_data('600848', ktype='M') #获取月k线数据
ts.get_hist_data('600848', ktype='5') #获取5分钟k线数据
ts.get_hist_data('600848', ktype='15') #获取15分钟k线数据
ts.get_hist_data('600848', ktype='30') #获取30分钟k线数据
ts.get_hist_data('600848', ktype='60') #获取60分钟k线数据
ts.get_hist_data('sh'）#获取上证指数k线数据，其它参数与个股一致，下同
ts.get_hist_data('sz'）#获取深圳成指k线数据
ts.get_hist_data('hs300'）#获取沪深300指数k线数据
ts.get_hist_data('sz50'）#获取上证50指数k线数据
ts.get_hist_data('zxb'）#获取中小板指数k线数据
ts.get_hist_data('cyb'）#获取创业板指数k线数据
'''

# 復權數據
# 獲取個股上市日期
# df2 = ts.get_stock_basics()
# date = df2.iloc['600848']['timeToMarket']  # 上市日期YYYYMMDD
# df3 = ts.get_h_data('002337')  # 前复权
'''
ts.get_h_data('002337', autype='hfq')  # 后复权
ts.get_h_data('002337', autype=None)  # 不复权
ts.get_h_data('002337', start='2015-01-01', end='2015-03-16')  # 两个日期之间的前复权数据
ts.get_h_data('399106', index=True)  # 深圳综合指数
'''

# 實時行情
# df4 = ts.get_today_all()
# 歷史分筆
# df5 = ts.get_tick_data('600848',date='2018-12-12',src='tt')
# df5.head(10)
# 當日分筆
# df6 = ts.get_today_ticks('601333')
# df6.head(10)
# 大盤指數
# df7 = ts.get_index()
# 大單交易
# df8 = ts.get_sina_dd('600848', date='2015-12-24') #默认400手
# df9 = ts.get_sina_dd('600848', date='2015-12-24', vol=500)  # 指定大于等于500手的数据
