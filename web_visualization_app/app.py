from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime

import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
import altair as alt
import streamlit as st

def get_data_ec():
    url_ec = 'https://scraping.official.ec/'
    res = requests.get(url_ec)
    soup = BeautifulSoup(res.text, 'html.parser')
    item_list = soup.find('ul', {'id':'itemList'})
    items = item_list.find_all('li')

    data_ec = []
    for item in items:
        datum_ec = {}
        datum_ec['title'] = item.find('p', {'class': 'item-grid_itemTitleText_b58666da'}).text
        price = item.find('p', {'class': 'items-grid_price_b58666da'}).text
        datum_ec['price'] = int(datum_ec['price'].replace('¥', '').replace(',', ''))
        datum_ec['link'] = item.find('a')['href']
        is_stock = item.find('p', {'class': 'items-grid_soldOut_b58666da'}) == None
        datum_ec['is_stock'] = '在庫あり' if datum_ec['is_stock'] == True else '在庫なし'
        data_ec.append(datum_ec)
    df_ec = pd.DataFrame(data_ec)

    return df_ec

def get_worksheet():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_file(
        'service_account.json',
        scopes=scopes
    )

    gc = gspread.authorize(credentials)

    SP_SHEET_KEY =  '1GUQltcAVjUPJLUYSJ4edJ-k_A33fSJqu75x3f6A8aoI'
    sh =gc.open_by_key(SP_SHEET_KEY)

    SP_SHEET = 'db'
    worksheet = sh.worksheet(SP_SHEET)

    return worksheet

def get_chart():
    worksheet = get_worksheet()
    data = worksheet.get_all_values()
    df_udemy = pd.DataFrame(data[1:], columns=data[0])

    df_udemy = df_udemy.astype({
        'n_subscriber': 'int',
        'n_review': 'int'
    })

    ymin1 = df_udemy['n_subscriber'].min() -10 
    ymax1 = df_udemy['n_subscriber'].max() + 10

    ymin2 = df_udemy['n_review'].min() -10
    ymax2 = df_udemy['n_review'].max() + 10

    base = alt.Chart(df_udemy).encode(
        alt.X('date:T', axis=alt.Axis(title=None)),
    )

    line1 = base.mark_line().encode(
        alt.Y('n_subscriber', 
            axis=alt.Axis(title='受講生数', titleColor='#57A44C'),
            scale=alt.Scale(domain=[ymin1, ymax1]))
    )

    line2 = base.mark_line().encode(
        alt.Y('n_review', 
            axis=alt.Axis(title='レビュー数', titleColor='#5276A7'),
            scale=alt.Scale(domain=[ymin2, ymax2]))
    )

    chart = alt.layer(line1, line2).resolve_scale(
        y='independent'
    )

    return chart 

# df_ec = get_data_ec()
chart = get_chart()

st.title('Webスクレイピング活用アプリ')
st.write('## Udemy情報')
st.altair_chart(chart, use_container_width=True)

# st.write('## EC在庫情報', df_ec)