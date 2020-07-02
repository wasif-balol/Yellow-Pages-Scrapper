from requests import get
from bs4 import BeautifulSoup
import csv
import random
import requests
from lxml.html import fromstring

rows = []
categories = ['autorepair', 'delivery', 'reservations', 'burgers', 'italian', 'takeout', 'waitlist', 'chinese',
              'mexican',
              'contractors', 'electricians', 'homecleaning', 'hvac', 'landscaping', 'locksmiths', 'movers', 'plumbing',
              'auto_detailing', 'bodyshops', 'carwash', 'car_dealers', 'oilchange', 'parking', 'towing',
              ]


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = list()
    for i in parser.xpath('//tbody/tr')[:35]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.append(proxy)
    return proxies


proxies = get_proxies()

try:
    for category in categories:
        response = ''
        print("scraping category: " + category)
        file = open(category + ".csv", 'a', encoding="utf-8")
        writer = csv.writer(file)
        # appending first row for column names
        rows.append(
            ['Title', 'About_business', 'Address', 'Site', 'Contact_number', 'Amenities', "Tags", 'Working_hours',
             'QnA'])

        main_page_url = 'https://www.yelp.com/search?find_desc=' + category + '&find_loc=New+York%2C+NY%2C+US'
        while True:
            try:
                proxy_index = random.randint(0, len(proxies) - 1)
                proxy = {"http": proxies[proxy_index], "https": proxies[proxy_index]}
                response = get(main_page_url)
                if response.status_code == 200:
                    break
                elif response.status_code != 200:
                    response = get(main_page_url, proxies=proxy, timeout=10)
                    if response.status_code == 200:
                        break
            except Exception as e:
                print("Blocked on category: " + category)
                print("retrying with Proxy: " + str(proxy))
                continue
        Main_Page = BeautifulSoup(response.text, 'html.parser')
        # loop for 20 pages per category
        for i in range(0, 20):
            print("on page: " + str(i))
            if i == 0:  # passing first iteration because we first scrap the current page
                pass
            else:  # changing the main_page_url and navigation to next page
                pagination = Main_Page.find("div", {
                    "class": "lemon--div__373c0__1mboc pagination-links__373c0"
                             "__3CXzO border-color--default__373c0__3-ifU nowrap__373c0__35McF"})
                link = pagination.find('a', {
                    "class": "lemon--a__373c0__IEZFH link__373c0__1G70M next-link navigation-button"
                             "__373c0__23BAT link-color--inherit__373c0__3dzpk link-size--inherit__373c0__1VFlE"})
                main_page_url = "https://www.yelp.com" + str(link['href'])
                while True:
                    try:
                        proxy_index = random.randint(0, len(proxies) - 1)
                        proxy = {"http": proxies[proxy_index], "https": proxies[proxy_index]}
                        response = get(main_page_url)
                        if response.status_code == 200:
                            break
                        elif response.status_code != 200:
                            response = get(main_page_url, proxies=proxy)
                            if response.status_code == 200:
                                break
                    except:
                        continue
                Main_Page = BeautifulSoup(response.text, 'html.parser')
            All_items = Main_Page.find_all("div", {
                "class": "lemon--div__373c0__1mboc container__373c0__3HMKB hoverable__373c0__VqkG7 margin-t3__373c0__1l90z margin-b3__373c0__q1DuY padding-t3__373c0__1gw9E padding-r3__373c0__57InZ padding-b3__373c0__342DA padding-l3__373c0__1scQ0 border--top__373c0__3gXLy border--right__373c0__1n3Iv border--bottom__373c0__3qNtD border--left__373c0__d1B7K border-color--default__373c0__3-ifU"})
            for item in All_items:
                # added try catch because if the single items fails due to any
                # reason then the whole execution will continue
                try:

                    if All_items.index(item) > 0:
                        Item_url = "https://www.yelp.com" + item.a["href"]
                        while True:
                            try:
                                proxy_index = random.randint(0, len(proxies) - 1)
                                proxy = {"http": proxies[proxy_index], "https": proxies[proxy_index]}
                                response2 = get(Item_url)
                                if response2.status_code == 200:
                                    break
                                elif response2.status_code != 200:
                                    response2 = get(main_page_url, proxies=proxy)
                                    if response2.status_code == 200:
                                        break
                            except:
                                continue
                        tags = ''
                        Single_item_page = BeautifulSoup(response2.text, 'html.parser')
                        print("fetching tags")
                        tags_div = Single_item_page.findAll("a", {
                            "class": "lemon--a__373c0__IEZFH link__373c0__29943 link-color--inherit__373c0__15ymx link-size--inherit__373c0__2JXk5"})
                        for j in range(4):
                            if tags_div[j].text == "Elite '2020" or tags_div[j].text == "Get free quotes on Yelp now":
                                continue
                            elif j == 3:
                                tags += tags_div[j].text
                            else:
                                tags += tags_div[j].text + ", "

                        print("Fetching Title")
                        title = Single_item_page.find("h1", {
                            "class": "lemon--h1__373c0__2ZHSL heading--h1__373c0__1VUMO heading--no-spacing__373c0__"
                                     "1PzQP heading--inline__373c0__1F-Z6"}).text
                        info = Single_item_page.find("div", {
                            "class": "lemon--div__373c0__1mboc island__373c0__3fs6U u-padding-t1 u-padding-r1 u-padding"
                                     "-b1 u-padding-l1 border--top__373c0__19Owr border--right__373c0__22AHO border"
                                     "--bottom__373c0__uPbXS border--left__373c0__1SjJs border-color"
                                     "--default__373c0__2oFDT background-color--white__373c0__GVEnp"})
                        # checking if site contains a website and assigning empty if not
                        try:
                            print("Fetching website")
                            site = info.a.text
                            if "." in site:
                                pass
                            else:
                                site = title + "'s site is not listed."
                        except Exception as e:
                            site = ''
                            pass
                        print("Fetching Contact Number")
                        contact_number = info.find("p", {
                            "class": "lemon--p__373c0__3Qnnj text__373c0__2pB8f text-color--normal"
                                     "__373c0__K_MKN text-align--left__373c0__2pnx_"}).text
                        try:
                            print("Fetching Business")
                            business = Single_item_page.findAll("section", {
                                "class": "lemon--section__373c0__fNwDM u-space-t4 u-padding-t4 border--top"
                                         "__373c0__19Owr border-color--default__373c0__2oFDT"})
                            business = business[3]
                            business = business.findAll("span")
                            b1 = business[0].text
                            b2 = business[1].text
                            about_bus = str(b1) + str(b2)
                            if "users haven’t asked any questions yet" in about_bus:
                                about_bus = ''
                                pass
                        except Exception as e:
                            about_business = title + "'s is not listed."
                            pass
                        try:
                            print("Fetching Question and Answers")
                            qna = Single_item_page.findAll("section", {
                                "class": "lemon--section__373c0__fNwDM u-space-t4 u-padding-t4 border--top"
                                         "__373c0__19Owr border-color--default__373c0__2oFDT"})
                            QnA_Cat = qna[4].div.ul.findAll("div", {
                                "class": "lemon--div__373c0__1mboc arrange-unit__373c0__1piwO arrange-unit-fill__373c0"
                                         "__17z0h border-color--default__373c0__2oFDT"})

                            q1 = QnA_Cat[0].text
                            a1 = QnA_Cat[1].text
                            q2 = QnA_Cat[2].text
                            a2 = QnA_Cat[3].text
                            QnA = {"Q1 : ": q1, "A1 : ": a1, "Q2 : ": q2, "A2 : ": a2}
                        except Exception as e:
                            QnA = "Community haven't asked any questions about " + title + " yet."
                            pass
                        # fetching whole amenities card
                        try:
                            Amenities_card = Single_item_page.find('div', {
                                "class": "lemon--div__373c0__1mboc arrange__373c0__UHqhV gutter-12__373c0"
                                         "__3kguh layout-wrap__373c0__34d4b layout-2-units__373c0__3CiAk border-color"
                                         "--default__373c0__2oFDT"})
                            amneties = {}
                            for amnety in Amenities_card:
                                # fetching each amenity div
                                data = amnety.find('div', {
                                    'class': 'lemon--div__373c0__1mboc arrange-unit__373c0__1piwO arrange-unit-fill'
                                             '__373c0__17z0h border-color--default__373c0__2oFDT'}).contents
                                for text in data:
                                    # iterating through all available amenities and making a dictionary name
                                    # amenities with key and values
                                    # passing on P element because it contain details of amenity nor key,value
                                    if text.name == 'p':
                                        pass
                                    elif data.index(text) % 2 == 0:
                                        key = text.text
                                    else:
                                        value = text.text
                                amneties[key] = value
                        except Exception as e:
                            amneties = {}
                            pass
                        try:
                            # fetching a whole container containing address and working hours and then separating both
                            detail_container = Single_item_page.find("div", {
                                "class": "lemon--div__373c0__1mboc arrange__373c0__UHqhV gutter-30"
                                         "__373c0__2PiuS border-color--default__373c0__2oFDT"})
                            address = detail_container.find('address',
                                                            {"class": "lemon--address__373c0__2sPac"}).text

                            working_hours_table = detail_container.find('tbody', {
                                "class": "lemon--tbody__373c0__2T6Pl"})
                            working_days_and_hours = {}
                            for single_day in working_hours_table:
                                days = single_day.find('th', {
                                    "class": "lemon--th__373c0__2EYOe table-header-cell__373c0__3vHHa table-header-cell"
                                             "__373c0___pz7p"}).p.text
                                hours_component = single_day.find('td', {
                                    "class": "lemon--td__373c0__gBfiC table-cell__373c0__HrAej table-cell"
                                             "__373c0__2eOj9 table-cell--top__373c0__2WIt-"})
                                hours = hours_component.find('ul', {
                                    "class": "lemon--ul__373c0__1_cxs undefined list__373c0__2G8oH"}).text
                                # Making a dictionary for all week days and hours
                                working_days_and_hours[days] = hours
                            # appending all values in a list name rows to write in csv at once
                        except Exception as e:
                            working_days_and_hours = {}
                            address = ''
                            pass
                        rows.append(
                            [title, about_bus, address, site, contact_number, amneties, tags, working_days_and_hours,
                             QnA])
                    else:
                        pass
                except Exception as e:
                    print(e.__str__())
                    pass
            writer.writerows(rows)
            rows.clear()
except Exception as e:
    print(e.__str__())
