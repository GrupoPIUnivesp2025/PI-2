from django.urls import path
from . import views
from . import views_feedback

urlpatterns = [
    path('', views.index, name='index'),
    path('polos/', views.PoloListView.as_view(), name='polo_list'),
    path('polo/<int:pk>/', views.PoloDetailView.as_view(), name='polo_detail'),
    path('polo/novo/', views.PoloCreateView.as_view(), name='polo_create'),
    path('polo/<int:pk>/editar/', views.PoloUpdateView.as_view(), name='polo_update'),
    path('busca/', views.busca_por_cep, name='busca_polo'),
    path('acessibilidade/', views.acessibilidade, name='acessibilidade'),
    path('feedback/', views_feedback.submit_feedback, name='submit_feedback'),
]
