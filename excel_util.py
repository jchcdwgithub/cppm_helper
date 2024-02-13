import pandas

def get_widest_column_widths(data):
    ''' Returns a list of widest length of data found in each column. '''
    if len(data) == 0:
        return []
    col_widths = [0 for _ in data[0]]
    for current_list in data:
        for col,ele in enumerate(current_list):
            ele_len = len(str(ele))
            if ele_len > col_widths[col]:
                col_widths[col] = ele_len
    return [col_width+2 for col_width in col_widths]

def format_cells_in_table(color_scheme:dict[str,str], writer:pandas.ExcelWriter, worksheet, 
                          start_cell:tuple, table_name:str, table_headers:list[str], table_data:list[list]) -> None:
    ''' Takes a color scheme, applies it to the table_data table and writes the data to the excel sheet '''
    start_row, start_col = start_cell
    workbook = writer.book
    table_header_format = workbook.add_format({'bg_color':color_scheme['header_bg_color'], 'font_color':color_scheme['header_font_color']})
    colored_row_format = workbook.add_format({'bg_color':color_scheme['row_bg_color'], 'font_color':color_scheme['row_font_color']})
    worksheet
    
    for col,header in enumerate(table_headers):
        worksheet.write(start_row, start_col+col, header, table_header_format)
    
    start_row += 1
    for row_index,row in enumerate(table_data):
        if row_index%2 == 0:
            for col_index, ele in enumerate(row):
                worksheet.write(start_row+row_index, start_col+col_index, ele, colored_row_format)
        else:
            for col_index, ele in enumerate(row):
                worksheet.write(start_row+row_index, start_col+col_index, ele)

def make_headers_object(headers:list[str]) -> list[dict[str, str]]:
    '''
    Return a list of {'header': 'table header name'} 
    '''
    return [{'header':header} for header in headers]

def add_headers_row_to_data(table:dict) -> list[list]:
    '''
    Add the headers row to the table data as the first row. Returns the new list of lists.
    '''
    with_headers = [table['headers']]
    for row in table['data']:
        with_headers.append(row)
    return with_headers

def find_max_number_of_columns_among_all_tables_in_set(tables:list[dict]) -> int:
    '''
    Given a list of tables, return the table with the most columns
    '''
    max_cols = 0
    for table in tables:
        current_number_cols = len(table['headers'])
        if current_number_cols > max_cols:
            max_cols = current_number_cols
    return max_cols

def find_largest_width_among_multiple_tables(max_cols:int, tables:list[dict]) -> list[int]:
    '''
    Create a list of widest widths for all columns across multiple tables.
    '''
    widths = [0 for _ in range(max_cols)]
    for table in tables:
        table_widths = get_widest_column_widths(add_headers_row_to_data(table))
        for index,col_width in enumerate(table_widths):
            if col_width > widths[index]:
                widths[index] = col_width

    for width_index,width in enumerate(widths):
        widths[width_index] = width + 5
    return widths

def write_table_to_excel_worksheet(worksheet, table:dict[str, list[list]], start_cell:tuple, title_format) -> int:
    '''
    Writes a single table to an excel worksheet. Returns the starting row and column for the next table. 
    Worksheet is an excel worksheet object taken from one of the sheets of the writer.
    The table is a dictionary that has two keys: name and data.
        name is a string representing the table name.
        data is a list of rows with the table data. Headers are included.
    '''
    current_row, current_col= start_cell
    worksheet.write(current_row, current_col, table['name'], title_format)
    current_row += 1
    table_headers = table['headers']
    table_rows = len(table['data'])
    table_columns = make_headers_object(table_headers)
    table_style = 'Table Style Medium 2'
    if 'style' in table:
        table_style = table['style']

    worksheet.add_table(
        current_row,
        current_col,
        current_row+len(table['data']),
        current_col+len(table_headers)-1,
        {
            'columns' : table_columns,
            'data' : table['data'],
            'style' : table_style
        }
    )
    
    return current_row+table_rows+1

def write_tables_to_excel_worksheets(excel_filename: str, worksheet_names:list[str], tables_sets:list[list[list[list]]]):
    ''' Takes a set of tables and writes them onto the same sheet in an excel file.
        Each element in the Tables list corresponds to a list of tables to be written vertically
        in relation to each other. Each table is a dictionary that contains the name, headers and
        data in the table.
    '''
    with pandas.ExcelWriter(excel_filename) as writer:
        workbook = writer.book
        for worksheet_name,tables in zip(worksheet_names,tables_sets):
            if len(worksheet_name) > 31:
                worksheet_name = worksheet_name[:31]
            worksheet = workbook.add_worksheet(worksheet_name)
            writer.sheets[worksheet_name] = worksheet
            table_title_cell_format = workbook.add_format({'bg_color': '#D9D9D9', 'font_size': 16, 'bold':True})
            next_table_row = 0
            next_table_col = 0

            for tables_in_set in tables:
                max_columns = find_max_number_of_columns_among_all_tables_in_set(tables_in_set)
                widths = find_largest_width_among_multiple_tables(max_columns, tables_in_set)
                for col_offset,width in enumerate(widths):
                    column = next_table_col + col_offset
                    worksheet.set_column(column,column,width)

                for table in tables_in_set:
                    next_table_row = write_table_to_excel_worksheet(worksheet, table, (next_table_row, next_table_col), table_title_cell_format)

                next_table_row = 0
                next_table_col += max_columns + 2