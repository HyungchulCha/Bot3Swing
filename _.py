import datetime
from dateutil.relativedelta import *

print(datetime.datetime.today().weekday() == 1)

today = datetime.datetime.today()
print(today)
next_month = datetime.datetime(today.year, today.month, 1) + relativedelta(months=1)
this_month_last = next_month + relativedelta(seconds=-1)
print(today.strftime('%Y%m%d'))
print(today.strftime('%Y%m%d') == this_month_last.strftime('%Y%m%d'))