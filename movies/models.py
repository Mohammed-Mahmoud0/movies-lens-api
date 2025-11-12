from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'genres'
        ordering = ['name']


class Movie(models.Model):
    movie_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=500)
    genres = models.ManyToManyField(Genre, related_name='movies', blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'movies'


class Rating(models.Model):
    user_id = models.IntegerField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings', to_field='movie_id')
    rating = models.FloatField()
    timestamp = models.BigIntegerField()
    
    def __str__(self):
        return f"User {self.user_id} - {self.movie.title} - {self.rating}"
    
    class Meta:
        db_table = 'ratings'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['rating']),
        ]


class Tag(models.Model):
    user_id = models.IntegerField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='tags', to_field='movie_id')
    tag = models.CharField(max_length=500)
    timestamp = models.BigIntegerField()
    
    def __str__(self):
        return f"{self.tag} - {self.movie.title}"
    
    class Meta:
        db_table = 'tags'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['tag']),
        ]


class Link(models.Model):
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE, related_name='links', to_field='movie_id', primary_key=True)
    imdb_id = models.CharField(max_length=20)
    tmdb_id = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"Links for {self.movie.title}"
    
    class Meta:
        db_table = 'links'
