from flask import Flask, render_template, redirect, url_for, flash, request
from models import db, Zimmerkategorie, Zimmer, Gast, B2BPartner, Vertrag, Reservierung, ReservierungsDetails, Rechnung
from forms import (ZimmerkategorieForm, ZimmerForm, GastForm, B2BPartnerForm, VertragForm,
                   ReservierungForm, ReservierungsDetailsForm, RechnungForm)
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------- Dashboard ----------
@app.route('/')
def index():
    zimmer_count = Zimmer.query.count()
    zimmer_frei = Zimmer.query.filter_by(Status='verfügbar').count()
    zimmer_besetzt = Zimmer.query.filter_by(Status='besetzt').count()
    zimmer_wartung = Zimmer.query.filter_by(Status='wartung').count()
    aktive_reservierungen = Reservierung.query.filter(Reservierung.CheckOutDatum >= datetime.now().date()).count()
    offene_rechnungen = Rechnung.query.filter(Rechnung.RechnungsStatus.in_(['offen', 'teilbezahlt'])).count()
    return render_template('index.html',
                           zimmer_count=zimmer_count,
                           zimmer_frei=zimmer_frei,
                           zimmer_besetzt=zimmer_besetzt,
                           zimmer_wartung=zimmer_wartung,
                           aktive_reservierungen=aktive_reservierungen,
                           offene_rechnungen=offene_rechnungen)

# ---------- Zimmerkategorie ----------
@app.route('/kategorien')
def list_kategorien():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'KategorieID')
    dir  = request.args.get('dir',  'desc')
    allowed = {'KategorieID', 'Name', 'MaxPersonen', 'AnzahlBetten', 'ErstelltAm'}
    if sort not in allowed: sort = 'KategorieID'
    col = getattr(Zimmerkategorie, sort)
    q = Zimmerkategorie.query.order_by(col.desc() if dir == 'desc' else col.asc())
    kategorien = q.paginate(page=page, per_page=10)
    return render_template('zimmerkategorie/list.html', kategorien=kategorien, sort=sort, dir=dir)

@app.route('/kategorien/create', methods=['GET', 'POST'])
def create_kategorie():
    form = ZimmerkategorieForm()
    if form.validate_on_submit():
        kategorie = Zimmerkategorie(
            Name=form.Name.data,
            Beschreibung=form.Beschreibung.data,
            MaxPersonen=form.MaxPersonen.data,
            AnzahlBetten=form.AnzahlBetten.data
        )
        db.session.add(kategorie)
        db.session.commit()
        flash('Zimmerkategorie wurde erstellt.', 'success')
        return redirect(url_for('list_kategorien'))
    return render_template('zimmerkategorie/create.html', form=form)

@app.route('/kategorien/<int:id>/edit', methods=['GET', 'POST'])
def edit_kategorie(id):
    kategorie = Zimmerkategorie.query.get_or_404(id)
    form = ZimmerkategorieForm(obj=kategorie)
    if form.validate_on_submit():
        form.populate_obj(kategorie)
        db.session.commit()
        flash('Zimmerkategorie wurde aktualisiert.', 'success')
        return redirect(url_for('list_kategorien'))
    return render_template('zimmerkategorie/edit.html', form=form, kategorie=kategorie)

@app.route('/kategorien/<int:id>/delete', methods=['POST'])
def delete_kategorie(id):
    kategorie = Zimmerkategorie.query.get_or_404(id)
    try:
        db.session.delete(kategorie)
        db.session.commit()
        flash('Zimmerkategorie wurde gelöscht.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Fehler beim Löschen: Möglicherweise existieren noch abhängige Zimmer.', 'danger')
    return redirect(url_for('list_kategorien'))

# ---------- Zimmer ----------
@app.route('/zimmer')
def list_zimmer():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'ZimmerID')
    dir  = request.args.get('dir',  'desc')
    allowed = {'ZimmerID', 'Zimmernummer', 'PreisProNacht', 'Status', 'Etage', 'KategorieID'}
    if sort not in allowed: sort = 'ZimmerID'
    col = getattr(Zimmer, sort)
    q = Zimmer.query.order_by(col.desc() if dir == 'desc' else col.asc())
    zimmer = q.paginate(page=page, per_page=10)
    return render_template('zimmer/list.html', zimmer=zimmer, sort=sort, dir=dir)

@app.route('/zimmer/create', methods=['GET', 'POST'])
def create_zimmer():
    form = ZimmerForm()
    if form.validate_on_submit():
        zimmer = Zimmer(
            Zimmernummer=form.Zimmernummer.data,
            PreisProNacht=form.PreisProNacht.data,
            Status=form.Status.data,
            Etage=form.Etage.data,
            KategorieID=form.KategorieID.data.KategorieID
        )
        db.session.add(zimmer)
        db.session.commit()
        flash('Zimmer wurde erstellt.', 'success')
        return redirect(url_for('list_zimmer'))
    return render_template('zimmer/create.html', form=form)

@app.route('/zimmer/<int:id>/edit', methods=['GET', 'POST'])
def edit_zimmer(id):
    zimmer = Zimmer.query.get_or_404(id)
    form = ZimmerForm(obj=zimmer)
    form.KategorieID.data = zimmer.kategorie
    if form.validate_on_submit():
        form.populate_obj(zimmer)
        zimmer.KategorieID = form.KategorieID.data.KategorieID
        db.session.commit()
        flash('Zimmer wurde aktualisiert.', 'success')
        return redirect(url_for('list_zimmer'))
    return render_template('zimmer/edit.html', form=form, zimmer=zimmer)

@app.route('/zimmer/<int:id>/delete', methods=['POST'])
def delete_zimmer(id):
    zimmer = Zimmer.query.get_or_404(id)
    try:
        db.session.delete(zimmer)
        db.session.commit()
        flash('Zimmer wurde gelöscht.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Fehler beim Löschen: Möglicherweise existieren noch Reservierungen für dieses Zimmer.', 'danger')
    return redirect(url_for('list_zimmer'))

# ---------- Gast ----------
@app.route('/gaeste')
def list_gaeste():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'Gast_ID')
    dir  = request.args.get('dir',  'desc')
    allowed = {'Gast_ID', 'Nachname', 'Vorname', 'Email', 'Telefon', 'ErstelltAm'}
    if sort not in allowed: sort = 'Gast_ID'
    col = getattr(Gast, sort)
    q = Gast.query.order_by(col.desc() if dir == 'desc' else col.asc())
    gaeste = q.paginate(page=page, per_page=10)
    return render_template('gast/list.html', gaeste=gaeste, sort=sort, dir=dir)

@app.route('/gaeste/create', methods=['GET', 'POST'])
def create_gast():
    form = GastForm()
    if form.validate_on_submit():
        gast = Gast(
            Vorname=form.Vorname.data,
            Nachname=form.Nachname.data,
            Email=form.Email.data,
            Telefon=form.Telefon.data
        )
        db.session.add(gast)
        db.session.commit()
        flash('Gast wurde erstellt.', 'success')
        return redirect(url_for('list_gaeste'))
    return render_template('gast/create.html', form=form)

@app.route('/gaeste/<int:id>/edit', methods=['GET', 'POST'])
def edit_gast(id):
    gast = Gast.query.get_or_404(id)
    form = GastForm(obj=gast)
    if form.validate_on_submit():
        form.populate_obj(gast)
        db.session.commit()
        flash('Gast wurde aktualisiert.', 'success')
        return redirect(url_for('list_gaeste'))
    return render_template('gast/edit.html', form=form, gast=gast)

@app.route('/gaeste/<int:id>/delete', methods=['POST'])
def delete_gast(id):
    gast = Gast.query.get_or_404(id)
    try:
        db.session.delete(gast)
        db.session.commit()
        flash('Gast wurde gelöscht.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Fehler beim Löschen: Möglicherweise existieren noch Reservierungen für diesen Gast.', 'danger')
    return redirect(url_for('list_gaeste'))

# ---------- B2B Partner ----------
@app.route('/partner')
def list_partner():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'PartnerID')
    dir  = request.args.get('dir',  'desc')
    allowed = {'PartnerID', 'Name', 'Typ', 'Email', 'Telefon', 'Status'}
    if sort not in allowed: sort = 'PartnerID'
    col = getattr(B2BPartner, sort)
    q = B2BPartner.query.order_by(col.desc() if dir == 'desc' else col.asc())
    partner = q.paginate(page=page, per_page=10)
    return render_template('b2bpartner/list.html', partner=partner, sort=sort, dir=dir)

@app.route('/partner/create', methods=['GET', 'POST'])
def create_partner():
    form = B2BPartnerForm()
    if form.validate_on_submit():
        partner = B2BPartner(
            Name=form.Name.data,
            Typ=form.Typ.data,
            Email=form.Email.data,
            Telefon=form.Telefon.data,
            Status=form.Status.data
        )
        db.session.add(partner)
        db.session.commit()
        flash('Partner wurde erstellt.', 'success')
        return redirect(url_for('list_partner'))
    return render_template('b2bpartner/create.html', form=form)

@app.route('/partner/<int:id>/edit', methods=['GET', 'POST'])
def edit_partner(id):
    partner = B2BPartner.query.get_or_404(id)
    form = B2BPartnerForm(obj=partner)
    if form.validate_on_submit():
        form.populate_obj(partner)
        db.session.commit()
        flash('Partner wurde aktualisiert.', 'success')
        return redirect(url_for('list_partner'))
    return render_template('b2bpartner/edit.html', form=form, partner=partner)

@app.route('/partner/<int:id>/delete', methods=['POST'])
def delete_partner(id):
    partner = B2BPartner.query.get_or_404(id)
    try:
        db.session.delete(partner)
        db.session.commit()
        flash('Partner wurde gelöscht.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Fehler beim Löschen: Möglicherweise existieren noch Verträge oder Reservierungen.', 'danger')
    return redirect(url_for('list_partner'))

# ---------- Vertrag ----------
@app.route('/vertraege')
def list_vertraege():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'VertragID')
    dir  = request.args.get('dir',  'desc')
    allowed = {'VertragID', 'PartnerID', 'VonDatum', 'BisDatum', 'VertragsStatus', 'ErstelltAm'}
    if sort not in allowed: sort = 'VertragID'
    col = getattr(Vertrag, sort)
    q = Vertrag.query.order_by(col.desc() if dir == 'desc' else col.asc())
    vertraege = q.paginate(page=page, per_page=10)
    return render_template('vertrag/list.html', vertraege=vertraege, sort=sort, dir=dir)

@app.route('/vertraege/create', methods=['GET', 'POST'])
def create_vertrag():
    form = VertragForm()
    if form.validate_on_submit():
        vertrag = Vertrag(
            VonDatum=form.VonDatum.data,
            BisDatum=form.BisDatum.data,
            VertragsStatus=form.VertragsStatus.data,
            PartnerID=form.PartnerID.data.PartnerID
        )
        db.session.add(vertrag)
        db.session.commit()
        flash('Vertrag wurde erstellt.', 'success')
        return redirect(url_for('list_vertraege'))
    return render_template('vertrag/create.html', form=form)

@app.route('/vertraege/<int:id>/edit', methods=['GET', 'POST'])
def edit_vertrag(id):
    vertrag = Vertrag.query.get_or_404(id)
    form = VertragForm(obj=vertrag)
    form.PartnerID.data = vertrag.partner
    if form.validate_on_submit():
        form.populate_obj(vertrag)
        vertrag.PartnerID = form.PartnerID.data.PartnerID
        db.session.commit()
        flash('Vertrag wurde aktualisiert.', 'success')
        return redirect(url_for('list_vertraege'))
    return render_template('vertrag/edit.html', form=form, vertrag=vertrag)

@app.route('/vertraege/<int:id>/delete', methods=['POST'])
def delete_vertrag(id):
    vertrag = Vertrag.query.get_or_404(id)
    db.session.delete(vertrag)
    db.session.commit()
    flash('Vertrag wurde gelöscht.', 'success')
    return redirect(url_for('list_vertraege'))

# ---------- Reservierung ----------
@app.route('/reservierungen')
def list_reservierungen():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'ReservierungsID')
    dir  = request.args.get('dir',  'desc')
    allowed = {'ReservierungsID', 'ReservierungsReferenz', 'CheckInDatum', 'CheckOutDatum', 'AnzahlNaechte', 'ReservierungsStatus'}
    if sort not in allowed: sort = 'ReservierungsID'
    col = getattr(Reservierung, sort)
    q = Reservierung.query.order_by(col.desc() if dir == 'desc' else col.asc())
    reservierungen = q.paginate(page=page, per_page=10)
    return render_template('reservierung/list.html', reservierungen=reservierungen, sort=sort, dir=dir)

@app.route('/reservierungen/create', methods=['GET', 'POST'])
def create_reservierung():
    form = ReservierungForm()
    if form.validate_on_submit():
        reservierung = Reservierung(
            AnzahlNaechte=form.AnzahlNaechte.data,
            CheckInDatum=form.CheckInDatum.data,
            CheckOutDatum=form.CheckOutDatum.data,
            ReservierungsStatus=form.ReservierungsStatus.data,
            ReservierungsReferenz=form.ReservierungsReferenz.data,
            GastID=form.GastID.data.Gast_ID if form.GastID.data else None,
            PartnerID=form.PartnerID.data.PartnerID if form.PartnerID.data else None
        )
        db.session.add(reservierung)
        db.session.commit()
        flash('Reservierung wurde erstellt.', 'success')
        return redirect(url_for('list_reservierungen'))
    return render_template('reservierung/create.html', form=form)

@app.route('/reservierungen/<int:id>/edit', methods=['GET', 'POST'])
def edit_reservierung(id):
    reservierung = Reservierung.query.get_or_404(id)
    form = ReservierungForm(obj=reservierung)
    form.GastID.data = reservierung.gast
    form.PartnerID.data = reservierung.partner
    if form.validate_on_submit():
        form.populate_obj(reservierung)
        reservierung.GastID = form.GastID.data.Gast_ID if form.GastID.data else None
        reservierung.PartnerID = form.PartnerID.data.PartnerID if form.PartnerID.data else None
        db.session.commit()
        flash('Reservierung wurde aktualisiert.', 'success')
        return redirect(url_for('list_reservierungen'))
    return render_template('reservierung/edit.html', form=form, reservierung=reservierung)

@app.route('/reservierungen/<int:id>/delete', methods=['POST'])
def delete_reservierung(id):
    reservierung = Reservierung.query.get_or_404(id)
    try:
        db.session.delete(reservierung)
        db.session.commit()
        flash('Reservierung wurde gelöscht.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Fehler beim Löschen: Möglicherweise existieren noch abhängige Daten.', 'danger')
    return redirect(url_for('list_reservierungen'))

# ---------- ReservierungsDetails ----------
@app.route('/reservierungsdetails')
def list_reservierungsdetails():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'ReservierungsDetailID')
    dir  = request.args.get('dir',  'desc')
    allowed = {'ReservierungsDetailID', 'ReservierungsID', 'ZimmerID', 'AnzahlZimmer', 'PreisProNachtZumZeitpunkt', 'GesamtPreis'}
    if sort not in allowed: sort = 'ReservierungsDetailID'
    col = getattr(ReservierungsDetails, sort)
    q = ReservierungsDetails.query.order_by(col.desc() if dir == 'desc' else col.asc())
    details = q.paginate(page=page, per_page=10)
    return render_template('reservierungsdetails/list.html', details=details, sort=sort, dir=dir)

@app.route('/reservierungsdetails/create', methods=['GET', 'POST'])
def create_reservierungsdetails():
    form = ReservierungsDetailsForm()
    if form.validate_on_submit():
        detail = ReservierungsDetails(
            AnzahlZimmer=form.AnzahlZimmer.data,
            PreisProNachtZumZeitpunkt=form.PreisProNachtZumZeitpunkt.data,
            GesamtPreis=form.GesamtPreis.data,
            ReservierungsID=form.ReservierungsID.data.ReservierungsID,
            ZimmerID=form.ZimmerID.data.ZimmerID
        )
        db.session.add(detail)
        db.session.commit()
        flash('Reservierungsdetail wurde erstellt.', 'success')
        return redirect(url_for('list_reservierungsdetails'))
    return render_template('reservierungsdetails/create.html', form=form)

@app.route('/reservierungsdetails/<int:id>/edit', methods=['GET', 'POST'])
def edit_reservierungsdetails(id):
    detail = ReservierungsDetails.query.get_or_404(id)
    form = ReservierungsDetailsForm(obj=detail)
    form.ReservierungsID.data = detail.reservierung
    form.ZimmerID.data = detail.zimmer
    if form.validate_on_submit():
        form.populate_obj(detail)
        detail.ReservierungsID = form.ReservierungsID.data.ReservierungsID
        detail.ZimmerID = form.ZimmerID.data.ZimmerID
        db.session.commit()
        flash('Reservierungsdetail wurde aktualisiert.', 'success')
        return redirect(url_for('list_reservierungsdetails'))
    return render_template('reservierungsdetails/edit.html', form=form, detail=detail)

@app.route('/reservierungsdetails/<int:id>/delete', methods=['POST'])
def delete_reservierungsdetails(id):
    detail = ReservierungsDetails.query.get_or_404(id)
    db.session.delete(detail)
    db.session.commit()
    flash('Reservierungsdetail wurde gelöscht.', 'success')
    return redirect(url_for('list_reservierungsdetails'))

# ---------- Rechnung ----------
@app.route('/rechnungen')
def list_rechnungen():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'RechnungsID')
    dir  = request.args.get('dir',  'desc')
    allowed = {'RechnungsID', 'RechnungsNummer', 'RechnungsDatum', 'ReservierungsID', 'BetragGesamt', 'Faelligkeitsdatum', 'RechnungsStatus'}
    if sort not in allowed: sort = 'RechnungsID'
    col = getattr(Rechnung, sort)
    q = Rechnung.query.order_by(col.desc() if dir == 'desc' else col.asc())
    rechnungen = q.paginate(page=page, per_page=10)
    return render_template('rechnung/list.html', rechnungen=rechnungen, sort=sort, dir=dir)

@app.route('/rechnungen/create', methods=['GET', 'POST'])
def create_rechnung():
    form = RechnungForm()
    if form.validate_on_submit():
        rechnung = Rechnung(
            RechnungsNummer=form.RechnungsNummer.data,
            RechnungsDatum=form.RechnungsDatum.data,
            RechnungsStatus=form.RechnungsStatus.data,
            BetragGesamt=form.BetragGesamt.data,
            Faelligkeitsdatum=form.Faelligkeitsdatum.data,
            ReservierungsID=form.ReservierungsID.data.ReservierungsID
        )
        db.session.add(rechnung)
        db.session.commit()
        flash('Rechnung wurde erstellt.', 'success')
        return redirect(url_for('list_rechnungen'))
    return render_template('rechnung/create.html', form=form)

@app.route('/rechnungen/<int:id>/edit', methods=['GET', 'POST'])
def edit_rechnung(id):
    rechnung = Rechnung.query.get_or_404(id)
    form = RechnungForm(obj=rechnung)
    form.ReservierungsID.data = rechnung.reservierung
    if form.validate_on_submit():
        form.populate_obj(rechnung)
        rechnung.ReservierungsID = form.ReservierungsID.data.ReservierungsID
        db.session.commit()
        flash('Rechnung wurde aktualisiert.', 'success')
        return redirect(url_for('list_rechnungen'))
    return render_template('rechnung/edit.html', form=form, rechnung=rechnung)

@app.route('/rechnungen/<int:id>/delete', methods=['POST'])
def delete_rechnung(id):
    rechnung = Rechnung.query.get_or_404(id)
    db.session.delete(rechnung)
    db.session.commit()
    flash('Rechnung wurde gelöscht.', 'success')
    return redirect(url_for('list_rechnungen'))

if __name__ == '__main__':
    app.run(debug=True)