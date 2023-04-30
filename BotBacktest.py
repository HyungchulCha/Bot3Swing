from Bot_3m import *
from BotConfig import *
import pandas as pd
import numpy as np
import os

kosdaq = []
B3 = Bot_3m()

dir = os.getcwd()
flist = os.listdir(dir + '/_back_3m')
xlsx_list = np.array([x for x in flist if x.endswith('.xlsx')])

ttl_code_array = []
ttl_buy_array = []
ttl_sel_array = []
ttl_sucs_per_array = []
ttl_fail_per_array = []
ttl_prft_array = []

for x in np.nditer(xlsx_list):
    code = str(x).split('.')[0]

    if not (code in kosdaq):
        code_df = pd.read_excel(dir + '/_back_3m/' + str(x))
        code_df = code_df[::-1]

        temp_df = pd.DataFrame({'close': code_df['현재가'].abs().to_list()}).dropna()
        ma5 = temp_df.rolling(5).mean()
        ma20 = temp_df.rolling(20).mean()
        ma60 = temp_df.rolling(60).mean()
        df_l = len(temp_df.columns.to_list())
        temp_df.insert(df_l, 'ma5', ma5)
        temp_df.insert(df_l + 1, 'ma20', ma20)
        temp_df.insert(df_l + 2, 'ma60', ma60)
        temp_df['ma5p'] = temp_df['ma5'].shift()
        temp_df['ma20p'] = temp_df['ma20'].shift()
        temp_df['ma60p'] = temp_df['ma60'].shift()

        # print(f'{code} ========================================================================')
        # print(temp_df)

        buy_p = 0
        buy_c = 0
        sucs_c = 0
        fail_c = 0
        item_buy_c = 0
        item_sel_c = 0
        _ror = 1

        has_buy = False

        for i, row in temp_df.iterrows():
            
            # buy 1
            # if \
            # (row['ma5'] >= row['ma20']) and \
            # (row['ma5p'] < row['ma20p']) and \
            # has_buy == False\
            # :
            # buy 3
            if \
            (row['ma5'] >= row['ma5p']) and \
            has_buy == False\
            :
            # buy 2
            # if \
            # (row['ma5'] > row['ma5p']) and \
            # (row['ma5'] >= row['ma20']) and \
            # (row['ma5'] < row['ma60']) and \
            # (row['ma20'] > row['ma60']) and \
            # has_buy == False\
            # :
                buy_p = buy_p + row['close']
                has_buy = True
                buy_c += 1
                item_buy_c += 1

            # cut 1
            if \
            has_buy == True\
            :
                if buy_p * 0.96 > row['close']:
                    sel_close = row['close']
                    has_buy = False
                    _ror = B3.ror(buy_p, sel_close, _ror)
                    if sel_close - buy_p > 0:
                        sucs_c += 1
                    else:
                        fail_c += 1
                    item_sel_c += 1
                    buy_p = 0
                    buy_c = 0

            # self 1
            # if \
            # (row['ma5'] < row['ma5p']) and \
            # (row['ma5'] <= row['ma20']) and \
            # (row['ma5'] > row['ma60']) and \
            # (row['ma20'] > row['ma60']) and \
            # has_buy == True\
            # :
            # self 2
            if \
            (row['ma5'] < row['ma5p']) and \
            (row['ma5'] <= row['ma20']) and \
            (row['ma5'] > row['ma60']) and \
            (row['ma20'] > row['ma60']) and \
            has_buy == True\
            :
                sel_close = row['close']
                has_buy = False
                _ror = B3.ror(buy_p, sel_close, _ror)
                if sel_close - buy_p > 0:
                    sucs_c += 1
                else:
                    fail_c += 1
                item_sel_c += 1
                buy_p = 0
                buy_c = 0

        if sucs_c != 0:
            sucs_per = round(((sucs_c * 100) / (sucs_c + fail_c)), 2)
            fail_per = round((100 - sucs_per), 2)
            prft_per = round(((_ror - 1) * 100), 2)
        else:
            sucs_per = 0
            if item_buy_c > 0:
                fail_per = round((100 - sucs_per), 2)
                prft_per = round(((_ror - 1) * 100), 2)
            else:
                fail_per = 0
                prft_per = 0

        ttl_code_array.append(code)
        ttl_buy_array.append(item_buy_c)
        ttl_sel_array.append(item_sel_c)
        ttl_sucs_per_array.append(sucs_per)
        ttl_fail_per_array.append(fail_per)
        ttl_prft_array.append(prft_per)

        print('종목:{}, 매수: {}회, 매도: {}회, 성공률 : {}%, 실패율 : {}%, 누적수익률 : {}%'.format(code, item_buy_c, item_sel_c, sucs_per, fail_per, prft_per))

prft_df = pd.DataFrame({'code': ttl_code_array, 'buy': ttl_buy_array, 'sell': ttl_sel_array, 'success': ttl_sucs_per_array, 'fail': ttl_fail_per_array, 'profit': ttl_prft_array})
prft_df = prft_df.sort_values('profit', ascending=False)
prft_df.to_excel(dir + '/_back_result/Bot3mBacktest' + datetime.datetime.now().strftime('%m%d%H%M%S') + '.xlsx')