Django Agata
============

django-agata is a management software developed by 4Sigma.

Available modules
-----------------

* Anagrafiche

* Contabilità

* Articoli

* Magazzino

* Ordini


Configuration
-------------

1. Add ``agata`` to your ``INSTALLED_APPS``.

2. Include django-agata urls in ``urls.py``::

    url(r'^agata/', include('agata.urls'))

Options
-------

AGATA_INSTANCE = '4Sigma'

IVA = Decimal('0.22')

ORIGINI_FATTURE = (
    ('4Sigma Snc', '4Sigma Snc'),
    ('Studio Associato 4Sigma', 'Studio Associato 4Sigma'),
)

DEFAULT_ORIGINE_FATTURA = '4Sigma Snc'

ANNI = [ 2015, 2014, 2013, ] # Aggiungere qui gli anni man mano che passano

TIPI_INDIRIZZO = (
    ('Sede legale', 'Sede legale'),
    ('Sede operativa', 'Sede operativa'),
    ('Sede commerciale', 'Sede commerciale'),
    ('Altra sede', 'Altra sede'),
    ('Punto di esercizio', 'Punto di esercizio'),
    ('Negozio', 'Negozio'),
    ('Magazzino', 'Magazzino'),
    ('Contatto aziendale', 'Contatto aziendale'),
)

TIPI_FATTURA = (
    ('Prestazione professionale', 'Prestazione professionale'),
    ('Vendita', 'Vendita'),
    ('', ''),
    )

TIPI_ATTIVITA = (
    ('Sviluppo e manutenzione software', 'Sviluppo e manutenzione software'),
    ('Di sistema', 'Di sistema'),
    ('Sviluppo driver', 'Sviluppo driver'),
    ('Applicativi ERP, CRM, SCM', 'Applicativi ERP, CRM, SCM'),
    ('Applicativi E-Commerce, E-Business, E-Finance', 'Applicativi E-Commerce, E-Business, E-Finance'),
    ('Applicativi GIS, CAD, CAM', 'Applicativi GIS, CAD, CAM'),
    ('Altri software applicativi', 'Altri software applicativi'),
    ('Commercializzazione software', 'Commercializzazione software'),
    ('Sviluppo Siti (Internet, Intranet, Extranet', 'Sviluppo Siti (Internet, Intranet, Extranet)'),
    ('Consulenza', 'Consulenza'),
    ('Audit EDP', 'Audit EDP'),
    ('Progettazione sistema informativo (dimensionamento, scelta piattaforme HW e SW)', 'Progettazione sistema informativo (dimensionamento, scelta piattaforme HW e SW)'),
    ('Studio di fattibilità', 'Studio di fattibilità'),
    ('Assist. alla gestione dei progetti', 'Assist. alla gestione dei progetti'),
    ('Assistenza alla gestione del sistema informativo aziendale', 'Assistenza alla gestione del sistema informativo aziendale'),
    ('Implementazione dei sistemi (installazione, configurazione, test)', 'Implementazione dei sistemi (installazione, configurazione, test)'),
    ('Soluzioni ERP, CRM, SCM', 'Soluzioni ERP, CRM, SCM'),
    ('Soluzione web-based (portali, siti, e-commerce, e-business, e-finance)', 'Soluzione web-based (portali, siti, e-commerce, e-business, e-finance)'),
    ('Acquisizione ed elaborazione dati', 'Acquisizione ed elaborazione dati'),
    ('Formazione erogata', 'Formazione erogata'),
    ('Elaborazione grafiche', 'Elaborazione grafiche'),
    ('Hosting/ASP', 'Hosting/ASP'),
    ('Attività di sicurezza informatica', 'Attività di sicurezza informatica'),
    ('Altro', 'Altro'),
    )


TIPOLOGIA_CLIENTELA = (
    ('D36-Aziende di informatica', 'D36-Aziende di informatica'),
    ('D37-Imprenditori individuali ed esercenti arti e professioni', 'D37-Imprenditori individuali ed esercenti arti e professioni'),
    ('D38-Societa\'', 'D38-Societa\''),
    ('D39-Enti pubblici e privati', 'D39-Enti pubblici e privati'),
    ('D40-di cui Enti Pubblici Territoriali (comuni , province , regioni)', 'D40-di cui Enti Pubblici Territoriali (comuni , province , regioni)'),
    ('D41-di cui tribunali e altre sedi giudiziarie', 'D41-di cui tribunali e altre sedi giudiziarie'),
    ('D42-Altri soggetti', 'D42-Altri soggetti'),
    ('D43-di cui privati', 'D43-di cui privati')
)



Usage
-----------

WIP
