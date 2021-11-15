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
		next_be_short = 0
		next_add_header = b''
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

				header = next_add_header + self.fd.read( 24 - next_be_short)
				#print(header)
				if not header:  # EOF
					self.fd.close()
					self.fd = None
				else:
					record_size = int( header[0:5] )
					#前五碼，長度
					#print(record_size)
					record_data = self.fd.read( record_size - 24 )
					#print('+' ,record_size , header)
					#天圖匯出以 % 結尾，但有時記錄長度和讀取長度會不一致（會多1字），加以再加入檢查。
					next_be_short = 0
					next_add_header=b''
					if record_data[-1] != 37:			# %結尾
						#print('===' ,record_size , header , record_data)
						for bchar in record_data[::-1] :
							#print(bchar)
							if bchar == 37:
								break
							next_be_short += 1
						next_add_header = record_data[next_be_short*-1:]
						#print('---' , next_be_short , next_add_header )

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
			
			field_length = int( header[20:21] )
			field_offset = int( header[21:22] )
			data_begin_offset = int( header[12:17] )
			raw_field_info = rawdata[24:data_begin_offset - 1]      # skip field end delimiter
			
			#print('raw_field_info' , field_length,field_offset ,data_begin_offset ,raw_field_info )

			dictField = {}
			for i in range( 0 , len(raw_field_info) , 12 ):
				#out = []
				begin = i
				end = i+3
				sub_field_name = raw_field_info[ begin : end ]
				#print(sub_field_name)
				sub_field_name=sub_field_name.decode('big5' , "ignore")

				begin = end
				end = begin + field_length
				sub_field_data_length = raw_field_info[ begin : end ]
				
				#print('sub_field_name' , sub_field_name , int(sub_field_data_length) )

				begin = end
				end = begin + field_offset
				sub_field_data_offset = raw_field_info[ begin : end ]

				#print(sub_field_data_offset)

				if sub_field_name not in dictField:
					dictField[ sub_field_name ] = []
				raw_value = [ int(sub_field_data_length) , int(sub_field_data_offset) + data_begin_offset ]
				
				#print('raw_value' , int(sub_field_data_length),int(sub_field_data_offset) + int(data_begin_offset) )
				
				dictField[ sub_field_name ].append( raw_value )
				###


		out_list = []
		out = {}
		#if field is not None and field in dictField:
		for field  in dictField:
			#print(field)
			for data_length_and_offset in dictField[field]:
				vv= (rawdata[ data_length_and_offset[1] : data_length_and_offset[0] + data_length_and_offset[1] ])
				
				vvsu= vv.decode("big5" , "ignore")
				#天圖匯出不是一本畫一筆紀錄，而是相同書同一筆紀錄，最後以 805 分列多本書
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
