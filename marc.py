'''
圖書機讀  iso 2709 機讀碼
記錄標示，最前面的 24 位元組 前5碼代表這筆的總長度 12~16 資料首字位址
每個索引 12 位元組（3位元欄位代碼 4位元長度 5位元首字位址）


'''
import re
from typing import NoReturn, final
class MARC( object ):
	def __init__ ( self , file_list=[] ):
		self.file_list = file_list if file_list is not None and len(file_list) > 0 else []
		self.fd = None
		#self.RE_FIELD_DATA = re.compile( '\x1f.([^\x1e\x1f]+)' )
		self.RE_FIELD_DATA = re.compile( '\$([^\$\#]+)' )
	def get_raw_entries( self , cnt = None ):
		out = []
		cnt = int(cnt) if cnt is not None else 0
		while True:
			if self.fd is None:
				if  self.file_list is None or len( self.file_list ) == 0 :
					return out
				try:
					self.fd = open( self.file_list[0] , 'rb' )
					self.file_list = self.file_list[1:]
				except Exception as inst:
					print (inst)
					return out
			try:
				header = self.fd.read( 24 )

				if not header:  # EOF
					self.fd.close()
					self.fd = None
				else:
					record_size = int( header[0:5] )
					#前四碼，長度
					record_data = self.fd.read( record_size - 24 )
					out.append( header + record_data )
			except Exception as inst:
				print (inst)
				return out

			if cnt != 0 and len(out) == cnt:
					return out

	def get_field_value( self , rawdata , field , dictField = None ):

		if dictField is None:
			out = []
			header = rawdata[0:24]

			#print('header' , header)

			#索引㯗內容存放位元長度
			field_length = int( header[20:21] )
			#索引㯗偏移位置，開始讀資料
			field_offset = int( header[21:22] )
			#開始資料處 12 倍數+1 （每個索引 3+4+5）
			data_begin_offset = int( header[12:17] )
			raw_field_info = rawdata[24:data_begin_offset - 1]      # skip field end delimiter

			#print('raw_field_info' , field_length,field_offset ,data_begin_offset ,raw_field_info )

			dictField = {}
			for i in range( 0 , len(raw_field_info) , 12 ):
				#3碼索引  4碼長度 5碼開始位置
				#out = []
				begin = i
				end = i+3
				sub_field_name = raw_field_info[ begin : end ]
				#print(sub_field_name)
				sub_field_name=sub_field_name.decode('big5' , "ignore")

				begin = end
				end = begin + field_length
				#索引長度
				sub_field_data_length = raw_field_info[ begin : end ]

				#print('sub_field_name' , sub_field_name , int(sub_field_data_length) )

				begin = end
				end = begin + field_offset
				#索引開始讀取位置
				sub_field_data_offset = raw_field_info[ begin : end ]

				#print(sub_field_data_offset)

				if sub_field_name not in dictField:
					dictField[ sub_field_name ] = []
				#索引陣列，存放每一索引欄的開始及結束位置
				raw_value = [ int(sub_field_data_length) , int(sub_field_data_offset) + data_begin_offset ]

				#print('raw_value' , int(sub_field_data_length),int(sub_field_data_offset) , int(data_begin_offset) )

				dictField[ sub_field_name ].append( raw_value )
				###


		out_list = []
		out = {}
		#if field is not None and field in dictField:
		#讀取每索引的內容
		for field  in dictField:
			#print(field)
			for data_length_and_offset in dictField[field]:
				vv= (rawdata[ data_length_and_offset[1] : data_length_and_offset[0] + data_length_and_offset[1] ])

				vvsu= vv.decode("big5" , "ignore")
				#天圖圖書系統，會把同一本書合併輸出，只在 805 欄位多筆呈現
				if (field == '805' ):
					#print('v' , field , vvsu )
					if ( out.get(field)!= None )  :
						#add one line
						new_out =out.copy()
						new_out[field]=  vvsu
						#print('add')
						out_list.append(new_out)
					else :
						out[field]=  vvsu
						out_list.append(out)
				else:
					out[field]=  vvsu

		#out_list.append(out)


		#print('list len' , len(out_list))
		return ( out_list , dictField )
