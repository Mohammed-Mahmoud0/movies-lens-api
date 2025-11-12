from rest_framework import serializers
from .models import Movie, Rating, Tag, Link, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ['imdb_id', 'tmdb_id']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'user_id', 'movie', 'rating', 'timestamp']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'user_id', 'movie', 'tag', 'timestamp']


class MovieListSerializer(serializers.ModelSerializer):
    """Simple serializer for movie list view"""
    genres = GenreSerializer(many=True, read_only=True)
    
    class Meta:
        model = Movie
        fields = ['movie_id', 'title', 'genres']


class MovieDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with related data"""
    genres = GenreSerializer(many=True, read_only=True)
    links = LinkSerializer(read_only=True)
    ratings = RatingSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = ['movie_id', 'title', 'genres', 'links', 'average_rating', 
                  'ratings_count', 'ratings', 'tags']
    
    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings:
            return round(sum(r.rating for r in ratings) / len(ratings), 2)
        return None
    
    def get_ratings_count(self, obj):
        return obj.ratings.count()
