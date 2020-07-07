import pandas as pd
import numpy as np
import sqlite3
import re
from pymongo import MongoClient
import json 
from datetime import datetime

# get dataframe
df = pd.read_csv('../data/articles_pubmed.csv')

# noramlization
def normalize_data(df):

  # remove brackets around title
  def sanitize_title(title):
      try :
          pattern = re.compile(r'\[(.*)\]')
          result = pattern.search(title)
          return result.group(1)
      except:
          return title

  def encode_col(name_col, df, name_new_col=None):
    # get unique categories
    cat = df[name_col].astype('category').cat.categories.values

    # transform data in the database as categorical data
    df.loc[:, f"{name_col}_id"] = df[name_col].astype('category').cat.codes
    
    # create dataframe
    if name_new_col is not None:
      name_col = name_new_col
    
    cat_table = pd.DataFrame(cat, columns=[name_col])

    return cat_table

  df.loc[:, "title"] = df.title.apply(sanitize_title)

  # duplicate so that we have a clean version for the article table for SQL
  articles_table = df

  # 4 tables to create : author, publication_date, journal, keywords

  publication_date_table = encode_col('publication_date', articles_table, 'date')
  publication_date_table.loc[:, 'date'] = pd.to_datetime(publication_date_table.date, infer_datetime_format=True)
  journal_table = encode_col('journal', articles_table)
  author_table = encode_col('author', articles_table)

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

  return tables

def normalize_data_no_sql(df):
  # remove brackets around title
  def sanitize_title(title):
      try :
          pattern = re.compile(r'\[(.*)\]')
          result = pattern.search(title)
          return result.group(1)
      except:
          return title

  # transform keywords to list of words
  def get_keywords_list(keyword):
    if not isinstance(keyword, float):
      keyword = keyword.split(", ")
    return keyword

  df.loc[:, "title"] = df.title.apply(sanitize_title)
  df.loc[:, "keywords"] = df.keywords.apply(get_keywords_list)

  return df
  

# save tables - to finish
def create_connection_sql(db_file, tables):
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

def create_connection_mongo(df) :

  # connection to database
  client = MongoClient('localhost', 27017)
  db = client.pubmed
  article = db.article

  # prepare json
  df_json = df.apply(lambda x: json.loads(x.to_json()), axis=1)
  

  def normalize_date(json_str):
    if json_str['publication_date'] is not None:
      json_str['publication_date'] = datetime.strptime(json_str['publication_date'], '%Y-%m-%d')
    return json_str

  df_json = df_json.apply(normalize_date).values.tolist()
  
  # save to database
  article.insert_many(df_json)

# SQLite
tables = normalize_data(df)
create_connection_sql('../data/pubmed.db', tables)

# MongoDB
df_nosql = normalize_data_no_sql(df)
create_connection_mongo(df_nosql)

# do look up to get the same results in mongodb

