import pandas as pd
import numpy as np
import sqlite3
import requests
import xml.etree.ElementTree as ET
import datetime
import re

# get dataframe
df = pd.read_csv('articles_pubmed.csv')

# duplicate so that we have a clean version for the article table
articles_table = df

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

# create related tables
publication_date_table = pd.DataFrame(dates_id, columns=["date"])
journal_table = pd.DataFrame(journal_id, columns=["journal"])
author_table = pd.DataFrame(author_id, columns=["author"])

articles_table.drop(['author', 'journal', 'publication_date'], axis = 1, inplace=True)
print(articles_table.columns.values)

# remove brackets around title
def sanitize_title(title):
    try :
        pattern = re.compile(r'\[(.*)\]')
        result = pattern.search(title)
        return result.group(1)
    except:
        return title

articles_table.loc[:, "title"] = articles_table.title.apply(sanitize_title)

# tables and their names
tables = {
    "article" : articles_table,
    "publication_date" : publication_date_table,
    "journal" : journal_table,
    "author" : author_table
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

create_connection('pubmed.db', tables)

