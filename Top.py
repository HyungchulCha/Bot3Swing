from Bot_3m import *
b3 = Bot_3m()
top_code = [
'001740',
'008560',
'035890',
'030200',
'138040',
'012030',
'105630',
'402340',
'035720',
'016740',
'036540',
'088980',
'122690',
'086790',
'010060',
'000990',
'121440',
'042700',
'036930',
'090460',
'000660',
'418420',
'088130',
'100090',
'084010',
'240810',
'003200',
'294090',
'323410',
'035080',
'005500',
'005090',
'047810',
'047050',
'095660',
'363250',
'196170',
'000270',
'403870',
'055550',
'017800',
'293490',
'361610',
'302440',
'145020',
'200130',
'003490',
'105560',
'016790',
'048260',
'034120',
'006360',
'066970',
'108320',
'064350',
'161890',
'101490',
'000250',
'417010',
'009240',
'247540',
'003120',
'058470',
'131970',
'011780',
'095340',
'096770',
'002310',
'005380',
'039030',
'008930',
'002790',
'079550',
'215200',
'035900',
'348210',
'008770',
'214450',
'357780',
'145720',
'064760',
'068270',
'090430',
'086520',
'128940',
'383220',
'014680',
'278280',
'011070',
'004370'
]

top_code_filter = b3.get_caution_code_list(top_code, True, True)
print(top_code_filter)
print(len(top_code_filter))