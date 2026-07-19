# TG Management

Sistema de gestión comercial y operativa desarrollado en Django.

## Módulos

- CRM
- Cotizaciones
- Proyectos
- Finanzas
- Soporte

## Requisitos

- Python 3.13
- Django 5.2

## Instalación

python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
