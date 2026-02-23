from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DecimalField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, Email, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from models import Zimmerkategorie, Gast, B2BPartner, Zimmer, Reservierung
from datetime import date

# ----- Hilfsfunktionen für Dropdowns -----
def get_kategorien():
    return Zimmerkategorie.query.all()

def get_gaeste():
    return Gast.query.all()

def get_partner():
    return B2BPartner.query.all()

def get_zimmer():
    return Zimmer.query.all()

def get_reservierungen():
    return Reservierung.query.all()

# ----- Eigene Validatoren -----
def validate_checkout(form, field):
    if form.CheckInDatum.data and field.data and field.data <= form.CheckInDatum.data:
        raise ValidationError('Check-Out Datum muss nach dem Check-In Datum liegen.')

# ----- Formulare -----
class ZimmerkategorieForm(FlaskForm):
    Name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    Beschreibung = TextAreaField('Beschreibung', validators=[Optional()])
    MaxPersonen = IntegerField('Max. Personen', validators=[DataRequired(), NumberRange(min=1)])
    AnzahlBetten = IntegerField('Anzahl Betten', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Speichern')

class ZimmerForm(FlaskForm):
    Zimmernummer = StringField('Zimmernummer', validators=[DataRequired(), Length(max=10)])
    PreisProNacht = DecimalField('Preis pro Nacht', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    Status = SelectField('Status', choices=[('verfügbar', 'verfügbar'), ('besetzt', 'besetzt'), ('wartung', 'wartung'), ('gesperrt', 'gesperrt')], validators=[DataRequired()])
    Etage = IntegerField('Etage', validators=[DataRequired(), NumberRange(min=0)])
    KategorieID = QuerySelectField('Kategorie', query_factory=get_kategorien, get_label='Name', allow_blank=False, validators=[DataRequired()])
    submit = SubmitField('Speichern')

class GastForm(FlaskForm):
    Vorname = StringField('Vorname', validators=[DataRequired(), Length(max=100)])
    Nachname = StringField('Nachname', validators=[DataRequired(), Length(max=100)])
    Email = StringField('Email', validators=[Optional(), Email(), Length(max=150)])
    Telefon = StringField('Telefon', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Speichern')

class B2BPartnerForm(FlaskForm):
    Name = StringField('Name', validators=[DataRequired(), Length(max=200)])
    Typ = SelectField('Typ', choices=[('Hotel', 'Hotel'), ('Agentur', 'Agentur'), ('Vermittler', 'Vermittler'), ('Konzern', 'Konzern'), ('Sonstiges', 'Sonstiges')], validators=[DataRequired()])
    Email = StringField('Email', validators=[Optional(), Email(), Length(max=150)])
    Telefon = StringField('Telefon', validators=[Optional(), Length(max=20)])
    Status = SelectField('Status', choices=[('aktiv', 'aktiv'), ('inaktiv', 'inaktiv'), ('gesperrt', 'gesperrt')], validators=[DataRequired()])
    submit = SubmitField('Speichern')

class VertragForm(FlaskForm):
    VonDatum = DateField('Von Datum', validators=[DataRequired()], format='%Y-%m-%d')
    BisDatum = DateField('Bis Datum', validators=[DataRequired()], format='%Y-%m-%d')
    VertragsStatus = SelectField('Status', choices=[('aktiv', 'aktiv'), ('abgelaufen', 'abgelaufen'), ('beendet', 'beendet'), ('ausgesetzt', 'ausgesetzt')], validators=[DataRequired()])
    PartnerID = QuerySelectField('Partner', query_factory=get_partner, get_label='Name', allow_blank=False, validators=[DataRequired()])
    submit = SubmitField('Speichern')

    def validate_BisDatum(self, field):
        if self.VonDatum.data and field.data and field.data < self.VonDatum.data:
            raise ValidationError('Bis Datum muss nach Von Datum liegen.')

class ReservierungForm(FlaskForm):
    AnzahlNaechte = IntegerField('Anzahl Nächte', validators=[DataRequired(), NumberRange(min=1)])
    CheckInDatum = DateField('Check-In Datum', validators=[DataRequired()], format='%Y-%m-%d')
    CheckOutDatum = DateField('Check-Out Datum', validators=[DataRequired(), validate_checkout], format='%Y-%m-%d')
    ReservierungsStatus = SelectField('Status', choices=[('bestätigt', 'bestätigt'), ('storniert', 'storniert'), ('in Bearbeitung', 'in Bearbeitung'), ('abgeschlossen', 'abgeschlossen')], validators=[DataRequired()])
    ReservierungsReferenz = StringField('Referenz', validators=[Optional(), Length(max=50)])
    GastID = QuerySelectField('Gast', query_factory=get_gaeste, get_label=lambda g: f"{g.Nachname}, {g.Vorname}", allow_blank=True, blank_text='-- Kein Gast --')
    PartnerID = QuerySelectField('Partner', query_factory=get_partner, get_label='Name', allow_blank=True, blank_text='-- Kein Partner --')
    submit = SubmitField('Speichern')

    def validate(self):
        if not super().validate():
            return False
        if self.GastID.data is None and self.PartnerID.data is None:
            self.GastID.errors.append('Es muss entweder ein Gast oder ein Partner angegeben werden.')
            self.PartnerID.errors.append('Es muss entweder ein Gast oder ein Partner angegeben werden.')
            return False
        return True

class ReservierungsDetailsForm(FlaskForm):
    AnzahlZimmer = IntegerField('Anzahl Zimmer', validators=[DataRequired(), NumberRange(min=1)])
    PreisProNachtZumZeitpunkt = DecimalField('Preis pro Nacht (zum Zeitpunkt)', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    GesamtPreis = DecimalField('Gesamtpreis', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    ReservierungsID = QuerySelectField('Reservierung', query_factory=get_reservierungen, get_label='ReservierungsReferenz', allow_blank=False, validators=[DataRequired()])
    ZimmerID = QuerySelectField('Zimmer', query_factory=get_zimmer, get_label='Zimmernummer', allow_blank=False, validators=[DataRequired()])
    submit = SubmitField('Speichern')

class RechnungForm(FlaskForm):
    RechnungsNummer = StringField('Rechnungsnummer', validators=[DataRequired(), Length(max=50)])
    RechnungsDatum = DateField('Rechnungsdatum', validators=[DataRequired()], format='%Y-%m-%d', default=date.today)
    RechnungsStatus = SelectField('Status', choices=[('offen', 'offen'), ('teilbezahlt', 'teilbezahlt'), ('bezahlt', 'bezahlt'), ('storniert', 'storniert')], validators=[DataRequired()])
    BetragGesamt = DecimalField('Gesamtbetrag', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    Faelligkeitsdatum = DateField('Fälligkeitsdatum', validators=[DataRequired()], format='%Y-%m-%d')
    ReservierungsID = QuerySelectField('Reservierung', query_factory=get_reservierungen, get_label='ReservierungsReferenz', allow_blank=False, validators=[DataRequired()])
    submit = SubmitField('Speichern')

    def validate_Faelligkeitsdatum(self, field):
        if self.RechnungsDatum.data and field.data and field.data < self.RechnungsDatum.data:
            raise ValidationError('Fälligkeitsdatum muss nach Rechnungsdatum liegen.')