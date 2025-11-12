import csv
from django.core.management.base import BaseCommand
from movies.models import Movie, Rating, Tag, Link, Genre


class Command(BaseCommand):
    help = 'Import movie data from CSV files'

    def handle(self, *args, **options):
        self.stdout.write('Extracting and importing genres...')
        movies_file = r'Movie db\movies.csv'
        genres_set = set()
        
        with open(movies_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                genre_list = row['genres'].split('|')
                genres_set.update(genre_list)
        
        genres_to_create = [Genre(name=g) for g in genres_set if g]
        Genre.objects.bulk_create(genres_to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(genres_to_create)} genres'))
        
        genre_lookup = {g.name: g for g in Genre.objects.all()}
        
        self.stdout.write('Importing movies...')
        with open(movies_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            movies_to_create = []
            movie_genres_map = {}
            
            for row in reader:
                movie_id = int(row['movieId'])
                movies_to_create.append(Movie(
                    movie_id=movie_id,
                    title=row['title']
                ))
                genre_names = [g for g in row['genres'].split('|') if g]
                movie_genres_map[movie_id] = genre_names
            
            Movie.objects.bulk_create(movies_to_create, batch_size=1000)
            self.stdout.write(f'Created {len(movies_to_create)} movies')
            
            self.stdout.write('Adding genre relationships...')
            through_model = Movie.genres.through
            relationships = []
            
            for movie_id, genre_names in movie_genres_map.items():
                for genre_name in genre_names:
                    if genre_name in genre_lookup:
                        relationships.append(through_model(
                            movie_id=movie_id,
                            genre_id=genre_lookup[genre_name].id
                        ))
            
            through_model.objects.bulk_create(relationships, batch_size=1000)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(movies_to_create)} movies with {len(relationships)} genre relationships'))

        self.stdout.write('Importing links...')
        links_file = r'Movie db\links.csv'
        with open(links_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            links_to_create = []
            for row in reader:
                tmdb_id = row['tmdbId'] if row['tmdbId'] else None
                links_to_create.append(Link(
                    movie_id=int(row['movieId']),
                    imdb_id=row['imdbId'],
                    tmdb_id=tmdb_id
                ))
            Link.objects.bulk_create(links_to_create, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(links_to_create)} links'))

        self.stdout.write('Importing ratings (this may take a while)...')
        ratings_file = r'Movie db\ratings.csv'
        with open(ratings_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            ratings_to_create = []
            count = 0
            for row in reader:
                ratings_to_create.append(Rating(
                    user_id=int(row['userId']),
                    movie_id=int(row['movieId']),
                    rating=float(row['rating']),
                    timestamp=int(row['timestamp'])
                ))
                count += 1
                if count % 10000 == 0:
                    Rating.objects.bulk_create(ratings_to_create, batch_size=1000)
                    self.stdout.write(f'Imported {count} ratings...')
                    ratings_to_create = []
            if ratings_to_create:
                Rating.objects.bulk_create(ratings_to_create, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} ratings'))

        self.stdout.write('Importing tags...')
        tags_file = r'Movie db\tags.csv'
        with open(tags_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            tags_to_create = []
            for row in reader:
                tags_to_create.append(Tag(
                    user_id=int(row['userId']),
                    movie_id=int(row['movieId']),
                    tag=row['tag'],
                    timestamp=int(row['timestamp'])
                ))
            Tag.objects.bulk_create(tags_to_create, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(tags_to_create)} tags'))

        self.stdout.write(self.style.SUCCESS('All data imported successfully!'))
