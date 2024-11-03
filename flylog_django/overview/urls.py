from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.FlightCreateView.as_view(), name='create'),
    path('create_from_igc/', views.FlightCreateFromIGCView.as_view(), name='create-from-igc'),
    path('photos/', views.PhotosView.as_view(), name='photos'),
    path('<pk>/detail/', views.FlightDetailView.as_view(), name='detail'),
    path('<pk>/delete/', views.FlightDeleteView.as_view(), name='delete'),
    path('<pk>/update/', views.FlightUpdateView.as_view(), name='update'),
    path('<pk>/add-image/', views.FlightAddImageView.as_view(), name='add-image'),
    path('<pk>/delete-image/', views.FlightDeleteImageView.as_view(), name='delete-image'),
    path('<pk>/add-video/', views.FlightAddVideoView.as_view(), name='add-video'),
    path('<pk>/delete-video/', views.FlightDeleteVideoView.as_view(), name='delete-video'),
]
