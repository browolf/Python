BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "coins" (
	"id"	TEXT,
	"symbol"	TEXT,
	"name"	NUMERIC,
	"categories"	TEXT,
	"twitter"	TEXT,
	"genesis"	TEXT,
	"mcr"	INTEGER,
	"coingecko_rank"	INTEGER,
	"coingecko_score"	REAL,
	"developer_score"	REAL,
	"community_score"	REAL,
	"public_interest_score"	REAL,
	"total_score"	REAL,
	"alexa"	INTEGER,
	"age"	TEXT,
	"updated"	TEXT,
	PRIMARY KEY("id")
);
COMMIT;
