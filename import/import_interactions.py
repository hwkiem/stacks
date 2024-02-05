import pandas as pd
import sqlite3 as sql
import gzip

def main():
    con = sql.connect('data/library.db')
    file_name = 'data/goodreads_interactions.csv'

    full = pd.read_csv(file_name)

    # write to sql
    full.to_sql(
        'import_book_interactions', 
        con, 
        index = False, 
        if_exists = 'replace')

if __name__ == '__main__':
    main()
