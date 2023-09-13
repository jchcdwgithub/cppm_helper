import textfsm

def extract_table_from_config_file(textfsm_template:str, config_file:str) -> tuple[list[str], list[list[str]]]:
    '''
    Extracts a table of values from the config_file using the textfsm_template provided. Returns the table headers and table rows.
    '''
    with open(textfsm_template) as template_f, open(config_file, errors="replace") as config_f:
        config_table = textfsm.TextFSM(template_f)
        headers = config_table.header
        table_values = config_table.ParseText(config_f.read())
    return (headers, table_values)

def extract_tables_from_config_file(template_files:dict[str,str], config_file:str, hostname:str) -> dict[str,dict[list[str],list[list[str]]]]:
    '''
    Uses all files found in the template_files dictionary and returns a dictionary of tables.
    '''
    tables = {}
    for template_file,template_filepath in template_files.items():
        extracted_header, extracted_table = extract_table_from_config_file(template_filepath, config_file)
        if len(extracted_table) != 0:
            tables[template_file] = {'headers':extracted_header, 'results':extracted_table}
        tables['hostname'] = remove_file_extension_from_filename(hostname)
    return tables

def remove_file_extension_from_filename(filename:str) -> str:
    '''
    Removes any file extensions from the end of the filename. Assumes that a file extension is a dot followed by three letters.
    '''
    filename_len = len(filename)
    if '.' == filename[filename_len-4]:
        return filename[:filename_len-4]
    return filename