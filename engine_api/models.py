from django.db import models

class BookAuthors(models.Model):
    author_id = models.AutoField(primary_key = True)
    author_name = models.TextField()
    author_average_rating = models.FloatField()
    author_text_reviews_count = models.IntegerField()
    author_ratings_count = models.IntegerField()


class Books(models.Model):
    book_id = models.AutoField(primary_key = True)
    work_id = models.IntegerField(null = True)
    title = models.TextField(null = True)
    title_without_series = models.TextField(null = True)
    isbn = models.BigIntegerField(null = True)
    isbn13 = models.BigIntegerField(null = True)
    text_reviews_count = models.IntegerField(null = True)
    ratings_count = models.IntegerField(null = True)
    average_rating = models.FloatField(null = True)
    series = models.TextField(null = True)
    country_code = models.TextField(null = True)
    language_code = models.TextField(null = True)
    asin = models.CharField(null = True, max_length = 20)
    kindle_asin = models.CharField(null = True, max_length = 20)
    is_ebook = models.TextField(null = True)
    description = models.TextField(null = True)
    link = models.TextField(null = True)
    url = models.TextField(null = True)
    image_url = models.TextField(null = True)
    num_pages = models.IntegerField(null = True)
    publication_day = models.IntegerField(null = True)
    publication_month = models.IntegerField(null = True)
    publication_year = models.IntegerField(null = True)
    format = models.TextField(null = True)
    publisher = models.TextField(null = True)
    edition_information = models.TextField(null = True)
    similar_books = models.TextField(null = True)


class Authors(models.Model):
    author_id = models.IntegerField()
    book_id = models.IntegerField()
    role = models.TextField()


class Shelves(models.Model):
    work_id = models.IntegerField()
    tag_name = models.TextField()
    count = models.IntegerField()


class BuildWorks(models.Model):
    book_id = models.IntegerField()
    work_id = models.IntegerField(primary_key = True)
    title = models.TextField(null = True)
    title_without_series = models.TextField(null = True)
    isbn = models.BigIntegerField(null = True)
    isbn13 = models.BigIntegerField(null = True)
    text_reviews_count = models.IntegerField(null = True)
    ratings_count = models.IntegerField(null = True)
    average_rating = models.FloatField(null = True)
    series = models.TextField(null = True)
    country_code = models.TextField(null = True)
    language_code = models.TextField(null = True)
    asin = models.CharField(null = True, max_length = 20)
    kindle_asin = models.CharField(null = True, max_length = 20)
    is_ebook = models.TextField(null = True)
    description = models.TextField(null = True)
    link = models.TextField(null = True)
    url = models.TextField(null = True)
    image_url = models.TextField(null = True)
    num_pages = models.IntegerField(null = True)
    publication_day = models.IntegerField(null = True)
    publication_month = models.IntegerField(null = True)
    publication_year = models.IntegerField(null = True)
    format = models.TextField(null = True)
    publisher = models.TextField(null = True)
    edition_information = models.TextField(null = True)
    similar_books = models.TextField(null = True)


# class BuildShelves(models.Model):
#     id = models.AutoField(primary_key = True)
#     work_id = models.IntegerField()
#     tag_id = models.IntegerField()
#     counter = models.IntegerField()
#     tag_total_count = models.IntegerField()
#     tag_total_count_norm = models.FloatField()
#     tag_num_work = models.IntegerField()
#     work_total_count = models.IntegerField()
#     work_total_count_norm = models.FloatField(null = True)

    # class Meta:
    #     indexes = [
    #         models.Index(fields=['work_id',]),
    #         models.Index(fields=['tag_id',]),
    #     ]


# class Tags(models.Model):
#     tag_id = models.AutoField(primary_key=True)
#     tag_name = models.TextField()
#     tag_total_count = models.IntegerField()
#     tag_num_work = models.IntegerField()


# class BuildShelves(models.Model):
#     work_id = models.IntegerField()
#     tag_id = models.IntegerField()
#     work_total = models.IntegerField()
#     tag_total = models.IntegerField()

#     class Meta:

# TODO: Playlist
