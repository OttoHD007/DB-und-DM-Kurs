-- WAB Hotelreservierungssystem - PostgreSQL Datenbankschema
-- Erstellt: 2025-12-03
-- Beschreibung: Vollständiges relationales Schema für Hotelreservierungen mit B2B-Partnern
-- Enthält: CREATE TABLE-Befehle + Testdaten für alle Kategorien

-- ===================================================================
-- 1. TABELLE: Zimmerkategorie
-- ===================================================================
--DROP table Zimmerkategorie CASCADE;

CREATE TABLE Zimmerkategorie (
                                 KategorieID SERIAL PRIMARY KEY,
                                 Name VARCHAR(100) NOT NULL UNIQUE,
                                 Beschreibung TEXT,
                                 MaxPersonen INT NOT NULL CHECK (MaxPersonen > 0),
                                 AnzahlBetten INT NOT NULL CHECK (AnzahlBetten > 0),
                                 ErstelltAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================
-- 2. TABELLE: Zimmer
-- ===================================================================
CREATE TABLE Zimmer (
                        ZimmerID SERIAL PRIMARY KEY,
                        Zimmernummer VARCHAR(10) NOT NULL UNIQUE,
                        PreisProNacht DECIMAL(10, 2) NOT NULL CHECK (PreisProNacht > 0),
                        Status VARCHAR(20) NOT NULL DEFAULT 'verfügbar'
                            CHECK (Status IN ('verfügbar', 'besetzt', 'wartung', 'gesperrt')),
                        Etage INT NOT NULL CHECK (Etage >= 0),
                        KategorieID INT NOT NULL,
                        ErstelltAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT fk_zimmer_kategorie FOREIGN KEY (KategorieID)
                            REFERENCES Zimmerkategorie(KategorieID) ON DELETE RESTRICT
);

CREATE INDEX idx_zimmer_status ON Zimmer(Status);
CREATE INDEX idx_zimmer_kategorie ON Zimmer(KategorieID);

-- ===================================================================
-- 3. TABELLE: Gast
-- ===================================================================
CREATE TABLE Gast (
                      Gast_ID SERIAL PRIMARY KEY,
                      Vorname VARCHAR(100) NOT NULL,
                      Nachname VARCHAR(100) NOT NULL,
                      Email VARCHAR(150) UNIQUE,
                      Telefon VARCHAR(20),
                      ErstelltAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      AktualisiertAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_gast_name ON Gast(Nachname, Vorname);
CREATE INDEX idx_gast_email ON Gast(Email);

-- ===================================================================
-- 4. TABELLE: B2BPartner
-- ===================================================================
CREATE TABLE B2BPartner (
                            PartnerID SERIAL PRIMARY KEY,
                            Name VARCHAR(200) NOT NULL,
                            Typ VARCHAR(50) NOT NULL
                                CHECK (Typ IN ('Hotel', 'Agentur', 'Vermittler', 'Konzern', 'Sonstiges')),
                            Email VARCHAR(150),
                            Telefon VARCHAR(20),
                            Status VARCHAR(20) NOT NULL DEFAULT 'aktiv'
                                CHECK (Status IN ('aktiv', 'inaktiv', 'gesperrt')),
                            ErstelltAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            AktualisiertAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_partner_status ON B2BPartner(Status);
CREATE INDEX idx_partner_typ ON B2BPartner(Typ);

-- ===================================================================
-- 5. TABELLE: Vertrag
-- ===================================================================
CREATE TABLE Vertrag (
                         VertragID SERIAL PRIMARY KEY,
                         VonDatum DATE NOT NULL,
                         BisDatum DATE NOT NULL CHECK (BisDatum >= VonDatum),
                         VertragsStatus VARCHAR(20) NOT NULL DEFAULT 'aktiv'
                             CHECK (VertragsStatus IN ('aktiv', 'abgelaufen', 'beendet', 'ausgesetzt')),
                         PartnerID INT NOT NULL,
                         ErstelltAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         AktualisiertAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                         CONSTRAINT fk_vertrag_partner FOREIGN KEY (PartnerID)
                             REFERENCES B2BPartner(PartnerID) ON DELETE CASCADE,
                         CONSTRAINT check_gueltig_von_bis CHECK (BisDatum >= VonDatum)
);

CREATE INDEX idx_vertrag_status ON Vertrag(VertragsStatus);
CREATE INDEX idx_vertrag_partner ON Vertrag(PartnerID);
CREATE INDEX idx_vertrag_datum ON Vertrag(VonDatum, BisDatum);

-- ===================================================================
-- 6. TABELLE: Reservierung
-- ===================================================================
CREATE TABLE Reservierung (
                              ReservierungsID SERIAL PRIMARY KEY,
                              AnzahlNaechte INT NOT NULL CHECK (AnzahlNaechte > 0),
                              CheckInDatum DATE NOT NULL,
                              CheckOutDatum DATE NOT NULL CHECK (CheckOutDatum > CheckInDatum),
                              ReservierungsStatus VARCHAR(20) NOT NULL DEFAULT 'bestätigt'
                                  CHECK (ReservierungsStatus IN ('bestätigt', 'storniert', 'in Bearbeitung', 'abgeschlossen')),
                              ReservierungsReferenz VARCHAR(50) UNIQUE,
                              GastID INT,
                              PartnerID INT,
                              ErstelltAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                              AktualisiertAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                              CONSTRAINT fk_reservierung_gast FOREIGN KEY (GastID)
                                  REFERENCES Gast(Gast_ID) ON DELETE SET NULL,
                              CONSTRAINT fk_reservierung_partner FOREIGN KEY (PartnerID)
                                  REFERENCES B2BPartner(PartnerID) ON DELETE SET NULL,
                              CONSTRAINT check_mindestens_gastOderPartner
                                  CHECK (GastID IS NOT NULL OR PartnerID IS NOT NULL),
                              CONSTRAINT check_checkout_groesser_checkin
                                  CHECK (CheckOutDatum > CheckInDatum)
);

CREATE INDEX idx_reservierung_status ON Reservierung(ReservierungsStatus);
CREATE INDEX idx_reservierung_gast ON Reservierung(GastID);
CREATE INDEX idx_reservierung_partner ON Reservierung(PartnerID);
CREATE INDEX idx_reservierung_datum ON Reservierung(CheckInDatum, CheckOutDatum);

-- ===================================================================
-- 7. TABELLE: ReservierungsDetails
-- ===================================================================
CREATE TABLE ReservierungsDetails (
                                      ReservierungsDetailID SERIAL PRIMARY KEY,
                                      AnzahlZimmer INT NOT NULL CHECK (AnzahlZimmer > 0),
                                      PreisProNachtZumZeitpunkt DECIMAL(10, 2) NOT NULL CHECK (PreisProNachtZumZeitpunkt > 0),
                                      GesamtPreis DECIMAL(12, 2) NOT NULL CHECK (GesamtPreis > 0),
                                      ReservierungsID INT NOT NULL,
                                      ZimmerID INT NOT NULL,
                                      ErstelltAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                      CONSTRAINT fk_details_reservierung FOREIGN KEY (ReservierungsID)
                                          REFERENCES Reservierung(ReservierungsID) ON DELETE CASCADE,
                                      CONSTRAINT fk_details_zimmer FOREIGN KEY (ZimmerID)
                                          REFERENCES Zimmer(ZimmerID) ON DELETE RESTRICT
);

CREATE INDEX idx_reservierungsdetails_reservierung ON ReservierungsDetails(ReservierungsID);
CREATE INDEX idx_reservierungsdetails_zimmer ON ReservierungsDetails(ZimmerID);

-- ===================================================================
-- 8. TABELLE: Rechnung
-- ===================================================================
CREATE TABLE Rechnung (
                          RechnungsID SERIAL PRIMARY KEY,
                          RechnungsNummer VARCHAR(50) NOT NULL UNIQUE,
                          RechnungsDatum DATE NOT NULL DEFAULT CURRENT_DATE,
                          RechnungsStatus VARCHAR(20) NOT NULL DEFAULT 'offen'
                              CHECK (RechnungsStatus IN ('offen', 'teilbezahlt', 'bezahlt', 'storniert')),
                          BetragGesamt DECIMAL(12, 2) NOT NULL CHECK (BetragGesamt > 0),
                          Faelligkeitsdatum DATE NOT NULL,
                          ReservierungsID INT NOT NULL,
                          ErstelltAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          AktualisiertAm TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          CONSTRAINT fk_rechnung_reservierung FOREIGN KEY (ReservierungsID)
                              REFERENCES Reservierung(ReservierungsID) ON DELETE CASCADE,
                          CONSTRAINT check_faelligkeit_nach_rechnung
                              CHECK (Faelligkeitsdatum >= RechnungsDatum)
);

CREATE INDEX idx_rechnung_status ON Rechnung(RechnungsStatus);
CREATE INDEX idx_rechnung_reservierung ON Rechnung(ReservierungsID);
CREATE INDEX idx_rechnung_nummer ON Rechnung(RechnungsNummer);

-- ===================================================================
-- TESTDATEN: Zimmerkategorie
-- ===================================================================
INSERT INTO Zimmerkategorie (Name, Beschreibung, MaxPersonen, AnzahlBetten) VALUES
                                                                                ('Einzelzimmer', 'Komfortables Einzelzimmer mit Dusche', 1, 1),
                                                                                ('Doppelzimmer', 'Gemütliches Doppelzimmer mit König-Bett', 2, 1),
                                                                                ('Suite', 'Luxus Suite mit Wohn- und Schlafzimmer', 4, 2),
                                                                                ('Familienzimmer', 'Großes Zimmer für Familien', 6, 3),
                                                                                ('Superior Einzelzimmer', 'Einzelzimmer mit Balkon', 1, 1),
                                                                                ('Deluxe Doppelzimmer', 'Doppelzimmer mit Meerblick', 2, 1),
                                                                                ('Junior Suite', 'Suite mit Lounge Bereich', 3, 2),
                                                                                ('Premium Suite', 'Große Suite mit Whirlpool', 4, 2),
                                                                                ('Penthouse', 'Luxus Penthouse mit Dachterrasse', 6, 3),
                                                                                ('Apartment', 'Apartment mit Küchenzeile', 4, 2);

-- ===================================================================
-- TESTDATEN: Zimmer
-- ===================================================================
INSERT INTO Zimmer (Zimmernummer, PreisProNacht, Status, Etage, KategorieID) VALUES
                                                                                 ('101', 79.99, 'verfügbar', 1, 1),
                                                                                 ('102', 79.99, 'verfügbar', 1, 1),
                                                                                 ('103', 99.99, 'besetzt', 1, 1),
                                                                                 ('201', 129.99, 'verfügbar', 2, 2),
                                                                                 ('202', 129.99, 'verfügbar', 2, 2),
                                                                                 ('203', 129.99, 'wartung', 2, 2),
                                                                                 ('301', 249.99, 'verfügbar', 3, 3),
                                                                                 ('302', 249.99, 'besetzt', 3, 3),
                                                                                 ('401', 199.99, 'verfügbar', 4, 4),
                                                                                 ('402', 199.99, 'verfügbar', 4, 4),

                                                                                 ('104',79.99,'verfügbar',1,1),
                                                                                 ('105',79.99,'verfügbar',1,1),
                                                                                 ('106',89.99,'wartung',1,5),
                                                                                 ('107',89.99,'verfügbar',1,5),
                                                                                 ('108',89.99,'besetzt',1,5),

-- Etage 2
                                                                                 ('204',129.99,'verfügbar',2,2),
                                                                                 ('205',129.99,'verfügbar',2,2),
                                                                                 ('206',149.99,'verfügbar',2,6),
                                                                                 ('207',149.99,'besetzt',2,6),
                                                                                 ('208',149.99,'wartung',2,6),

-- Etage 3
                                                                                 ('303',249.99,'verfügbar',3,3),
                                                                                 ('304',249.99,'verfügbar',3,3),
                                                                                 ('305',199.99,'verfügbar',3,7),
                                                                                 ('306',199.99,'besetzt',3,7),
                                                                                 ('307',299.99,'verfügbar',3,8),
                                                                                 ('308',299.99,'verfügbar',3,8),

-- Etage 4
                                                                                 ('403',199.99,'verfügbar',4,4),
                                                                                 ('404',199.99,'verfügbar',4,4),
                                                                                 ('405',219.99,'verfügbar',4,10),
                                                                                 ('406',219.99,'besetzt',4,10),

-- Etage 5
                                                                                 ('501',399.99,'verfügbar',5,9),
                                                                                 ('502',399.99,'verfügbar',5,9),
                                                                                 ('503',399.99,'wartung',5,9);
-- ===================================================================
-- TESTDATEN: Gast
-- ===================================================================
INSERT INTO Gast (Vorname, Nachname, Email, Telefon) VALUES
                                                         ('Hans', 'Müller', 'hans.mueller@example.com', '+49 30 12345678'),
                                                         ('Anna', 'Schmidt', 'anna.schmidt@example.com', '+49 40 87654321'),
                                                         ('Klaus', 'Weber', 'klaus.weber@example.com', '+49 89 11223344'),
                                                         ('Julia', 'Fischer', 'julia.fischer@example.com', '+49 70 55443322'),
                                                         ('Peter', 'Bauer', 'peter.bauer@example.com', '+49 60 99887766'),
                                                         ('Lukas','Meier','lukas.meier@test.de','+49 151 1111111'),
                                                         ('Sophie','Lang','sophie.lang@test.de','+49 152 2222222'),
                                                         ('Tim','Kraus','tim.kraus@test.de','+49 153 3333333'),
                                                         ('Laura','Neumann','laura.neumann@test.de','+49 154 4444444'),
                                                         ('Felix','Zimmer','felix.zimmer@test.de','+49 155 5555555'),
                                                         ('Marie','Wolf','marie.wolf@test.de','+49 156 6666666'),
                                                         ('Jonas','Becker','jonas.becker@test.de','+49 157 7777777'),
                                                         ('Emma','Schulz','emma.schulz@test.de','+49 158 8888888'),
                                                         ('Leon','Hartmann','leon.hartmann@test.de','+49 159 9999999'),
                                                         ('Mia','Krüger','mia.krueger@test.de','+49 160 1112222'),
                                                         ('Ben','Koch','ben.koch@test.de','+49 161 3334444'),
                                                         ('Lena','Busch','lena.busch@test.de','+49 162 5556666'),
                                                         ('Paul','Vogel','paul.vogel@test.de','+49 163 7778888'),
                                                         ('Clara','Graf','clara.graf@test.de','+49 164 9990000'),
                                                         ('Noah','Brandt','noah.brandt@test.de','+49 165 1231231'),
                                                         ('Ella','Roth','ella.roth@test.de','+49 166 4564564'),
                                                         ('Max','Lorenz','max.lorenz@test.de','+49 167 7897897'),
                                                         ('Hanna','Jäger','hanna.jaeger@test.de','+49 168 1010101'),
                                                         ('David','Kuhn','david.kuhn@test.de','+49 169 2020202'),
                                                         ('Nina','Simon','nina.simon@test.de','+49 170 3030303');

-- ===================================================================
-- TESTDATEN: B2BPartner
-- ===================================================================
INSERT INTO B2BPartner (Name, Typ, Email, Telefon, Status) VALUES
                                                               ('TravelPartner AG', 'Agentur', 'contact@travelpartner.de', '+49 30 100200300', 'aktiv'),
                                                               ('Hotel Chain Europa', 'Konzern', 'booking@hotelchaineuropa.de', '+49 40 400500600', 'aktiv'),
                                                               ('Local Tours GmbH', 'Vermittler', 'info@localtours.de', '+49 89 700800900', 'aktiv'),
                                                               ('Businesstravel Plus', 'Agentur', 'business@travel-plus.de', '+49 69 200300400', 'aktiv'),
                                                               ('City Hotels Network', 'Hotel', 'network@cityhotels.de', '+49 20 500600700', 'inaktiv'),
                                                               ('Global Travel GmbH','Agentur','info@globaltravel.de','+49 30 111000','aktiv'),
                                                               ('BusinessStay AG','Konzern','contact@businessstay.de','+49 40 222000','aktiv'),
                                                               ('EventWorld','Vermittler','info@eventworld.de','+49 50 333000','aktiv'),
                                                               ('Holiday Experts','Agentur','mail@holidayexperts.de','+49 60 444000','aktiv'),
                                                               ('Luxury Booking','Agentur','booking@luxury.de','+49 70 555000','aktiv'),
                                                               ('CityTrip Europe','Vermittler','info@citytrip.de','+49 80 666000','aktiv'),
                                                               ('Corporate Lodging','Konzern','corp@lodging.de','+49 90 777000','aktiv');

-- ===================================================================
-- TESTDATEN: Vertrag
-- ===================================================================
INSERT INTO Vertrag (VonDatum, BisDatum, VertragsStatus, PartnerID) VALUES
                                                                        ('2024-01-01', '2025-12-31', 'aktiv', 1),
                                                                        ('2024-03-15', '2025-03-14', 'aktiv', 2),
                                                                        ('2024-06-01', '2026-06-01', 'aktiv', 3),
                                                                        ('2025-01-01', '2025-12-31', 'aktiv', 4),
                                                                        ('2023-01-01', '2024-12-31', 'abgelaufen', 5),
                                                                        ('2025-02-01', '2026-01-31', 'aktiv', 6),
                                                                        ('2024-09-01', '2025-08-31', 'beendet', 7),
                                                                        ('2023-05-01', '2024-05-01', 'abgelaufen', 8);

-- ===================================================================
-- TESTDATEN: Reservierung
-- ===================================================================
INSERT INTO Reservierung (AnzahlNaechte, CheckInDatum, CheckOutDatum, ReservierungsStatus, ReservierungsReferenz, GastID, PartnerID) VALUES
                                                                                                                                         (3, '2025-12-05', '2025-12-08', 'bestätigt', 'RES-2025-001', 1, NULL),
                                                                                                                                         (2, '2025-12-06', '2025-12-08', 'bestätigt', 'RES-2025-002', 2, NULL),
                                                                                                                                         (4, '2025-12-10', '2025-12-14', 'in Bearbeitung', 'RES-2025-003', 3, NULL),
                                                                                                                                         (5, '2025-12-15', '2025-12-20', 'bestätigt', 'RES-2025-004', NULL, 1),
                                                                                                                                         (2, '2025-12-08', '2025-12-10', 'bestätigt', 'RES-2025-005', 4, NULL),
                                                                                                                                         (7, '2025-12-12', '2025-12-19', 'bestätigt', 'RES-2025-006', NULL, 2),
                                                                                                                                         (3, '2025-12-25', '2025-12-28', 'bestätigt', 'RES-2025-007', 5, NULL),
                                                                                                                                         (2,'2026-01-05','2026-01-07','bestätigt','RES-2026-001',6,NULL),
                                                                                                                                         (4,'2026-01-10','2026-01-14','bestätigt','RES-2026-002',7,NULL),
                                                                                                                                         (3,'2026-01-15','2026-01-18','in Bearbeitung','RES-2026-003',NULL,3),
                                                                                                                                         (5,'2026-02-01','2026-02-06','bestätigt','RES-2026-004',8,NULL),
                                                                                                                                         (7,'2026-02-10','2026-02-17','bestätigt','RES-2026-005',NULL,4),
                                                                                                                                         (1,'2026-03-01','2026-03-02','bestätigt','RES-2026-006',9,NULL),
                                                                                                                                         (3,'2026-03-05','2026-03-08','bestätigt','RES-2026-007',10,NULL),
                                                                                                                                         (2,'2026-03-15','2026-03-17','bestätigt','RES-2026-008',NULL,5);

-- ===================================================================
-- TESTDATEN: ReservierungsDetails
-- ===================================================================
INSERT INTO ReservierungsDetails (AnzahlZimmer, PreisProNachtZumZeitpunkt, GesamtPreis, ReservierungsID, ZimmerID) VALUES
                                                                                                                       (1, 79.99, 239.97, 1, 1),
                                                                                                                       (1, 129.99, 259.98, 2, 4),
                                                                                                                       (2, 199.99, 799.96, 3, 9),
                                                                                                                       (2, 249.99, 1249.95, 4, 7),
                                                                                                                       (1, 129.99, 259.98, 5, 5),
                                                                                                                       (1, 79.99, 559.93, 6, 2),
                                                                                                                       (3, 199.99, 599.97, 7, 10),
                                                                                                                       (1,79.99,159.98,8,4),
                                                                                                                       (1,129.99,519.96,9,5),
                                                                                                                       (2,199.99,1199.94,10,9),
                                                                                                                       (1,399.99,1999.95,11,21),
                                                                                                                       (1,89.99,89.99,12,14),
                                                                                                                       (2,249.99,1499.94,13,7),
                                                                                                                       (1,149.99,449.97,14,16);

-- ===================================================================
-- TESTDATEN: Rechnung
-- ===================================================================
INSERT INTO Rechnung (RechnungsNummer, RechnungsDatum, RechnungsStatus, BetragGesamt, Faelligkeitsdatum, ReservierungsID) VALUES
                                                                                                                              ('INV-2025-001', '2025-12-03', 'offen', 239.97, '2025-12-10', 1),
                                                                                                                              ('INV-2025-002', '2025-12-03', 'bezahlt', 259.98, '2025-12-08', 2),
                                                                                                                              ('INV-2025-003', '2025-12-03', 'offen', 799.96, '2025-12-17', 3),
                                                                                                                              ('INV-2025-004', '2025-12-03', 'offen', 1249.95, '2025-12-22', 4),
                                                                                                                              ('INV-2025-005', '2025-12-03', 'teilbezahlt', 259.98, '2025-12-15', 5),
                                                                                                                              ('INV-2025-006', '2025-12-03', 'offen', 559.93, '2025-12-17', 6),
                                                                                                                              ('INV-2025-007', '2025-12-03', 'offen', 599.97, '2025-12-31', 7),
                                                                                                                              ('INV-2026-001','2026-01-03','offen',159.98,'2026-01-10',8),
                                                                                                                              ('INV-2026-002','2026-01-08','bezahlt',519.96,'2026-01-15',9),
                                                                                                                              ('INV-2026-003','2026-01-13','offen',1199.94,'2026-01-20',10),
                                                                                                                              ('INV-2026-004','2026-01-30','offen',1999.95,'2026-02-06',11),
                                                                                                                              ('INV-2026-005','2026-02-08','offen',89.99,'2026-02-15',12),
                                                                                                                              ('INV-2026-006','2026-03-03','offen',1499.94,'2026-03-10',13),
                                                                                                                              ('INV-2026-007','2026-03-13','offen',449.97,'2026-03-20',14);

-- ===================================================================
-- VIEWS FÜR HÄUFIGE ABFRAGEN
-- ===================================================================

-- View: Aktuelle Reservierungen mit Gastdetails
CREATE VIEW v_aktuelle_reservierungen AS
SELECT
    r.ReservierungsID,
    r.ReservierungsReferenz,
    COALESCE(g.Vorname || ' ' || g.Nachname, 'B2B Partner') AS Gast_Name,
    COALESCE(g.Email, bp.Email) AS Email,
    r.CheckInDatum,
    r.CheckOutDatum,
    r.AnzahlNaechte,
    r.ReservierungsStatus,
    COUNT(rd.ZimmerID) AS Anzahl_Zimmer,
    SUM(rd.GesamtPreis) AS Gesamtpreis
FROM Reservierung r
         LEFT JOIN Gast g ON r.GastID = g.Gast_ID
         LEFT JOIN B2BPartner bp ON r.PartnerID = bp.PartnerID
         LEFT JOIN ReservierungsDetails rd ON r.ReservierungsID = rd.ReservierungsID
GROUP BY r.ReservierungsID, g.Gast_ID, g.Vorname, g.Nachname, g.Email, bp.Email
ORDER BY r.CheckInDatum DESC;

-- View: Verfügbare Zimmer pro Kategorie
CREATE VIEW v_zimmer_verfuegbarkeit AS
SELECT
    zk.KategorieID,
    zk.Name AS Kategorie,
    COUNT(z.ZimmerID) AS Gesamt_Zimmer,
    SUM(CASE WHEN z.Status = 'verfügbar' THEN 1 ELSE 0 END) AS Verfuegbare_Zimmer,
    zk.MaxPersonen,
    zk.AnzahlBetten,
    ROUND(100.0 * SUM(CASE WHEN z.Status = 'verfügbar' THEN 1 ELSE 0 END) / COUNT(z.ZimmerID), 1) AS Verfuegbarkeit_Prozent
FROM Zimmer z
         JOIN Zimmerkategorie zk ON z.KategorieID = zk.KategorieID
GROUP BY zk.KategorieID, zk.Name, zk.MaxPersonen, zk.AnzahlBetten
ORDER BY zk.Name;

-- View: Offene Rechnungen nach Partner
CREATE VIEW v_offene_rechnungen_partner AS
SELECT
    bp.PartnerID,
    bp.Name AS Partner_Name,
    bp.Typ AS Partner_Typ,
    COUNT(r.RechnungsID) AS Anzahl_Offene_Rechnungen,
    SUM(r.BetragGesamt) AS Gesamtbetrag_Offen,
    MAX(r.Faelligkeitsdatum) AS Aelteste_Faelligkeit
FROM Rechnung r
         JOIN Reservierung res ON r.ReservierungsID = res.ReservierungsID
         JOIN B2BPartner bp ON res.PartnerID = bp.PartnerID
WHERE r.RechnungsStatus IN ('offen', 'teilbezahlt')
GROUP BY bp.PartnerID, bp.Name, bp.Typ
ORDER BY Gesamtbetrag_Offen DESC;

-- View: Reservierungen nach Gastname
CREATE VIEW v_reservierungen_pro_gast AS
SELECT
    g.Gast_ID,
    g.Vorname,
    g.Nachname,
    g.Email,
    COUNT(r.ReservierungsID) AS Anzahl_Reservierungen,
    SUM(r.AnzahlNaechte) AS Gesamt_Naechte,
    SUM(rd.GesamtPreis) AS Gesamtausgaben,
    MAX(r.CheckInDatum) AS Letzte_Reservierung
FROM Gast g
         LEFT JOIN Reservierung r ON g.Gast_ID = r.GastID
         LEFT JOIN ReservierungsDetails rd ON r.ReservierungsID = rd.ReservierungsID
GROUP BY g.Gast_ID, g.Vorname, g.Nachname, g.Email
ORDER BY g.Nachname, g.Vorname;





-- ===================================================================
-- TRANSAKTION 1: Neue Reservierung mit Rechnung (Privatgast)
-- Ziel: Eine vollständige Buchung atomar anlegen
-- ===================================================================

START TRANSACTION;

-- 1. Neue Reservierung anlegen
INSERT INTO Reservierung
(AnzahlNaechte, CheckInDatum, CheckOutDatum, ReservierungsStatus, ReservierungsReferenz, GastID, PartnerID)
VALUES
    (3, '2026-06-10', '2026-06-13', 'bestätigt', 'RES-2026-006', 9, NULL);

-- 2. Reservierungsdetails hinzufügen (Zimmer 205)
INSERT INTO ReservierungsDetails
(AnzahlZimmer, PreisProNachtZumZeitpunkt, GesamtPreis, ReservierungsID, ZimmerID)
VALUES
    (1, 139.99, 419.97, LAST_INSERT_ID(), 10);

-- 3. Rechnung erzeugen
INSERT INTO Rechnung
(RechnungsNummer, RechnungsDatum, RechnungsStatus, BetragGesamt, Faelligkeitsdatum, ReservierungsID)
VALUES
    ('INV-2026-006', CURDATE(), 'offen', 419.97, DATE_ADD(CURDATE(), INTERVAL 14 DAY), LAST_INSERT_ID());

COMMIT;



-- ===================================================================
-- TRANSAKTION 2: Check-In Prozess
-- Ziel: Zimmerstatus ändern + Reservierung aktualisieren
-- ===================================================================

START TRANSACTION;

-- 1. Zimmer auf "besetzt" setzen
UPDATE Zimmer
SET Status = 'besetzt'
WHERE ZimmerID = 10;

-- 2. Reservierung auf "eingecheckt" setzen
UPDATE Reservierung
SET ReservierungsStatus = 'eingecheckt'
WHERE ReservierungsID = 1;

COMMIT;



-- ===================================================================
-- TRANSAKTION 3: Zahlung einer Rechnung
-- Ziel: Rechnung als bezahlt markieren
-- ===================================================================

START TRANSACTION;

UPDATE Rechnung
SET RechnungsStatus = 'bezahlt'
WHERE RechnungsNummer = 'INV-2025-003';

COMMIT;



-- ===================================================================
-- TRANSAKTION 4: Stornierung einer Reservierung
-- Ziel: Reservierung stornieren + Zimmer freigeben
-- ===================================================================

START TRANSACTION;

-- 1. Reservierung stornieren
UPDATE Reservierung
SET ReservierungsStatus = 'storniert'
WHERE ReservierungsID = 3;

-- 2. Zimmer wieder verfügbar machen
UPDATE Zimmer
SET Status = 'verfügbar'
WHERE ZimmerID = 15;

-- 3. Rechnung stornieren
UPDATE Rechnung
SET RechnungsStatus = 'storniert'
WHERE ReservierungsID = 3;

COMMIT;



-- ===================================================================
-- TRANSAKTION 5: Fehlerfall mit Rollback
-- Ziel: Demonstration von ROLLBACK bei Fehler
-- ===================================================================

START TRANSACTION;

-- 1. Neue Reservierung
INSERT INTO Reservierung
(AnzahlNaechte, CheckInDatum, CheckOutDatum, ReservierungsStatus, ReservierungsReferenz, GastID, PartnerID)
VALUES
    (2, '2026-07-01', '2026-07-03', 'bestätigt', 'RES-2026-007', 10, NULL);

-- 2. Fehlerhafte Zimmerzuweisung (nicht existierende ZimmerID 999)
INSERT INTO ReservierungsDetails
(AnzahlZimmer, PreisProNachtZumZeitpunkt, GesamtPreis, ReservierungsID, ZimmerID)
VALUES
    (1, 199.99, 399.98, LAST_INSERT_ID(), 999);

-- Falls Fehler auftritt → alles rückgängig machen
ROLLBACK;


-- ===================================================================
-- VERWENDUNGSHINWEISE
-- ===================================================================
-- 1. Alle 8 Tabellen werden mit korrekten Constraints erstellt
-- 2. Testdaten werden automatisch eingefügt
-- 3. 4 Views stehen für häufige Abfragen zur Verfügung
-- 4. Für neue Abfragen: SELECT * FROM v_[ViewName];
-- 5. Transaktionen erstellt für sichere Aktionen in der Datenbank