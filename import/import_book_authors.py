import pandas as pd
from sqlalchemy import create_engine
import gzip
from nm_secrets import PG_USER, PG_PASS

def main():
    engine = create_engine(f'postgresql+psycopg2://{PG_USER}:{PG_PASS}@engine-api-db.cxcc4u6cay2w.us-east-2.rds.amazonaws.com/postgres')
    
    file_name = 'data/goodreads_book_authors.json.gz'

    with gzip.open(file_name) as fin:
        # encoding for some author names is off
        full = pd.read_json(
            fin,
            lines=True).rename(
                columns={
                    'name': 'author_name',
                    'average_rating': 'author_average_rating',
                    'ratings_count': 'author_ratings_count',
                    'text_reviews_count': 'author_text_reviews_count'
                }
            )
        
        # write to sql
        full.to_sql(
            name = 'engine_api_bookauthors', 
            con = engine, 
            index = False, 
            if_exists = 'append')

if __name__ == '__main__':
    main()
