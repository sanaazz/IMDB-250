# -*- coding: utf-8 -*-


from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import ssl
import json
import re
import csv
from tqdm import tqdm
import time
from urllib.error import HTTPError, URLError


def fetch_movie_details(url, max_retries=5):
    retries = 0
    backoff_factor = 1  # Initial wait time between retries in seconds
    while retries < max_retries:
        try:
            req = Request(
                url=url,
                headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US,en;q=0.5'}
            )
            html = urlopen(req).read().decode('utf-8')
            return BeautifulSoup(html, "html.parser")
        except HTTPError as e:
            if e.code == 504:
                # Only retry for 504 errors
                retries += 1
                time.sleep(backoff_factor * (2 ** retries))  # Exponential backoff
            else:
                raise  # For other HTTP errors, re-raise the exception
        except URLError as e:
            # Handle URL errors (like network disconnections)
            retries += 1
            time.sleep(backoff_factor * (2 ** retries))  # Exponential backoff
    raise Exception(f"Failed to fetch {url} after {max_retries} retries")


def extract_id(lnk):
    match = re.search(r'(tt|nm)(\d+)', lnk)
    return match.group(2) if match else None


def get_250(lnk):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = Request(
        url=lnk,
        headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'en-US,en;q=0.5'}
    )
    html = urlopen(req, context=ctx).read().decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    return soup


def get_movie_info(soup_obj):
    movie_links = soup_obj.find_all('a')
    extracted_movies = {}
    for link in movie_links:
        if 'href' in link.attrs and '/title/' in link['href']:
            title = link.text.strip()
            if title:
                url = "https://www.imdb.com" + link['href']
                extracted_movies[title] = url
    extracted_movies.pop('IMDb Podcasts', None)
    movies_data = []

    for title, url in tqdm(list(extracted_movies.items())):
        try:
            soup = fetch_movie_details(url)
            ul_tags = soup.find_all('ul',
                                    class_='ipc-inline-list ipc-inline-list--show-dividers sc-d8941411-2 cdJsTz baseAlt')
            a_tags = ul_tags[0].find_all('a') if ul_tags else []

            year_tag = next((tag for tag in a_tags if 'releaseinfo' in tag.get('href', '')), None)
            guide_tag = next((tag for tag in a_tags if 'parentalguide' in tag.get('href', '')), None)

            sub_li_tags_str = str(ul_tags[0]) if ul_tags else ''
            duration = re.findall("\d+h(?:\s+\d+m)?|\d+m", sub_li_tags_str)

            a_tags = soup.find_all('a', class_='ipc-chip ipc-chip--on-baseAlt')
            genre_tags = [tag for tag in a_tags if 'genres' in tag.get('href', '')]
            genres = [tag.text.strip() for tag in genre_tags]

            script = soup.find('script', {'type': 'application/ld+json'})
            directs = []
            directs_url = []
            creats = []
            creats_url = []
            act = []
            act_url = []

            if script:
                data = json.loads(script.string)
                if 'director' in data:
                    directors = data['director']
                    if isinstance(directors, list):
                        for director in directors:
                            if director.get('name'):
                                directs.append(director.get('name'))
                            if director.get('url'):
                                directs_url.append(extract_id(director.get('url')))
                if 'creator' in data:
                    creators = data['creator']
                    if isinstance(creators, list):
                        for creator in creators:
                            if creator.get('name'):
                                creats.append(creator.get('name'))
                            if creator.get('url'):
                                creats_url.append(extract_id(creator.get('url')))
                if 'actor' in data:
                    actors = data['actor']
                    if isinstance(actors, list):
                        for actor in actors:
                            if actor.get('name'):
                                act.append(actor.get('name'))
                            if actor.get('url'):
                                act_url.append(extract_id(actor.get('url')))

            gross_us_canada_label = soup.find('span', string="Gross US & Canada")
            amount_text = ''
            if gross_us_canada_label:
                amount_container = gross_us_canada_label.find_next('div',
                                                                   class_='ipc-metadata-list-item__content-container')
                if amount_container:
                    amount_tag = amount_container.find('span', class_='ipc-metadata-list-item__list-content-item')
                    if amount_tag:
                        amount_text = amount_tag.text.strip()

            movie_id = extract_id(url)
            act_url = [element for element in act_url if element is not None]
            directs_url = [element for element in directs_url if element is not None]
            creats_url = [element for element in creats_url if element is not None]

            movie_dict = {
                'ID': movie_id,
                'title': title,
                'year': year_tag.text.strip() if year_tag else '',
                'parental_guide': guide_tag.text.strip() if guide_tag else '',
                'duration': duration[0] if duration else '',
                'genres': ', '.join(genres),
                'directors': ', '.join(directs),
                'director IDs': ', '.join(directs_url),
                'creators': ', '.join(creats),
                'creator IDs': ', '.join(creats_url),
                'actors': ', '.join(act),
                'actor IDs': ', '.join(act_url),
                'gross_usa': amount_text,
            }

            movies_data.append(movie_dict)
        except Exception as e:
            print(f"Error fetching details for {title}: {e}")

    return movies_data


def export_info(data, path):
    field_names = ['ID', 'title', 'year', 'parental_guide', 'duration', 'genres', 'directors', 'director IDs',
                   'creators', 'creator IDs', 'actors', 'actor IDs', 'gross_usa']
    with open(path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for movie in data:
            writer.writerow(movie)


if __name__ == '__main__':
    main_page = get_250('https://www.imdb.com/chart/top/?ref_=nv_mv_250')
    movies_info = get_movie_info(main_page)
    export_info(movies_info, 'movies.csv')

