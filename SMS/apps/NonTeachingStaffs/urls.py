from django.urls import path
from .views import (
    NonTeachingStaffsListView,
    NonTeachingStaffsDetailView,
    NonTeachingStaffsCreateView,
    NonTeachingStaffsUpdateView,
    NonTeachingStaffsDeleteView,
)

urlpatterns = [
    path("list/", NonTeachingStaffsListView.as_view(), name="non-teaching-staffs-list"),
    path("<int:pk>/", NonTeachingStaffsDetailView.as_view(), name="non-teaching-staffs-detail"),
    path("create/", NonTeachingStaffsCreateView.as_view(), name="non-teaching-staffs-create"),
    path("<int:pk>/update/", NonTeachingStaffsUpdateView.as_view(), name="non-teaching-staffs-update"),
    path("<int:pk>/delete/", NonTeachingStaffsDeleteView.as_view(), name="non-teaching-staffs-delete"),
]
