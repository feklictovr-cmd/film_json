from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload_movie_file, name="upload_movie_file"),
    path("example/<str:extension>/", views.download_example, name="download_example"),
]
