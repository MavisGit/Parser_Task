import requests
from bs4 import BeautifulSoup
from time import sleep
import csv

from function_lib_agent import get_agent


headers = {
    "Accept": "*/*",
    "User-agent": get_agent(),
    }

home_url = "https://himbio.ru/catalog/steklo_borosil/"
cookies = {
        "_ym_debug": "null",
        "beget": "begetok",
        "BITRIX_CONVERSION_CONTEXT_s1": '{"ID":3,"EXPIRE":1691441940,"UNIQUE":["conversion_visit_day"]}',
        "BITRIX_SM_SALE_UID": "053617dddf18fa542e2a9d0e0acc3dbd",
        "PHPSESSID": "771913a6c94b7723304da2a5934833d7",
           }


def get_url_group():

    url_list = {}

    respons = requests.get(home_url, cookies=cookies, headers=headers)

    soup = BeautifulSoup(respons.text, "lxml")

    data = soup.find("div", class_="articles-list sections wrap_md")
    groups = data.find_all("div", class_="item iblock section_item_inner")
    for group in groups:

        url = "https://himbio.ru" + group.find("div", class_="item-title").find("a").get("href")
        name_group = group.find("div", class_="item-title").find("span").text
        print(name_group, url, "\n")

        url_list[url] = name_group

        with open("data/csv/group_url.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    name_group,
                    url,
                ]
            )

    return url_list


def get_info(url_page, cookies, headers, name_group):
    response_page = requests.get(url_page, cookies=cookies, headers=headers)

    soup_page = BeautifulSoup(response_page.text, "lxml")

    data_page = soup_page.find("div", class_="ajax_load block").find("div", class_="top_wrapper")

    if data_page is not None:

        catalog_items = data_page.find_all("div", class_="catalog_item_wrapp")
        print(len(catalog_items))
        count = 1
        for item in catalog_items:
            sleep(1)
            print("Обработка товара...")
            img_url = "https://himbio.ru" + item.find("div", class_="image_wrapper_block").find("img").get("src")
            item_info = item.find("div", class_="item_info TYPE_1")
            item_url = "https://himbio.ru" + item_info.find("a").get("href")

            response_item = requests.get(item_url, cookies=cookies, headers=headers)

            soup_item = BeautifulSoup(response_item.text, "lxml")

            data_item = soup_item.find("div", class_="container")

            artikul_item = data_item.find("div", class_="article iblock").find("span", class_="value").text
            name_item = data_item.find("h1").text

            description = data_item.find("ul", class_="tabs_content tabs-body")
            detail = description.find("div", class_="detail_text")
            manufacturer_name = description.find("td", class_="char_value")
            price = data_item.find("div", class_="price")

            if price is None:
                price = "Нет информации о цене"
            else:
                price = price.text

            if detail is None:
                detail = "Нет описания данного товара"
            else:
                detail = detail.text

            if manufacturer_name is None:
                manufacturer_name = "Нет информации о производителе"
            else:
                manufacturer_name = manufacturer_name.text

            with open(f"data/csv/items_card/{artikul_item}.csv", "w", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(
                        [
                            "Название товора",
                            "Ссылка",
                            "Артикул",
                            "Описание",
                            "Производитель",
                            "Цена",
                            "Изображение",
                        ]
                            )

                writer.writerow(
                    [
                        name_item.strip(),
                        item_url.strip(),
                        artikul_item.strip(),
                        detail,
                        manufacturer_name.strip(),
                        price.strip(),
                        img_url,
                    ]
                )
            with open("data/csv/all_item.csv", "a", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                        str(name_group).strip(),
                        name_item.strip(),
                        img_url,
                        artikul_item.strip(),
                        detail,
                        manufacturer_name.strip(),
                        ])
            img_bytes = requests.get(img_url).content

            with open(f"data/img/{artikul_item}.png", "wb") as file:
                file.write(img_bytes)
            print(f"Осталось обработать: {len(catalog_items) - count}...")
            count += 1
    else:
        with open("data/csv/all_item.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                    str(name_group).strip(),
                    "Раздел пуст",
                    "Раздел пуст",
                    "Раздел пуст",
                    "Раздел пуст",
                    "Раздел пуст",
                    ])


groups = get_url_group()

for group_url in groups:

    print(group_url)
    name_group = groups[group_url]
    print(name_group)
    response = requests.get(group_url, cookies=cookies, headers=headers)

    soup = BeautifulSoup(response.text, "lxml")

    page_data = soup.find("span", class_="nums")

    if page_data is not None:

        page_num = page_data.find_all("a")

        page = int(page_num[-1].text)

        for num_page in range(1, page+1):

            print(f"Обработка листа номер {num_page}...")
            url_page = group_url + f"?PAGEN_1={num_page}"

            get_info(url_page, cookies, headers, name_group)

    else:

        get_info(group_url, cookies, headers, name_group)
