from requests import request
from bs4 import BeautifulSoup

SSET_URL = 'https://marketdata.set.or.th/mkt/sectorquotation.do?sector=sSET&language=en&country=TH'
MAI_URL = 'https://marketdata.set.or.th/mkt/sectorquotation.do?sector=MAI&language=th&country=TH'


def main():
    symbol_list = []
    symbol_list += get_symbol_list(SSET_URL)
    symbol_list += get_symbol_list(MAI_URL)

    fact_sheet = get_factsheet(symbol_list[0])
    income_statement_table = get_income_statement_table(fact_sheet)
    sales = get_table_value(income_statement_table,1,label='Sales')
    print(sales)


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
    tag = factsheet.find('Price(B.)')
    return find_parent_table(tag)


def get_income_statement_table(factsheet: BeautifulSoup):
    tag = factsheet.find(string='Statement of Comprehensive Income (MB.)')
    return find_parent_table(tag)


def get_balance_sheet_table(factsheet: BeautifulSoup):
    tag = factsheet.find(string='Statement of Financial Position (MB.)')
    return find_parent_table(tag)


def find_parent_table(tag):
    if tag.parent is None:
        raise Exception('no income statement table found')

    while tag.parent.name != 'table':
        tag = tag.parent
        if tag is None:
            raise Exception('no income statement table found')
    return tag.parent


def get_table_value(table: BeautifulSoup,col_index,label=None,row_index=None):
    if label:
        row = table.find(string=label).parent.parent
        return row.find_all('td')[col_index].text.strip()
    elif row_index:
        row = table.find_all('tr')[row_index]
        return row.find_all('td')[col_index].text.strip()
    else:
        raise Exception('no label or row_index specified')


main()
