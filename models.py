from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Zimmerkategorie(db.Model):
    __tablename__ = 'zimmerkategorie'
    KategorieID  = db.Column('kategorieid',  db.Integer, primary_key=True, autoincrement=True)
    Name         = db.Column('name',         db.String(100), nullable=False, unique=True)
    Beschreibung = db.Column('beschreibung', db.Text)
    MaxPersonen  = db.Column('maxpersonen',  db.Integer, nullable=False)
    AnzahlBetten = db.Column('anzahlbetten', db.Integer, nullable=False)
    ErstelltAm   = db.Column('erstelltam',   db.DateTime, default=datetime.now)

    zimmer = db.relationship('Zimmer', backref='kategorie', lazy=True)

    def __repr__(self):
        return self.Name

class Zimmer(db.Model):
    __tablename__ = 'zimmer'
    ZimmerID      = db.Column('zimmerid',      db.Integer, primary_key=True, autoincrement=True)
    Zimmernummer  = db.Column('zimmernummer',  db.String(10), nullable=False, unique=True)
    PreisProNacht = db.Column('preispronacht', db.Numeric(10, 2), nullable=False)
    Status        = db.Column('status',        db.String(20), nullable=False, default='verfügbar')
    Etage         = db.Column('etage',         db.Integer, nullable=False)
    KategorieID   = db.Column('kategorieid',   db.Integer, db.ForeignKey('zimmerkategorie.kategorieid', ondelete='RESTRICT'), nullable=False)
    ErstelltAm    = db.Column('erstelltam',    db.DateTime, default=datetime.now)

    reservierungsdetails = db.relationship('ReservierungsDetails', backref='zimmer', lazy=True)

    def __repr__(self):
        return self.Zimmernummer

class Gast(db.Model):
    __tablename__ = 'gast'
    Gast_ID       = db.Column('gast_id',       db.Integer, primary_key=True, autoincrement=True)
    Vorname       = db.Column('vorname',       db.String(100), nullable=False)
    Nachname      = db.Column('nachname',      db.String(100), nullable=False)
    Email         = db.Column('email',         db.String(150), unique=True)
    Telefon       = db.Column('telefon',       db.String(20))
    ErstelltAm    = db.Column('erstelltam',    db.DateTime, default=datetime.now)
    AktualisiertAm= db.Column('aktualisiertam',db.DateTime, default=datetime.now, onupdate=datetime.now)

    reservierungen = db.relationship('Reservierung', backref='gast', lazy=True)

    def __repr__(self):
        return f"{self.Nachname}, {self.Vorname}"

class B2BPartner(db.Model):
    __tablename__ = 'b2bpartner'
    PartnerID      = db.Column('partnerid',      db.Integer, primary_key=True, autoincrement=True)
    Name           = db.Column('name',           db.String(200), nullable=False)
    Typ            = db.Column('typ',            db.String(50), nullable=False)
    Email          = db.Column('email',          db.String(150))
    Telefon        = db.Column('telefon',        db.String(20))
    Status         = db.Column('status',         db.String(20), nullable=False, default='aktiv')
    ErstelltAm     = db.Column('erstelltam',     db.DateTime, default=datetime.now)
    AktualisiertAm = db.Column('aktualisiertam', db.DateTime, default=datetime.now, onupdate=datetime.now)

    vertraege      = db.relationship('Vertrag',      backref='partner', lazy=True, cascade='all, delete-orphan')
    reservierungen = db.relationship('Reservierung', backref='partner', lazy=True)

    def __repr__(self):
        return self.Name

class Vertrag(db.Model):
    __tablename__ = 'vertrag'
    VertragID      = db.Column('vertragid',      db.Integer, primary_key=True, autoincrement=True)
    VonDatum       = db.Column('vondatum',       db.Date, nullable=False)
    BisDatum       = db.Column('bisdatum',       db.Date, nullable=False)
    VertragsStatus = db.Column('vertragsstatus', db.String(20), nullable=False, default='aktiv')
    PartnerID      = db.Column('partnerid',      db.Integer, db.ForeignKey('b2bpartner.partnerid', ondelete='CASCADE'), nullable=False)
    ErstelltAm     = db.Column('erstelltam',     db.DateTime, default=datetime.now)
    AktualisiertAm = db.Column('aktualisiertam', db.DateTime, default=datetime.now, onupdate=datetime.now)

class Reservierung(db.Model):
    __tablename__ = 'reservierung'
    ReservierungsID      = db.Column('reservierungsid',      db.Integer, primary_key=True, autoincrement=True)
    AnzahlNaechte        = db.Column('anzahlnaechte',        db.Integer, nullable=False)
    CheckInDatum         = db.Column('checkindatum',         db.Date, nullable=False)
    CheckOutDatum        = db.Column('checkoutdatum',        db.Date, nullable=False)
    ReservierungsStatus  = db.Column('reservierungsstatus',  db.String(20), nullable=False, default='bestätigt')
    ReservierungsReferenz= db.Column('reservierungsreferenz',db.String(50), unique=True)
    GastID               = db.Column('gastid',               db.Integer, db.ForeignKey('gast.gast_id', ondelete='SET NULL'))
    PartnerID            = db.Column('partnerid',            db.Integer, db.ForeignKey('b2bpartner.partnerid', ondelete='SET NULL'))
    ErstelltAm           = db.Column('erstelltam',           db.DateTime, default=datetime.now)
    AktualisiertAm       = db.Column('aktualisiertam',       db.DateTime, default=datetime.now, onupdate=datetime.now)

    details   = db.relationship('ReservierungsDetails', backref='reservierung', lazy=True, cascade='all, delete-orphan')
    rechnungen= db.relationship('Rechnung',             backref='reservierung', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return self.ReservierungsReferenz or f"Res-{self.ReservierungsID}"

class ReservierungsDetails(db.Model):
    __tablename__ = 'reservierungsdetails'
    ReservierungsDetailID       = db.Column('reservierungsdetailid',        db.Integer, primary_key=True, autoincrement=True)
    AnzahlZimmer                = db.Column('anzahlzimmer',                 db.Integer, nullable=False)
    PreisProNachtZumZeitpunkt   = db.Column('preispronachtzumzeitpunkt',    db.Numeric(10, 2), nullable=False)
    GesamtPreis                 = db.Column('gesamtpreis',                  db.Numeric(12, 2), nullable=False)
    ReservierungsID             = db.Column('reservierungsid',              db.Integer, db.ForeignKey('reservierung.reservierungsid', ondelete='CASCADE'), nullable=False)
    ZimmerID                    = db.Column('zimmerid',                     db.Integer, db.ForeignKey('zimmer.zimmerid', ondelete='RESTRICT'), nullable=False)
    ErstelltAm                  = db.Column('erstelltam',                   db.DateTime, default=datetime.now)

class Rechnung(db.Model):
    __tablename__ = 'rechnung'
    RechnungsID     = db.Column('rechnungsid',     db.Integer, primary_key=True, autoincrement=True)
    RechnungsNummer = db.Column('rechnungsnummer', db.String(50), nullable=False, unique=True)
    RechnungsDatum  = db.Column('rechnungsdatum',  db.Date, nullable=False, default=datetime.now)
    RechnungsStatus = db.Column('rechnungsstatus', db.String(20), nullable=False, default='offen')
    BetragGesamt    = db.Column('betraggesamt',    db.Numeric(12, 2), nullable=False)
    Faelligkeitsdatum= db.Column('faelligkeitsdatum', db.Date, nullable=False)
    ReservierungsID = db.Column('reservierungsid', db.Integer, db.ForeignKey('reservierung.reservierungsid', ondelete='CASCADE'), nullable=False)
    ErstelltAm      = db.Column('erstelltam',      db.DateTime, default=datetime.now)
    AktualisiertAm  = db.Column('aktualisiertam',  db.DateTime, default=datetime.now, onupdate=datetime.now)
