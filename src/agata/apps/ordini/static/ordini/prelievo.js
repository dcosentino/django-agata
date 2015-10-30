function articolo_obj(bcr, descr, qta, letti) {
    this.bcr = bcr;
    this.descr = descr;
    this.qta = qta;
    this.letti = letti;

    //Torna true se il pezzo è aspettato o false se in eccedenza
    this.marca = function() {
        this.letti++;
        if (this.letti<=this.qta) {
            // ok
            return true;
        }
        // eccesso
        return false;
    }

    //Torna true se esiste almeno un pezzo da cancellare
    this.cancella = function() {
        if (this.letti<=0)
            return false;
        this.letti--;
        return true;
    }

    //Restituisce il numero di pezzi ancora da fare
    this.mancanti = function() {
        return this.qta - this.letti;
    }

    this.testata = function(richiesto) {
        var ret;

        ret="<table cellpadding='1' cellspacing='0'><tr><td class='xxsmall_text'>Articolo(Codice)/Colore/Taglia</td>\n"+
        "<td style='font-weight:bold' class='small_text'>"+this.descr+"</td></tr>\n"+
        "<tr><td class='xxsmall_text'>Codice</td>\n"+
        "<td style='font-weight:bold' class='small_text'>"+this.bcr+"</td></tr>\n";
        if (richiesto) {
            ret+="<tr><td class='xxsmall_text'>Pezzi letti/richiesti</td>\n"+
                "<td style='font-weight:bold' class='small_text'>"+(this.qta-this.mancanti()).toString()+"/"+this.qta.toString()+"</td></tr>\n";
        }
        ret+="</table><hr/>";
  
        return ret;
    }
    
    return this;
}

function play_sound(what) {
    what.currentTime=0;
    what.play();
}

function update_gui(cancella_codice) {
    // Update dei campi
    var lista;
    
    $("#codici").val(letture.join("\n"));
    lista = $("#lista");
    lista.html("Lista dei codici letti:<br/>"+letture.join("<br/>")).scrollTop(lista.innerHeight());
    if (cancella_codice)
        $("#codice").val("").focus();
    else
        $("#codice").focus();
}

function verifica(style, messaggio, art) {
    $("#verifica").attr("class",style);

    if (art == null) {
        $("#verifica").html(messaggio);
    } else {
        $("#verifica").html(messaggio+"<br/>"+art.testata(true));
    }
}

function nuovo_collo() {
    var last;

    last = letture[letture.length-1];
    if (last != "*" && last != "+") {
        // Un solo cambio collo alla volta
        add_code("+");
    }
    // Non fare nulla
}

function add_code(codice) {
    if (codice == null)
        codice = $("#codice").val();

    // Normalizzazione a causa di alcune pistole
    if (codice.length==12) {
        codice=(new Array("0",codice)).join("");
    }

    // campo vuoto?
    if (codice=="")
        return;

    if (codice == "+" || codice == "*") {
        // cambio collo
        letture.push("+");
        play_sound(audiofx.letturaok);
        verifica("tab_magazzino_ok","Cambio collo",null);
    } else {
        var art;
        
        art = expected_codes[codice];
        letture.push(codice);
        if (!isObject(art)) {
            // codice non riconosciuto
            verifica("tab_magazzino_unknown","Codice "+codice+" sconosciuto o non richiesto", null);
            play_sound(audiofx.letturasconosciuto);
        } else {
            // codice articolo riconosciuto
            var art_ok;
            art_ok = art.marca();

            if (!art_ok) {
                // eccesso
                verifica("tab_magazzino_more","Articolo in eccedenza",art);
                play_sound(audiofx.letturaesubero);
            } else if (art.mancanti() == 0) {
                // completo
                verifica("tab_magazzino_ok","Completamente soddisfatta",art);
                play_sound(audiofx.letturaartcompleto);
            } else {
                // ancora incompleto
                verifica("tab_magazzino_some","Da caricare altri "+art.mancanti()+" pezzi",art);
                play_sound(audiofx.letturacompleto);
            }
        }
    }

    update_gui(true);
}

function delete_last() {
    var codice;
    
    if (letture.length==0)
        // Non fare nulla
        return;

    codice = letture.pop();
    if (codice=="+" || codice=="*") {
        verifica("tab_magazzino_ok","Cambio collo annullato", null);
    } else {
        var art;

        art=expected_codes[codice];
        if (!isObject(art)) {
            verifica("tab_magazzino_ok","Codice non richiesto "+codice+" stornato", null);
        } else {
            art.cancella();

            if (art.letti==0) {
                // Completamente rimosso
                verifica("tab_magazzino_some","Articolo completamente rimosso", art);
            } else if (art.mancanti()<0) {
                // Ancora in esubero
                eccedenza = -art.mancanti();
                verifica("tab_magazzino_more","Eccedenza rimasta di "+eccedenza+" pezzi", art);
            } else if (art.mancanti() == 0) {
                // Tornato ok
                verifica("tab_magazzino_ok","Completamente soddisfatta",art);
            } else {
                // alcuni pezzi sono ancora da caricare
                verifica("tab_magazzino_some","Da caricare altri "+art.mancanti()+" pezzi",art);
            }
        }
    }
    update_gui(false);
}

function conferma_bcr(e) {
    switch (e.keyCode) {
    case 13:
        add_code();
        break;
    }    
}

function setup() {
    var lista = $("#lista");
    
    $("#codice").focus();
    $("#verifica").html("Leggere i codici");

    update_gui(true);

    $("#codice").keypress(conferma_bcr);
}

$(document).ready(setup);
