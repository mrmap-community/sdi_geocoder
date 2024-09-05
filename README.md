# GDI Geocoder

## Beschreibung

Einfache Django-Anwendung zum automatischen Geokodieren von CSV-Dateien. Die Kodierung erfolgt dabei auf Basis von OGC API Feature Interfaces, die im Geocoder registriert werden. Das Projekt ist als "Proof of Concept" gedacht und läßt sich gut für ein Django Tutorial nutzen.

## Funktionen

* Registrieren von OGC API-Features Landing Pages
* Extraktion der Collections und des zugehörigen Datenmodells
* Generierung von CSV-Templates für jede Collection
* Upload von CSV-Dateien
* Geokodierung
* Dokumentation des Prozesses in Form von CSV-Dateien
* ...

## Installation
 
 Einfach unter Debian 11 ausprobieren ;-) 

 ```console
git clone https://github.com/mrmap/sdi_geocoder.git
cd sdi_geocoder
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py collectstatic
python3 manage.py createsuperuser
python3 manage.py runserver
```