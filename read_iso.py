'''
需安裝套件
pip install pandas
pip install openpyxl
pip install xlsxwriter
'''
from marc import MARC
import re
import pandas as pd

#你匯出的 iso 檔名放在這：
m = MARC(['040001-043023'])



row=0
i = 0
output_dict={}
for rawdata in m.get_raw_entries():
	tmp = None

	try:
		getList , tmp = m.get_field_value( rawdata , '700' , tmp )

		for values in  getList:
			new_row={}
			#print(row , values['200'] , values['805'] )
			for key, value in values.items():
			#if len(value) > 0:

				new_row[key]= value

				for raw in re.findall( m.RE_FIELD_DATA , value ):
					new_row[str(key)+'K'+raw[0]]= raw[1:]

					#break

			output_dict[row]= new_row

			row += 1
			i += 1

	except Exception as e  :
		print( e )
#print(output_dict[0])
df = pd.DataFrame.from_dict(output_dict)
df2= df.T

# 全部欄位的檔案，如果不需要可以略去
df2.to_excel('0000.xlsx' ,engine='xlsxwriter' )

# 再檢查想要保留的必要欄位 ，存成 0001.xlsx
df3 = df2[['010Ka','010Kd','200Ka','200Kf' , '200Kg','210Ka','210Kc' ,'210Kd','681Ka' ,'681Kb' , '805Kc','805Kd', '805Ke' , '805Ku', '805Kw' ,'805Kz' ]]
df3.to_excel('0001.xlsx' ,engine='xlsxwriter' )
print('其轉出 {} 筆記錄'.format(i))