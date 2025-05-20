import os

import pandas as pd

PRICES_FILE = 'prices.xlsx'

DEFAULT_PRICES = {
    'route_price': 500,       # цена за метр трассы
    'groove_price': 300,      # цена за метр штробы
    'ac_standard': 15000,     # стандартный кондиционер
    'ac_inverter': 20000,     # инверторный кондиционер
    'ac_premium': 25000,      # премиум кондиционер
    'extra_mounting': 0.2,    # 20% за сложный монтаж
    'warranty': 0.15          # 15% за гарантию
}


def load_prices():
    try:
        if not os.path.exists(PRICES_FILE):
            return DEFAULT_PRICES

        prices_df = pd.read_excel(PRICES_FILE, engine='openpyxl')
        prices_dict = prices_df.set_index('Название')['Цена'].to_dict()

        return prices_dict
    except Exception as e:
        print(f'Ошибка загрузки цен: {str(e)}')
        return DEFAULT_PRICES
