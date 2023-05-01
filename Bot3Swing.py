from BotConfig import *
from BotUtil import *
from BotKIKr import BotKIKr
import pandas as pd
import datetime
import threading
import os
import copy

class Bot3Swing():


    def __init__(self):

        self.mock = True
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

        self.init_marketday = None
        self.init_stockorder_timer = None


    def init_per_day(self):

        self.bkk = BotKIKr(self.key, self.secret, self.account, self.mock)
        self.bdf = load_xlsx(FILE_URL_DATA_3M).set_index('date')
        self.b_l = self.bdf.columns.to_list()
        self.q_l = self.get_guant_code_list()
        self.r_l = list(set(self.get_balance_code_list()).difference(self.q_l))

        self.tot_evl_price = self.get_total_price()
        self.buy_max_price = self.tot_evl_price / 20
        self.init_marketday = self.bkk.fetch_marketday()

        line_message(f'Bot3Swing \n평가금액 : {self.tot_evl_price}원, 다른종목: {len(self.r_l)}개')
    

    def stock_order(self):

        tn = datetime.datetime.now()
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

        if os.path.isfile(FILE_URL_BALANCE_LIST_3M):
            obj_lst = load_file(FILE_URL_BALANCE_LIST_3M)
            print('Loaded!!!')
        else:
            obj_lst = {}
            save_file(FILE_URL_BALANCE_LIST_3M, obj_lst)
            print('Saved!!!')

        for code in self.b_l:

            min_lst = self.bkk.fetch_today_1m_ohlcv(code, tn_df_req, True)['output2'][:3]
            chk_cls = min_lst[0]['stck_prpr']
            chk_opn = min_lst[2]['stck_oprc']
            chk_hig = max([int(min_lst[i]['stck_hgpr']) for i in range(3)])
            chk_low = min([int(min_lst[i]['stck_lwpr']) for i in range(3)])
            chk_vol = sum([int(min_lst[i]['cntg_vol']) for i in range(3)])
            self.bdf.at[tn_df_idx, code] = str(chk_opn) + '|' + str(chk_hig) + '|' + str(chk_low) + '|' + str(chk_cls) + '|' + str(chk_vol)

            is_late = tn_div == 2

            if (not is_late):

                is_remain = code in self.r_l
                is_alread = code in bal_lst
                
                if (not is_alread) and (not is_remain):

                    df = min_max_height(moving_average(get_code_df(self.bdf, code)))
                    df_t = df.tail(1)

                    if \
                    (df_t['close'] < df_t['close_p'] * 1.05) and \
                    (df_t['height'] > 1.1) and \
                    (df_t['ma05'] > df_t['ma20'] > df_t['ma60']) and \
                    (df_t['ma20'] * 1.05 > df_t['close'] > df_t['ma20']) and \
                    (df_t['close'] > df_t['ma05'])\
                    :
                        ord_q = get_qty(int(chk_cls), self.buy_max_price)
                        buy_r = self.bkk.create_market_buy_order(code, ord_q) if tn < tn_153000 else self.bkk.create_over_buy_order(code, ord_q)

                        if buy_r['rt_cd'] == '0':
                            print(f'매수 - 종목: {code}, 수량: {ord_q}주')
                            obj_lst[code] = {'a': int(chk_cls), 'x': int(chk_cls), 's': 1}
                            sel_lst.append({'c': '[B] ' + code, 'r': str(ord_q) + '주'})
                        else:
                            msg = buy_r['msg1']
                            print(f'{msg}')

                if is_alread:

                    t1 = 0.035
                    t2 = 0.045
                    t3 = 0.055
                    ct = 0.8
                    hp = 100

                    if obj_lst[code]['x'] < bal_lst[code]['p']:
                        obj_lst[code]['x'] = copy.deepcopy(bal_lst[code]['p'])
                        obj_lst[code]['a'] = copy.deepcopy(bal_lst[code]['a'])

                    if obj_lst[code]['x'] > bal_lst[code]['p']:

                        if 1 < bal_lst[code]['pft'] < hp:

                            pft_max = float(obj_lst[code]['x']) / float(obj_lst[code]['a'])
                            los_dif = pft_max - bal_lst[code]['pft']

                            if (obj_lst[code]['s'] == 1) and (t1 <= los_dif):

                                ord_qty = int(bal_lst[code]['q'] * 0.2) if int(bal_lst[code]['q'] * 0.2) != 0 else 1
                                sel_r = self.bkk.create_market_sell_order(code, ord_qty) if tn < tn_153000 else self.bkk.create_over_sell_order(code, ord_qty)
                                _ror = ror(bal_lst[code]['ptp'] * 0.2, bal_lst[code]['ctp'] * 0.2)

                                if sel_r['rt_cd'] == '0':
                                    print(f'매도 - 종목: {code}, 수익: {round(_ror, 4)}')
                                    sel_lst.append({'c': '[S1] ' + code, 'r': round(_ror, 4)})
                                else:
                                    msg = sel_r['msg1']
                                    print(f'{msg}')

                                prev_sel = copy.deepcopy(obj_lst[code]['sel'])
                                obj_lst[code]['sel'] = prev_sel + 1
                            
                            elif (obj_lst[code]['sel'] == 2) and (t2 <= los_dif):

                                ord_qty = int(bal_lst[code]['q'] * (3/8)) if int(bal_lst[code]['q'] * (3/8)) != 0 else 1
                                sel_r = self.bkk.create_market_sell_order(code, ord_qty) if tn < tn_153000 else self.bkk.create_over_sell_order(code, ord_qty)
                                _ror = ror(bal_lst[code]['ptp'] * (3/8), bal_lst[code]['ctp'] * (3/8))

                                if sel_r['rt_cd'] == '0':
                                    print(f'매도 - 종목: {code}, 수익: {round(_ror, 4)}')
                                    sel_lst.append({'c': '[S2] ' + code, 'r': round(_ror, 4)})
                                else:
                                    msg = sel_r['msg1']
                                    print(f'{msg}')

                                prev_sel = copy.deepcopy(obj_lst[code]['sel'])
                                obj_lst[code]['sel'] = prev_sel + 1

                            elif (obj_lst[code]['sel'] == 3) and (t3 <= los_dif):
                                if t3 <= los_dif:
                                    
                                    sel_r = self.bkk.create_market_sell_order(code, bal_lst[code]['q']) if tn < tn_153000 else self.bkk.create_over_sell_order(code, bal_lst[code]['q'])
                                    _ror = ror(bal_lst[code]['ptp'], bal_lst[code]['ctp'])

                                    if sel_r['rt_cd'] == '0':
                                        print(f'매도 - 종목: {code}, 수익: {round(_ror, 4)}')
                                        sel_lst.append({'c': '[S3] ' + code, 'r': round(_ror, 4)})
                                    else:
                                        msg = sel_r['msg1']
                                        print(f'{msg}')

                                    obj_lst.pop(code, None)

                        elif hp <= bal_lst[code]['pft']:

                            sel_r = self.bkk.create_market_sell_order(code, bal_lst[code]['q']) if tn < tn_153000 else self.bkk.create_over_sell_order(code, bal_lst[code]['q'])
                            _ror = ror(bal_lst[code]['ptp'], bal_lst[code]['ctp'])

                            if sel_r['rt_cd'] == '0':
                                print(f'매도 - 종목: {code}, 수익: {round(_ror, 4)}')
                                sel_lst.append({'c': '[S+] ' + code, 'r': round(_ror, 4)})
                            else:
                                msg = sel_r['msg1']
                                print(f'{msg}')

                            obj_lst.pop(code, None)

                        elif bal_lst[code]['pft'] <= ct:

                            sel_r = self.bkk.create_market_sell_order(code, bal_lst[code]['q']) if tn < tn_153000 else self.bkk.create_over_sell_order(code, bal_lst[code]['q'])
                            _ror = ror(bal_lst[code]['ptp'], bal_lst[code]['ctp'])

                            if sel_r['rt_cd'] == '0':
                                print(f'매도 - 종목: {code}, 수익: {round(_ror, 4)}')
                                sel_lst.append({'c': '[S-] ' + code, 'r': round(_ror, 4)})
                            else:
                                msg = sel_r['msg1']
                                print(f'{msg}')

                            obj_lst.pop(code, None)

        save_file(FILE_URL_BALANCE_LIST_3M, obj_lst)

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
    
    
    def market_to_excel(self, rebalance=False):

        _code_list = list(set(self.get_guant_code_list() + self.get_balance_code_list()))

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
            
            df_a = []
            for c, code in enumerate(_code_list):
                print(f"{c + 1}/{len(_code_list)} {code}")
                df_a.append(self.bkk.df_today_1m_ohlcv(code, tn_req, 3))
            df = pd.concat(df_a, axis=1)
            df = df.loc[~df.index.duplicated(keep='last')]

            print('##################################################')
            line_message(f'File Download Complete : {FILE_URL_DATA_3M}')
            print(df)
            df.to_excel(FILE_URL_DATA_3M)

            _tn = datetime.datetime.now()
            _tn_div = _tn.minute % 3

            if tn_pos_c and _tn_div == 2:
                self.bool_threshold = True

    
    def deadline_to_excel(self):
        save_file(FILE_URL_QUANT_LAST_3M, self.bkk.filter_code_list())
        self.market_to_excel(True)

    
    def get_total_price(self):
        _total_eval_price = int(self.bkk.fetch_balance()['output2'][0]['tot_evlu_amt'])
        return _total_eval_price if _total_eval_price < 20000000 else 20000000
        
    
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
                            'q': q,
                            'p': p,
                            'a': a,
                            'max': p,
                            'pft': p/a,
                            'sel': 1,
                            'ptp': float(a) * int(q),
                            'ctp': float(p) * int(q)
                        }
                    else:
                        a.append(i['pdno'])
        return o if obj else a
    
    
    def get_guant_code_list(self):
        _l = load_file(FILE_URL_QUANT_LAST_3M)
        l = [str(int(i)).zfill(6) for i in _l]
        return l


if __name__ == '__main__':

    B3 = Bot3Swing()
    # 일주일에 한번
    # B3.deadline_to_excel()
    # B3.market_to_excel(True)

    while True:

        try:

            t_n = datetime.datetime.now()
            t_085000 = t_n.replace(hour=8, minute=50, second=0)
            t_090300 = t_n.replace(hour=9, minute=3, second=0)
            t_152500 = t_n.replace(hour=15, minute=25, second=0)
            t_153000 = t_n.replace(hour=15, minute=30, second=0)
            t_160000 = t_n.replace(hour=16, minute=00, second=0)

            if t_n >= t_085000 and t_n <= t_153000 and B3.bool_marketday == False:
                if os.path.isfile(os.getcwd() + '/token.dat'):
                    os.remove('token.dat')
                B3.init_per_day()
                B3.bool_marketday = True
                B3.bool_marketday_end = False

                line_message(f'Stock Start' if B3.init_marketday == 'Y' else 'Holiday Start')

            if B3.init_marketday == 'Y':

                if t_n > t_152500 and t_n < t_153000 and B3.bool_stockorder_timer == False:
                    B3.bool_stockorder_timer = True

                if t_n >= t_090300 and t_n <= t_153000 and B3.bool_stockorder == False:
                    B3.stock_order()
                    B3.bool_stockorder = True

            if t_n == t_160000 and B3.bool_marketday_end == False:

                if B3.init_marketday == 'Y':
                    B3.market_to_excel()
                    B3.bool_stockorder_timer = False
                    B3.bool_stockorder = False

                if datetime.datetime.weekday() == 6:
                    B3.deadline_to_excel()

                B3.bool_marketday = False
                B3.bool_marketday_end = True

                line_message(f'Stock End' if B3.init_marketday == 'Y' else 'Holiday End')

        except Exception as e:

            line_message(f"Bot3 Error : {e}")
            break