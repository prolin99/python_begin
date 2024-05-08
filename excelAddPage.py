#openpyxl open d:\codes\xl\123.xlsx
import openpyxl
from openpyxl.worksheet.pagebreak import Break, RowBreak

wb = openpyxl.load_workbook('F:\\codes\\xl\\123.xlsx')

# in row 5 insert a page break  ws.row_breaks.append(page_break) 

ws = wb.active

#第五列第十列加分頁
ws.row_breaks.append(Break(id=5))
ws.row_breaks.append(Break(id=10))


wb.save('F:\\codes\\xl\\00.xlsx')
