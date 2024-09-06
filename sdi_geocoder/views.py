import csv, os, base64
from sdi_geocoder.forms import UploadForm
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.shortcuts import redirect
from io import BytesIO, TextIOWrapper
import requests, json
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.utils.timezone import datetime
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from sdi_geocoder.models import RawCsv, OgcApiFeatures, OgcApiFeaturesCollection, GeoCoding, GeoCodingResult
from sdi_geocoder.forms import RegistrationForm
from django.urls import reverse_lazy
from django.conf import settings
# Create your views here.

def home(request):
    return render(request, "sdi_geocoder/home.html")

def about(request):
    return render(request, "sdi_geocoder/about.html")

def contact(request):
    return render(request, "sdi_geocoder/contact.html")

# https://dev.to/balt1794/registration-page-using-usercreationform-django-part-1-21j7
def register(request):
    if request.method != 'POST':
        form = RegistrationForm()
    else:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            #
            user = form.save()
            login(request, user)
            #
            return redirect('home')
        else:
            print('form is invalid')
    context = {'form': form}

    return render(request, 'registration/register.html', context)


def decode_utf8(line_iterator):
    for line in line_iterator:
        yield line.decode('utf-8')

@login_required
def geocodingresult_csv(request, pk):
    try:
        geocoding_results = GeoCodingResult.objects.filter(owned_by_user=request.user, geo_coding=pk)
    except geocoding_results.DoesNotExist:
        geocoding_results = None
        return HttpResponse("No GeoCodingResult found", status=404) 
    if geocoding_results:
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="geocoding_results.csv"'},
        )
        writer = csv.writer(response, delimiter='|')
        writer.writerow(["zeile", "located", "url"])
        for geocoding_result in geocoding_results:
            writer.writerow([
                geocoding_result.line_number, 
                geocoding_result.result, 
                geocoding_result.get_url,
                             ])
        return response
    else:
        return HttpResponse("No geocodingresults found", status=404) 

def oaf_collection_example_csv(request, pk):
    try:
        oaf_collection = OgcApiFeaturesCollection.objects.filter(pk=pk)
    except oaf_collection.DoesNotExist:
        oaf_collection = None
        return HttpResponse("No GeoCodingResult found", status=404) 
    if oaf_collection:
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="oaf_collection_' + oaf_collection[0].name + '.csv"'},
        )
        writer = csv.writer(response, delimiter='|')
        header = []
        for key in oaf_collection[0].data_example['properties']:
            header.append(key)
        writer.writerow(header)
        data_line = []
        for value in oaf_collection[0].data_example['properties'].values():
            data_line.append(value)
        writer.writerow(data_line)
        return response
    else:
        return HttpResponse("No info about collection found", status=404) 


"""def geocoder_csv_upload(request):
    print("form invoked")
    if request.method == 'GET':
        print("GET")
        form = UploadForm()
        return render(request, 'sdi_geocoder/upload_csv.html', {'form': form})

    form = UploadForm(request.POST, request.FILES)

    # Validate the form
    if form.is_valid():
        
        # Get the correct type string instead of byte without reading full file into memory with a generator to decode line by line
        geocoder_file = csv.reader(decode_utf8(request.FILES['sent_file']), delimiter='|')
        csv_array = enumerate(geocoder_file)
        header_array = next(geocoder_file)
        #print("header: " + str(header_array))
        base_uri = "https://www.geoportal.rlp.de/spatial-objects/519/collections"
        collection = "ave:Flurstueck"
        #base_uri + "/" + collection + "/items?f=json&" + query_string 

        # Define template for FeatureCollection to return
        #  
        
        result_collection = {
            'type': 'FeatureCollection',
            'features': [],
        }
        number_of_feature = 0
        for counter, line in csv_array:
            param_dict = {}
            query_string = ""
            column = 0
            param_dict['f'] = 'json'
            for element in line:
                if header_array[column] == "flurschl":
                    element = "0" + element
                query_string = query_string + header_array[column] + "=" + element + "&"
                param_dict[header_array[column]] = element
                column = column + 1
                
            # print(query_string)
            url = base_uri + "/" + collection + "/items?f=json&" + query_string 
            base_uri_2 = base_uri + "/" + collection + "/items"
            # print(str(param_dict))

            print(str(number_of_feature))
            print(url)
            resp = requests.get(url=base_uri_2, params=param_dict)
            print(resp.status_code)
            #print(resp.text)
            data = resp.json()
            print("Found " + str(len(data['features'])) + " Objects")
            # get geojson object from service and add other columns to json
            if len(data['features']) == 1:
                # append keys from csv, that does not already exists in dataset
                column = 0
                for element in line:
                    if not header_array[column] in data['features'][0]['properties'].keys():
                        data['features'][0]['properties'][header_array[column]] = element
                    column = column + 1
                result_collection['features'].append(data['features'][0])
            number_of_feature = number_of_feature + 1
        # print(json.dumps(result_collection))
        f = open("result.geojson", 'w', encoding='utf-8')
        json.dump(result_collection, f, ensure_ascii=False, indent=4)
        f.close()

        #next(geocoder_file)  # Skip header row

        #for counter, line in enumerate(geocoder_file):
        #    print(str(line[0]))
        messages.success(request, 'Uploaded successfully!')

        return redirect('home')
"""
        
@login_required
def geocoding_geometries(request, pk):
    try:
        geocoding = GeoCoding.objects.get(owned_by_user=request.user, pk=pk)
    except GeoCoding.DoesNotExist:
        geocoding = None
    if geocoding:
        if geocoding.feature_collection:
            response = JsonResponse(geocoding.feature_collection, status=200)
            response['Access-Control-Allow-Origin'] = '*'
            response['cross-origin-resource-policy'] = 'cross-origin'
            return response
        else:
           return HttpResponse("Geometries not found", status=404) 
    else:
        return HttpResponse("Object not found", status=404)



# My default view classes
class MyCreateView(LoginRequiredMixin, CreateView):

    def form_valid(self, form):
        form.instance.created = datetime.now()
        form.instance.changed = datetime.now()
        form.instance.owned_by_user = self.request.user
        return super().form_valid(form)


class MyListView(LoginRequiredMixin, ListView):

    def get_queryset(self):
        return self.model.objects.filter(
            owned_by_user=self.request.user
        ).order_by('-created')


class MyUpdateView(LoginRequiredMixin, UpdateView):
     
     def form_valid(self, form):
        if form.instance.owned_by_user == self.request.user:
            form.instance.changed = datetime.now()
            return super().form_valid(form)
        else:
            return HttpResponse("Object not owned by logged in user!", status=401)


class MyDeleteView(LoginRequiredMixin, DeleteView):

    def form_valid(self, form):
        object = self.get_object()
        if object.owned_by_user == self.request.user:
            return super().form_valid(form)
        else:
            return HttpResponse("Object not owned by logged in user!", status=401)


class MyDetailView(LoginRequiredMixin, DetailView):

    def get_queryset(self):
        return self.model.objects.filter(
            owned_by_user=self.request.user
        ).order_by('-created')
    

class CsvCreateView(MyCreateView):
    model = RawCsv
    fields = ["name", "description", "attachment"]
    
    # reduce choices for invoice to own invoices    
    # https://stackoverflow.com/questions/48089590/limiting-choices-in-foreign-key-dropdown-in-django-using-generic-views-createv
    
    def get_form_kwargs(self):
        form = super().get_form_kwargs()
        form['initial'].update({'owned_by_user': self.request.user})
        return form
    
    def form_valid(self, form):
        # extract header to store it in database
        f = TextIOWrapper(form.cleaned_data.get('attachment').file, encoding='UTF-8')
        geocoder_file = csv.reader(f, delimiter='|')
        header_array = next(geocoder_file)            
        form.instance.data_scheme = header_array
        # get number of lines
        max_rows = 2000
        row_count = sum(1 for row in geocoder_file)
        if row_count > max_rows:
            return HttpResponse("Die maximale Zahl von " + str(max_rows)+ " Zeilen  ist überschritten!", status=422) 
        else:
            form.instance.rows = row_count
            return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy("csv-list")   
    

class CsvListView(MyListView):
    """Renders the InvoiceLines"""
    model = RawCsv


class CsvUpdateView(MyUpdateView):
    model = RawCsv
    fields = ["name", "description", "attachment"] 

    def form_valid(self, form):
        # extract header to store it in database
        f = TextIOWrapper(form.cleaned_data.get('attachment').file, encoding='UTF-8')
        geocoder_file = csv.reader(f, delimiter='|')
        header_array = next(geocoder_file)            
        form.instance.data_scheme = header_array
        # get number of lines
        max_rows = 200
        row_count = sum(1 for row in geocoder_file)
        if row_count > max_rows:
            return HttpResponse("Die maximale Zahl von " + str(max_rows)+ " Zeilen  ist überschritten!", status=422) 
        else:
            form.instance.rows = row_count
            return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("csv-list")


class CsvDeleteView(MyDeleteView):
    model = RawCsv

    def get_success_url(self):
        return reverse_lazy("csv-list")


class OgcApiFeaturesCreateView(MyCreateView, PermissionRequiredMixin):
    model = OgcApiFeatures
    fields = ["base_uri"]
    permission_required = ["ogcapifeatures.can_create"]
    
    # reduce choices for invoice to own invoices    
    # https://stackoverflow.com/questions/48089590/limiting-choices-in-foreign-key-dropdown-in-django-using-generic-views-createv
    
    def get_form_kwargs(self):
        form = super().get_form_kwargs()
        form['initial'].update({'owned_by_user': self.request.user})
        return form
    
    def form_valid(self, form):
        base_uri = form.cleaned_data["base_uri"]
        param_dict = {'f': 'json'}
        resp = requests.get(url=base_uri, params=param_dict, proxies=settings.PROXIES)
        data = resp.json()
        # get collections
        #print("Found " + str(len(data['collections'])) + " collections")
        if len(data['collections']) > 0:
            # create oaf object
            oaf = OgcApiFeatures(base_uri=base_uri, title=data['title'], owned_by_user=self.request.user, created=datetime.now())
            oaf.save()
            primary_key = oaf.pk
            # parse collections
            for collection in data['collections']:
                param_dict = {'f': 'json', 'limit': '1'}
                resp = requests.get(url=base_uri + '/collections/' + collection['name'] + '/items', params=param_dict, proxies=settings.PROXIES)
                example_object = resp.json()
                #print(str(example_object))
                # parse example object and extract schema
                # https://stackoverflow.com/questions/76758745/how-to-determine-data-types-of-multiple-dictionary-values-in-a-json-file-when-so
                #properties = []
                #for property in example_object['features'][0]['properties']:
                #    properties.append(property)
                # test if collection already exists
                oaf_collection = OgcApiFeaturesCollection.objects.filter(name=collection['name'], 
                                                          ogc_api_features=OgcApiFeatures.objects.get(pk=primary_key), 
                                                          owned_by_user=self.request.user,
                                                          )
                if oaf_collection:
                    # update collection
                    oaf_collection_primary_key = oaf_collection[0].pk
                    obj = OgcApiFeaturesCollection.objects.get(pk=oaf_collection_primary_key)
                    setattr(obj, 'title', collection['title'])
                    setattr(obj, 'geom_type', example_object['features'][0]['geometry']['type'])
                    setattr(obj, 'changed', datetime.now())
                    setattr(obj, 'data_example', example_object['features'][0])
                    obj.save()
                else:
                    oaf_collection = OgcApiFeaturesCollection(title=collection['title'],
                                                              name=collection['name'],
                                                              geom_type=example_object['features'][0]['geometry']['type'],
                                                              created=datetime.now(), owned_by_user=self.request.user,
                                                              ogc_api_features = OgcApiFeatures.objects.get(pk=primary_key),
                                                              data_example=example_object['features'][0],
                                                              )
                    oaf_collection.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponse("JSON from landing page could not be parsed!", status=507) 

    def get_success_url(self):
        return reverse_lazy("oaf-list")   
    

class OgcApiFeaturesListView(MyListView, PermissionRequiredMixin):
    """Renders the InvoiceLines"""
    model = OgcApiFeatures
    permission_required = ["ogcapifeatures.can_view"]


class OgcApiFeaturesUpdateView(MyUpdateView, PermissionRequiredMixin):
    model = OgcApiFeatures
    fields = ["base_uri"] 
    permission_required = ["ogcapifeatures.can_edit"]

    def form_valid(self, form):
        base_uri = form.cleaned_data["base_uri"]
        param_dict = {'f': 'json'}
        resp = requests.get(url=base_uri, params=param_dict, proxies=settings.PROXIES)
        data = resp.json()
        # get collections
        if len(data['collections']) > 0:
            # create oaf object if not already exists! check base_uri
            oaf = OgcApiFeatures.objects.filter(base_uri=base_uri, 
                                                          owned_by_user=self.request.user,
                                                          )
            if oaf:
                oaf_primary_key = oaf[0].pk
                obj = oaf[0]
                setattr(obj, 'title', data['title'])
                setattr(obj, 'changed', datetime.now())
                obj.save()
                primary_key = oaf_primary_key
            else:
                oaf = OgcApiFeatures(base_uri=base_uri, title=data['title'], owned_by_user=self.request.user, created=datetime.now())
                oaf.save()
                primary_key = oaf.pk
            # parse collections
            for collection in data['collections']:
                param_dict = {'f': 'json', 'limit': '1'}
                resp = requests.get(url=base_uri + '/collections/' + collection['name'] + '/items', params=param_dict, proxies=settings.PROXIES)
                example_object = resp.json()
                # test if collection already exists
                oaf_collection = OgcApiFeaturesCollection.objects.filter(name=collection['name'], 
                                                          ogc_api_features=OgcApiFeatures.objects.get(pk=primary_key), 
                                                          owned_by_user=self.request.user,
                                                          )
                if oaf_collection:
                    # update collection
                    oaf_collection_primary_key = oaf_collection[0].pk
                    obj = OgcApiFeaturesCollection.objects.get(pk=oaf_collection_primary_key)
                    setattr(obj, 'title', collection['title'])
                    setattr(obj, 'geom_type', example_object['features'][0]['geometry']['type'])
                    setattr(obj, 'changed', datetime.now())
                    setattr(obj, 'data_example', example_object['features'][0])
                    obj.save()
                else:
                    oaf_collection = OgcApiFeaturesCollection(title=collection['title'],
                                                              name=collection['name'],
                                                              geom_type=example_object['features'][0]['geometry']['type'],
                                                              created=datetime.now(),
                                                              owned_by_user=self.request.user,
                                                              ogc_api_features = OgcApiFeatures.objects.get(pk=primary_key),
                                                              data_example=example_object['features'][0]
                                                              )
                    oaf_collection.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return HttpResponse("JSON from landing page could not be parsed!", status=507) 

    def get_success_url(self):
        return reverse_lazy("oaf-list")


class OgcApiFeaturesDeleteView(MyDeleteView, PermissionRequiredMixin):
    model = OgcApiFeatures
    permission_required = ["ogcapifeatures.can_delete"]

    def get_success_url(self):
        return reverse_lazy("oaf-list")


class OgcApiFeaturesCollectionListView(ListView):
    """Renders the OgcApiFeaturesCollection"""
    model = OgcApiFeaturesCollection
    
    def get_queryset(self):
        return self.model.objects.all().order_by('-name') 


class GeoCodingCreateView(MyCreateView, LoginRequiredMixin):
    model = GeoCoding
    fields = ["title", "raw_csv", "ogc_api_feature_collection"]
    
    # reduce choices for csv to own csv 
    # https://stackoverflow.com/questions/48089590/limiting-choices-in-foreign-key-dropdown-in-django-using-generic-views-createv
    
    def get_form_kwargs(self):
        form = super().get_form_kwargs()
        form['initial'].update({'owned_by_user': self.request.user})
        return form
    
    def form_valid(self, form):
        # read csv file from filesystem
        path = str(form.cleaned_data['raw_csv'])
        file = open(path)
        geocoder_file = csv.reader(file, delimiter='|')
        csv_array = enumerate(geocoder_file)
        header_array = next(geocoder_file)
        #print("header: " + str(header_array))
        collection = form.cleaned_data['ogc_api_feature_collection'].name
        base_uri = form.cleaned_data['ogc_api_feature_collection'].ogc_api_features.base_uri + "/collections"
        result_collection = {
            'type': 'FeatureCollection',
            'features': [],
        }
        # check if some attributes of the two datasources are identical
        data_example = form.cleaned_data['ogc_api_feature_collection'].data_example
        data_scheme_csv = form.cleaned_data['raw_csv'].data_scheme
        #print(data_example)
        #print(data_scheme_csv)

        common_attributes = []
        for property in data_example['properties']:
            #print(property)
            if property in data_scheme_csv:
                #print("attribute found")
                common_attributes.append(property)
            else:
                #print("attribute not found found in ")
                #print(data_scheme_csv)
                pass
        #print(str(common_attributes))
        
        if len(common_attributes) == 0:
            collection_attributes = str(list(data_example['properties'].keys()))
            csv_attributes = str(data_scheme_csv)
            message = "Die beiden Datenquellen haben keine gemeinsamen Felder - bitte wählen sie eine andere Kombination!<br>"
            message = message + "<br>"
            message = message + "CSV Datenfelder:<br>"
            message = message + csv_attributes + "<br><br>"
            message = message + str(collection) + " Datenfelder:<br>"
            message = message + collection_attributes + "<br><br>"
            message = message + "Beispiel für Geometrieobjekte:<br>" 
            message = message + str(data_example)

            return HttpResponse(message, status=422) 

        # save geocoding to database 
        geocoding = GeoCoding(title=form.cleaned_data['title'],
                              raw_csv=form.cleaned_data['raw_csv'],
                              ogc_api_feature_collection=form.cleaned_data['ogc_api_feature_collection'],
                              owned_by_user=self.request.user,
                              created=datetime.now(),
                              )
        geocoding.save()
        geocoding_primary_key = geocoding.pk
        number_of_feature = 0
        for counter, line in csv_array:
            param_dict = {}
            query_string = ""
            column = 0
            param_dict['f'] = 'json'
            #print(str(line))
            for element in line:
                if header_array[column] == "flurschl":
                    element = "0" + element
                query_string = query_string + header_array[column] + "=" + element + "&"
                param_dict[header_array[column]] = element
                column = column + 1
            url = base_uri + "/" + collection + "/items?f=json&" + query_string 
            feature_url = base_uri + "/" + collection + "/items"
            resp = requests.get(url=feature_url, params=param_dict, proxies=settings.PROXIES)
            data = resp.json()
            # print("Found " + str(len(data['features'])) + " Objects")
            # get geojson object from service and add other columns to json
            if len(data['features']) == 1:
                # append keys from csv, that does not already exists in dataset
                column = 0
                for element in line:
                    if not header_array[column] in data['features'][0]['properties'].keys():
                        data['features'][0]['properties'][header_array[column]] = element
                    column = column + 1
                # store feature to to geojson collection and in database
                result_collection['features'].append(data['features'][0])
                geocoding_result = GeoCodingResult(geo_coding=GeoCoding.objects.get(pk=geocoding_primary_key),
                                                   line_number=counter + 1,
                                                   result=True,
                                                   geometry_object=data['features'][0],
                                                   owned_by_user=self.request.user,
                                                   created=datetime.now(),
                                                   get_url=url,
                                                   )
                geocoding_result.save()
                number_of_feature = number_of_feature + 1
            else:
                geocoding_result = GeoCodingResult(geo_coding=GeoCoding.objects.get(pk=geocoding_primary_key),
                                                   line_number=counter + 1,
                                                   result=False,
                                                   owned_by_user=self.request.user,
                                                   created=datetime.now(),
                                                   get_url=url,
                                                   )
                geocoding_result.save()
        # save feature collection to geocoding jsonfield
        setattr(geocoding, 'feature_collection', result_collection)
        geocoding.save()
        file.close()
        return HttpResponseRedirect(self.get_success_url())
        if True:
            return super().form_valid(form)
        else:
            return HttpResponse("XRechnung XML could not be parsed!", status=507)
    
    def get_success_url(self):
        return reverse_lazy("geocoding-list")   


class GeoCodingListView(MyListView):
    """Renders the Geocodings"""
    model = GeoCoding

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        #context['id'] = self.kwargs['pk']
        context['urli'] = self.request.get_host
        return context
    

    def get_success_url(self):
        return reverse_lazy("geocoding-list")

class GeoCodingUpdateView(MyUpdateView):
    model = GeoCoding
    fields = ["title", "raw_csv", "ogc_api_feature_collection"]
      
    def get_success_url(self):
        return reverse_lazy("geocoding-list")


class GeoCodingDeleteView(MyDeleteView):
    model = GeoCoding

    def get_success_url(self):
        return reverse_lazy("geocoding-list")
    

class GeoCodingResultListView(MyListView):
    """Renders the Geocodings"""
    model = GeoCodingResult

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        #context['id'] = self.kwargs['pk']
        geocodingresult = GeoCodingResult.objects.filter(geo_coding=GeoCoding.objects.get(pk=self.kwargs['pk']))
        context['geocodingresult_list'] = geocodingresult
        return context
    
    def get_queryset(self):
        return self.model.objects.filter(
            owned_by_user=self.request.user
        ).order_by('line_number')

    def get_success_url(self):
        return reverse_lazy("geocodingresult-list")
