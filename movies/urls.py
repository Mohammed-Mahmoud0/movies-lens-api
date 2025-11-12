from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    
    # Lab Question 1: N+1 Query Problem
    path('movies/n-plus-one/', views.movies_n_plus_one, name='movies-n-plus-one'),
    
    # Lab Question 2: Using select_related
    path('movies/select-related/', views.movies_select_related, name='movies-select-related'),
    
    # Lab Question 3: Using prefetch_related
    path('movies/prefetch-related/', views.movies_prefetch_related, name='movies-prefetch-related'),
    
    # Bonus: Combined optimization
    path('movies/combined/', views.movies_combined_optimization, name='movies-combined'),
]
