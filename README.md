# Movies API - Database Schema

## Schema

```
Genre(id PK, name UNIQUE)

Movie(movie_id PK, title)

Movie_Genres(id PK, movie_id FK->Movie.movie_id, genre_id FK->Genre.id)

Rating(id PK, user_id, movie_id FK->Movie.movie_id, rating, timestamp)

Tag(id PK, user_id, movie_id FK->Movie.movie_id, tag, timestamp)

Link(movie_id PK FK->Movie.movie_id, imdb_id, tmdb_id)
```

## Relationships

- Movie ↔ Genre: Many-to-Many (via Movie_Genres)
- Movie → Rating: One-to-Many
- Movie → Tag: One-to-Many
- Movie ↔ Link: One-to-One