# Hotel Management System - DBundDM

Flask-basierte Management-GUI fur deine bestehende Hotel-PostgreSQL-Datenbank.

## Funktionen

- CRUD-Verwaltung fur `Zimmerkategorie`, `Zimmer`, `Gast`, `B2BPartner`, `Vertrag`, `Reservierung`, `ReservierungsDetails`, `Rechnung`
- Sortierbare Listenansichten mit Pagination
- Formularvalidierung mit CSRF-Schutz (Flask-WTF)

## Voraussetzungen

- Python 3.10+ (deine bestehende `.venv` ist ausreichend)
- PostgreSQL (bei dir in Docker auf Port `5432`)
- Zugriffsdaten fur die bestehende Datenbank

## 1) Abhangigkeiten installieren / aktualisieren

Aktiviere zuerst deine virtuelle Umgebung und installiere dann die Pakete:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2) `.env` anlegen

Lege im Projektroot eine Datei `.env` an (neben `app.py`) und trage die Werte ein:

```dotenv
DB_USER=postgres
DB_PASSWORD=dein_passwort
DB_HOST=localhost
DB_PORT=5432
DB_NAME=deine_datenbank
CSRF_SECRET_KEY=hier_ein_langer_zufaelliger_key
```

## 3) CSRF_SECRET_KEY erzeugen und eintragen

Der `CSRF_SECRET_KEY` wird als `SECRET_KEY` von Flask genutzt und ist fur CSRF-Token notwendig.

### Option A (empfohlen, Python)

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Die Ausgabe komplett als Wert fur `CSRF_SECRET_KEY` in `.env` ubernehmen.

### Option B (OpenSSL, falls vorhanden)

```powershell
openssl rand -hex 64
```

## 4) Anwendung starten

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

Danach im Browser offnen: `http://127.0.0.1:5000`

## Hinweise zur Datenbank

- Das Projekt ist auf eine **bereits vorhandene** Datenbank ausgelegt.
- Es wird **keine** Initial-SQL-Datei benotigt.
- Falls die Verbindung fehlschlagt, zuerst `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` in `.env` prufen.

## Hauptrouten

| Bereich | URL |
|---|---|
| Dashboard | `/` |
| Zimmerkategorien | `/kategorien` |
| Zimmer | `/zimmer` |
| Gaste | `/gaeste` |
| B2B Partner | `/partner` |
| Vertrage | `/vertraege` |
| Reservierungen | `/reservierungen` |
| Reservierungsdetails | `/reservierungsdetails` |
| Rechnungen | `/rechnungen` |

## Troubleshooting

- `ModuleNotFoundError: wtforms.ext`
  - Das Projekt nutzt `wtforms_sqlalchemy` (`WTForms-SQLAlchemy`) und **nicht** `wtforms.ext`.
  - Stelle sicher, dass die Pakete aus `requirements.txt` in der aktiven `.venv` installiert sind.
- CSRF-Fehler bei Formularen
  - Prufe, ob `CSRF_SECRET_KEY` in `.env` gesetzt ist und die App danach neu gestartet wurde.

