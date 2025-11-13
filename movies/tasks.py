from celery import shared_task
from time import sleep
from .models import Movie, Rating


# Heavy Task 1: Calculate movie statistics
@shared_task
def calculate_movie_stats(movie_id):
    """
    Heavy task: Calculate statistics for a movie
    Simulates intensive computation
    """
    sleep(5)  # Simulate heavy processing
    
    ratings = Rating.objects.filter(movie_id=movie_id)
    count = ratings.count()
    
    if count > 0:
        total = sum(r.rating for r in ratings)
        avg = total / count
        return {
            'movie_id': movie_id,
            'total_ratings': count,
            'average_rating': round(avg, 2),
            'message': 'Statistics calculated successfully'
        }
    
    return {'movie_id': movie_id, 'message': 'No ratings found'}


# Heavy Task 2: Bulk data processing
@shared_task
def process_bulk_ratings(user_id):
    """
    Heavy task: Process all ratings for a user
    Simulates data processing
    """
    sleep(8)  # Simulate heavy processing
    
    ratings = Rating.objects.filter(user_id=user_id)
    count = ratings.count()
    
    if count > 0:
        avg = sum(r.rating for r in ratings) / count
        return {
            'user_id': user_id,
            'total_ratings': count,
            'average_rating': round(avg, 2),
            'message': 'Bulk processing completed'
        }
    
    return {'user_id': user_id, 'message': 'No ratings found'}
