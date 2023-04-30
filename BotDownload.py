from Bot_3m import *
from BotConfig import *
from pykiwoom.kiwoom import *
import pandas as pd
import numpy as np
import time
import pickle
import os

B3 = Bot_3m()
kp = B3.bkk.fetch_kospi_symbols()
kp = kp.loc[(kp['그룹코드'] == 'ST') 
        & (kp['시가총액규모'] != 0) 
        & (kp['시가총액'] != 0) 
        & (kp['우선주'] == 0) 
        & (kp['단기과열'] == 0) 
        & (kp['락구분'] == 0)
        & (kp['액면변경'] == 0) 
        & (kp['증자구분'] == 0)
        & (kp['ETP'] != 'Y') 
        & (kp['SRI'] != 'Y') 
        & (kp['ELW발행'] != 'Y') 
        & (kp['KRX은행'] != 'Y') 
        & (kp['KRX증권'] != 'Y')
        & (kp['KRX섹터_보험'] != 'Y')
        & (kp['SPAC'] != 'Y') 
        & (kp['거래정지'] != 'Y') 
        & (kp['정리매매'] != 'Y') 
        & (kp['관리종목'] != 'Y') 
        & (kp['시장경고'] != 'Y') 
        & (kp['경고예고'] != 'Y') 
        & (kp['불성실공시'] != 'Y') 
        & (kp['우회상장'] != 'Y') 
        & (kp['공매도과열'] != 'Y') 
        & (kp['이상급등'] != 'Y') 
        & (kp['회사신용한도초과'] != 'Y') 
        & (kp['담보대출가능'] != 'Y') 
        & (kp['대주가능'] != 'Y') 
        & (kp['신용가능'] == 'Y')
        & (kp['증거금비율'] != 100)
        & (kp['전일거래량'] > 300000) 
        ]
B3.save_file(FILE_URL_QUANT_LIST_3M, kp['단축코드'].to_list())

# 2 키움에서 5분봉 데이터 추출
# /_back_5m 폴더에 xlsx 파일 저장
kiwoom = Kiwoom()
kiwoom.CommConnect()

# 전종목 종목코드
# kospi = kiwoom.GetCodeListByMarket('0')
# kosdaq = kiwoom.GetCodeListByMarket('10')
# codes = kospi + kosdaq

_codes = None
with open(FILE_URL_QUANT_LIST_3M, 'rb') as f:
    _codes = pickle.load(f)
codes = _codes
        
for i, code in enumerate(codes):
    print(f"{i + 1}/{len(codes)} {code}")
    df = kiwoom.block_request("opt10080", 종목코드=code, 틱범위=3, 수정주가구분=1, output="주식분봉차트조회", next=0)
    df.drop(df[(df['체결시간'].str.contains('153300'))].index, inplace=True)
    df.to_excel(f"C:\\Bot3Swing\\_back_3m\\{code}.xlsx")
    time.sleep(0.25)
for i, code in enumerate(codes):
    print(f"{i + 1}/{len(codes)} {code}")
    df = kiwoom.block_request("opt10080", 종목코드=code, 틱범위=5, 수정주가구분=1, output="주식분봉차트조회", next=0)
    df.drop(df[(df['체결시간'].str.contains('153300'))].index, inplace=True)
    df.to_excel(f"C:\\Bot3Swing\\_back_5m\\{code}.xlsx")
    time.sleep(0.25)
for i, code in enumerate(codes):
    print(f"{i + 1}/{len(codes)} {code}")
    df = kiwoom.block_request("opt10080", 종목코드=code, 틱범위=10, 수정주가구분=1, output="주식분봉차트조회", next=0)
    df.drop(df[(df['체결시간'].str.contains('153300'))].index, inplace=True)
    df.to_excel(f"C:\\Bot3Swing\\_back_10m\\{code}.xlsx")
    time.sleep(0.25)
for i, code in enumerate(codes):
    print(f"{i + 1}/{len(codes)} {code}")
    df = kiwoom.block_request("opt10080", 종목코드=code, 틱범위=15, 수정주가구분=1, output="주식분봉차트조회", next=0)
    df.drop(df[(df['체결시간'].str.contains('153300'))].index, inplace=True)
    df.to_excel(f"C:\\Bot3Swing\\_back_15m\\{code}.xlsx")
    time.sleep(0.25)