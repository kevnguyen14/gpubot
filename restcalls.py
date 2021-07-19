from bs4 import BeautifulSoup
import requests
import sys
from datetime import datetime
from pytz import timezone
import pytz
import ast
import time
from slack import WebClient
import re

format = '%m/%d/%Y %I:%M %p'
slack = "https://hooks.slack.com/services/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"
headers = {
        'User-Agent': 'PostmanRuntime/7.26.8',
        'Cache-Control': 'no-cache'
    }
slack_headers = {
    'Content-type': 'application/json'
}
channels = {
    'gpu-drops': 'C022XB5QG5V',
    'rtx-3080': 'C026657SCH5',
    'rtx-3060': 'C026E4EEW3Y',
    'rtx-3070': 'C026E4FG7U6',
    'rtx-3080-ti': 'C026E4J3HTQ',
    'rtx-3070-ti': 'C026LSFU666',
    'rtx-3060-ti': 'C026E5DTLP8',
    'rtx-3090': 'C026M34KMNX',
    'rx-6800-xt': 'C026M3A7091',
    'rx-6900-xt': 'C026M3AL30T',
    'rx-6700-xt': 'C026T39G9RA',
    'rx-6800': 'C026T39S02Y',
    'ps5': 'C026T3B93K6'
}
client = WebClient(
    token='xoxb-2107367144342-2137979784480-a67dHcgertqe6UZ3gyUzgMF1')

def send_message_to_channel(name: str, msg: str):
    name = name.lower()
    if "3060 ti" in name or "3060ti" in name:
        ch = channels['rtx-3060-ti']
    elif "3070 ti" in name or "3070ti" in name:
        ch = channels['rtx-3070-ti']
    elif "3080 ti" in name or "3080ti" in name:
        ch = channels['rtx-3080-ti']
    elif "3060" in name:
        ch = channels['rtx-3060']
    elif "3070" in name:
        ch = channels['rtx-3070']
    elif "3080" in name:
        ch = channels['rtx-3080']
    elif "3090" in name:
        ch = channels['rtx-3090']
    elif "6700" in name:
        ch = channels['rx-6700-xt']
    elif "6800 xt" in name or "6800xt" in name:
        ch = channels['rx-6800-xt']
    elif "6800" in name:
        ch = channels['rx-6800']
    elif "6900" in name:
        ch = channels['rx-6900-xt']
    elif "ps5" in name or "playstation" in name or "sony" in name:
        ch = channels['ps5']
    else:
        ch = 'C024LS4LBCJ'
    try:
        client.chat_postMessage(channel=ch,
                                text=msg)
    except Exception as e:
        print(e)

def send_to_main_channel(name, body):
    requests.post(slack, headers=slack_headers, json=body, timeout=5)

def run_bb_bot(skus):
    skus_in_stock = set()
    while True:
        for sku in skus:
            try:
                link = f"https://www.bestbuy.com/site/{sku}.p?skuId={sku}"
                response = requests.get(f"{link}", headers=headers, cookies={'locStoreId': '190'}, timeout=10)
                soup = BeautifulSoup(response.text)
                btns = soup.find_all("div", {'class':'fulfillment-add-to-cart-button'})
                page_class = BeautifulSoup(str(btns))
                btn_class2 = page_class.find("button")
                add_enabled2 = "SOLD_OUT" not in btn_class2.get_attribute_list("data-button-state")
                #print(f"{link} in stock: {add_enabled2}")
                if add_enabled2 and sku not in skus_in_stock:
                    skus_in_stock.add(sku)
                    in_stock = "IN STOCK" if btn_class2.text.strip() != "Shop Open-Box" else "OPEN BOX"
                    sku_name = soup.find("div", {'class': 'sku-title'}).text
                    price = soup.find("div", {'class': 'priceView-customer-price'}).text.split(" ")[-1]
                    if in_stock == "OPEN BOX":
                        scripts = soup.find_all("script", {
                            "type": "application/ld+json"})
                        block = next((s.contents[0] for s in scripts if
                                      s.contents and len(
                                          s.contents) and 'lowPrice' in str(
                                          s.contents[0])), None)
                        if block:
                            dc = ast.literal_eval(str(block))
                            price = f"${dc['offers']['lowPrice']}"
                    # notify on slack
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {"text" : f"{sku_name}\n{in_stock}:\n{link}\nprice: {price}\ndate: {date_today.strftime(format)}"}
                    send_to_main_channel(sku_name, body)
                    send_message_to_channel(sku_name, body['text'])
                elif not add_enabled2 and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

def run_amd_bot(skus):
    skus_in_stock = set()
    while True:
        for sku in skus:
            try:
                link = f"https://www.amd.com/en/direct-buy/{sku}/us"
                response = requests.get(link, headers=headers,
                                         timeout=10)
                soup = BeautifulSoup(response.text)
                items = soup.find_all("p", {'class': 'product-out-of-stock'})
                if not len(items) and sku not in skus_in_stock:
                    skus_in_stock.add(sku)
                    item = soup.find("div",
                                     {'class': 'product-page-description'})
                    sku_name = item.h2.string
                    price = item.h4.string
                    # notify on slack
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {"text": f"{sku_name}\nIN STOCK:\n{link}\nprice: {price}\ndate: {date_today.strftime(format)}"}
                    send_to_main_channel(sku_name, body)
                    send_message_to_channel(sku_name, body['text'])
                elif len(items) and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

def run_gs_bot(skus):
    skus_in_stock = set()
    while True:
        for sku in skus:
            try:
                link = f"https://www.gamestop.com/{sku}.html"
                response = requests.get(link, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text)
                btn = soup.find("button",
                                {'class': 'add-to-cart btn btn-primary'})
                info_dict = ast.literal_eval(
                    btn.get_attribute_list("data-gtmdata")[0])
                prod_info = info_dict['productInfo']
                price_info = info_dict['price']
                if prod_info['availability'] != "Not Available" and sku not in skus_in_stock:
                    skus_in_stock.add(sku)
                    # notify on slack
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {"text": f"{prod_info['name']}\nIN STOCK:\n{link}\nprice: ${price_info['sellingPrice']}\ndate: {date_today.strftime(format)}"}
                    send_to_main_channel(prod_info['name'], body)
                    send_message_to_channel(prod_info['name'], body['text'])
                elif prod_info['availability'] == "Not Available" and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

def run_amazon_bot(skus):
    skus_in_stock = set()
    while True:
        for sku in skus:
            try:
                link = f"https://www.amazon.com/dp/{sku}"
                response = requests.get(link, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text)
                btns = soup.find_all('input', {'id': 'add-to-cart-button'})
                buy_box = soup.find("span", {"id": "tabular-buybox-truncate-1"})
                sold_by = buy_box.find("span",
                                       {"class": "tabular-buybox-text"}).text
                if len(btns) and sku not in skus_in_stock and "amazon" in sold_by.lower():
                    skus_in_stock.add(sku)
                    # notify on slack
                    name = soup.find('span',
                                     {'id': 'productTitle'}).text.strip()
                    price = soup.find('span', {
                        'class': 'a-size-medium a-color-price priceBlockBuyingPriceString'}).text.strip()
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {"text": f"{name}\nIN STOCK:\n{link}\nprice: {price}\ndate: {date_today.strftime(format)}"}
                    send_to_main_channel(name, body)
                    send_message_to_channel(name, body['text'])
                elif not len(btns) and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

def run_msi_bot(skus):
    skus_in_stock = set()
    while True:
        for sku in skus:
            try:
                link = f"https://us-store.msi.com/index.php?route=product/product&path=75_76_246&product_id={sku}"
                response = requests.get(link, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text)
                btn = soup.find("button",
                                {'type': 'button',
                                 'id': 'button-cart'})
                if btn and sku not in skus_in_stock:
                    skus_in_stock.add(sku)
                    # notify on slack
                    name = soup.find("h2",
                                      {'class': 'crop-text-1 title'}).text.strip()
                    price = soup.find("span",
                                      {'class': 'prices-new'}).text.strip()
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {"text": f"{name}\nIN STOCK:\n{link}\nprice: {price}\ndate: {date_today.strftime(format)}"}
                    send_to_main_channel(name, body)
                    send_message_to_channel(name, body['text'])
                elif not btn and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

def run_newegg_bot(skus):
    skus_in_stock = set()
    while True:
        for sku in skus:
            try:
                link = f"https://www.newegg.com/p/{sku}?Item={sku}"
                response = requests.get(link, headers=headers,
                                        timeout=10)
                soup = BeautifulSoup(response.text)
                sold_by = soup.find('div',
                                    {'class': 'product-seller'}).find_next(
                    'strong').text
                if sold_by.strip() != "Newegg":
                    continue
                btn = soup.find('button', {'class': 'btn btn-primary btn-wide'})
                notify_btns = soup.find_all('button',
                                     {'class': 'btn btn-secondary btn-wide'})
                if btn and not len(notify_btns) and sku not in skus_in_stock:
                    skus_in_stock.add(sku)
                    # notify on slack
                    name = soup.find('h1',
                                     {'class': 'product-title'}).text.strip()
                    price = soup.find('span', {'class': 'price-current-label'})
                    price = f"${price.find_next('strong').text}{price.find_next('sup').text}"
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {"text": f"{name}\nIN STOCK:\n{link}\nprice: {price}\ndate: {date_today.strftime(format)}"}
                    send_to_main_channel(name, body)
                    send_message_to_channel(name, body['text'])
                elif not btn and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

if __name__ == "__main__":
    list_str = sys.argv[1][1:-1]
    arguments = list_str.split(",")
    site = arguments[0]
    skus = set(arguments[1::])
    if site == "bestbuy":
        run_bb_bot(skus)
    elif site == "amd":
        run_amd_bot(skus)
    elif site == "gamestop":
        run_gs_bot(skus)
    elif site == "amazon":
        run_amazon_bot(skus)
    elif site == "msi":
        run_msi_bot(skus)
    elif site == "newegg":
        run_newegg_bot(skus)
    else:
        print(f"invalid site {site}")