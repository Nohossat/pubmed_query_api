from pymongo import MongoClient
import pprint

article = MongoClient().pubmed.article

# abstracts by authors being published more than twice
print("Extraits des auteurs ayant publié au moins 2 fois")
pipeline_abstracts = [
    {"$group": {"_id": {"author" : "$author"}, "numPublications" : { "$sum" : 1 }, "abstracts" : {"$push" : "$abstract"}}},
    {"$match" : {"numPublications" : { "$gt" : 1 }}},
    {"$sort": {"numPublications" : 1 }},
    {"$limit" : 2}
]

pprint.pprint(list(article.aggregate(pipeline_abstracts)))

# journal ranking by number of publications

print("Nombre de publications par journal")
pipeline_journal = [
    {"$group": {"_id": {"journal" : "$journal"}, "numPublications" : { "$sum" : 1 }}},
    {"$match" : {"numPublications" : { "$gt" : 1 }}},
    {"$sort": {"numPublications" : -1 }}
]

pprint.pprint(list(article.aggregate(pipeline_journal)))

# number of articles published by year

pipeline_year = [
    {"$group": {"_id": {"year" : { "$year": "$publication_date" }}, "numPublications" : { "$sum" : 1 }}},
    {"$match" : {"numPublications" : { "$gt" : 1 }}},
    {"$sort": {"numPublications" : -1 }}
]

print("Nombre de publications par an")
pprint.pprint(list(article.aggregate(pipeline_year)))

