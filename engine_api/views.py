from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import BookAuthors, Books, BuildWorks
from .serializers import BookSerializer, AuthorSerializer, WorkSerializer

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
        books = BuildWorks.objects.filter(title__icontains = search).order_by('-ratings_count')[:10]

        serializer = WorkSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# TODO: Below

class SimilarBooks(APIView):
    def get(self, request, work_id: int):
        books = WorkSerializer.objects.raw(
            f"""
            WITH A AS (
                SELECT DISTINCT TAG_ID
                FROM BUILDSHELVES
                WHERE WORK_ID = {work_id}
            ),
            B AS (
                SELECT 
                FROM BUILDSHELVES
                INNER JOIN A
                USING(TAG_ID)
            )
            SELECT *
            FROM ENGINE_API_BOOKS
            INNER JOIN B
            USING(WORK_ID)
            """
        )
    
        serializer = WorkSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class SimilarAuthors(APIView):
    def get(self, request):
        pass

