#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Packtpub Downloader
"""


import sys
import os
import argparse
import requests
import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


__author__ = "Anthony Da Mota"
__credits__ = ["Anthony Da Mota"]
__license__ = "MIT"
__version__ = "0.5"
__maintainer__ = "Anhony Da Mota"
__email__ = "anthony@damota.me"
__status__ = "Development"


def arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument("-u", "--username", type=str, help="Packtpub username", required=True)
  parser.add_argument("-p", "--password", type=str, help="Packtpub password", required=True)
  parser.add_argument("-d", "--dlpath", type=str, help="Download path", default="downloads/")
  args = parser.parse_args()
  return args


def clear_and_write():
  if os.name == "nt":
      os.system("cls")
  else:
      os.system("clear")
  print "[PacktPub Downloader v{}]\n".format(__version__)


def get_user_agent():
  return UserAgent().random


def valid_filename(text, title=False):
  output = ""
  if title:
    output = text.replace(" [eBook]", "")
    output = re.sub('\W', '_', output)
  else:
    output = re.sub('\W', '_', text)
  return output


def download_all(login_username, login_password, dl_path, base_url, ebooks_url):
  req = requests.Session()

  try:
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)

    clear_and_write()
    print "\nLogging in..."

    headers = {'User-Agent' : get_user_agent(), "Referer": base_url}
    login_data = {
        "email": login_username,
        "password": login_password,
        "op": "Login",
        "form_id": "packt_user_login_form"
    }
    the_login = req.post(base_url, data=login_data, headers=headers)

    if the_login.status_code == 200:
      print "\nLogin success!\n"

      the_books = req.get(ebooks_url, headers=headers)
      books_soup = BeautifulSoup(the_books.text, 'html.parser')

      product_account_list = books_soup.find(attrs={"id": "product-account-list"})

      media_pattern = re.compile("(code|ebook)_download\/\d+\/?(pdf|epub|mobi)?")

      for product in product_account_list.find_all("div", {"class": "product-line"}):
        if 'title' in product.attrs:
          title = product.attrs['title'].encode('utf-8')
          print "Downloading {}".format(title)
          for link in product.find('div', {'class': 'product-buttons-line'}).select('div.download-container')[1].find_all('a'):
            if link.attrs['href'] != "#":
              ebook_link = "{}{}".format(base_url, link.attrs['href'])

              ebook_link_divider = media_pattern.search(ebook_link)
              if ebook_link_divider.group(1) == "ebook":
                media_type = ".{}".format(ebook_link_divider.group(2))
              else:
                media_type = ".zip"

              filename = valid_filename(title, True)
              directory = filename
              filename_with_extension = "{}{}".format(filename, media_type)

              print("\t... {}".format(media_type)),

              if not os.path.exists("{}{}".format(dl_path, directory)):
                os.makedirs("{}{}".format(dl_path, directory))
              if not os.path.isfile("{}{}/{}".format(dl_path, directory, filename_with_extension)):
                product_req = req.get(ebook_link, headers=headers, allow_redirects=True)
                with open("{}{}/{}".format(dl_path, directory, filename_with_extension), "wb") as item:
                  item.write(product_req.content)
                print "DONE ✅"
              else:
                print "Already downloaded 👌"
    else:
      print "\nLogin failed. Please check credentials.\n"

  except KeyboardInterrupt:
    print "\nExiting...\n"
    sys.exit()


def main(argv):
  args = arguments()
  login_username = args.username
  login_password = args.password
  if args.dlpath.endswith("/"):
    dl_path = args.dlpath
  else:
    dl_path = "{}/".format(args.dlpath)
  base_url = "https://www.packtpub.com"
  ebooks_url = "{}/account/my-ebooks".format(base_url)

  download_all(login_username, login_password, dl_path, base_url, ebooks_url)


if __name__ == "__main__":
  main(sys.argv[1:])
