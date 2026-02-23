# Hotel Management System – DBundDM

Flask-basierte Web-GUI zur Verwaltung der Hotel-Datenbank.

## Voraussetzungen

- Python 3.8+
- PostgreSQL (z. B. Docker auf Port 5432)
- `.venv` mit installierten Paketen

## Starten

```bash
# Umgebung aktivieren
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac

# App starten
python app.py
# → http://localhost:5000
```

## Datenbank konfigurieren

Entweder Umgebungsvariable setzen:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/hotel_db
```

Oder direkt in `app.py` anpassen:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://USER:PASS@localhost:5432/hotel_db'
```

## Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

> **Wichtig:** `wtforms.ext.sqlalchemy` wurde in WTForms 3.x entfernt.
> Stattdessen wird `wtforms-sqlalchemy` verwendet (bereits in `requirements.txt`).

## Funktionsübersicht

| Modul | URL |
|---|---|
| Dashboard | `/` |
| Zimmerkategorien | `/kategorien` |
| Zimmer | `/zimmer` |
| Gäste | `/gaeste` |
| B2B Partner | `/partner` |
| Verträge | `/vertraege` |
| Reservierungen | `/reservierungen` |
| Reservierungsdetails | `/reservierungsdetails` |
| Rechnungen | `/rechnungen` |

