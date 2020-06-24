import pandas as pd
import numpy as np
import sqlite3
import requests
import xml.etree.ElementTree as ET
import datetime
import re

# get dataframe
df = pd.read_csv('data/articles_pubmed.csv')

# duplicate so that we have a clean version for the article table
articles_table = df

# remove brackets around title
def sanitize_title(title):
    try :
        pattern = re.compile(r'\[(.*)\]')
        result = pattern.search(title)
        return result.group(1)
    except:
        return title

articles_table.loc[:, "title"] = articles_table.title.apply(sanitize_title)

# normalize data : 4 tables to create : author, publication_date, journal, keywords

# get unique dates
dates_id = df["publication_date"].astype('category').cat.categories.values

# transform data in the database as categorical data
articles_table.loc[:, "publication_date_id"] = df["publication_date"].astype('category').cat.codes

# get unique journal values
journal_id = df["journal"].astype('category').cat.categories.values
articles_table.loc[:, "journal_id"] = df["journal"].astype('category').cat.codes

# get unique author values
author_id = df["author"].astype('category').cat.categories.values
articles_table.loc[:, "author_id"] = df["author"].astype('category').cat.codes

# get unique keywords
keywords_from_df = df.keywords.values
keywords = []

# keywords in one article are a string, so we need to transform them into a list
for keyword in keywords_from_df:
  if not isinstance(keyword, float):
    keyword = keyword.split(", ")
    for word in keyword:
      keywords.append(word)

# transform into a set to get unique values
keywords_unique_list = list(set(keywords))

# join table
keywords_join_list = []

for idx, keywords in enumerate(df.keywords):
  if not isinstance(keywords, float):
    for word in keywords.split(", "):
      keyword_id = keywords_unique_list.index(word)
      keywords_join_list.append([idx, keyword_id])

# create related tables
publication_date_table = pd.DataFrame(dates_id, columns=["date"])
journal_table = pd.DataFrame(journal_id, columns=["journal"])
author_table = pd.DataFrame(author_id, columns=["author"])
keywords_table = pd.DataFrame(keywords_unique_list, columns=["keyword"])
keywords_join_table = pd.DataFrame(keywords_join_list, columns=["article_id", "keyword_id"])


articles_table.drop(['author', 'journal', 'publication_date', 'keywords'], axis = 1, inplace=True)

# tables and their names
tables = {
    "article" : articles_table,
    "publication_date" : publication_date_table,
    "journal" : journal_table,
    "author" : author_table,
    "keywords" : keywords_table,
    "articles_keywords" : keywords_join_table
}

# save tables - to finish
def create_connection(db_file, tables):
  conn = None
  try:
    conn = sqlite3.connect(db_file)
    for name, table in tables.items():
        table.to_sql(name, con=conn)
  except Exception as e:
    print(e)
  finally:
    if conn:
      conn.close()

create_connection('data/pubmed.db', tables)

# todo : add shell script to get sql query results directly in a csv file

