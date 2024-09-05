from django.db import models
import os, uuid
from django.utils.text import slugify
from django.contrib.auth.models import User
import magic

def data_scheme():
    return {}

# Models

class GenericMetadata(models.Model):
    generic_id = models.UUIDField(default = uuid.uuid4)
    created = models.DateTimeField(null=True)
    changed = models.DateTimeField(null=True)
    deleted = models.DateTimeField(null=True)
    active = models.BooleanField(default=True)
    owned_by_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True


class RawCsv(GenericMetadata):

    # https://gist.github.com/chhantyal/5370749
    def get_upload_path(self, filename):
        name, ext = os.path.splitext(filename)
        return os.path.join('raw', 'csv' , str(self.generic_id), slugify(name)) + ext
    
    name = models.CharField(max_length=1024, verbose_name="Name", help_text="")
    description = models.CharField(max_length=4096, verbose_name="Beschreibung", help_text="")
    attachment = models.FileField(null = True, blank = True, upload_to=get_upload_path, verbose_name="CSV Dokument", help_text="")
    data_scheme = models.JSONField(max_length=1024, verbose_name="Datenschema", help_text="", null=True)
    rows = models.IntegerField(verbose_name="Anzahl der Datenzeilen", null=True)
    
    def filename_from_attachment(self):
        return self.attachment.file.name.split('/')[-1]
    
    #def get_base64_attachment(self):
    #    return base64.b64encode(self.attachment.file.read()).decode('utf-8')

    def get_mime_type(self):
        """
        Get MIME by reading the header of the file
        """
        initial_pos = self.attachment.file.tell()
        self.attachment.file.seek(0)
        mime_type = magic.from_buffer(self.attachment.file.read(2048), mime=True)
        self.attachment.file.seek(initial_pos)
        return mime_type

    def __str__(self):
        """Returns a string representation of an RawCsv object."""
        return f"{ self.attachment }"
    

class OgcApiFeatures(GenericMetadata):
    title = models.CharField(max_length=1024, verbose_name="Titel", help_text="")
    base_uri = models.URLField(verbose_name="Basis-URL", help_text="", unique=True)

    def __str__(self):
        """Returns a string representation of the object"""
        return f"{ self.title }"


class OgcApiFeaturesCollection(GenericMetadata):
    title = models.CharField(max_length=1024, verbose_name="Titel", help_text="")
    name = models.CharField(max_length=1024, verbose_name="Name", help_text="")
    geom_type = models.CharField(max_length=1024, verbose_name="Geometrietyp", help_text="")
    data_example = models.JSONField(verbose_name="Beispieldatensatz", help_text="", null=True, editable=False)
    ogc_api_features = models.ForeignKey(OgcApiFeatures, on_delete=models.CASCADE, verbose_name="OGC API Features", help_text="", editable=False, null=True)

    def __str__(self):
        """Returns a string representation of the object"""
        return f"{ self.name }"
    

class GeoCoding(GenericMetadata):
    title = models.CharField(max_length=1024, verbose_name="Titel", help_text="")
    raw_csv = models.ForeignKey(RawCsv, on_delete=models.CASCADE, verbose_name="CSV-Datei")
    ogc_api_feature_collection = models.ForeignKey(OgcApiFeaturesCollection, on_delete=models.CASCADE, verbose_name="OGC API Feature Collection")
    feature_collection = models.JSONField(verbose_name="Geometrieobjekte", help_text="", null=True, editable=False)

    def __str__(self):
        """Returns a string representation of the object"""
        return f"{ self.title }"
    
    @property
    def number_of_features(self):
        if self.feature_collection:
            return len(self.feature_collection['features'])
        else:
            return 0
    

class GeoCodingResult(GenericMetadata):
    geo_coding = models.ForeignKey(GeoCoding, on_delete=models.CASCADE, verbose_name="Geocoding")
    line_number = models.IntegerField(verbose_name="Zeilennummer", help_text="", null=True, editable=False)
    result = models.BooleanField(verbose_name="Ergebnis", help_text="", null=True, editable=False)
    get_url = models.URLField(verbose_name="GET-Url", help_text="", null=True)
    error_message = models.JSONField(verbose_name="Fehlermeldung", help_text="", null=True, editable=False)
    geometry_object = models.JSONField(verbose_name="Geometrieobjekt", help_text="", null=True, editable=False)

    class Meta:
        ordering = ['line_number']

    """def get_queryset(self):
        queryset = self.model.objects.filter(
            owned_by_user=self.request.user
        )
        queryset = queryset.order_by('line_number')
        return queryset
    """

    def __str__(self):
        """Returns a string representation of the object"""
        return f"{ self.line_number }" + f"{ self.result }"
