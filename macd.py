#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# 加载pandas包和os包
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
import numpy as np


# 计算EMA(周期, 收盘价序列, 返回序列)：指数平均移动量
def calculateEMA(period, closeArray, emaArray=[]):
    length = len(closeArray)
    if not emaArray:
        # 首日EMA記為當日收盤價
        emaArray.append(closeArray[0])
        for i in range(1, length):
            ema = (2 * closeArray[i] + (period - 1) * emaArray[-1]) / (period + 1)
            emaArray.append(ema)
    return np.array(emaArray)


# 计算MACD(收盘价序列, 短周期, 长周期, 目标周期)
def calculateMACD(closeArray, ema12, ema26, signalPeriod=9):
    # =========計算離散值diff, diff[0]=0 ============================
    diff = ema12 - ema26
    # =========計算離差平均值DEA，默認為9日, dea[0]=0 ============
    dea = calculateEMA(signalPeriod, diff, [])
    # =========計算MACD柱線====================================
    macd = 2*(diff - dea)
    fast_values = diff
    slow_values = dea
    diff_values = macd
    # 以下可繪出指定時間內MACD折線圖，暫定週期為50天，紅色為diff，綠色為dea，藍色為MACD柱
    period = 50
    x_d = np.linspace(0, period, period)
    diff_p = diff[(len(diff)-period): len(diff)]
    dea_p = dea[(len(dea) - period): len(dea)]
    macd_p = macd[(len(macd) - period): len(macd)]
    yz = np.zeros(period, dtype=np.int)
    plt.plot(x_d, diff_p, 'r--')
    plt.plot(x_d, dea_p, 'g*-')
    plt.plot(x_d, macd_p, 'b-')
    plt.plot(x_d, yz, 'black')
    plt.savefig("MACD.png")
    return fast_values, slow_values, diff_values


# ===============修改ma，计算5日、20日和60日移动平均线MA =============
stock_data2 = pd.read_csv('000001.csv')
stock_data2.columns = ['date','gpdm','mc','spj','zgj','zdj','kpj','qsp','zde','zdf','cjl']
stock_data2['date'] = pd.to_datetime(stock_data2['date'])  # 轉換日期格式
stock_data2 = stock_data2.set_index('date')  # 選定index
stock_data2.head()
ma=20
stock_data2['ma_'+str(ma)]=stock_data2['spj'].rolling(ma).mean()
# stock_data2.to_csv('000001_ma.csv',index=False)  # 單獨保存ma
# ==========================計算EMA================
# 設定短週期和長週期；默認為12和26
short_period = 12
long_period = 26
# 計算短週期和長週期EMA
stock_data2['EMA_short'] = calculateEMA(short_period, stock_data2['cjl'], [])
stock_data2['EMA_long'] = calculateEMA(long_period, stock_data2['cjl'], [])
# stock_data2.to_csv('000001_EMA.csv',index=False)  # 單獨保存EMA

fast, slow, diff = calculateMACD(stock_data2['cjl'], stock_data2['EMA_short'], stock_data2['EMA_long'])
stock_data2['Diff'] = fast
stock_data2['DEA'] = slow
stock_data2['MACD'] = diff
stock_data2.to_csv('000001_MACD.csv',index=True)
