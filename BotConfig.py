import os
DIRECTORY = os.getcwd()

KI_ID = "ckgudcjf"
KI_URL_PRACTICE = 'https://openapi.koreainvestment.com:9443'
KI_ACCOUNT_PRACTICE = '19213040-01'
KI_ACCOUNT_PRACTICE_C = '19213040'
KI_APPKEY_PRACTICE = 'PSBbKwct4IS2abFaFknj5t5G1fesOvUbKovh'
KI_APPSECRET_PRACTICE = 'V9QdcVXKpjz1vFk5LCA2G6aXrbSDk4bk/+cXckKOk0/x1NqumlNW1MB8mvCaAexNauUWTlTwVDbkelgZEeGMkWmfE3c5eYuqt9YWD+81u6k7Nrhbf6CSlkzlHES50qL5hUEDdLW6XlR1l7c0/ENrTqoU2RZI1LDmtxE/9cvAUfzczRx25Qs='

KI_URL_IMITATION = 'https://openapivts.koreainvestment.com:29443'
KI_ACCOUNT_IMITATION = '50081061-01'
KI_ACCOUNT_IMITATION_C = '50081061'
KI_APPKEY_IMITATION = 'PSgFaLpCMY9CLFFUCaguWyDVdnOwnfYNQSPs'
KI_APPSECRET_IMITATION = 'FfxV9JO+iOSy+OiwyPl3Yh+UM7koPNcv0z6X6omA7w+0CCz7WSUtcMU+zz9ZL7P73YOGq8sVyr6UgII+R8lfczwTVcXeb0WQQUEB7/D1rz9TrH13vVjCVA8ciTBGi+QDj+bV4r5HJBJBZpgzRbCALs6D3XsC+4QXuwkT/leKBQTbROWqobU='

LINE_URL = 'https://notify-api.line.me/api/notify'
LINE_TOKEN = '48zl8RmuB0lZoPOoVmqowZzjsUE0P53JO7jfVFCyLwh'

FILE_URL = DIRECTORY + '/_data'
FILE_URL_BACK = DIRECTORY + '/_back_3m/'
FILE_URL_BACKTEST = DIRECTORY + '/BacktestResult/'
FILE_URL_QUANT_TOTAL = FILE_URL + '/QuantData.xlsx'
FILE_URL_DATA_3M = FILE_URL + '/BotData_3m.xlsx'
FILE_URL_DATA_BACK_3M = FILE_URL + '/BotData_3m_backup.xlsx'
FILE_URL_QUANT_LIST_3M = FILE_URL + '/QuantDataList_3m.pickle'
FILE_URL_QUANT_RANK_3M = FILE_URL + '/QuantDataRank_3m.xlsx'
FILE_URL_QUANT_LAST_3M = FILE_URL + '/QuantLast_3m.pickle'
FILE_URL_BALANCE_LIST_3M = FILE_URL + '/BalanceList_3m.pickle'
FILE_URL_BALANCE_LIST_TEST_3M = FILE_URL_BACKTEST + '/BalanceListTest_3m.pickle'