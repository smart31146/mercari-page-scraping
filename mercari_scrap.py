#! /usr/bin/env python3
import time
import datetime
import csv
import subprocess
from subprocess import PIPE
from time import sleep
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
#日付
dt = datetime.datetime.now()
today = dt.strftime("%Y%m%d%H%M")

#商品タイトルの行末に付けるキーワードを指定
tail_item_name = "【出荷まで平均1～3日】"  
#メルカリの何倍の価格設定にするか default = 2.5
org_price = 2.5
#Amazon最低出品価格 default = 3000
Amazon_price_low = 3000
#リサーチ対象とする最低メルカリ販売額を指定 default = 3000
mercari_price_min = 5000
#リサーチ対象とする最高メルカリ販売額を指定 default = 80000
mercari_price_max = 80000
#除外キーワードを指定
jogai1 = "メルカリ"
jogai2 = "専用"
jogai3 = "特設"
jogai4 = "匿名"
#リサーチ対象とするカテゴリーIDを指定
category_id = 1328
#主なカテゴリー
#id=1328   おもちゃ・ホビー・グッズ
#id=1      レディース(服)
#id=2      メンズ(服)
#id=5      本・音楽・ゲーム
#id=6      コスメ・香水・美容
#id=9      ハンドメイド

# Chromeオプション
options = Options()
options.add_argument("start-maximized")
options.add_argument("--headless=new")
options.add_argument('ignoreHTTPSErrors')

#CSV作成
with open(today+'_mercari_'+str(category_id)+'.csv', 'w', newline="", encoding='utf_8_sig') as f:
    writer = csv.writer(f)
    writer.writerow(["1.商品タイプ",
            "2.出品者SKU",
            "3.ブランド名",
            "4.商品タイトル",
            "5.商品コード",
            "6.商品コードのタイプ",
            "7.メーカー名",
            "8.推奨ブラウズノード",
            "9.アダルド商品",
            "10.在庫数",
            "11.価格",
            "12.商品画像URL",
            "13.対象性別",
            "14.メーカー型番",
            "15.商品説明",
            "16.メルカリページ"])
f.close()

try:
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
  
    #カテゴリページの何ページ目までスクレイピングするか
    for page in range(60): #ページ指定 MAX100
       
        
        p = page
        # メルカリURL カテゴリ=おもちゃ・ホビー・グッズ 商品状態=新品、未使用 最低価格= 3000 最高価格=80000 販売状況=販売中 並び順=新しい順
        url = "https://jp.mercari.com/search?order=desc&sort=created_time&category_id=" + str(category_id) + "&price_min=" + str(mercari_price_min) + "&item_condition_id=1&price_max=" + str(mercari_price_max) + "&status=on_sale" + "&exclude_keyword=" + jogai1 + "%20" +  jogai2 + "%20" + jogai3 + "%20" + jogai4 + "&page_token=v1%3A" + str(p)#ソートの種類で取得できる件数が変わる、新しい順・おすすめ順推奨
        print(url)
        driver.get(url)
        prev_height = -1
        max_scrolls = 50
        scroll_count = 0
        time.sleep(5)
        lastHeight = 300
        print("height", lastHeight)
        while scroll_count < max_scrolls:
            driver.execute_script(f"window.scrollBy(0, {lastHeight});")
            time.sleep(2)  # give some time for new results to load
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height <= lastHeight:
                break
            lastHeight = lastHeight+300
            scroll_count += 1
        
        time.sleep(5)
        #csv書き込み
        with open(today+'_mercari_'+str(category_id)+'.csv', 'a', newline="", encoding='UTF-8') as f:
            writer = csv.writer(f)
            elements = driver.find_element(By.XPATH,'//*[@id="item-grid"]/ul').find_elements(By.TAG_NAME,'li')
            for j, element in enumerate(elements):
                #商品タイプ feed_product_type
                feed_product_type = "hobbies"
                #出品者SKU item_sku
                skuToday = datetime.datetime.now().strftime('%Y%m%d')
                item_sku = str(skuToday) + "-" + str(random.randint(100000, 999999)) + "-" + str(category_id)
                #ブランド名 brand_name
                brand_name = "ノーブランド品"
                #商品タイトル item_name
                # item_name = element.find_elements(By.CLASS_NAME,'merItemThumbnail')[0].find_elements(By.CSS_SELECTOR, 'span[data-testid:"thumbnail-item-name"]')[0].text+ tail_item_name
                item_name = element.find_elements(By.CLASS_NAME,'merItemThumbnail')[0].get_attribute('aria-label')
                
                # find_elements(By.TAG_NAME,'img')[0].get_attribute('alt') + tail_item_name
                
                if "メルカリ" in item_name or "専用" in item_name or "特設" in item_name:
                    continue
                
                #商品コード external_product_id
                external_product_id = ""
                #商品コードのタイプ external_product_id_type
                external_product_id_type = ""
                #メーカー名 manufacturer
                manufacturer = "ノーブランド"
                #推奨ブラウズノード recommended_browse_nodes
                recommended_browse_nodes = "2277722051"
                #アダルド商品 is_adult_product
                is_adult_product = "いいえ"
                #在庫数 quantity
                quantity = "1"
                #価格 standard_price value = value.replace(',', '')
                standard_price_text=element.find_elements(By.CLASS_NAME,'merItemThumbnail')[0].find_elements(By.CLASS_NAME,'merPrice')[0].find_elements(By.TAG_NAME,'span')[1].text+'円'
                standard_price = (float((element.find_elements(By.CLASS_NAME,'merItemThumbnail')[0].find_elements(By.CLASS_NAME,'merPrice')[0].find_elements(By.TAG_NAME,'span')[1].text).replace(',', '')))
                item_name = element.find_elements(By.CLASS_NAME,'merItemThumbnail')[0].get_attribute('aria-label').replace(standard_price_text,'').replace('の画像 ','')
                if standard_price < 20000:
                    standard_price = standard_price * org_price
                elif standard_price >= 20000:
                    standard_price = standard_price * (org_price - 0.5)
                elif standard_price < Amazon_price_low:
                    standard_price = Amazon_price_low
                #商品画像URL main_image_url
                main_image_url = element.find_elements(By.CLASS_NAME,'merItemThumbnail')[0].find_elements(By.TAG_NAME,'img')[0].get_attribute('src')
                main_image_url = main_image_url.replace("c!/w=240/thumb", "item/detail/orig")
                #対象性別 target_gender
                target_gender = "unisex"
                #商品のサブ画像URL1 other_image_url1
                # other_image_url1 = main_image_url.replace("1.jpg?", "2.jpg?")
                #商品のサブ画像URL2 other_image_url2
                # other_image_url2 = main_image_url.replace("1.jpg?", "3.jpg?")
                #商品のサブ画像URL3 other_image_url3
                # other_image_url3 = main_image_url.replace("1.jpg?", "4.jpg?")
                #商品のサブ画像URL4 other_image_url4
                # other_image_url4 = main_image_url.replace("1.jpg?", "5.jpg?")
                #メーカー型番 part_number
                part_number = item_sku
                #商品説明 product_description
                product_description = "全国送料無料 新品の商品です。店舗でも販売しておりますので、在庫切れの場合はキャンセルさせていただく場合があります。セットものは別々に届く場合があります。お届けまでに1週間ｰ10日ほどかかる場合がございますので、ご了承願います。"
                #参照用→ blank
                blank = " "
                #メルカリページ mercari_page
                mercari_page = element.find_elements(By.TAG_NAME,'a')[0].get_attribute('href')
                print(mercari_page)
                print("num:", j)
                writer.writerow([
                    feed_product_type,
                    item_sku,         
                    brand_name,       
                    item_name,        
                    external_product_id, 
                    external_product_id_type, 
                    manufacturer,           
                    recommended_browse_nodes,           
                    is_adult_product,
                    quantity,
                    standard_price,
                    main_image_url,
                    target_gender,
                    # other_image_url1,
                    # other_image_url2,
                    # other_image_url3,
                    # other_image_url4,
                    part_number,
                    product_description,
                    # blank,
                    mercari_page
                ])

        f.close()

    else:
        print('スクレイピング完了')
            
except Exception as e:
    print(e)
    print("エラーが発生しました。")
    if driver is not None:
        driver.close()
        driver.quit()
finally:
    print('good bye')