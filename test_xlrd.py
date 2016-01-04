import xlrd

def read_xl(filename, sht_name, x, y, width, height):
    wb = xlrd.open_workbook(filename)

    sht = wb.sheet_by_name(sht_name)

    return [sht.row_values(i, x - 1, x - 1 + width) for i in xrange(y - 1, y - 1 + height)]

test = read_xl('/Users/othello/Projects/OFCE/ThreeME/data/calibrations/SAM_FRA_ADEMEhaut.xls', 'Supply_Use_dom', 6, 5, 150, 130)



#print test
