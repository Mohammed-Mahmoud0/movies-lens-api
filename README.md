# Movies Lens API - Django Advanced Project# Movies API - Database Schema



Django REST API demonstrating ORM optimization, caching, profiling, and asynchronous tasks.## Schema



---```

Genre(id PK, name UNIQUE)

## What We Built

Movie(movie_id PK, title)

### 1. Query Optimization

- **N+1 Problem Demo** - Shows the issue (11 queries)Movie_Genres(id PK, movie_id FK->Movie.movie_id, genre_id FK->Genre.id)

- **select_related()** - Fixed with JOIN (1 query)

- **prefetch_related()** - Optimized ManyToMany (3 queries)Rating(id PK, user_id, movie_id FK->Movie.movie_id, rating, timestamp)

- **Result**: 91% query reduction

Tag(id PK, user_id, movie_id FK->Movie.movie_id, tag, timestamp)

### 2. Advanced ORM Features

- **Q()** - Complex filters (AND/OR/NOT)Link(movie_id PK FK->Movie.movie_id, imdb_id, tmdb_id)

- **F()** - SQL-level updates without Python```

- **only()/defer()** - Select specific fields

- **values()/values_list()** - Return dict/tuple## Relationships

- **Database Indexes** - Performance boost

- **CONN_MAX_AGE** - Connection pooling (600 sec)- Movie ↔ Genre: Many-to-Many (via Movie_Genres)

- Movie → Rating: One-to-Many

### 3. Caching with Redis- Movie → Tag: One-to-Many

- Manual caching with cache.get/set- Movie ↔ Link: One-to-One
- Per-view caching (entire response)
- Partial/fragment caching (specific data)

### 4. Profiling & Monitoring
- **Django Debug Toolbar** - SQL query inspection
- **Django Silk** - Request/response profiling
- **cProfile** - Python function timing

### 5. Celery - Background Tasks
- 2 heavy tasks (5-8 seconds each)
- Tasks run in background
- Response returns immediately
- Monitor with Flower

### 6. Celery Beat - Scheduled Tasks
- **Task 1**: Runs every 3 minutes (configured in code)
- **Task 2**: Interval-based (configured via admin)
- **Task 3**: Specific time (configured via admin)

---

## Tech Stack

**Backend**: Django 5.2, Django REST Framework  
**Cache & Broker**: Redis  
**Tasks**: Celery, Celery Beat, Flower  
**Profiling**: Django Silk, Debug Toolbar, cProfile  
**Database**: SQLite

---

## Quick Start

### 1. Install Dependencies
```bash
pip install django djangorestframework redis celery flower django-celery-beat django-debug-toolbar django-silk
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Start Services

**Django Server:**
```bash
python manage.py runserver
```

**Redis:**
```bash
redis-server
```

**Celery Worker:**
```bash
celery -A movies_api worker --loglevel=info --pool=solo
```

**Celery Beat (for scheduled tasks):**
```bash
celery -A movies_api beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Flower (monitoring):**
```bash
celery -A movies_api flower
```

---

## Key Endpoints

### API Root
`GET /api/` - Lists all endpoints

### Query Optimization
- `/api/movies/n-plus-one/` - N+1 problem (11 queries)
- `/api/movies/select-related/` - Optimized (1 query)
- `/api/movies/prefetch-related/` - Optimized (3 queries)

### Advanced ORM
- `/api/movies/q-filters/` - Q() expressions
- `/api/movies/f-update/` - F() updates (POST)
- `/api/movies/only/` - only() method
- `/api/movies/values/` - Data as dict
- `/api/movies/values-list/` - Data as tuple
- `/api/movies/index-compare/` - Index performance

### Caching
- `/api/cache/manual/` - Manual caching
- `/api/cache/per-view/` - View caching
- `/api/cache/partial/` - Fragment caching

### Background Tasks
- `/api/celery/task1/` - Heavy task 1 (5 sec)
- `/api/celery/task2/` - Heavy task 2 (8 sec)

### Monitoring
- **Admin**: http://127.0.0.1:8000/admin/
- **Silk**: http://127.0.0.1:8000/silk/
- **Flower**: http://localhost:5555

---

## Database Schema

```
Genre(id, name)
Movie(movie_id, title)
Rating(id, user_id, movie_id, rating, timestamp)
Tag(id, user_id, movie_id, tag, timestamp)
Link(movie_id, imdb_id, tmdb_id)
```

**Relationships:**
- Movie ↔ Genre: ManyToMany
- Movie → Rating: OneToMany
- Movie → Tag: OneToMany
- Movie ↔ Link: OneToOne

---

## Configuration

### Redis
- **Cache**: redis://127.0.0.1:6379/1
- **Celery Broker**: redis://127.0.0.1:6379/0
- **Celery Results**: redis://127.0.0.1:6379/0

### Database Indexes
- Movie.title ✓
- Rating.user_id ✓ (indexed)
- Rating.rating ✓
- Rating.timestamp ✗ (NOT indexed - for comparison)
- Link.imdb_id ✓

### Celery Settings
- Serializer: JSON
- Task time limit: 30 minutes
- Pool: solo (for Windows)

---

## What You Learn

✓ Identify and fix N+1 query problems  
✓ Use select_related & prefetch_related  
✓ Build complex queries with Q()  
✓ Perform SQL-level updates with F()  
✓ Add strategic database indexes  
✓ Implement caching strategies  
✓ Profile queries with Silk and Debug Toolbar  
✓ Run tasks in background with Celery  
✓ Schedule periodic tasks with Celery Beat  
✓ Monitor tasks with Flower  

---

## Project Structure

```
movies-lens-api/
├── movies/
│   ├── models.py            # Database models
│   ├── views.py             # API endpoints
│   ├── tasks.py             # Celery tasks
│   ├── urls.py              # URL routing
│   └── admin.py             # Admin configuration
├── movies_api/
│   ├── settings.py          # Project configuration
│   ├── celery.py            # Celery app & beat schedule
│   └── urls.py              # Main URL routing
├── start_celery_worker.bat  # Start worker script
├── start_celery_beat.bat    # Start beat script
├── start_flower.bat         # Start flower script
└── db.sqlite3               # SQLite database
```

---

## Results Achieved

### Query Optimization
- N+1 queries: 11 → 1 query (91% reduction)
- Prefetch queries: 21 → 3 queries (86% reduction)

### Performance
- Added 5 database indexes
- Connection pooling: 600 seconds
- Indexed queries: ~10× faster than non-indexed

### Caching
- Cache hit: Instant response
- Cache miss: Full processing + cache store

### Background Tasks
- Response time: Immediate (task runs async)
- Task execution: 5-8 seconds in background
- Monitoring: Real-time via Flower

---

**ITI Django Advanced Course Project**
