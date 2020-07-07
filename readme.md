# SQLITE Mini Project

We want to have a first introduction to the PubMed API and make some SQL queries on the collected data turned into tables.

## Getting Started

For the following code to work, the **sqlite3** module and **MongoDB Server** must be installed on the machine.

Then, inside the **/src** folder: 

```python
python -m venv venv/ 
source /venv/bin/activate # OSX - bash/zsh
.\venv\Scripts\activate # Windows - Powershell
pip install -r requirements.txt
```

## First Step : Consume PubMed API to fetch data

We fetch 1000 articles dealing with genetics on PubMed website.

We needed 2 steps to get the data :
    - fetch the ids (PMCID) of the targeted articles  
    - for each PMCID, collect the title, abstract, pubmed_id, publication date, keywords, journal, doi and first author. 

The code consuming the API can be found in **src/app.py**.

## Second Step : Data normalization and save to databases

### Relational Database

With Pandas library, we separated the data collected to create our database **data/pubmed.db**.

The code normalizing the data can be found in **src/normalize_data.py**.

Below the physical model for our database.

![sql_model](img/model.png)

### Document-Based Database

We prepare the data (convert data from CSV to JSON) to save into a MongoDB database.

We will only use one collection : article.


## Third step : SQL queries

From the SQL database, we decided to extract the following data:
    - abstracts by authors being published more than twice
    - journal ranking by number of publications
    - number of articles published by year

The query results were saved in the **data** folder.

You can also execute the **src/save_query_results.sh** to fetch the data again.

The standalone SQL queries are also in the **src/script_pubmed.sql**.
