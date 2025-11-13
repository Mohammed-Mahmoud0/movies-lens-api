from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.db import connection, reset_queries
from django.conf import settings
from django.db.models import Q, F, Avg, Count
from .models import Movie, Rating, Tag, Link, Genre
import cProfile
import pstats
import io
from functools import wraps
import time


# cProfile decorator for manual profiling
def profile_view(func):
    """
    Decorator to profile a view function using cProfile.
    Adds profiling stats to the response.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()

        # Execute the view
        response = func(*args, **kwargs)

        profiler.disable()

        # Get profiling stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
        ps.print_stats(20)  # Show top 20 functions

        # Add profiling info to response if it's a Response object
        if isinstance(response, Response):
            if isinstance(response.data, dict):
                response.data["cProfile_stats"] = s.getvalue()

        return response

    return wrapper


@api_view(["GET"])
def api_root(request, format=None):
    """
    API Root - Lists all available endpoints
    """
    return Response(
        {
            "message": "Welcome to Movies API - with profiling tools!",
            "optimization_endpoints": {
                "n-plus-one-problem": reverse("movies-n-plus-one", request=request, format=format),
                "select-related-optimization": reverse("movies-select-related", request=request, format=format),
                "prefetch-related-optimization": reverse("movies-prefetch-related", request=request, format=format),
            },
            "advanced_orm_features": {
                "q-expression-filters": reverse("movies-q-filters", request=request, format=format),
                "f-expression-update": reverse("movies-f-update", request=request, format=format),
                "only-method": reverse("movies-only", request=request, format=format),
                "defer-method": reverse("movies-defer", request=request, format=format),
                "values-as-dict": reverse("movies-values", request=request, format=format),
                "values-list-as-tuple": reverse("movies-values-list", request=request, format=format),
                "index-comparison": reverse("movies-index-compare", request=request, format=format),
            },
            "caching_endpoints": {
                "manual-cache": reverse("cache-manual", request=request, format=format),
                "per-view-cache": reverse("cache-per-view", request=request, format=format),
                "partial-cache": reverse("cache-partial", request=request, format=format),
            },
            "profiling_tools": {
                "debug-toolbar": "Available on the right side of the page (for HTML views)",
                "silk-dashboard": "/silk/",
            },
        }
    )


# N+1 Query Problem
# this is results from monitoring:
# Avg. Time 342ms
# Avg. #Queries: 11
# Avg. #Queries: 15ms
@api_view(["GET"])
def movies_n_plus_one(request):
    """
    Demonstrates N+1 query problem.
    Retrieves all movies and accesses their related Link data.
    This will cause 1 query for movies + N queries for links (one per movie).
    """
    reset_queries()

    # Get first 10 movies
    movies = Movie.objects.all()[:10]

    result = []
    for movie in movies:
        result.append(
            {
                "movie_id": movie.movie_id,
                "title": movie.title,
                "imdb_id": movie.links.imdb_id if hasattr(movie, "links") else None,
            }
        )

    queries_count = len(connection.queries)

    return Response(
        {
            "method": "N+1 Problem (No Optimization)",
            "movies_count": len(result),
            "queries_count": queries_count,
            "queries": (
                connection.queries if settings.DEBUG else "Enable DEBUG to see queries"
            ),
            "data": result,
        }
    )


#  Using select_related to fix N+1 problem
# this is results from monitoring:
# Avg. Time 1851ms
# Avg. #Queries: 858ms
# Avg. #Queries: 1
@api_view(["GET"])
def movies_select_related(request):
    """
    Uses select_related to optimize the query.
    select_related does a SQL JOIN to fetch related Link data in ONE query.
    """
    reset_queries()

    movies = Movie.objects.select_related("links").all()[:10]

    result = []
    for movie in movies:
        # Now accessing movie.links does NOT create additional queries
        result.append(
            {
                "movie_id": movie.movie_id,
                "title": movie.title,
                "imdb_id": movie.links.imdb_id if hasattr(movie, "links") else None,
            }
        )

    queries_count = len(connection.queries)

    return Response(
        {
            "method": "With select_related (Optimized)",
            "movies_count": len(result),
            "queries_count": queries_count,
            "queries": (
                connection.queries if settings.DEBUG else "Enable DEBUG to see queries"
            ),
            "data": result,
        }
    )


# Question 3: Using prefetch_related for Many-to-Many relationships
# this is results from monitoring:
# Avg. Time 1531ms
# Avg. #Queries: 613ms
# Avg. #Queries: 3
@api_view(["GET"])
def movies_prefetch_related(request):
    """
    Uses prefetch_related to optimize Many-to-Many relationships.
    """
    reset_queries()

    # prefetch_related for genres (Many-to-Many)
    movies = Movie.objects.prefetch_related("genres", "ratings").all()[:10]

    result = []
    for movie in movies:
        # Accessing genres and ratings does NOT create additional queries
        genres_list = [g.name for g in movie.genres.all()]
        ratings_count = movie.ratings.count()

        result.append(
            {
                "movie_id": movie.movie_id,
                "title": movie.title,
                "genres": genres_list,
                "ratings_count": ratings_count,
            }
        )

    queries_count = len(connection.queries)

    return Response(
        {
            "method": "With prefetch_related (Many-to-Many)",
            "movies_count": len(result),
            "queries_count": queries_count,
            "queries": (
                connection.queries if settings.DEBUG else "Enable DEBUG to see queries"
            ),
            "data": result,
        }
    )



# Q() Expression - Dynamic Filters
@api_view(["GET"])
def movies_with_q_filters(request):
    """
    Using Q() objects for complex dynamic queries.
    """
    reset_queries()
    
    # Build dynamic filters using Q()
    
    # Filter 1: Movies with 'Action' or 'Comedy' genre
    action_or_comedy = Movie.objects.filter(
        Q(genres__name='Action') | Q(genres__name='Comedy')
    ).distinct()[:5]
    
    # Filter 2: Movies with specific title patterns (AND + OR + NOT)
    complex_filter = Movie.objects.filter(
        Q(title__icontains='Star') | Q(title__icontains='War'),
        ~Q(title__icontains='Episode')  # NOT containing 'Episode'
    )[:5]
    
    # Filter 3: Ratings-based filter
    highly_rated = Movie.objects.filter(
        Q(ratings__rating__gte=4.5) | Q(ratings__rating__lte=1.5)
    ).distinct()[:5]
    
    queries_count = len(connection.queries)
    
    return Response({
        "method": "Q() Expression - Dynamic Filters",
        "queries_count": queries_count,
        "filters_applied": {
            "filter1": "Action OR Comedy movies",
            "filter2": "Title contains 'Star' OR 'War' BUT NOT 'Episode'",
            "filter3": "Rating >= 4.5 OR Rating <= 1.5"
        },
        "results": {
            "action_or_comedy": [{"id": m.movie_id, "title": m.title} for m in action_or_comedy],
            "complex_filter": [{"id": m.movie_id, "title": m.title} for m in complex_filter],
            "highly_rated": [{"id": m.movie_id, "title": m.title} for m in highly_rated],
        },
        "queries": connection.queries if settings.DEBUG else "Enable DEBUG"
    })



# F() Expression - Update fields in SQL directly
@api_view(["POST"])
def update_with_f_expression(request):
    """
    Using F() to update fields directly in SQL without loading into Python.
    """
    reset_queries()
    
    # Example 1: Update timestamp based on another field (SQL-level operation)
    updated_count = Rating.objects.filter(rating__lt=2.0).update(
        timestamp=F('timestamp') + 1000  # Add 1000 to timestamp
    )
    
    # Example 2: Mathematical operations
    Rating.objects.filter(user_id=1).update(
        rating=F('rating') * 1.0  # Keep same rating (demo purpose)
    )
    
    queries_count = len(connection.queries)
    
    return Response({
        "method": "F() Expression - SQL-level Updates",
        "updated_count": updated_count,
        "queries_count": queries_count,
        "explanation": "F() updates fields in SQL without loading data to Python",
        "benefit": "Much faster for bulk updates, no race conditions",
        "queries": connection.queries if settings.DEBUG else "Enable DEBUG"
    })


# only() - Select specific fields only
@api_view(["GET"])
def movies_with_only(request):
    """
    Using only() to fetch specific fields only.
    Reduces data transfer and memory usage.
    """
    reset_queries()
    
    # Fetch only movie_id and title (lighter query)
    movies_light = Movie.objects.only('movie_id', 'title')[:10]
    
    result = [{"id": m.movie_id, "title": m.title} for m in movies_light]
    queries_count = len(connection.queries)
    
    return Response({
        "method": "only() - Fetch specific fields",
        "movies_count": len(result),
        "queries_count": queries_count,
        "fields_fetched": ["movie_id", "title"],
        "benefit": "Reduced data transfer, faster queries",
        "data": result,
        "queries": connection.queries if settings.DEBUG else "Enable DEBUG"
    })


# defer() - Exclude specific fields
@api_view(["GET"])
def movies_with_defer(request):
    """
    Using defer() to exclude heavy fields from initial query.
    """
    reset_queries()
    
    # Fetch all fields EXCEPT some heavy ones (if you have text/blob fields)
    movies_deferred = Movie.objects.defer('title')[:10]
    
    # When we access movie_id, it's already loaded
    # When we access title, it triggers an additional query
    result = [{"id": m.movie_id} for m in movies_deferred]
    
    queries_count = len(connection.queries)
    
    return Response({
        "method": "defer() - Exclude fields",
        "movies_count": len(result),
        "queries_count": queries_count,
        "fields_deferred": ["title"],
        "benefit": "Delay loading heavy fields until needed",
        "data": result,
        "queries": connection.queries if settings.DEBUG else "Enable DEBUG"
    })


# values() - Return data as dictionaries
@api_view(["GET"])
def movies_as_dict(request):
    """
    Using values() to get data as dictionaries instead of model instances.
    """
    reset_queries()
    
    # Returns list of dicts, not model instances
    movies_dict = Movie.objects.values('movie_id', 'title')[:10]
    
    queries_count = len(connection.queries)
    
    return Response({
        "method": "values() - Data as Dictionaries",
        "movies_count": len(movies_dict),
        "queries_count": queries_count,
        "data_type": "list of dicts",
        "benefit": "No model instantiation overhead, faster",
        "data": list(movies_dict),
        "queries": connection.queries if settings.DEBUG else "Enable DEBUG"
    })


# values_list() - Return data as tuples
@api_view(["GET"])
def movies_as_tuples(request):
    """
    Using values_list() to get data as tuples.
    Most efficient format, minimal memory usage.
    """
    reset_queries()
    
    # Returns list of tuples
    movies_tuples = Movie.objects.values_list('movie_id', 'title')[:10]
    
    # With flat=True for single field
    movie_ids_only = Movie.objects.values_list('movie_id', flat=True)[:10]
    
    queries_count = len(connection.queries)
    
    return Response({
        "method": "values_list() - Data as Tuples",
        "queries_count": queries_count,
        "data_type": "list of tuples",
        "benefit": "Fastest, least memory, good for bulk operations",
        "data": {
            "tuples": list(movies_tuples),
            "flat_list": list(movie_ids_only)
        },
        "queries": connection.queries if settings.DEBUG else "Enable DEBUG"
    })


# Index Performance Comparison
@api_view(["GET"])
def compare_indexed_vs_non_indexed(request):
    """
    Compare query performance on indexed vs non-indexed columns.
    Rating.user_id is indexed, Rating.timestamp is not.
    """
    reset_queries()
    
    # Query on INDEXED field (user_id)
    start_indexed = time.time()
    indexed_results = Rating.objects.filter(user_id=1)[:100]
    list(indexed_results)  # Force evaluation
    time_indexed = (time.time() - start_indexed) * 1000  # Convert to ms
    
    queries_after_indexed = len(connection.queries)
    
    # Query on NON-INDEXED field (timestamp)
    start_non_indexed = time.time()
    non_indexed_results = Rating.objects.filter(timestamp__gt=1000000000)[:100]
    list(non_indexed_results)  # Force evaluation
    time_non_indexed = (time.time() - start_non_indexed) * 1000
    
    queries_total = len(connection.queries)
    
    return Response({
        "method": "Index Performance Comparison",
        "indexed_field": {
            "field": "user_id",
            "has_index": True,
            "time_ms": round(time_indexed, 2),
            "results_count": len(list(Rating.objects.filter(user_id=1)[:100]))
        },
        "non_indexed_field": {
            "field": "timestamp",
            "has_index": False,
            "time_ms": round(time_non_indexed, 2),
            "results_count": len(list(Rating.objects.filter(timestamp__gt=1000000000)[:100]))
        },
        "performance_difference": {
            "speedup": round(time_non_indexed / time_indexed, 2) if time_indexed > 0 else "N/A",
            "conclusion": "Indexed queries are faster" if time_indexed < time_non_indexed else "Results may vary"
        },
        "queries_count": queries_total,
        "queries": connection.queries if settings.DEBUG else "Enable DEBUG"
    })


# ============================================
# CACHING EXAMPLES
# ============================================

from django.core.cache import cache
from django.views.decorators.cache import cache_page
from datetime import datetime


# 1. LOW-LEVEL CACHE API (Manual Cache)
@api_view(['GET'])
def cache_manual_example(request):
    """
    Low-Level Manual Caching - Full control over what and when to cache
    """
    cache_key = 'manual_movies_list'
    
    # Try to get from cache first
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return Response({
            'method': 'Low-Level Manual Cache',
            'cache_status': 'HIT - Data from cache',
            'cached_at': cached_data['timestamp'],
            'data': cached_data['movies']
        })
    
    # Cache miss - fetch from database
    movies = Movie.objects.all()[:5]
    movies_data = [{'id': m.movie_id, 'title': m.title} for m in movies]
    
    # Store in cache for 5 minutes (300 seconds)
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'movies': movies_data
    }
    cache.set(cache_key, cache_data, timeout=300)
    
    return Response({
        'method': 'Low-Level Manual Cache',
        'cache_status': 'MISS - Data from database',
        'cached_at': cache_data['timestamp'],
        'data': movies_data,
        'note': 'Next request will be cached for 5 minutes'
    })


# 2. PER-VIEW CACHE (Using decorator)
@api_view(['GET'])
@cache_page(60 * 2)  # Cache for 2 minutes
def cache_per_view_example(request):
    """
    Per-View Caching - Entire view response is cached automatically
    """
    # This entire response will be cached
    movies = Movie.objects.all()[:5]
    movies_data = [{'id': m.movie_id, 'title': m.title} for m in movies]
    
    return Response({
        'method': 'Per-View Cache (Decorator)',
        'cache_duration': '2 minutes',
        'timestamp': datetime.now().isoformat(),
        'data': movies_data,
        'note': 'This entire response is cached automatically'
    })


# 3. TEMPLATE FRAGMENT CACHE (for partial caching)
@api_view(['GET'])
def cache_partial_example(request):
    """
    Partial/Fragment Caching - Cache only parts of the response
    """
    # Cache only the expensive query
    cache_key = 'expensive_query_result'
    expensive_data = cache.get(cache_key)
    
    if not expensive_data:
        # Simulate expensive operation
        expensive_data = Movie.objects.select_related('links').prefetch_related('genres')[:10]
        expensive_data = [{
            'id': m.movie_id,
            'title': m.title,
            'genres': [g.name for g in m.genres.all()]
        } for m in expensive_data]
        cache.set(cache_key, expensive_data, timeout=180)  # 3 minutes
        cache_status = 'MISS'
    else:
        cache_status = 'HIT'
    
    # This part is always fresh (not cached)
    current_time = datetime.now().isoformat()
    
    return Response({
        'method': 'Partial/Fragment Cache',
        'cache_status': cache_status,
        'expensive_data': expensive_data,  # Cached
        'current_timestamp': current_time,  # Always fresh
        'note': 'Only expensive data is cached, timestamp is always fresh'
    })
