from Bot3Swing import *
from BotConfig import *
from pykiwoom.kiwoom import *
import time
import pickle

B3 = Bot3Swing()
save_file(FILE_URL_QUANT_LAST_3M, B3.bkk.filter_code_list())

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