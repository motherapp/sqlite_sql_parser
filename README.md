# sqlite\_sql\_parser


## Introduction
This script parses the SQL files exported form `sqlite3 .dump`, and make it compatible for MySQL import.


## Basic Usage

    python parse_sqlite_sql.py export.sql

Two files would be generated: `export.sql.schema.sql` and `export.sql.data.sql`

One is for DB schema, and the other is for DB data, both are updated for MySQL import purpose.

## Further Notes

It's strongly advised that one should further modify the DB schema for his own purpose, especially:

1. Replace some `text` field with `varchar(255)`, for better performance 
2. Replace some `integer` with  `bigint`
3. add quote for tables named by reserved keywords

One should also note that this script would replace _all_ values of `t` with `1`, and _all_ values of `f` with `0`, in order to adapt to boolean field change. If you really need a `t` there, you might change back manually.



## Advantages
Unlike most other line based parsers, this parser treat literal strings and non-literal strings _separately_. So even if you table data contains some special statements like `CREATE TABLE`, `INSERT VALUE` or 'AUTOINCREMENT`, they would _not_ be updated. 

## Disadvantages
It's very slow. Took about 2 seconds to parse a SQL file of 100,000 lines.

For other Perl or Python based scripts, it could be done in less than 0.1 second.

## Hacking Points
The following methods are likely to be modified for futher customization:

    process_literal
    process_schema


