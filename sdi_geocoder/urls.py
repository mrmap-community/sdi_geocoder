from django.urls import path
from sdi_geocoder import views
from django.contrib.auth import views as auth_views
from sdi_geocoder.views import CsvListView, CsvCreateView, CsvUpdateView, CsvDeleteView
from sdi_geocoder.views import OgcApiFeaturesListView, OgcApiFeaturesCreateView, OgcApiFeaturesUpdateView, OgcApiFeaturesDeleteView
from sdi_geocoder.views import GeoCodingListView, GeoCodingCreateView, GeoCodingUpdateView, GeoCodingDeleteView
from sdi_geocoder.views import GeoCodingResultListView
from sdi_geocoder.views import OgcApiFeaturesCollectionListView


urlpatterns = [
    path("home/", views.home, name="home"),
    path("about/", views.home, name="about"),
    path("contact/", views.home, name="contact"),
    path("accounts/login/", auth_views.LoginView.as_view(next_page="home"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="home"), name='logout'),
    # https://dev.to/donesrom/how-to-set-up-django-built-in-registration-in-2023-41hg
    path("register/", views.register, name = "register"),

    # path("csv/upload/", views.geocoder_csv_upload, name="geocoder-csv-upload"),
    
    path("csv/", CsvListView.as_view(), name="csv-list"),
    path("csv/create/", CsvCreateView.as_view(), name="csv-create"),
    path("csv/<int:pk>/update/", CsvUpdateView.as_view(), name="csv-update"),
    path("csv/<int:pk>/delete/", CsvDeleteView.as_view(), name="csv-delete"),

    path("geocoding/", GeoCodingListView.as_view(), name="geocoding-list"),
    path("geocoding/create", GeoCodingCreateView.as_view(), name="geocoding-create"),
    path("geocoding/<int:pk>/update", GeoCodingUpdateView.as_view(template_name="sdi_geocoder/geocoding_form_update.html"), name="geocoding-update"),
    path("geocoding/<int:pk>/delete", GeoCodingDeleteView.as_view(template_name="sdi_geocoder/geocoding_confirm_delete.html"), name="geocoding-delete"),

    path("geocoding/<int:pk>/geometries/", views.geocoding_geometries, name="geocoding-geometries"),
    path("geocoding/<int:pk>/public/geometries/", views.geocoding_public_geometries, name="geocoding-public-geometries"),

    path("geocoding/<int:pk>/geocodingresult/", GeoCodingResultListView.as_view(template_name="sdi_geocoder/geocoding_result_list.html"), name="geocodingresult-list"),
    path("geocoding/<int:pk>/geocodingresult/csv/", views.geocodingresult_csv, name="geocodingresult-list-csv"),

    path("oaf/", OgcApiFeaturesListView.as_view(template_name="sdi_geocoder/oaf_list.html"), name="oaf-list"),
    path("oaf/create/", OgcApiFeaturesCreateView.as_view(template_name="sdi_geocoder/oaf_form.html"), name="oaf-create"),
    path("oaf/<int:pk>/update/", OgcApiFeaturesUpdateView.as_view(template_name="sdi_geocoder/oaf_form_update.html"), name="oaf-update"),
    path("oaf/<int:pk>/delete/", OgcApiFeaturesDeleteView.as_view(template_name="sdi_geocoder/oaf_confirm_delete.html"), name="oaf-delete"),

    path("collections/", OgcApiFeaturesCollectionListView.as_view(template_name="sdi_geocoder/oaf_collection_list.html"), name="oaf-collection-list"),
    path("collections/<int:pk>/example/csv/", views.oaf_collection_example_csv, name="oaf-collection-example-csv"),

    path("", views.home, name="home"),
]