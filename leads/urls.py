from django.urls import path
from .views import (lead_create, 
    lead_create_view, lead_delete, lead_list, 
    lead_detail, lead_update, card_view, 
    loadlistView, LeadDetailView, lead_update_view, 
    lead_delete_view, AssignAgentView,
    categoryListView, CategoryDetailView,
    LeadCategoryUpdateView)


app_name = "leads"

urlpatterns = [
    path('', lead_list, name = 'lead-list'),
    path('card/', loadlistView.as_view(), name = 'lead-card-view'),
    path('<int:pk>/', LeadDetailView.as_view(), name='lead-detail'),
    path('<int:pk>/update/', lead_update_view.as_view(), name='lead-update'),
    path('<int:pk>/delete/', lead_delete_view.as_view(), name = 'lead-delete'),
    path('create/', lead_create_view.as_view(), name='lead-create'),
    path('<int:pk>/assign/', AssignAgentView.as_view(), name='lead-assign'),
    path('<int:pk>/assign_category/', LeadCategoryUpdateView.as_view(), name='lead-category-update'),
    path('categories/', categoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>', CategoryDetailView.as_view(), name='category-detail'),

]