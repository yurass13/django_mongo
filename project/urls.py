from django.urls import path, include

urlpatterns = [
    path('_api/v1/', include('custom_forms.urls', namespace='custom_forms'))
]
