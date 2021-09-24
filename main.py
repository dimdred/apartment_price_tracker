from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import csv
import os

URL = "https://www.havenatwater.com/floorplans"


def url_parser(url):
    price_dict = {}

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    all_cards = soup.findAll("div", class_="card-body")

    for card in all_cards:
        floor_plan = card.a['data-floorplan-name']
        price_data = card.p.get_text()
        price = re.search(r'(\S+)to', price_data)
        # add only plans with price
        if price is not None:
            formatted_price = int(price.group(1).replace('$', '').replace(',', ''))
            price_dict[floor_plan] = formatted_price

    sorted_price_dict = dict(sorted(price_dict.items(), key=lambda item: item[1]))
    return sorted_price_dict


def create_csv(filename):
    with open(filename, "w", newline='') as f:
        csv_file = csv.writer(f)
        csv_file.writerow(["Date", "Price", "Floor Plan"])


def check_file(filename):
    if not os.path.exists(filename):
        create_csv(filename)


def write_data(data):
    # get the first key-value pair (min price)
    pairs_iterator = iter(data.items())
    title, min_price = next(pairs_iterator)
    cur_date = datetime.now().strftime("%m/%d/%Y")

    with open("all_prices.csv", "a", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for plan, price in data.items():
            csv_writer.writerow([cur_date, price, plan])
    with open("cheapest_price.csv", "a", newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([cur_date, min_price, title])


if __name__ == "__main__":
    check_file("all_prices.csv")
    check_file("cheapest_price.csv")
    content = url_parser(URL)
    write_data(content)
