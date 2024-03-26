import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import *
from nm_secrets import PG_USER, PG_PASS
# import sqlite3 as sql
import gzip

def main():
    engine = create_engine(f'postgresql+psycopg2://{PG_USER}:{PG_PASS}@engine-api-db.cxcc4u6cay2w.us-east-2.rds.amazonaws.com/postgres')
    file_name = 'data/goodreads_books.json.gz'

    with gzip.open(file_name) as fin:
        full = pd.read_json(fin, lines=True, chunksize = 1000)

        seen_works = set()
        counter = 0

        books_schema = {
            'book_id': Integer,
            'work_id': Integer,
            'title': Text,
            'title_without_series': Text,
            'isbn': BigInteger,
            'isbn13': BigInteger,
            'text_reviews_count': Integer,
            'ratings_count': Integer,
            'average_rating': Float,
            'series': Text,
            'country_code': Text,
            'language_code': Text,
            'asin': Text,
            'kindle_asin': Text,
            'is_ebook': Text,
            'description': Text,
            'link': Text,
            'url': Text,
            'image_url': Text,
            'num_pages': Integer,
            'publication_day': Integer,
            'publication_month': Integer,
            'publication_year': Integer,
            'format': Text,
            'publisher': Text,
            'edition_information': Text,
            'similar_books': Text
        }

        int_cols = ['book_id', 
                    'work_id', 
                    'text_reviews_count', 
                    'ratings_count', 
                    'isbn',
                    'isbn13',
                    'num_pages', 
                    'publication_day', 
                    'publication_month', 
                    'publication_year']
    
        float_cols = ['average_rating']

        authors_schema = {
            'author_id': Integer,
            'book_id': Integer,
            'role': Text
        }

        tags_schema = {
            'work_id': Integer,
            'tag_name': Text,
            'count':  Integer
        }

        for temp in full:

            authors = pd.DataFrame()
            tags = pd.DataFrame()

            # row by row... annoying
            for _, row in temp.iterrows():
                # only english books for now
                if 'en' not in row['language_code']:
                    continue

                work_id = row['work_id']
                book_id = row['book_id']

                # get authors for this book
                temp_author = pd.DataFrame(row['authors']).assign(book_id = book_id)
                authors = pd.concat([authors, temp_author])

                # get tags (for new works)
                if work_id not in seen_works:
                    temp_tag = pd.DataFrame(row['popular_shelves']).\
                        assign(work_id = work_id).\
                        rename(columns={'name': 'tag_name'}).\
                        drop_duplicates(['tag_name', 'work_id', 'count'])
                    tags = pd.concat([tags, temp_tag])

                    seen_works.add(work_id)

            temp = temp.drop(
                ['popular_shelves', 'authors'], 
                axis = 1
            ).astype(str)

            temp[int_cols] = temp[int_cols].apply(pd.to_numeric, errors='coerce')
            temp[float_cols] = temp[float_cols].apply(pd.to_numeric, errors='coerce')

            temp = temp[temp['language_code'].str.contains('en')]

            temp.to_sql(
                'engine_api_books', 
                engine, 
                index = False, 
                if_exists = 'append',
                dtype = books_schema
            )

            authors.to_sql(
                'engine_api_authors', 
                engine, 
                index = False, 
                if_exists = 'append',
                dtype = authors_schema
            )

            tags.to_sql(
                'engine_api_shelves', 
                engine, 
                index = False, 
                if_exists = 'append',
                dtype = tags_schema
            )
            
            print(f'chunk {counter}/2360 complete')
            counter += 1


if __name__ == '__main__':
    main()
