import requests
import bs4
import csv
import os
import errno
from multiprocessing import Pool


base_dir = os.path.abspath(os.path.dirname(__file__))
clue_dir = os.path.join(base_dir, 'clues')
base_link = "http://www.j-archive.com/"
season_suffix = "showseason.php?season="
all_seasons = "listseasons.php"
season_id_start = 47
season_id_without_base_start = 22
episode_id_start = 46
feildnames = ['category', 'value', 'clues', 'answer']
episodes_already_checked = []


# checks if directory exists and creates if missing
def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


# grabs the content divs from the provided link
def get_content(link):
    response = requests.get(link)
    soup = bs4.BeautifulSoup(response.text)
    content = soup.find('div', id='content')
    return content


# returns a list a links from a given soup structure
def get_links_from_content(content):
    links = []
    for row_tag in content.findAll('tr'):
        link_tag = row_tag.find('a')
        links.append(link_tag.get('href'))
    return links


# returns a list of season URLS
#
# will need base_link prefix in order to work
def j_archive_season_urls():
    content = get_content(base_link + all_seasons)
    grabbed_season_urls = get_links_from_content(content)
    return grabbed_season_urls


# returns a list of episode URLS from a given season URL
def j_archive_episode_urls(link):
    content = get_content(link)
    table = content.find('table')
    episode_urls = get_links_from_content(table)
    return episode_urls


# creates a csv file of clues from a given episode URL
def get_clues(link):
    content = get_content(link)
    print('start: ' + link[episode_id_start:])

    with open(os.path.join(clue_dir, str(link[episode_id_start:]) + '.csv'),
              'w', encoding='utf-8') as clue_csv_file:
        clue_csv_writer = csv.writer(clue_csv_file, quoting=csv.QUOTE_ALL)
        clue_csv_writer.writerow(feildnames)

        for game_round in content.findAll('table', 'round'):
            categories = [i.text for i in game_round.findAll('td', class_='category_name')]

            for clue in game_round.findAll('td', 'clue'):
                clue_text = clue.find('td', 'clue_text')
                if clue_text is not None:
                    category_id = clue_text.get('id')
                    category_number = int(category_id.split("_")[2])
                    category = categories[category_number - 1]

                    answer_div = clue.find('div')
                    answer_mouse_over = answer_div['onmouseover']
                    answer_mouse_over_code = answer_mouse_over.split("', '")[2]
                    answer_reparsed = bs4.BeautifulSoup(answer_mouse_over_code)
                    answer = answer_reparsed.find_all('em')[0].text

                    value_td = answer_div.findAll('td')[1]
                    value_string = value_td.text
                    if value_string[:2] == "DD":
                        value = int(value_string[5:].replace(',', ''))
                    else:
                        value = int(value_string[1:])
                    clue_csv_writer.writerow([category,
                                              value,
                                              clue_text.text,
                                              answer])
    print('end::: ' + link[episode_id_start:])


# makes a list of missing csv files from
#
# useful for updating csv files or continuing timeouts
def get_missing_ids(seasons_selected):
    clue_dir_list = set([csv_file[:-4] for csv_file in os.listdir(clue_dir)])
    missing_ep_id = []
    for season_link in seasons_selected:
        print("checking season " + season_link[season_id_without_base_start:])
        episode_urls = j_archive_episode_urls(base_link + season_link)
        for ep in episode_urls:
            if ep[episode_id_start:] not in clue_dir_list:
                print(ep)
                missing_ep_id.append(ep)
    return missing_ep_id


if __name__ == "__main__":
    make_sure_path_exists(clue_dir)
    season_urls = j_archive_season_urls()
    missing_ep_ids = get_missing_ids(season_urls)
    pool = Pool(8)
    pool.map(get_clues, missing_ep_ids)