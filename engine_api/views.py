from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Max
# from rest_framework.decorators import api_view
from rest_framework import status, permissions, serializers
from .models import BookAuthors, Books, BuildWorks, Playlists
from .serializers import BookSerializer, AuthorSerializer, WorkSerializer, PlaylistSerializer

class SearchAuthor(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request):
        '''
        List all the authors that have a similar name
        '''
        search = request.GET.get('q')
        authors = BookAuthors.objects.filter(author_name__icontains = search).order_by('-author_ratings_count')[:10]

        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class SearchBook(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    def get(self, request):
        '''
        List all the books that have a similar name
        '''
        search = request.GET.get('q')
        books = BuildWorks.objects.filter(title__icontains = search).order_by('-total_ratings_count')[:10]

        serializer = WorkSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class DisplayAuthor(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    # handling an author_id that does not exist
    def get(self, request, author_id: int):
        '''
        List all books by a given author.
        '''
        works = BuildWorks.objects.raw(
            f"""
            SELECT ENGINE_API_BUILDWORKS.*
            FROM ENGINE_API_AUTHORS
            INNER JOIN ENGINE_API_BUILDWORKS
            USING(BOOK_ID)
            WHERE AUTHOR_ID = {author_id}
            ORDER BY TOTAL_RATINGS_COUNT DESC
            """
        )

        serializer = WorkSerializer(works, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CreatePlaylist(APIView):
    # TODO: DEBUG ME
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response({"message": "Please enter a name for your new playlist!"})
    
    def post(self, request):
        val = Playlists.objects.aggregate(Max('playlist_id')) + 1
        playlist = Playlists(playlist_id = val,
                             plalist_name = request.data['playlist_name'],
                             work_id = 0)
    
        # validating for already existing data
        # if Playlists.objects.filter(**request.data).exists():
        #     raise serializers.ValidationError('This data already exists')
    
        if playlist.is_valid():
            playlist.save()
            return Response(playlist.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

class AddToPlaylist(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]
    def get(self, request, playlist_id: int):
        playlist = Playlists.objects.filter(playlist_id = playlist_id)
        serializer = PlaylistSerializer(playlist, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, playlist_id: int):
        # handling a playlist_id that does not exist
        filtered = Playlists.objects.filter(playlist_id = playlist_id)

        work_to_add = request.data['work_id']

        if work_to_add in filtered.values_list('work_id', flat=True):
            return Response({"message": "This book already exists in the playlist!"},
                            status=status.HTTP_409_CONFLICT)

        playlist = Playlists(playlist_id = playlist_id,
                             playlist_name = filtered.values_list('playlist_name', flat=True).distinct(),
                             work_id = work_to_add)
        playlist.save()

        serializer = PlaylistSerializer(playlist)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class RemoveFromPlaylist(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]
    def get(self, request, playlist_id: int):
        playlist = Playlists.objects.filter(playlist_id = playlist_id)
        serializer = PlaylistSerializer(playlist, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, playlist_id: int):
        # handling a playlist_id that does not exist
        filtered = Playlists.objects.filter(playlist_id = playlist_id)

        work_to_delete = request.data['work_id']

        if work_to_delete not in filtered.values_list('work_id', flat=True):
            return Response({"message": "This book does not exist in the playlist!"},
                            status=status.HTTP_404_NOT_FOUND)

        Playlists.objects.filter(playlist_id = playlist_id, work_id = work_to_delete).delete()

        return Response({"message": "Successfully deleted from the playlist!"}, status=status.HTTP_200_OK)
    

class DeletePlaylist(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]
    def get(self, request, playlist_id: int):
        playlist = Playlists.objects.filter(playlist_id = playlist_id)
        serializer = PlaylistSerializer(playlist, many = True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, playlist_id: int):
        # handling a playlist_id that does not exist
        Playlists.objects.filter(playlist_id = playlist_id).delete()

        return Response({"message": "Successfully deleted this playlist!"}, status=status.HTTP_200_OK)
    

class RecommendForPlaylist(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]
    def get(self, request, playlist_id: int):
        works = BuildWorks.objects.raw(
                f"""
                WITH A AS (
                    SELECT 
                        TAG_ID,
                        COUNT(*) AS NUM_WORK,
                        SUM(PERC) AS TOTAL_PERC
                    FROM ENGINE_API_PLAYLISTS
                    INNER JOIN BUILDSHELVES
                    USING(WORK_ID)
                    WHERE PLAYLIST_ID = {playlist_id}
                    --AND RANKER MODULO OR LESS THAN SOME THRESHOLD?
                    GROUP BY TAG_ID
                ),
                B AS (
                    SELECT 
                        WORK_ID,
                        SUM(NUM_WORK) AS TOTAL_WORK,
                        SUM(TOTAL_PERC) AS TOTAL_PERC
                    FROM BUILDSHELVES
                    INNER JOIN A
                    USING(TAG_ID)
                    WHERE WORK_ID NOT IN (
                        SELECT DISTINCT WORK_ID 
                        FROM ENGINE_API_PLAYLISTS 
                        WHERE PLAYLIST_ID = {playlist_id}
                    )
                    GROUP BY WORK_ID
                    ORDER BY TOTAL_WORK DESC
                    LIMIT 20
                )
                SELECT *
                FROM ENGINE_API_BUILDWORKS
                INNER JOIN B
                USING(WORK_ID)
                """
            )
        
        serializer = WorkSerializer(works, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# TODO: Below

class SimilarBooks(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, work_id: int):
        books = BuildWorks.objects.raw(
            f"""
            WITH A AS (
                SELECT DISTINCT TAG_ID
                FROM BUILDSHELVES
                WHERE WORK_ID = {work_id}
            ),
            B AS (
                SELECT
                    WORK_ID,
                    COUNT(DISTINCT TAG_ID) AS NUM_OVERLAP
                FROM BUILDSHELVES
                INNER JOIN A
                USING(TAG_ID)
                WHERE WORK_ID != {work_id}
                GROUP BY WORK_ID
                ORDER BY NUM_OVERLAP DESC
                LIMIT 20
            )
            SELECT ENGINE_API_BUILDWORKS.*
            FROM ENGINE_API_BUILDWORKS
            INNER JOIN B
            USING(WORK_ID)
            ORDER BY NUM_OVERLAP DESC
            """
        )
    
        serializer = WorkSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class SimilarAuthors(APIView):
    def get(self, request):
        pass

