from django.urls import path
from .views import (
    SearchAuthor,
    DisplayAuthor,
    SearchBook,
    SimilarBooks,
    # CreatePlaylist,
    AddToPlaylist,
    RemoveFromPlaylist,
    RecommendForPlaylist,
    DeletePlaylist,
)

urlpatterns = [
    path('api/search/author', SearchAuthor.as_view()),
    path('api/search/book', SearchBook.as_view()),
    path('api/author/<int:author_id>', DisplayAuthor.as_view()),
    path('api/similar/book/<int:work_id>', SimilarBooks.as_view()),
    # path('api/create/playlist/', CreatePlaylist.as_view()),
    path('api/playlist/<int:playlist_id>/add', AddToPlaylist.as_view()),
    path('api/playlist/<int:playlist_id>/remove', RemoveFromPlaylist.as_view()),
    path('api/playlist/<int:playlist_id>/recommend', RecommendForPlaylist.as_view()),
    path('api/playlist/<int:playlist_id>/delete', DeletePlaylist.as_view()),
]