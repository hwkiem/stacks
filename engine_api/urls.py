from django.urls import path
from .views import (
    SearchAuthor,
    SearchBook,
)

urlpatterns = [
    path('api/search/author', SearchAuthor.as_view()),
    path('api/search/book', SearchBook.as_view()),
]