# TODO: delete this file
import operator


class Language(object):
    def __getattribute__(self, *item):
        print(item)
        pass
    def __getitem__(self, item):
        print(item)

x = Language()
x['a', 'b']

import xlsxwriter
workbook = xlsxwriter.Workbook("/home/david/Temp/testxlsx/test.xlsx")
worksheet = workbook.add_worksheet(name="Testovani")
# Logic: row, col, what
worksheet.write(0, 0, 1)
worksheet.write(0, 1, 2)
# logic: row, col, (format (how it looks), like color, bold, etc), number
currency_format = workbook.add_format({'num_format': '[$$-409]#,##0.00'})
worksheet.write_formula(0, 2,
                        '=SUM(A1:B1)',
                        cell_format=currency_format, # can be None
                        value=3)
workbook.close()

print(slice("a", "b"))