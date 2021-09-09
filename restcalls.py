from bs4 import BeautifulSoup
import requests
import sys
from datetime import datetime, date
import calendar
from pytz import timezone
import pytz
import ast
import time
from slack import WebClient
import re, json
import base64
import string
import random
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5

format = '%m/%d/%Y %I:%M %p'
slack =
headers = {
        'User-Agent': 'PostmanRuntime/7.26.8',
        'Cache-Control': 'no-cache'
    }
slack_headers = {
    'Content-type': 'application/json'
}
channels = {
    'all-drops': 'C022XB5QG5V',
    'rtx-3080': 'C026657SCH5',
    'rtx-3060': 'C026E4EEW3Y',
    'rtx-3070': 'C026E4FG7U6',
    'rtx-3080-ti': 'C026E4J3HTQ',
    'rtx-3070-ti': 'C026LSFU666',
    'rtx-3060-ti': 'C026E5DTLP8',
    'rtx-3090': 'C026M34KMNX',
    'rx-6600-xt': 'C02BB83R06R',
    'rx-6800-xt': 'C026M3A7091',
    'rx-6900-xt': 'C026M3AL30T',
    'rx-6700-xt': 'C026T39G9RA',
    'rx-6800': 'C026T39S02Y',
    'ps5': 'C026T3B93K6',
    'xbox': 'C02CPEHLZEW'
}
client = WebClient(
    token=

def send_message_to_channel(name: str, msg: str, sku=None):
    client.chat_postMessage(channel=channels['all-drops'],
                            text=msg)
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
    elif "6600" in name:
        ch = channels['rx-6600-xt']
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
    elif 'xbox' in name:
        ch = channels['xbox']
    else:
        ch = 'C024LS4LBCJ'
    try:
        client.chat_postMessage(channel=ch,
                                text=msg)
    except Exception as e:
        print(e)
    # send message to kevin
    # if 'bestbuy' in msg:
    #     try:
    #         messages = msg.split('\n')
    #         messages[2] = f"https://api.bestbuy.com/click/5592e2b895800000/{sku}/cart"
    #         messages.append(f"https://api.bestbuy.com/click/-/{sku}/cart")
    #         msg2 = "\n".join(messages)
    #         client.chat_postMessage(channel='U023J95PAUC', text=msg2)
    #     except Exception as e:
    #         print(e)

def send_to_main_channel(body):
    requests.post(slack, headers=slack_headers, json=body, timeout=5)

def run_bb_bot(skus):
    skus_in_stock = set()
    while True:
        for sku in skus:
            try:
                link = f"https://www.bestbuy.com/site/{sku}.p?skuId={sku}"
                response = requests.get(f"{link}", headers=headers, cookies={'locStoreId': '190', 'customerZipCode': '95136|N', 'bby_cbc_lb': 'p-browse-w', 'bby_rdp': 'l', 'pst2': '190|N', 'physical_dma': '807'}, timeout=10)
                soup = BeautifulSoup(response.text)
                btns = soup.find_all("div", {'class':'fulfillment-add-to-cart-button'})
                page_class = BeautifulSoup(str(btns))
                btn_class2 = page_class.find("button")
                add_enabled2 = btn_class2.get_attribute_list("data-button-state") not in ("IN_STORE_ONLY", "SOLD_OUT") and "btn-disabled" not in btn_class2.get_attribute_list(
                    "class") and "Sold Out" not in btn_class2.text
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
                    send_message_to_channel(sku_name, body['text'], sku)
                elif not add_enabled2 and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

def run_amd_bot(skus):
    skus_in_stock = set()
    while True:
        for sku in skus:
            try:
                link = f"https://www.amd.com/en/direct-buy/products/{sku}/us"
                link2 = f"https://www.amd.com/en/direct-buy/{sku}/us"
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
                    body = {"text": f"{sku_name}\nIN STOCK:\n{link2}\nprice: {price}\ndate: {date_today.strftime(format)}"}
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
                if prod_info['availability'] != "Not Available" and sku not in skus_in_stock:
                    skus_in_stock.add(sku)
                    # notify on slack
                    price = str(soup.find("div", {
                        "class": "primary-details-row"}).find("span", {
                        "class": "actual-price"}).text).strip()
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {"text": f"{prod_info['name']}\nIN STOCK:\n{link}\nprice: {price}\ndate: {date_today.strftime(format)}"}
                    send_message_to_channel(prod_info['name'], body['text'])
                elif prod_info['availability'] == "Not Available" and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

def run_amazon_bot(skus):
    skus_in_stock = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55',
        'Cache-Control': 'no-cache'
    }
    while True:
        for sku in skus:
            try:
                link = f"https://www.amazon.com/dp/{sku}"
                response = requests.get(link, headers=headers, cookies={'session-id':''}, timeout=10)
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
                    send_message_to_channel(name, body['text'])
                elif not btn and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

def run_staples_bot(skus):
    skus_in_stock = set()
    while True:
        for sku in skus:
            try:
                link = f"https://www.staples.com/product_{sku}"
                response = requests.get(f"{link}", headers=headers, cookies={'zipcode': '95136', 'geocode': 'geocode=37.3435,-121.8887'}, timeout=5)
                soup = BeautifulSoup(response.text)
                json_data = json.loads(str(
                    soup.find("script", {"id": "__NEXT_DATA__"}).next_element))
                details = \
                json_data['props']['initialStateOrStore']['skuState'][
                    'skuData']['items'][0]
                name = details['product']['name']
                link2 = f"https://www.staples.com/ele-lpd/api/sku/{name.replace(' ', '-').replace('.', '-')}/product_{sku}"
                json_data = requests.get(f"{link2}", headers=headers, cookies={'zipcode': '95136'}, timeout=5).json()
                details = json_data['skuState']['skuData']['items'][0]
                in_stock = details['inventory']['items'][0]['productIsOutOfStock'] != True
                if in_stock and sku not in skus_in_stock:
                    skus_in_stock.add(sku)
                    name = details['product']['name']
                    zip = details['price']['zipCode']
                    price = details['price']['item'][0]['finalPriceText']
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {"text": f"{name}\nIN STOCK {zip}:\n{link}\nprice: {price}\ndate: {date_today.strftime(format)}"}
                    send_message_to_channel(name, body['text'])
                elif not in_stock and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

def run_target_bot(store_ids, sku):
    stores_in_stock = set()
    while True:
        for store_id in store_ids:
            try:
                url1 = "https://redsky.target.com/redsky_aggregations/v1/web/pdp_fulfillment_v1"
                payload1 = {
                    'key': 'ff457966e64d5e877fdbad070f276d18ecec4a01',
                    'tcin': sku,
                    'store_id': store_id,
                    'store_positions_store_id': store_id,
                    'has_store_positions_store_id': True,
                    'scheduled_delivery_store_id': store_id,
                    'pricing_store_id': store_id,
                    'useragent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                    'visitor_id': '0175BD9F28450201A8D13BFDD94CA6D0',
                    'latitude': '37.2701301574707',
                    'longitude': '121.85092163085938',
                    'state': 'CA',
                    'zip': '95136',
                    "has_pricing_store_id": True,
                    "is_bot": False
                }
                jsonData = requests.get(url1, params=payload1).json()
                pickup_available = True if \
                jsonData['data']['product']['fulfillment']['store_options'][0][
                    'order_pickup'][
                    'availability_status'] == "IN_STOCK" else False
                shipping_available = True if \
                jsonData['data']['product']['fulfillment']['shipping_options'][
                    'availability_status'] == "IN_STOCK" else False
                stock_text = ""
                store = jsonData['data']['product']['fulfillment']['store_options'][0]['location_name']
                # print(f"{store}\nin stock: {True if len(stock_text) else False}")
                if pickup_available and shipping_available:
                    stock_text += f"In Store Pickup Or Shipping At {store}"
                elif pickup_available and not shipping_available:
                    stock_text += f"In Store Pickup At {store}"
                elif shipping_available and not pickup_available:
                    stock_text += "Shipping Available"
                if stock_text != "" and store_id not in stores_in_stock:
                    stores_in_stock.add(store_id)
                    url2 = 'https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1'
                    payload2 = {
                        'key': 'ff457966e64d5e877fdbad070f276d18ecec4a01',
                        'tcin': sku,
                        'store': store_id,
                        'pricing_store_id': store_id,
                        'useragent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                        'visitor_id': '0175BD9F28450201A8D13BFDD94CA6D0',
                        'latitude': '37.2701301574707',
                        'longitude': '121.85092163085938',
                        'state': 'CA',
                        'zip': '95136'
                    }
                    jsonData = requests.get(url2, params=payload2).json()
                    name = jsonData['data']['product']['item']['product_description']['title']
                    price = jsonData['data']['product']['price']['formatted_current_price']
                    buy_url = jsonData['data']['product']['item']['enrichment']['buy_url']
                    # notify on slack
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {"text": f"{name}\n{stock_text}:\n{buy_url}\nprice: {price}\ndate: {date_today.strftime(format)}"}
                    send_message_to_channel(name, body['text'])
                elif stock_text == "" and store_id in stores_in_stock:
                    stores_in_stock.remove(store_id)
            except:
                continue

def run_target_bot2(skus):
    stores_in_stock = set()
    while True:
        for sku in skus:
            try:
                url1 = "https://redsky.target.com/redsky_aggregations/v1/web/pdp_fulfillment_v1"
                payload1 = {
                    'key': 'ff457966e64d5e877fdbad070f276d18ecec4a01',
                    'tcin': sku,
                    'store_id': '1927',
                    'store_positions_store_id': '1927',
                    'has_store_positions_store_id': True,
                    'scheduled_delivery_store_id': '1927',
                    'pricing_store_id': '1927',
                    'useragent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                    'visitor_id': '0175BD9F28450201A8D13BFDD94CA6D0',
                    'latitude': '37.2701301574707',
                    'longitude': '121.85092163085938',
                    'state': 'CA',
                    'zip': '95136',
                    "has_pricing_store_id": True,
                    "is_bot": False
                }
                jsonData = requests.get(url1, params=payload1).json()
                pickup_available = True if \
                jsonData['data']['product']['fulfillment']['store_options'][0][
                    'order_pickup'][
                    'availability_status'] == "IN_STOCK" else False
                shipping_available = True if \
                jsonData['data']['product']['fulfillment']['shipping_options'][
                    'availability_status'] == "IN_STOCK" else False
                stock_text = ""
                store = jsonData['data']['product']['fulfillment']['store_options'][0]['location_name']
                # print(f"{store}\nin stock: {True if len(stock_text) else False}")
                if pickup_available and shipping_available:
                    stock_text += f"In Store Pickup Or Shipping At {store}"
                elif pickup_available and not shipping_available:
                    stock_text += f"In Store Pickup At {store}"
                elif shipping_available and not pickup_available:
                    stock_text += "Shipping Available"
                if stock_text != "" and store_id not in stores_in_stock:
                    stores_in_stock.add(store_id)
                    url2 = 'https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1'
                    payload2 = {
                        'key': 'ff457966e64d5e877fdbad070f276d18ecec4a01',
                        'tcin': sku,
                        'store': store_id,
                        'pricing_store_id': store_id,
                        'useragent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                        'visitor_id': '0175BD9F28450201A8D13BFDD94CA6D0',
                        'latitude': '37.2701301574707',
                        'longitude': '121.85092163085938',
                        'state': 'CA',
                        'zip': '95136'
                    }
                    jsonData = requests.get(url2, params=payload2).json()
                    name = jsonData['data']['product']['item']['product_description']['title']
                    price = jsonData['data']['product']['price']['formatted_current_price']
                    buy_url = jsonData['data']['product']['item']['enrichment']['buy_url']
                    # notify on slack
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {"text": f"{name}\n{stock_text}:\n{buy_url}\nprice: {price}\ndate: {date_today.strftime(format)}"}
                    send_message_to_channel(name, body['text'])
                elif stock_text == "" and store_id in stores_in_stock:
                    stores_in_stock.remove(store_id)
            except:
                continue

def run_walmart_bot(skus):
    skus_in_stock = set()
    while True:
        for sku in skus:
            try:
                with open('/home/tstdb2t/privatekey2', 'r') as f:
                    key = RSA.importKey(f.read(), passphrase="happy123")
                consumerId = '3a4784cd-1630-4789-b2ab-3f6d8b655488'
                epoxTime = str(int(time.time() * 1000))
                keyVersion = '1'
                hashDict = {'WM_CONSUMER.ID': consumerId,
                            'WM_CONSUMER.INTIMESTAMP': epoxTime,
                            'WM_SEC.KEY_VERSION': keyVersion
                            }
                sortedHashString = hashDict['WM_CONSUMER.ID'] + '\n' + \
                                   hashDict['WM_CONSUMER.INTIMESTAMP'] + '\n' + \
                                   hashDict['WM_SEC.KEY_VERSION'] + '\n'
                encodedHashString = sortedHashString.encode()
                hasher = SHA256.new(encodedHashString)
                signer = PKCS1_v1_5.new(key)
                signature = signer.sign(hasher)
                signature_enc = str(base64.b64encode(signature), 'utf-8')
                hashDict['WM_SEC.AUTH_SIGNATURE'] = signature_enc
                URL = f'https://developer.api.walmart.com/api-proxy/service/affil/product/v2/items/{sku}'
                response = requests.get(URL, headers=hashDict)
                json_data = response.json()
                in_stock = json_data['sellerInfo'] == "Walmart.com" and \
                           json_data['stock'] == "Available"
                if in_stock and sku not in skus_in_stock:
                    skus_in_stock.add(sku)
                    name = json_data['name']
                    price = f"${json_data['salePrice']}"
                    if price.endswith(".0"):
                        price += "0"
                    link = f"https://walmart.com/ip/{sku}"
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {"text": f"{name}\nIN STOCK:\n{link}\nprice: {price}\ndate: {date_today.strftime(format)}"}
                    send_message_to_channel(name, body['text'])
                elif not in_stock and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

def run_adorama_bot(skus):
    skus_in_stock = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55',
        'Cache-Control': 'no-cache',
    }
    while True:
        for sku in skus:
            try:
                link = f"https://www.adorama.com/api/catalog/GetProductData?sku={sku}"
                headers['cookie'] = '_px2=' + ''.join(
                    random.choice(string.ascii_letters + string.digits) for _
                    in range(100))
                response = requests.get(link, headers=headers,
                                        timeout=10)
                jsonData = response.json()
                in_stock = True if jsonData['data'][sku][
                                       'priceType'] == "Add to Cart" else False
                if in_stock and sku not in skus_in_stock:
                    skus_in_stock.add(sku)
                    link2 = jsonData['data'][sku]['link']
                    name = jsonData['data'][sku]['shortTitle']
                    price = f"${jsonData['data'][sku]['prices']['price']}"
                    if price.endswith(".0"):
                        price += "0"
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {
                        "text": f"{name}\nIN STOCK:\n{link2}\nprice: {price}\ndate: {date_today.strftime(format)}"}
                    send_message_to_channel(name, body['text'])
                elif not in_stock and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

def run_bhphoto_bot(skus):
    skus_in_stock = set()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55',
        'Cache-Control': 'no-cache',
        'cookie': '_px3=30a3d00ead084a4704e24a54a5b4181257041413b5723265159ed3f56160998c:Mm8qSl4/xzPbBjETeVXF9Kdo+3LB+j+6+fhr6hpCY1+QCYF4VKG6wU0xV3M1HO9QQvLCdIW8VXUASCSUQHyaXA==:1000:Ce9I1hvcDPNLuJgFJXsTSC0JOhwZpf55QFtuRI8jt/q/8wAUxIJ2qOvvucrLXrtfu4e2cGSHgBz6PgZHvYzU7wvrgbx8bcwjpEB+zl5q+XXKXTOCB+nKmRWBk2n16774sVMjGpW5Y/PrdSgAEmC9S4W+Gd+t5kXJHPGDmbUxVrgwSSZTsUyZ89/uOt19kCuXhNKrS4RknkJuYbnhDDZDsg=='
    }
    while True:
        for sku in skus:
            try:
                link = "https://www.bhphotovideo.com/api/item/p/product-details"
                data = {"params": {
                    "itemList": [{"skuNo": sku, "itemSource": "REG"}],
                    "channels": ["priceInfo"], "channelParams": {"priceInfo": {
                        "PRICING_CONTEXT": "DETAILS_CART_LAYER"}}}}
                response = requests.post(link, headers=headers, json=data,
                                          timeout=10)
                json_data = response.json()['data'][0]
                in_stock = True if json_data['priceInfo'][
                    'addToCartFunction'] else False
                if in_stock and sku not in skus_in_stock:
                    skus_in_stock.add(sku)
                    link2 = json_data['core']['bitlyUrl']
                    name = json_data['core']['shortDescription']
                    price = f"${json_data['priceInfo']['price']}"
                    if price.endswith(".0"):
                        price += "0"
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    body = {
                        "text": f"{name}\nIN STOCK:\n{link2}\nprice: {price}\ndate: {date_today.strftime(format)}"}
                    send_message_to_channel(name, body['text'])
                elif not in_stock and sku in skus_in_stock:
                    skus_in_stock.remove(sku)
            except:
                continue

def run_amd_queue_bot():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55',
        'Cache-Control': 'no-cache'
    }
    already_started = False
    while True:
        try:
            if calendar.day_name[date.today().weekday()] == "Thursday":
                link = "https://inline.amd.com/afterevent.aspx?c=amd&e=us0812h9m1er7x&t=https%3A%2F%2Fwww.amd.com%2Fen%2Fdirect-buy&cid=en-US"
                response = requests.get(link, headers=headers,
                                        timeout=10)
                if response.status_code != 200:
                    queue_started = True
                else:
                    soup = BeautifulSoup(response.text)
                    direct_buy = soup.find('body', {'class': 'path-direct-buy'})
                    if not direct_buy:
                        queue_started = True
                    else:
                        queue_started = False
                if queue_started and not already_started:
                    already_started = True
                    link2 = "https://www.amd.com/en/direct-buy/us"
                    date_today = datetime.now(tz=pytz.utc)
                    date_today = date_today.astimezone(timezone('US/Pacific'))
                    start_time = soup.find('span', {'id': 'MainPart_lbEventStartTime'}).text
                    zone = soup.find('span', {'id': 'MainPart_lbEventStartTimeTimeZonePostfix'}).text
                    msg = f"AMD queue starts at {start_time} {zone}, queue up now!\n{link2}\ndate: {date_today.strftime(format)}"
                    client.chat_postMessage(channel='C02CELT8CJU', text=msg)
                elif not queue_started and already_started:
                    already_started = False
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
    elif site == "staples":
        run_staples_bot(skus)
    elif site == "tgt_disc":
        run_target_bot(skus, '81114595')
    elif site == "tgt_digital":
        run_target_bot(skus, '81114596')
    elif site == "tgt":
        run_target_bot2(skus)
    elif site == "walmart":
        run_walmart_bot(skus)
    elif site == "adorama":
        run_adorama_bot(skus)
    elif site == "bhphoto":
        run_bhphoto_bot(skus)
    elif site == "amd_queue":
        run_amd_queue_bot()
    else:
        print(f"invalid site {site}")