from django.urls import path, re_path
import store.views as views

urlpatterns = [
    path('', views.StoreView.as_view(), name='home'),
    path('search/', views.SearchBaseItemView.as_view(), name='search_items'),
    re_path('api/suggestions/', views.SearchBaseItemSuggestionView.as_view(), name='search_suggestion'),
    path('my/folders/', views.MyFoldersView.as_view(), name='my_folders'),
    path('folder/<slug:folder_slug>/', views.FolderDetailView.as_view(), name='detail_folder'),
    path('delete/folder/<slug:folder_slug>/', views.DeleteFolderView.as_view(), name='delete_folder'),
    path('new/folder/', views.CreateItemFolderView.as_view(), name='new_folder'),
    path('new/item/<slug:folder_slug>/', views.NewBaseItemView.as_view(), name='new_item'),
    path('add/size/<int:pk>/', views.AddSizeFood.as_view(), name='add_size'),
    path('add/flavor/<slug:folder_slug>/', views.AddNewFlavorView.as_view(), name='add_flavor'),
    path('delete/item/<int:pk>/', views.DeleteItemView.as_view(), name='delete_item'),
    path('item/<slug:folder_slug>/<int:pk>/', views.ItemDetailView.as_view(), name='detail_item'),
    path('update/item/<int:pk>/', views.UpdateBaseItemView.as_view(), name='update_item'),
    path('<slug:animal_slug>/<slug:type_food_slug>/', views.ShowCategoryByTypeOfFood.as_view(), name='food_animal_cat'),
    path('<slug:slug>/', views.ShowCategoryByAnimal.as_view(), name='cat_animal'),
]
