from django.contrib import admin
from .models import Movie, Rating, Tag, Link, Genre


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['movie_id', 'title', 'get_genres']
    search_fields = ['title']
    list_filter = ['genres']
    filter_horizontal = ['genres']
    
    def get_genres(self, obj):
        return ", ".join([g.name for g in obj.genres.all()])
    get_genres.short_description = 'Genres'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'movie', 'rating', 'timestamp']
    list_filter = ['rating']
    search_fields = ['movie__title']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'movie', 'tag', 'timestamp']
    search_fields = ['tag', 'movie__title']


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['movie', 'imdb_id', 'tmdb_id']
    search_fields = ['movie__title', 'imdb_id', 'tmdb_id']
