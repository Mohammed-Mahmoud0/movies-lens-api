from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection, reset_queries
from django.conf import settings
from .models import Movie, Rating, Tag, Link, Genre


# Question 1: N+1 Query Problem - WITHOUT optimization
@api_view(['GET'])
def movies_n_plus_one(request):
    """
    Demonstrates N+1 query problem.
    Retrieves all movies and accesses their related Link data.
    This will cause 1 query for movies + N queries for links (one per movie).
    """
    reset_queries()
    
    # Get first 10 movies to keep output manageable
    movies = Movie.objects.all()[:10]
    
    result = []
    for movie in movies:
        # Accessing movie.links creates an additional query for EACH movie
        result.append({
            'movie_id': movie.movie_id,
            'title': movie.title,
            'imdb_id': movie.links.imdb_id if hasattr(movie, 'links') else None,
        })
    
    queries_count = len(connection.queries)
    
    return Response({
        'method': 'N+1 Problem (No Optimization)',
        'movies_count': len(result),
        'queries_count': queries_count,
        'queries': connection.queries if settings.DEBUG else 'Enable DEBUG to see queries',
        'data': result
    })


# Question 2: Using select_related to fix N+1 problem
@api_view(['GET'])
def movies_select_related(request):
    """
    Uses select_related to optimize the query.
    select_related does a SQL JOIN to fetch related Link data in ONE query.
    Works with ForeignKey and OneToOne relationships.
    """
    reset_queries()
    
    # select_related('links') performs a JOIN - gets movies + links in 1 query
    movies = Movie.objects.select_related('links').all()[:10]
    
    result = []
    for movie in movies:
        # Now accessing movie.links does NOT create additional queries
        result.append({
            'movie_id': movie.movie_id,
            'title': movie.title,
            'imdb_id': movie.links.imdb_id if hasattr(movie, 'links') else None,
        })
    
    queries_count = len(connection.queries)
    
    return Response({
        'method': 'With select_related (Optimized)',
        'movies_count': len(result),
        'queries_count': queries_count,
        'queries': connection.queries if settings.DEBUG else 'Enable DEBUG to see queries',
        'data': result
    })


# Question 3: Using prefetch_related for Many-to-Many relationships
@api_view(['GET'])
def movies_prefetch_related(request):
    """
    Uses prefetch_related to optimize Many-to-Many relationships.
    prefetch_related does separate queries but reduces total query count.
    Works with ManyToMany and reverse ForeignKey relationships.
    """
    reset_queries()
    
    # prefetch_related for genres (Many-to-Many) and ratings (reverse ForeignKey)
    movies = Movie.objects.prefetch_related('genres', 'ratings').all()[:10]
    
    result = []
    for movie in movies:
        # Accessing genres and ratings does NOT create additional queries
        genres_list = [g.name for g in movie.genres.all()]
        ratings_count = movie.ratings.count()
        
        result.append({
            'movie_id': movie.movie_id,
            'title': movie.title,
            'genres': genres_list,
            'ratings_count': ratings_count,
        })
    
    queries_count = len(connection.queries)
    
    return Response({
        'method': 'With prefetch_related (Many-to-Many)',
        'movies_count': len(result),
        'queries_count': queries_count,
        'queries': connection.queries if settings.DEBUG else 'Enable DEBUG to see queries',
        'data': result
    })


# Bonus: Combined optimization
@api_view(['GET'])
def movies_combined_optimization(request):
    """
    Combines select_related and prefetch_related for complete optimization.
    - select_related for OneToOne/ForeignKey (links)
    - prefetch_related for ManyToMany (genres) and reverse ForeignKey (ratings)
    """
    reset_queries()
    
    movies = Movie.objects.select_related('links').prefetch_related('genres', 'ratings').all()[:10]
    
    result = []
    for movie in movies:
        genres_list = [g.name for g in movie.genres.all()]
        ratings_count = movie.ratings.count()
        avg_rating = sum(r.rating for r in movie.ratings.all()) / ratings_count if ratings_count > 0 else 0
        
        result.append({
            'movie_id': movie.movie_id,
            'title': movie.title,
            'imdb_id': movie.links.imdb_id if hasattr(movie, 'links') else None,
            'genres': genres_list,
            'ratings_count': ratings_count,
            'average_rating': round(avg_rating, 2),
        })
    
    queries_count = len(connection.queries)
    
    return Response({
        'method': 'Combined Optimization (select_related + prefetch_related)',
        'movies_count': len(result),
        'queries_count': queries_count,
        'queries': connection.queries if settings.DEBUG else 'Enable DEBUG to see queries',
        'data': result
    })
