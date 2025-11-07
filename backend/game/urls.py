"""
URL configuration for game app.
"""

from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('api/game/new/', views.new_game, name='new_game'),
    path('api/game/<str:game_id>/move/', views.make_move, name='make_move'),
    path('api/game/<str:game_id>/state/', views.get_state, name='get_state'),
    path('api/game/<str:game_id>/ai-move/', views.ai_move, name='ai_move'),
    path('api/game/<str:game_id>/reset/', views.reset_game, name='reset_game'),
]

