from django.urls import path
from . import views

urlpatterns = [
    path('registration/', views.RegistrationUserView.as_view(), name='registration'),
    path('login/', views.LoginUserView.as_view(), name='user-login'),
    path('documents/', views.DocumentsView.as_view(), name='documents'),
    path('document/<int:pk>/', views.DocumentCRUD.as_view(), name='document-CRUD'),
    path('document/download/<int:pk>/', views.DocumentDownload.as_view(), name='download'),
    path('document/share/<int:pk>/', views.DocumentShareView.as_view(), name='document-share'),
    path('document/search/', views.DocumentSearchView.as_view(), name='document-search'),
]