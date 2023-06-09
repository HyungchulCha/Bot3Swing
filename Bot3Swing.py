from BotConfig import *
from BotUtil import *
from BotKIKr import BotKIKr
from dateutil.relativedelta import *
import pandas as pd
import datetime
import threading
import os
import copy

class Bot3Swing():


    def __init__(self):

        self.mock = False
        self.key = KI_APPKEY_IMITATION if self.mock else KI_APPKEY_PRACTICE
        self.secret = KI_APPSECRET_IMITATION if self.mock else KI_APPSECRET_PRACTICE
        self.account = KI_ACCOUNT_IMITATION if self.mock else KI_ACCOUNT_PRACTICE

        self.bkk = BotKIKr(self.key, self.secret, self.account, self.mock)
        self.bdf = None
        self.b_l = None
        self.q_l = None
        self.r_l = None

        self.tot_evl_price = 0
        self.buy_max_price = 0

        self.bool_marketday = False
        self.bool_stockorder = False
        self.bool_stockorder_timer = False
        self.bool_marketday_end = False
        self.bool_threshold = False
        self.bool_market = False

        self.init_marketday = self.bkk.fetch_marketday()
        self.init_stockorder_timer = None


    def init_per_day(self):

        self.bkk = BotKIKr(self.key, self.secret, self.account, self.mock)
        self.init_marketday = self.bkk.fetch_marketday()

        if self.bool_market == False and self.init_marketday == 'Y':

            self.init_to_excel()

            self.bdf = load_xlsx(FILE_URL_DATA_3M).set_index('date')
            self.b_l = self.bdf.columns.to_list()
            self.q_l = self.get_guant_code_list()
            self.r_l = list(set(self.get_balance_code_list()).difference(self.q_l))

            _ttl_prc = int(self.bkk.fetch_balance()['output2'][0]['tot_evlu_amt'])
            # _buy_cnt = len(self.q_l) if len(self.q_l) > 45 else 45
            _buy_cnt = 100
            
            self.tot_evl_price = _ttl_prc if _ttl_prc < 40000000 else 40000000
            self.buy_max_price = self.tot_evl_price / _buy_cnt

            line_message(f'Bot3Swing \n평가금액 : {self.tot_evl_price}원, 다른종목: {len(self.r_l)}개')
    

    def stock_order(self):

        tn = datetime.datetime.now()
        tn_0900 = tn.replace(hour=9, minute=0)
        tn_153000 = tn.replace(hour=15, minute=30, second=0)
        tn_div = tn.minute % 3
        tn_del = None

        if tn_div == 0:
            tn_del = 1
        elif tn_div == 1:
            tn_del = 2
        elif tn_div == 2:
            tn_del = 3

        tn_del_min = tn - datetime.timedelta(minutes=tn_del)
        tn_df_idx = tn_del_min.strftime('%Y%m%d%H%M00') if tn < tn_153000 else tn.strftime('%Y%m%d153000')
        tn_df_req = tn_del_min.strftime('%H%M00') if tn < tn_153000 else '153000'

        print('##################################################')

        if self.bool_threshold and tn_div == 2:
            self.bdf = self.bdf[:-1]
        self.bool_threshold = False

        bal_lst = self.get_balance_code_list(True)
        sel_lst = []

        if os.path.isfile(FILE_URL_BLNC_3M):
            obj_lst = load_file(FILE_URL_BLNC_3M)
        else:
            obj_lst = {}
            save_file(FILE_URL_BLNC_3M, obj_lst)

        for code in self.b_l:

            if tn != tn_0900:
                min_lst = self.bkk.fetch_today_1m_ohlcv(code, tn_df_req, True)['output2'][:3]
                chk_cls = float(min_lst[0]['stck_prpr'])
                chk_opn = float(min_lst[2]['stck_oprc'])
                chk_hig = max([float(min_lst[i]['stck_hgpr']) for i in range(3)])
                chk_low = min([float(min_lst[i]['stck_lwpr']) for i in range(3)])
                chk_vol = sum([float(min_lst[i]['cntg_vol']) for i in range(3)])
                self.bdf.at[tn_df_idx, code] = str(chk_opn) + '|' + str(chk_hig) + '|' + str(chk_low) + '|' + str(chk_cls) + '|' + str(chk_vol)
            
            else:
                chk_cls = float(self.bdf[code].iloc[-1].split('|')[3])

            is_late = tn_div == 2

            if (not is_late):

                is_remain = code in self.r_l
                is_alread = code in bal_lst
                is_notnul = not (not obj_lst)

                if is_alread and not (code in obj_lst):
                    obj_lst[code] = {'x': copy.deepcopy(bal_lst[code]['a']), 'a': copy.deepcopy(bal_lst[code]['a']), 's': 1, 'd': datetime.datetime.now().strftime('%Y%m%d')}

                if not is_alread and (code in obj_lst):
                    obj_lst.pop(code, None)

                if is_alread and (code in obj_lst) and (not ('d' in obj_lst[code])):
                    obj_lst[code]['d'] = datetime.datetime.now().strftime('%Y%m%d')
                
                if (not is_alread) and (not is_remain):
                    
                    df = gen_neck_df(gen_code_df(self.bdf, code))
                    df_t = df.tail(1)

                    cls_v = df_t['close'].iloc[-1]
                    clp_v = df_t['close_prev'].iloc[-1]
                    m05_v = df_t['ma05'].iloc[-1]
                    m20_v = df_t['ma20'].iloc[-1]
                    m60_v = df_t['ma60'].iloc[-1]
                    hgt_v = df_t['height_5_20'].iloc[-1]

                    if \
                    (1.1 < hgt_v < 15) and \
                    (m60_v < m20_v < m05_v < cls_v < clp_v * 1.05) and \
                    (m20_v < cls_v < m20_v * 1.05) \
                    :
                        # if chk_cls < self.buy_max_price:

                        ord_q = get_qty(chk_cls, self.buy_max_price)
                        buy_r = self.bkk.create_market_buy_order(code, ord_q) if tn < tn_153000 else self.bkk.create_over_buy_order(code, ord_q)

                        if buy_r['rt_cd'] == '0':
                            print(f'매수 - 종목: {code}, 수량: {ord_q}주')
                            obj_lst[code] = {'a': chk_cls, 'x': chk_cls, 's': 1, 'd': datetime.datetime.now().strftime('%Y%m%d')}
                            sel_lst.append({'c': '[B] ' + code, 'r': str(ord_q) + '주'})
                        else:
                            msg = buy_r['msg1']
                            print(f'{msg}')
                

                if is_alread and is_notnul:

                    obj_d = copy.deepcopy(obj_lst[code]['d'])
                    obj_s = copy.deepcopy(obj_lst[code]['s'])
                    now_d = datetime.datetime.now().strftime('%Y%m%d')
                    dif_d = datetime.datetime(int(now_d[:4]), int(now_d[4:6]), int(now_d[6:])) - datetime.datetime(int(obj_d[:4]), int(obj_d[4:6]), int(obj_d[6:]))

                    if (dif_d.days) >= 10 and obj_s == 1:

                        bal_fst = bal_lst[code]['a']
                        bal_qty = bal_lst[code]['q']

                        sel_r = self.bkk.create_market_sell_order(code, bal_qty) if tn < tn_153000 else self.bkk.create_over_sell_order(code, bal_qty)
                        _ror = ror(bal_fst * bal_qty, chk_cls * bal_qty)

                        if sel_r['rt_cd'] == '0':
                            print(f'매도 - 종목: {code}, 수익: {round(_ror, 4)}')
                            sel_lst.append({'c': '[SL] ' + code, 'r': round(_ror, 4)})
                            obj_lst.pop(code, None)
                        else:
                            msg = sel_r['msg1']
                            print(f'{msg}')

                    else:

                        t1 = 0.035
                        t2 = 0.045
                        t3 = 0.055
                        ct = 0.8
                        hp = 100

                        if obj_lst[code]['x'] < chk_cls:
                            obj_lst[code]['x'] = chk_cls

                        if obj_lst[code]['x'] > chk_cls:

                            bal_fst = copy.deepcopy(bal_lst[code]['a'])
                            bal_qty = copy.deepcopy(bal_lst[code]['q'])
                            obj_max = copy.deepcopy(obj_lst[code]['x'])
                            sel_cnt = copy.deepcopy(obj_lst[code]['s'])
                            rto_01 = 0.2
                            rto_02 = (3/8)
                            ord_qty_01 = int(bal_qty * rto_01) if int(bal_qty * rto_01) != 0 else 1
                            ord_qty_02 = int(bal_qty * rto_02) if int(bal_qty * rto_02) != 0 else 1
                            is_qty_01 = bal_qty == ord_qty_01
                            is_qty_02 = bal_qty == ord_qty_02
                            obj_pft = ror(bal_fst, obj_max)
                            bal_pft = ror(bal_fst, chk_cls)
                            los_dif = obj_pft - bal_pft

                            if 1 < bal_pft < hp:

                                if (sel_cnt == 1) and (t1 <= los_dif):

                                    sel_r = self.bkk.create_market_sell_order(code, ord_qty_01) if tn < tn_153000 else self.bkk.create_over_sell_order(code, ord_qty_01)
                                    _ror = ror(bal_fst * ord_qty_01, chk_cls * ord_qty_01)

                                    if sel_r['rt_cd'] == '0':
                                        print(f'매도 - 종목: {code}, 수익: {round(_ror, 4)}')
                                        sel_lst.append({'c': '[S1] ' + code, 'r': round(_ror, 4)})
                                        obj_lst[code]['s'] = sel_cnt + 1
                                        obj_lst[code]['d'] = datetime.datetime.now().strftime('%Y%m%d')

                                        if is_qty_01:
                                            obj_lst.pop(code, None)
                                    else:
                                        msg = sel_r['msg1']
                                        print(f'{msg}')

                                elif (sel_cnt == 2) and (t2 <= los_dif):

                                    sel_r = self.bkk.create_market_sell_order(code, ord_qty_02) if tn < tn_153000 else self.bkk.create_over_sell_order(code, ord_qty_02)
                                    _ror = ror(bal_fst * ord_qty_02, chk_cls * ord_qty_02)

                                    if sel_r['rt_cd'] == '0':
                                        print(f'매도 - 종목: {code}, 수익: {round(_ror, 4)}')
                                        sel_lst.append({'c': '[S2] ' + code, 'r': round(_ror, 4)})
                                        obj_lst[code]['s'] = sel_cnt + 1
                                        obj_lst[code]['d'] = datetime.datetime.now().strftime('%Y%m%d')

                                        if is_qty_02:
                                            obj_lst.pop(code, None)
                                    else:
                                        msg = sel_r['msg1']
                                        print(f'{msg}')

                                elif (sel_cnt == 3) and (t3 <= los_dif):
                                        
                                    sel_r = self.bkk.create_market_sell_order(code, bal_qty) if tn < tn_153000 else self.bkk.create_over_sell_order(code, bal_qty)
                                    _ror = ror(bal_fst * bal_qty, chk_cls * bal_qty)

                                    if sel_r['rt_cd'] == '0':
                                        print(f'매도 - 종목: {code}, 수익: {round(_ror, 4)}')
                                        sel_lst.append({'c': '[S3] ' + code, 'r': round(_ror, 4)})
                                        obj_lst[code]['s'] = sel_cnt + 1
                                        obj_lst[code]['d'] = datetime.datetime.now().strftime('%Y%m%d')
                                        obj_lst.pop(code, None)
                                    else:
                                        msg = sel_r['msg1']
                                        print(f'{msg}')

                            elif hp <= bal_pft:

                                sel_r = self.bkk.create_market_sell_order(code, bal_qty) if tn < tn_153000 else self.bkk.create_over_sell_order(code, bal_qty)
                                _ror = ror(bal_fst * bal_qty, chk_cls * bal_qty)

                                if sel_r['rt_cd'] == '0':
                                    print(f'매도 - 종목: {code}, 수익: {round(_ror, 4)}')
                                    sel_lst.append({'c': '[S+] ' + code, 'r': round(_ror, 4)})
                                    obj_lst.pop(code, None)
                                else:
                                    msg = sel_r['msg1']
                                    print(f'{msg}')

                            elif bal_pft <= ct:

                                sel_r = self.bkk.create_market_sell_order(code, bal_qty) if tn < tn_153000 else self.bkk.create_over_sell_order(code, bal_qty)
                                _ror = ror(bal_fst * bal_qty, chk_cls * bal_qty)

                                if sel_r['rt_cd'] == '0':
                                    print(f'매도 - 종목: {code}, 수익: {round(_ror, 4)}')
                                    sel_lst.append({'c': '[S-] ' + code, 'r': round(_ror, 4)})
                                    obj_lst.pop(code, None)
                                else:
                                    msg = sel_r['msg1']
                                    print(f'{msg}')

        save_file(FILE_URL_BLNC_3M, obj_lst)

        sel_txt = ''
        for sl in sel_lst:
            sel_txt = sel_txt + '\n' + str(sl['c']) + ' : ' + str(sl['r'])
        
        _tn = datetime.datetime.now()
        _tn_152100 = _tn.replace(hour=15, minute=21, second=0)
        _tn_div = _tn.minute % 3
        _tn_sec = _tn.second
        _tn_del = None

        if _tn_div == 0:
            if tn_div == 2: 
                _tn_del = 0
                _tn_sec = 0
            else:
                _tn_del = 3
        elif _tn_div == 1:
            if tn_div == 2: 
                _tn_del = 0
                _tn_sec = 0
            else:
                _tn_del = 2
        elif _tn_div == 2:
            _tn_del = 1

        if _tn > _tn_152100:
            self.init_stockorder_timer = threading.Timer((60 * (30 - _tn.minute)) - _tn_sec, self.stock_order)
        else:
            self.init_stockorder_timer = threading.Timer((60 * _tn_del) - _tn_sec, self.stock_order)

        if self.bool_stockorder_timer:
            self.init_stockorder_timer.cancel()

        self.init_stockorder_timer.start()

        line_message(f'Bot3Swing \n시작 : {tn}, \n표기 : {tn_df_idx} \n종료 : {_tn}, {sel_txt}')
    
    
    def market_to_excel(self, rebalance=False, filter=False):

        tn = datetime.datetime.now()
        if rebalance:
            tn = tn.replace(hour=15, minute=30, second=0)
        tn_090600 = tn.replace(hour=9, minute=6, second=0)

        if tn > tn_090600:

            tn_div = tn.minute % 3
            tn_del = None

            if tn_div == 0:
                tn_del = 4
            elif tn_div == 1:
                tn_del = 5
            elif tn_div == 2:
                tn_del = 3

            tn_req = ''
            tn_int = int(tn.strftime('%H%M%S'))
            tn_pos_a = 153000 <= tn_int
            tn_pos_b = 152100 < tn_int and tn_int < 153000
            tn_pos_c = tn_int <= 152100

            if tn_pos_a:
                tn_req = '153000'
            elif tn_pos_b:
                tn_req = '152000'
            elif tn_pos_c:
                tn_req = (tn - datetime.timedelta(minutes=tn_del)).strftime('%H%M00')

            # if filter:
            #     fltr_list = self.bkk.get_condition_code_list()
            #     if len(fltr_list) > 0:
            #         save_file(FILE_URL_SMBL_3M, fltr_list)

            # q_list = self.get_guant_code_list()
            # b_list = self.get_balance_code_list()

            # _code_list = list(set(q_list + b_list))
            
            # df_a = []
            # for c, code in enumerate(_code_list):
            #     print(f"{c + 1}/{len(_code_list)} {code}")
            #     df_a.append(self.bkk.df_today_1m_ohlcv(code, tn_req, 3))
            # df = pd.concat(df_a, axis=1)
            # df = df.loc[~df.index.duplicated(keep='last')]

            # print('##################################################')
            # df.to_excel(FILE_URL_DATA_3M)
            # line_message(f'Bot3Swing \nQuant List: {len(q_list)}종목 \nBalance List: {len(b_list)}종목 \nTotal List: {len(_code_list)}개, \n{_code_list} \nFile Download Complete : {FILE_URL_DATA_3M}')
            # print(df)


            df_befor = load_xlsx(FILE_URL_DATA_3M).sort_index(axis=1)
            _code_list = df_befor.columns.to_list()[:-1]
            
            df_a = []
            for c, code in enumerate(_code_list):
                print(f"{c + 1}/{len(_code_list)} {code}")
                df_a.append(self.bkk.df_today_1m_ohlcv(code, tn_req, 3))
            df = pd.concat(df_a, axis=1)
            df = df.loc[~df.index.duplicated(keep='last')]
            
            df_after = df.sort_index(axis=1)
            df_final = pd.concat([df_befor, df_after], axis=0)
            df_final = df_final.tail(80).reset_index(level=None, drop=True)
            df_final.drop(['date'], axis=1, inplace=True)
            df_final.index.name = 'date'

            self.bdf = df_final
            self.b_l = self.bdf.columns.to_list()
            print(self.b_l)
            self.q_l = self.get_guant_code_list()
            self.r_l = list(set(self.get_balance_code_list()).difference(self.q_l))

            _ttl_prc = int(self.bkk.fetch_balance()['output2'][0]['tot_evlu_amt'])
            _buy_cnt = 80
            
            self.tot_evl_price = _ttl_prc if _ttl_prc < 40000000 else 40000000
            self.buy_max_price = self.tot_evl_price / _buy_cnt

            self.bool_market = True
            

            _tn = datetime.datetime.now()
            _tn_div = _tn.minute % 3

            if tn_pos_c and _tn_div == 2:
                self.bool_threshold = True


    def init_to_excel(self):
        
        b_list = self.get_balance_code_list()
        q_list = self.get_guant_code_list()
        f_list = list(set(q_list + b_list))
        f_df = gen_yf_df(f_list, 3)
        save_xlsx(FILE_URL_DATA_3M, f_df)
        print('##################################################')
        line_message(f'Bot3Swing \nSymbol List: {len(q_list)}종목 \nBalance List: {len(b_list)}종목 \nTotal List: {len(f_list)}개, \n{f_list} \nFile Download Complete : {FILE_URL_DATA_3M}')
        print(f_df)
        

    def deadline_symbol_list(self):

        q_list = self.bkk.get_condition_code_list()
        if len(q_list) != 0:
            save_file(FILE_URL_SMBL_3M, q_list)
            print('##################################################')
            line_message(f'Bot3Swing \nSymbol List: {len(q_list)}종목 \n{q_list}')

    
    def get_balance_code_list(self, obj=False):
        l = self.bkk.fetch_balance()['output1']
        a = []
        o = {}
        if len(l) > 0:
            for i in l:
                if int(i['ord_psbl_qty']) != 0:
                    if obj:
                        p = i['prpr']
                        q = i['ord_psbl_qty']
                        a = i['pchs_avg_pric']
                        o[i['pdno']] = {
                            'q': int(q),
                            'p': float(p),
                            'a': float(a),
                            'pft': float(p)/float(a),
                            'ptp': float(a) * int(q),
                            'ctp': float(p) * int(q)
                        }
                    else:
                        a.append(i['pdno'])
        return o if obj else a
    
    
    def get_guant_code_list(self):
        _l = load_file(FILE_URL_SMBL_3M)
        l = [str(int(i)).zfill(6) for i in _l]
        return l


if __name__ == '__main__':

    B3 = Bot3Swing()
    # B3.deadline_symbol_list()
    # B3.market_to_excel()

    while True:

        try:

            t_n = datetime.datetime.now()
            t_083000 = t_n.replace(hour=8, minute=30, second=0)
            t_090000 = t_n.replace(hour=9, minute=0, second=0)
            t_152500 = t_n.replace(hour=15, minute=25, second=0)
            t_153000 = t_n.replace(hour=15, minute=30, second=0)
            t_180000 = t_n.replace(hour=18, minute=0, second=0)

            if t_n >= t_083000 and t_n <= t_153000 and B3.bool_marketday == False:
                if os.path.isfile(os.getcwd() + '/token.dat'):
                    os.remove('token.dat')
                B3.init_per_day()
                B3.bool_marketday = True
                B3.bool_marketday_end = False

                line_message(f'Bot3Swing Stock Start' if B3.init_marketday == 'Y' else 'Bot3Swing Holiday Start')

            if B3.init_marketday == 'Y':

                if t_n > t_152500 and t_n < t_153000 and B3.bool_stockorder_timer == False:
                    B3.bool_stockorder_timer = True

                if t_n >= t_090000 and t_n <= t_153000 and B3.bool_stockorder == False:
                    B3.stock_order()
                    B3.bool_stockorder = True

            if t_n == t_180000 and B3.bool_marketday_end == False:

                if B3.init_marketday == 'Y':
                    B3.deadline_symbol_list()
                    B3.bool_stockorder_timer = False
                    B3.bool_stockorder = False
                
                B3.bool_marketday = False
                B3.bool_marketday_end = True

                line_message(f'Bot3Swing Stock End' if B3.init_marketday == 'Y' else 'Bot3Swing Holiday End')

        except Exception as e:

            line_message(f"Bot3Swing Error : {e}")
            break