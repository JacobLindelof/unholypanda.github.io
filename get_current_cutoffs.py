import json
import time
import datetime
import random

from incapsula import IncapSession
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def get_cutoff_for_rank(rank_cutoff):
    leagues_hightscores_url = "https://secure.runescape.com/m=hiscore_oldschool_seasonal/overall?category_type=1&table=0&page="
    page = int(rank_cutoff / 25) + 1

    options = Options()
    options.add_argument("window-size=1400,600")
    requests = webdriver.Chrome('./chromedriver')
    ua = UserAgent()
    a = ua.random
    user_agent = ua.random
    options.add_argument(f'user-agent={user_agent}')
    requests.get(leagues_hightscores_url + str(page))
    soup = BeautifulSoup(requests.page_source, 'html.parser')
    requests.quit()
        
    print(f"Rank Cutoff: {rank_cutoff} | Page: {page}")
    scores = soup.find_all("tr")
    
    for score in scores[2:]:
        columns = score.find_all('td')
        rank = int(columns[0].text.strip().replace(',', ''))
        points = int(columns[2].text.strip().replace(',', ''))

        print(rank)
        if rank == rank_cutoff:
            print("Found Cutoff")
            return points
        
    time.sleep(random.random())

def generate_chart_data(cutoff_data):
    start_date = datetime.datetime.strptime(list(cutoff_data)[0], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(list(cutoff_data)[-1], '%Y-%m-%d')

    date = start_date
    date_list = []
    while date <= end_date:
        date_list.append(date) 
        date += datetime.timedelta(days=1)

    datasets = {
        'iron': {
            "label": 'Iron',
            "fill": False,
            "backgroundColor": 'rgb(125, 117, 117)',
            "borderColor": 'rgb(125, 117, 117)',
            "data": []
        },
        'steel': {
            "label": 'Steel',
            "fill": False,
            "backgroundColor": 'rgb(170, 157, 157)',
            "borderColor": 'rgb(170, 157, 157)',
            "data": []
        },
        'mithril': {
            "label": 'Mithril',
            "fill": False,
            "backgroundColor": 'rgb(62, 62, 92)',
            "borderColor": 'rgb(62, 62, 92)',
            "data": []
        },
        'adamant': {
            "label": 'Adamant',
            "fill": False,
            "backgroundColor": 'rgb(67, 85, 67)',
            "borderColor": 'rgb(67, 85, 67)',
            "data": []
        },
        'rune': {
            "label": 'Rune',
            "fill": False,
            "backgroundColor": 'rgb(63, 85, 93)',
            "borderColor": 'rgb(63, 85, 93)',
            "data": []
        },
        'dragon': {
            "label": 'Dragon',
            "fill": False,
            "backgroundColor": 'rgb(91, 17, 9)',
            "borderColor": 'rgb(91, 17, 9)',
            "data": []
        },
    }

    labels = []
    for date in date_list:
        print(date)
        date_string = date.strftime('%Y-%m-%d')
        labels.append(date_string)
        if date_string in cutoff_data.keys():
            datasets['iron']['data'].append(cutoff_data[date_string]['iron'])
            datasets['steel']['data'].append(cutoff_data[date_string]['steel'])
            datasets['mithril']['data'].append(cutoff_data[date_string]['mithril'])
            datasets['adamant']['data'].append(cutoff_data[date_string]['adamant'])
            datasets['rune']['data'].append(cutoff_data[date_string]['rune'])
            datasets['dragon']['data'].append(cutoff_data[date_string]['dragon'])
        else:
            datasets['iron']['data'].append(None)
            datasets['steel']['data'].append(None)
            datasets['mithril']['data'].append(None)
            datasets['adamant']['data'].append(None)
            datasets['rune']['data'].append(None)
            datasets['dragon']['data'].append(None)

    date += datetime.timedelta(days=1)
    league_end_date = datetime.datetime(2021, 1, 6)
    while date <= league_end_date:
        labels.append(date.strftime('%Y-%m-%d')) 
        date += datetime.timedelta(days=1)

    
    open('data.json', 'w').write(json.dumps({
        "labels": labels,
        "datasets": list(datasets.values())
    }))


def get_current_cutoffs():
    requests = webdriver.Chrome('./chromedriver')

    try:
        last_page = open('last_page.txt', 'r').read()
    except FileNotFoundError:
        last_page = open('last_page.txt', 'w')
        last_page.write("9000")
        last_page.close()
        last_page = open('last_page.txt', 'r').read()
    
    last_page = int(last_page)

    leagues_hightscores_url = "https://secure.runescape.com/m=hiscore_oldschool_seasonal/overall?category_type=1&table=0&page="
    
    on_last_page = False
    bronze_cutoff = None

    increment = True
    increment_amount = 500
    outside = False

    while not on_last_page:
        print(last_page)


        options = Options()
        options.add_argument("window-size=1400,600")
        requests = webdriver.Chrome('./chromedriver')
        ua = UserAgent()
        a = ua.random
        user_agent = ua.random
        options.add_argument(f'user-agent={user_agent}')
        requests.get(leagues_hightscores_url + str(last_page))
        soup = BeautifulSoup(requests.page_source, 'html.parser')
        requests.quit()

        scores = soup.find_all("tr")

        first = scores[2].find_all('td')
        last = scores[-1].find_all('td')
        
        first_rank = int(first[0].text.strip().replace(',', ''))
        last_rank = int(last[0].text.strip().replace(',', ''))

        first_points = int(first[2].text.strip().replace(',', ''))
        last_points = int(last[2].text.strip().replace(',', ''))

        print(f"First Rank: {first_rank} | First Points: {first_points}")
        print(f"Last Rank: {last_rank} | Last Points: {last_points}")

        if len(scores) != 27:
            on_last_page = True
            bronze_cutoff = last_rank

        elif increment_amount > 0:
            print(f"First Rank: {first_rank}")
            if first_rank != 1:
                if outside:
                    increment_amount = int(increment_amount / 2)
                last_page += increment_amount
            else:
                outside = True
                increment_amount = int(increment_amount / 2)
                last_page -= increment_amount    
        
        else:
            if first_rank != 1:
                last_page += 1
            else:
                last_page -= 1

        time.sleep(random.random())

    try:
        cutoffs = json.loads(open("cutoffs.json", 'r').read())
    except FileNotFoundError:
        cutoffs = open('cutoffs.json', 'w')

        starter_data = {
            '2020-10-28': {
                "date": '2020-10-28',
                "iron": 0,
                "steel": 0,
                "mithril": 0,
                "adamant": 0,
                "rune": 0,
                "dragon": 0,
            },
            '2020-10-30':{
                "date": '2020-10-30',
                "iron": 510,
                "steel": 1370,
                "mithril": 2880,
                "adamant": 5300,
                "rune": 9850,
                "dragon": 15510,
            },
            '2020-11-06':{
                "date": '2020-11-06',
                "iron": 530,
                "steel": 1730,
                "mithril": 4480,
                "adamant": 9010,
                "rune": 18340,
                "dragon": 25270,
            }
        }

        cutoffs.write(json.dumps(starter_data))
        cutoffs.close()
        cutoffs = json.loads(open('cutoffs.json', 'r').read())
    
    iron_rank_cutoff = int(bronze_cutoff * .8)
    steel_rank_cutoff = int(bronze_cutoff * .6)
    mithril_rank_cutoff = int(bronze_cutoff * .4)
    adamant_rank_cutoff = int(bronze_cutoff * .2)
    rune_rank_cutoff = int(bronze_cutoff * .05)
    dragon_rank_cutoff = int(bronze_cutoff * .01)

    iron_rank_point_cutoff = get_cutoff_for_rank(iron_rank_cutoff)
    steel_rank_point_cutoff = get_cutoff_for_rank(steel_rank_cutoff)
    mithril_rank_point_cutoff = get_cutoff_for_rank(mithril_rank_cutoff)
    adamant_rank_point_cutoff = get_cutoff_for_rank(adamant_rank_cutoff)
    rune_rank_point_cutoff = get_cutoff_for_rank(rune_rank_cutoff)
    dragon_rank_point_cutoff = get_cutoff_for_rank(dragon_rank_cutoff)

    cutoffs[datetime.datetime.today().date().strftime("%Y-%m-%d")] = {
        "date": datetime.datetime.today().date().strftime("%Y-%m-%d"),
        "iron": iron_rank_point_cutoff,
        "steel": steel_rank_point_cutoff,
        "mithril": mithril_rank_point_cutoff,
        "adamant": adamant_rank_point_cutoff,
        "rune": rune_rank_point_cutoff,
        "dragon": dragon_rank_point_cutoff,
    }

    new_cutoffs = open('cutoffs.json', 'w').write(json.dumps(cutoffs))

    generate_chart_data(cutoffs)

if __name__ == "__main__":
    get_current_cutoffs()