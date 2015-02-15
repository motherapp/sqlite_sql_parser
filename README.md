# sqlite_sql_parser

Parse the SQL files exported form sqlite3 .dump, and make it portable for MySQL.

This script separate the literal and non-literal strings, so it should not change anything inside the content.

It's not so efficient, and it took about 2 seconds to parse 100K lines of SQL statements.

