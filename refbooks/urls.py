from django.urls import path

from refbooks.views import RefbookCheckElementView, RefbookElementsView, RefbookListView

app_name = 'refbooks'

urlpatterns = [
    path('refbooks/', RefbookListView.as_view(), name='refbook-list'),
    path('refbooks/<int:refbook_id>/elements', RefbookElementsView.as_view(), name='refbook-elements'),
    path('refbooks/<int:refbook_id>/check_element', RefbookCheckElementView.as_view(), name='refbook-check-element'),
]
