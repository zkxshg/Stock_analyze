#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pysnowball as ball

ball.set_token('xq_a_token=*')


# In[2]:


import pandas as pd
import xlrd
import numpy as np
import os
import talib
import time


# In[25]:


def crawRealStock():
    # ============= 取出样例数据 =============
    demo = ball.quotec('SZ002027')
    demoHead = ['公司名称']
    demoHead.extend(list(demo['data'][0].keys()))
    
    # ============= 获得表头 =============
    conclude = pd.DataFrame(columns=demoHead)
    concLen = len(conclude.columns.tolist())
    
    # ============================== 开始爬取数据 ==============================
    finish = False
    
    while not finish:
        # ============= 处理工作表 =============
        # 0-1 读入代码集
        print("正在读取：",path)
        try:
            sheet_i = pd.read_csv(path)
        except:
            print("无法找到工作表: ", path, "，已跳过")
            continue

        # 0-2读入股票代码列
        stockCode = sheet_i["code"]
        
        # ============= 0 根据股票代码读取日指数并保存 =============
        for SC in stockCode:
            code = str(SC)

            # ============= 1 补零到六位代码 =============
            while len(code) < 6:
                code = "0" + code

            # 2 补全复权代码
            if code[0] == '6':
                code = 'SH' + code
            else:
                code = 'SZ' + code
                
            # ============= 2 记录当前时间 =============
            df1 = ball.quotec(code)
            time_mills = df1['data'][0]['timestamp'] / 1000
            time_mills =  time.localtime(time_mills)
            currTime = time.strftime("%Y%m%d%H%M", time_mills) 

            # ============= 3 文件存放路径 =============
            saveFile = savePath + "/conclusion_realTime_" + code + ".csv"

            # 检查是否续写
            if os.path.exists(saveFile):
                print("文件", saveFile, "已存在，开始续写。")
            else:
                conclude.to_csv(saveFile, encoding="utf_8_sig", float_format='%.2f')

            # ============= 4 查看当前时间是否记录 =============
            conc = pd.read_csv(saveFile, encoding="utf_8_sig", error_bad_lines=False, engine='python')
            tlist = np.array(conc.iloc[:, 6].values).tolist()  # 已记录时间
        
            # 跳过已汇总代码
            if int(currTime) in tlist:
                print("时间", currTime, "已在表中，跳过读取。")
                continue
                
            # ============= 5 读入企业信息 =============
            # 取出公司名称
            if (len(tlist) >= 1):
                compName = np.array(conc.iloc[:, 1].values).tolist()[0]
            else:
                try:
                    compName = ball.cash_flow(code)['data']['quote_name']
                    # print(compName)
                except:
                    print("无法找到企业代码: ", code, " 的信息")
                    continue
            
            # ============= 6 读入实时指数 =============
            df1 = ball.quotec(code)
            # print(df1)
            if df1 is None:
                print("股票代码", end='')
                print(code, end='')
                print("的查询结果为空")
                continue
            
            # 更新时间格式
            df1['data'][0]['timestamp'] = currTime
            
            # ============= 7 将数据加入汇总表 =============
            # 7-1 合并各指数
            allRows = [compName]
            allRows.extend(list(df1['data'][0].values()))
            
            allRows = pd.DataFrame([allRows])
            allRows.columns = demoHead
            
            # 7-2 与汇总表 index 对接
            newRows = conclude.append(allRows)
            
            if concLen != newRows.shape[1]:
                print("股票代码", code, "读取失误，跳过输出，请重新计算")
                continue
            
            # 7-3 写入 csv 文件
            newRows.to_csv(saveFile, mode='a', header=False, encoding="utf_8_sig", float_format='%.2f')
            print("代码", code, "已记录")
            
            print("已将代码的结果保存在路径: ", saveFile)
            
        print("已将汇总表的结果保存在路径: ", savePath)
        break
    
    return savePath
    


# In[ ]:


# ============================== Initialize ==============================
# 输入文件路径
path = "a股.csv"

# 输入要读取的工作表 / sheet 数，默认读取第一张
sheets = [5]

# 输入储存文件路径
savePath = "./data/realTime_Single"

# 设置计算 ADX、PDI 和 MDI 的周期，默认为14
period = 14

# 设置计算 SMA 的周期 N
N = 13
N2 = 8
weight = 1

# 设置起始时间，两个要保持一致
start_time = '2021-06-05'
start_time2 = '20210605'

# 开始输出实时数据
head = crawRealStock()


# In[ ]:




