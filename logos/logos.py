"""This module contains a webscraper to download all of the logos for colleges that
participate in NCAA. See the wiki for a more in depth explanation."""


__author__ = "Sam Kasbawala"
__credits__ = ["Sam Kasbawala"]

__licence__ = "BSD"
__maintainer__ = "Sam Kasbawala"
__email__ = "samarth.kasbawala@uconn.edu"
__status__ = "Development"


import os
import sys
import json
import time
import shutil
import requests

from tqdm import tqdm
from datetime import timedelta
from bs4 import BeautifulSoup
from sportsipy.ncaab.teams import Teams


def get_logos_ncaa(
    save_dir, url="https://www.ncaa.com/schools-index/", clean_dir=False
):
    """Saves a json file in the specified save folder of all of the logos associated
    with each college in the NCAA.

    Args:
        save_dir (string): Name of folder on where to save json file.
        url (str, optional): The url on where to get the logos from. Defaults to
            "https://www.ncaa.com/schools-index/".
        clean_dir (bool): Clean the save_dir before writing json file.
    """

    start = time.time()

    # Dictionary to hold logos
    logos = {}

    # Start on page 0
    page_index = 0
    page = requests.get(os.path.join(url, str(page_index)))

    # Parse the contents of the page while we get an OK Response
    while page.status_code == 200:

        # Make a beautiful soup object
        soup = BeautifulSoup(page.content, "html.parser")

        # Isolate the rows
        table_div = soup.find("div", id="schools-index")
        table_body = table_div.find("tbody")
        rows = table_body.find_all("tr")

        # Loop through the rows, saving the image and the name of the college
        for row in rows:
            image = row.find("img").get("data-src")
            name = row.find_all("td")[2].text  # Name in third column of each row
            logos[name] = image

        # Parse next page
        page_index += 1
        page = requests.get(os.path.join(url, str(page_index)))

    # Clean the specified save directory
    if clean_dir:
        __clean_dir(save_dir)

    # Save the dictionary as a json file in the specified directory
    with open(os.path.join(save_dir, "logos_ncaa.json"), "w") as wf:
        json.dump(logos, wf, sort_keys=True, indent=4)

    elapsed = time.time() - start
    print(f"Scraping logos from NCAA took {timedelta(seconds=elapsed)}")


def get_logos_sr(
    save_dir, url="https://www.sports-reference.com/cbb/schools", clean_dir=False
):
    """Saves a json file in the specified save folder of all of the logos associated
    with each college in the NCAA.

    Args:
        save_dir (string): Name of folder on where to save json file.
        url (str, optional): The url on where to get the logos from. Defaults to
            "https://www.sports-reference.com/cbb/schools".
        clean_dir (bool): Clean the save_dir before writing json file.
    """

    start = time.time()

    # Dictionary to hold logos
    logos = {}

    # Get a list of all teams from sportsipy api (kinda slow)
    print("Getting a list of teams from sportsipy api...")
    teams = [team.abbreviation for team in Teams()]
    not_found = []

    # Loop through all the teams and get the image url
    for team in tqdm(teams, unit="teams"):
        try:
            page = requests.get(url + f"/{team.lower()}")

            soup = BeautifulSoup(page.content, "html.parser")
            meta = soup.find("div", id="meta")
            image = meta.find("img", class_="teamlogo").get("src")

            logos[team] = image
        except AttributeError:
            not_found.append(team)

    # Clean the specified save directory
    if clean_dir:
        __clean_dir(save_dir)

    # Save the dictionary as a json file in the specified directory
    with open(os.path.join(save_dir, "logos_sr.json"), "w") as wf:
        json.dump(logos, wf, sort_keys=True, indent=4)

    # Print out the teams that weren't found
    if not_found:
        print(f"Could not find logos for the following teams: {not_found}")

    # Print out elapsed time
    elapsed = time.time() - start
    print(f"Scraping logos from NCAA took {timedelta(seconds=elapsed)}")


def __clean_dir(dir):
    """Function that will remove all contents within a specified directory.

    Args:
        dir (string): Name of the directory that needs to have its contents removed
    """

    # Make folder if it doesn't exist
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Delete the contents of the folder
    for filename in os.listdir(dir):

        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        # Upon failure, print out the reason and exit
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))
            sys.exit(2)
