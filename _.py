from Bot3Swing import *
from pprint import pprint

b3 = Bot3Swing()
kp = b3.bkk.fetch_kospi_symbols()
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
                & (kp['저유동성'] != 'Y') 
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
                # & (kp['전일거래량'] > 500000) 
                ]
kp_tk = kp['단축코드'].to_list()
ft_kp = b3.bkk.get_caution_code_list(kp_tk, True)

# sym_lst = []

# i = 1

# for cl in ft_kp:

#     # print(f'{i} / {len(ft_kp)}')
    
#     d = b3.bkk.fetch_ohlcv_domestic(cl, 'D', '20230503', '20230504')
#     # print(d['output1'])
#     cur_p = int(d['output1']['stck_prpr'])
#     cur_v = int(d['output1']['acml_vol'])
#     cur_m = int(d['output1']['acml_tr_pbmn'])

#     if \
#     cur_p > 1000 and \
#     cur_v > 500000 and \
#     cur_m > 1500000000 \
#     :
#         print(cur_v, cur_m)
#         sym_lst.append(cl)

#     i += 1

# print(sym_lst)


kd = b3.bkk.fetch_kosdaq_symbols()
kd = kd.loc[(kd['그룹코드'] == 'ST') 
                & (kd['시가총액규모'] != 0) 
                & (kd['시가총액'] != 0) 
                & (kd['우선주'] == 0) 
                & (kd['단기과열'] == 0) 
                & (kd['락구분'] == 0)
                & (kd['액면변경'] == 0) 
                & (kd['증자구분'] == 0)
                & (kd['ETP'] != 'Y') 
                & (kd['KRX은행'] != 'Y') 
                & (kd['KRX증권'] != 'Y')
                & (kd['KRX섹터_보험'] != 'Y')
                & (kd['SPAC'] != 'Y') 
                & (kd['투자주의'] != 'Y') 
                & (kd['거래정지'] != 'Y') 
                & (kd['정리매매'] != 'Y') 
                & (kd['관리종목'] != 'Y') 
                & (kd['시장경고'] != 'Y') 
                & (kd['경고예고'] != 'Y') 
                & (kd['불성실공시'] != 'Y') 
                & (kd['우회상장'] != 'Y') 
                & (kd['공매도과열'] != 'Y') 
                & (kd['이상급등'] != 'Y') 
                & (kd['회사신용한도초과'] != 'Y') 
                & (kd['담보대출가능'] != 'Y') 
                & (kd['대주가능'] != 'Y') 
                & (kd['신용가능'] == 'Y')
                & (kd['증거금비율'] != 100)
                # & (kp['전일거래량'] > 500000) 
                ]
kd_tk = kd['단축코드'].to_list()
ft_kd = b3.bkk.get_caution_code_list(kd_tk, True)

# sym_lst = []

# i = 1

# for cl in ft_kd:

#     # print(f'{i} / {len(ft_kd)}')
    
#     d = b3.bkk.fetch_ohlcv_domestic(cl, 'D', '20230503', '20230504')
#     # print(d['output1'])
#     cur_p = int(d['output1']['stck_prpr'])
#     cur_v = int(d['output1']['acml_vol'])
#     cur_m = int(d['output1']['acml_tr_pbmn'])

#     if \
#     cur_p > 1000 and \
#     cur_v > 500000 and \
#     cur_m > 1500000000 \
#     :
#         print(cur_v, cur_m)
#         sym_lst.append(cl)

#     i += 1

# print(sym_lst)

tn = datetime.datetime.today()
tn_3m = tn - relativedelta(months=3)

symbol_list = ft_kp + ft_kd

filter_symbol_list = []

i = 1
for symbol in symbol_list:

    print(f'Items that meet the conditions: {i} / {len(symbol_list)}')
    symbol_data = b3.bkk.fetch_ohlcv_domestic(symbol, 'D', tn_3m.strftime('%Y%m%d'), tn.strftime('%Y%m%d'))['output2']

    opn_l = []
    hgh_l = []
    low_l = []
    cls_l = []
    vol_l = []
    vlm_l = []

    for d in symbol_data:
        opn_l.append(float(d['stck_oprc']))
        hgh_l.append(float(d['stck_hgpr']))
        low_l.append(float(d['stck_lwpr']))
        cls_l.append(float(d['stck_clpr']))
        vol_l.append(int(d['acml_vol']))
        vlm_l.append(int(d['acml_tr_pbmn']))

    _df = pd.DataFrame({'open': opn_l[::-1], 'high': hgh_l[::-1], 'low': low_l[::-1], 'close': cls_l[::-1], 'vol': vol_l[::-1], 'vlm': vlm_l[::-1]})
    df = min_max_height(moving_average(_df)).tail(1)

    cls_v = df['close'].iloc[-1]
    cls_p_v = df['close_p'].iloc[-1]
    hgt_v = df['height'].iloc[-1]
    m05_v = df['ma05'].iloc[-1]
    m20_v = df['ma20'].iloc[-1]
    m60_v = df['ma60'].iloc[-1]
    vol_v = df['vol'].iloc[-1]
    vlm_v = df['vlm'].iloc[-1]

    if \
    (cls_v > 1000) and \
    (cls_v < (cls_p_v * 1.05)) and \
    (hgt_v > 1.1) and \
    (m05_v > m20_v > m60_v) and \
    (m20_v * 1.05 > cls_v > m20_v) and \
    (cls_v > m05_v)\
    :
        print(vol_v, vlm_v)
        filter_symbol_list.append(symbol)

    i += 1

print(len(filter_symbol_list))
print(filter_symbol_list)