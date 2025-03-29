from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
import base64
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials

def get_data_udemy():
    url = 'https://scraping-for-beginner.herokuapp.com/udemy'
    requests.get(url)
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    n_subscriber = soup.find('p', {'class':'subscribers'}).text
    n_subscriber = int(n_subscriber.split('：')[1])

    n_review = soup.find('p', {'class':'reviews'}).text
    n_review = int(n_review.split('：')[1])

    return {
        'n_subscriber': n_subscriber,
        'n_review': n_review
    }

def main():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    service_account_json = base64.b64decode(os.environ['SERVICE_ACCOUNT_JSON_B64']).decode('utf-8')

    with open('service_account.json', 'w') as f:
        f.write(service_account_json)

    credentials = Credentials.from_service_account_file(
        'service_account.json',
        scopes=scopes
    )

    gc = gspread.authorize(credentials)

    SP_SHEET_KEY =  '1GUQltcAVjUPJLUYSJ4edJ-k_A33fSJqu75x3f6A8aoI'
    sh =gc.open_by_key(SP_SHEET_KEY)

    SP_SHEET = 'db'
    worksheet = sh.worksheet(SP_SHEET)

    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])

    data_udemy = get_data_udemy()
    today = datetime.date.today().strftime('%Y/%m/%d')
    data_udemy['date'] = today

    df = pd.concat([df, pd.DataFrame([data_udemy])], ignore_index=True)
    set_with_dataframe(worksheet, df, row=1, col=1)

if __name__ == '__main__':
    main()