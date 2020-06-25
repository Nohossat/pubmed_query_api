import pandas as pd
import numpy as np
import sqlite3
import requests
import xml.etree.ElementTree as ET
import datetime

# get pmcids from disk or fetch them again
def get_pmcids_list() :
    try :
        pmcids = pd.read_csv('data/pmcids.csv').values
    except:
        search = "gene"
        url_query = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={search}&sort=relevance&retmode=json&retmax=1000"
        resp = requests.get(url_query)
        
        if resp.status_code != 200:
            # This means something went wrong.
            raise ApiError('erreur: {}'.format(resp.status_code))

        results = resp.json()
        pmcids = results['esearchresult']['idlist']

        # save them in a CSV format
        pmcids = pd.DataFrame(pmcids, columns=['PMCID'])
        pmcids.to_csv('data/pmcids.csv', index=False)

        pmcids = pmcids.values

    return pmcids

def get_article_data(pmcids):

    def get_data(root, path, article) :
        try:
            data = root.find(article_root + path).text
        except :
            data = ""
        finally:
            article.append(data)

    # get pmcid related data 
    articles = []

    for pmcid in pmcids:
        article = [] # init article metadata list

        # pmcid : get value
        pmcid = pmcid[0]
        article.append(pmcid)

        # fetch XML other content
        url_article = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&retmode=XML&rettype=abstract"
        response = requests.get(url_article.format(pmcid))
        root = ET.fromstring(response.content)

        # root of the XML content we are interested in
        article_root = "./PubmedArticle/MedlineCitation/"

        # title
        get_data(root, "Article/ArticleTitle", article)

        # abstract
        get_data(root, "Article/Abstract/AbstractText", article)

        # publication_date - special case
        try:
            year = int(root.find(article_root + "DateCompleted/Year").text)
            month = int(root.find(article_root + "DateCompleted/Month").text)
            day = int(root.find(article_root + "DateCompleted/Day").text)
            publication_date = datetime.datetime(year, month, day)
        except:
            publication_date = None
        finally:
            article.append(publication_date)

        # keywords - special case
        keywords = []
        try :
            for keyword in root.findall(article_root + "/MeshHeadingList/MeshHeading"):
                keyword_name = keyword.find("DescriptorName").text
                keywords.append(keyword_name)
            keywords = ', '.join(keywords)
        except :
            pass
        finally:
            article.append(keywords)

        # journal
        get_data(root, "/MedlineJournalInfo/MedlineTA", article)

        # doi - special case
        try:
            doi_path = "./PubmedArticle/PubmedData/ArticleIdList/ArticleId"
            
            for article_id in root.findall(doi_path):
                if article_id.attrib['IdType'] == 'doi':
                    doi_id = article_id.text
                else :
                    doi_id = ""
        except:
            doi_id = ""
        finally:
            article.append(doi_id)

        # author
        get_data(root, "Article/AuthorList/Author/LastName", article)

        # append to the final articles list
        articles.append(article)

    # transform into Dataframe
    df = pd.DataFrame(articles, columns=['pmcid', 'title', 'abstract', 'publication_date', 'keywords', 'journal', 'doi', 'author'])

    # save to csv 
    df.to_csv('data/articles_pubmed_1.csv', index=False)

    return df

pmcids = get_pmcids_list()
df = get_article_data(pmcids)
        

    
