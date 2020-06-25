/* pour récupérer les abstracts des auteurs ayant été publié au moins deux fois  */
SELECT author.author, abstract 
FROM article 
INNER JOIN author ON article.author_id = author.rowid
GROUP BY author_id 
HAVING count(author_id) > 1 AND abstract IS NOT NULL
WHERE author_id in (SELECT author_id
                    FROM article
                    GROUP BY author_id
                    HAVING count(author_id) > 1) AND abstract IS NOT NULL
ORDER BY author_id DESC;

/* pour récupérer un classement des journaux scientifiques par rapport aux nombres d'articles publiés */
SELECT journal, count(journal_id) as count_journal
FROM article
INNER JOIN journal ON article.journal_id = journal.rowid
GROUP BY journal_id
ORDER BY count_journal DESC
LIMIT 10;

/* pour récupérer le nombre d'articles publiés par an */
SELECT strftime('%Y', publication_date.date) as pub_year, count(publication_date_id) as count_date
FROM article
INNER JOIN publication_date ON article.publication_date_id = publication_date.rowid
GROUP BY pub_year;


