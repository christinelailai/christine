import requests
import pandas as pd
import re

#資料獲取
url ='https://file.notion.so/f/f/d70b900c-92f2-4d32-870b-1fa0d80e953b/2cc1982f-a835-4d84-9002-318758475632/output_clean_date_technical.json?table=block&id=f447ef6f-695d-45bb-9e49-f6a9c2e5ddd0&spaceId=d70b900c-92f2-4d32-870b-1fa0d80e953b&expirationTimestamp=1733623200000&signature=jBdwLm79gC1BhDeSpZQbaypTzI3cI5d9sHP3TnAl2I0&downloadName=output_clean_date_technical.json'
api_response = requests.get(url)
data = api_response.json()

#獲取欄位內容並轉換為pd
keyName = ['financialGrowth','ratios','cashFlowStatementGrowth','incomeStatementGrowth','balanceSheetStatementGrowth','historicalPriceFull']
for i in range(len(keyName)):
    info = pd.DataFrame(data[keyName[i]])
    globals()[keyName[i]] = info

#將historicalPriceFull中由key組成的value轉換為pd
historicalPriceFull =pd.DataFrame(list(globals()[keyName[5]]['historical']))
#在索引欄1插入symbol欄位
historicalPriceFull.insert(1,'symbol','1101.TW')
#日期沒有重複
print(sum(historicalPriceFull['date'].duplicated()))

#合併'financialGrowth','ratios','cashFlowStatementGrowth','incomeStatementGrowth'(日期皆為period),命名為fin_merge
fin_merge = globals()[keyName[0]]
for i in range(1,5):
    fin_merge = pd.merge(fin_merge, globals()[keyName[i]],how='left',on=['date','symbol','calendarYear','period'])

#將fin_merge的date依據年季轉換為yyyy-mm-dd
date_column= []
for i in range(fin_merge.shape[0]):
    if fin_merge.iloc[i,3] in ['Q1','Q4']:
        fin_merge.iloc[i,1] = fin_merge.iloc[i,2]+'-'+str(int(fin_merge.iloc[i,3][1])*3)+'-'+'31' 
    else:
        fin_merge.iloc[i,1] = fin_merge.iloc[i,2]+'-'+str(int(fin_merge.iloc[i,3][1])*3)+'-'+'30' 
    date_column.append(fin_merge.iloc[i,1])

date_column = [re.sub(r'-(\d)-', r'-0\1-', date) for date in date_column]
fin_merge['date'] = date_column


#測試合併看看有沒有在fin_merge有出現但historicalPriceFull沒有出現的日期
merge_test = pd.merge(historicalPriceFull.iloc[:,:6], fin_merge,how='right',on='date')
missingDate = ['2023-09-30','2022-12-31','2021-12-31','2020-12-31']
origin_rows = historicalPriceFull.shape[0]

#將缺失日期補入historicalPriceFull
for i in range(origin_rows,origin_rows + 4):
    historicalPriceFull.loc[i,'date'] = missingDate[i - origin_rows]
    historicalPriceFull.loc[i,'symbol'] = '1101.TW'

#合併historicalPriceFull 跟 fin_merge
result = pd.merge(historicalPriceFull, fin_merge,how='left',on=['date','symbol'])

#下載為csv
result.to_csv('input.csv',index=False)


