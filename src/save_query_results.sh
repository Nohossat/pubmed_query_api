#!/bin/bash

sqlite3 data/pubmed.db << script_pubmed
.headers on
.mode csv

.output data/author_extracts.csv

SELECT author.author, abstract 
FROM article 
INNER JOIN author ON article.author_id = author.rowid
WHERE author_id in (SELECT author_id
                    FROM article
                    GROUP BY author_id
                    HAVING count(author_id) > 1) AND abstract IS NOT NULL
ORDER BY author_id DESC;

.output data/classement_journals.csv

SELECT journal, count(journal_id) as count_journal
FROM article
INNER JOIN journal ON article.journal_id = journal.rowid
GROUP BY journal_id
ORDER BY count_journal DESC
LIMIT 10;

.output data/articles_year.csv

SELECT strftime('%Y', publication_date.date) as pub_year, count(publication_date_id) as count_date
FROM article
INNER JOIN publication_date ON article.publication_date_id = publication_date.rowid
GROUP BY pub_year;

.output stdout
script_pubmed
