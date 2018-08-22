from requests import request
from bs4 import BeautifulSoup

from IO.writer import write_to_txt

SET100_URL = 'https://marketdata.set.or.th/mkt/sectorquotation.do?sector=SET&language=en&country=TH'
SSET_URL = 'https://marketdata.set.or.th/mkt/sectorquotation.do?sector=sSET&language=en&country=TH'
MAI_URL = 'https://marketdata.set.or.th/mkt/sectorquotation.do?sector=MAI&language=th&country=TH'


def main():
    symbol_list = []
    symbol_list += get_symbol_list(SET100_URL)
    symbol_list += get_symbol_list(SSET_URL)
    symbol_list += get_symbol_list(MAI_URL)

    result_list = []

    for symbol in symbol_list:
        print('start ', symbol)
        result_list.append({
            'symbol':symbol
        })
        result_list[-1].update(calculate_peg(symbol))
        print('finish', symbol)
    write_to_txt(result_list)
    pass




def calculate_peg(symbol):

    fact_sheet = get_factsheet(symbol)
    growth_table = get_growth_table(fact_sheet)
    revenue_growth = get_table_value(growth_table,1 , row_index=1)
    summary_table = get_summary_table(fact_sheet)

    price = get_table_value(summary_table,0,row_index=1)
    pe = get_table_value(summary_table,2,row_index=1)

    try:
        peg = '%.2f' % (float(pe)/float(revenue_growth)*100)
    except:
        peg = 'N/A'

    return {
        'price':price,
        'pe':pe,
        'revenue_growth':revenue_growth,
        'peg':peg
    }


def get_symbol_list(url):
    html = request('get',url)
    body = BeautifulSoup(html.content)
    symbol_tables = body.find_all('tbody')[2:]

    symbol_rows = []
    for table in symbol_tables:
        symbol_rows += table.find_all('tr')

    symbol_list = []
    for row in symbol_rows:
        # symbol_list.append({
        #     'symbol':row.a.text.strip(),
        #     'url':row.a.get('href')
        # })
        symbol_list.append(row.a.text.strip())
    return symbol_list


def get_factsheet(symbol):
    url = 'https://www.set.or.th/set/factsheet.do?symbol='+symbol+'&ssoPageId=3&language=en&country=US'
    html = request('get',url)
    body = BeautifulSoup(html.content)
    return body


def get_summary_table(factsheet: BeautifulSoup):
    tag = factsheet.find(string='Price (B.)')
    return find_parent_table(tag)


def get_income_statement_table(factsheet: BeautifulSoup):
    tag = factsheet.find(string='Statement of Comprehensive Income (MB.)')
    return find_parent_table(tag)


def get_balance_sheet_table(factsheet: BeautifulSoup):
    tag = factsheet.find(string='Statement of Financial Position (MB.)')
    return find_parent_table(tag)


def get_growth_table(factsheet: BeautifulSoup):
    tag = factsheet.find(string='Growth Rate (%)')
    return find_parent_table(tag)


def find_parent_table(tag):
    if tag is None or tag.parent is None:
        return None
    while tag.parent.name != 'table':
        tag = tag.parent
        if tag is None:
            return None
    return tag.parent


def get_table_value(table: BeautifulSoup,col_index,label=None,row_index=None):
    if table is None:
        return None

    if label:
        row = table.find(string=label).parent.parent
        return row.find_all('td')[col_index].text.strip()
    elif row_index:
        row = table.find_all('tr')[row_index]
        return row.find_all('td')[col_index].text.strip()
    else:
        raise Exception('no label or row_index specified')


main()
