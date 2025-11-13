from django.urls import path
from . import views

urlpatterns = [
    # API Root - shows all available endpoints
    path("", views.api_root, name="api-root"),
    # Optimization Endpoints
    path("movies/n-plus-one/", views.movies_n_plus_one, name="movies-n-plus-one"),
    path(
        "movies/select-related/",
        views.movies_select_related,
        name="movies-select-related",
    ),
    path(
        "movies/prefetch-related/",
        views.movies_prefetch_related,
        name="movies-prefetch-related",
    ),
    # Advanced ORM Features
    path("movies/q-filters/", views.movies_with_q_filters, name="movies-q-filters"),
    path("movies/f-update/", views.update_with_f_expression, name="movies-f-update"),
    path("movies/only/", views.movies_with_only, name="movies-only"),
    path("movies/defer/", views.movies_with_defer, name="movies-defer"),
    path("movies/values/", views.movies_as_dict, name="movies-values"),
    path("movies/values-list/", views.movies_as_tuples, name="movies-values-list"),
    path(
        "movies/index-compare/",
        views.compare_indexed_vs_non_indexed,
        name="movies-index-compare",
    ),
    # Cache Examples
    path("cache/manual/", views.cache_manual_example, name="cache-manual"),
    path("cache/per-view/", views.cache_per_view_example, name="cache-per-view"),
    path("cache/partial/", views.cache_partial_example, name="cache-partial"),
    
    # Celery Background Tasks - Simple GET requests
    path("celery/task1/", views.test_heavy_task_1, name="celery-task1"),
    path("celery/task2/", views.test_heavy_task_2, name="celery-task2"),
]
