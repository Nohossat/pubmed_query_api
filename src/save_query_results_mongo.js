use pubmed;

// abstracts by authors being published more than twice
db.article.aggregate([
    {
        $group : {
            _id : { author : "$author"}, 
            numPublications : { $sum : 1 },
            titles : {$push: "$title"},
            abstracts: { $push: "$abstract" } 
        }
    }, {
        $match : {
            "numPublications" : { $gt : 1 }
        }
    },{
        $sort : { "numPublications"  : 1 }
    }, {
        $limit : 5
    }
]).pretty()

// journal ranking by number of publications
db.article.aggregate([
    {
        $group : {
            _id : {
                journal : "$journal"
            },
            numPublications : { $sum : 1}
        }
    }, {
        $sort : { "numPublications" : -1 }
    }
])

// number of articles published by year
db.article.aggregate([
    {
        $group : {
            _id : {
                year: { $year: "$publication_date" }
            },
            numPublications : { $sum : 1}
        }
    }, {
        $sort : { "numPublications" : -1 }
    }
])


    
