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

    this.testata = function(non_richiesto) {
        var ret;

        ret="<table cellpadding='1' cellspacing='0'><tr><td class='xxsmall_text'>Articolo(Codice)/Colore/Taglia</td>\n"+
        "<td style='font-weight:bold' class='small_text'>"+this.descr+"</td></tr>\n"+
        "<tr><td class='xxsmall_text'>Codice</td>\n"+
        "<td style='font-weight:bold' class='small_text'>"+this.bcr+"</td></tr>\n";
        if (!non_richiesto) {
            ret+="<tr><td class='xxsmall_text'>Pezzi letti/richiesti</td>\n"+
                "<td style='font-weight:bold' class='small_text'>"+(this.qta-this.mancanti()).toString()+"/"+this.qta.toString()+"</td></tr>\n";
        }
        ret+="</table><hr/>";
  
        return ret;
    }
    
    return this;
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







function verificaStatoNonRichiesto(codice,visdiv_obj) {
    var data;

    data = null;
    // //Verifica in cache
    // data=codici_non_richiesti[codice];
    // if (data==null) {
    //     //Richiesta al server (si può fare sincrona?) 
    //     var bcr = document.getElementById("bcr_richiesta");
    //     bcr.value=codice;
    //     var res = ajax_sync_submit_form(document.getElementById("form_articolo"),null);
    //     if (!isArray(res) && res==false) {
    //         alert ("Richiesta fallita");
    //     } else if (!res[0]) {
    //         alert ("Richiesta fallita: "+res[1]);
    //     } else {
    //         var received = analizza_risposta(res[1]);
    //         //TODO: analizzare, impostare nella cache e restituire
    //         if (received!=false) {
    //             var riepilogo=findFirstChild(received,"elementi");
    //             var numero=riepilogo.attributes['numero'].value;
    //             //Non può che essere 1 o 0
    //             if (numero==1) {
    //                 var articolo = findFirstChild(received,"item");
    //                 var data = new Object();
    //                 data.codice=articolo.attributes['bcr'].value;
    //                 data.artcode=articolo.attributes['cod_art'].value;
    //                 data.taglia=articolo.attributes['taglia'].value;
    //                 data.colore=articolo.attributes['colore'].value;
    //                 data.descrizione=articolo.textContent;
    //                 codici_non_richiesti[codice]=data;
    //             }
    //         }
    //     }
    // }

    if (data==null) {
        //Anche sconosciuto
        visdiv_obj.innerHTML="Codice "+codice+" sconosciuto";
        visdiv_obj.className="tab_magazzino_unknown";
        return audiofx.letturasconosciuto;
    }

    //ci sono dei dati
    visdiv_obj.innerHTML=testata_codice_lettura(data,true)+"Non richiesto";
    //TODO: mettere i dati dell'articolo
    visdiv_obj.className="tab_magazzino_not_requested";
    return audiofx.letturasconosciuto;
}

function delete_last() {
    var ctrl=document.getElementById("codice");
    var verifica=document.getElementById("verifica");
    var lista=document.getElementById("lista");
    var hidden=document.getElementById("codici");

    if (letture.length>0) {
        var codice=letture.pop();
    
        if (codice=="+" || codice=="*") {
            //Storno di un cambio collo
            verifica.className="tab_magazzino_ok";
            verifica.innerHTML="Cambio collo stornato";
        } else if (isObject(expected_codes[codice])) {
            //Lo storno di una lettura va registrata opportunamente

            var art=expected_codes[codice];
            var rimozione=art.cancella();
            var descrizione_aggiuntiva="";
            if (rimozione==false) {
                //Mancanza: ?!?
                verifica.className="tab_magazzino_some";
                descrizione_aggiuntiva="Eliminati più pezzi di quelli letti?";
            } else if (art.richiesti-art.mancanti()==0) {
                verifica.className="tab_magazzino_some";
                descrizione_aggiuntiva="Nessun pezzo letto per questo prodotto";
            } else if (art.mancanti()>0) {
                verifica.className="tab_magazzino_some";
                descrizione_aggiuntiva="Da caricare altri "+ art.mancanti().toString() +" pezzi";
            } else if (art.mancanti()<0) {
                verifica.className="tab_magazzino_more";
                var eccedenza= -art.mancanti();
                descrizione_aggiuntiva="Eccedenza rimasta di "+ eccedenza +" pezzi";
            } else {  
                verifica.className="tab_magazzino_ok";
                descrizione_aggiuntiva="Completamente soddisfatta";
            }
      
            verifica.innerHTML=testata_codice_lettura(art,false)+descrizione_aggiuntiva;
      
        } else {
            //Storno di un codice sconosciuto
            verifica.className="tab_magazzino_ok";
            verifica.innerHTML="Voce sconosciuta stornata";
        }

        ctrl.value=codice;
    
        lista.innerHTML="Lista dei codici letti:<br/>"+letture.join("<br/>")+"<br/>";
        lista.scrollTop=lista.scrollHeight;
        hidden.value=letture.join("\n");
    } else {
        alert ("La lista delle letture è vuota");
    }
  
    gotoBcr(ctrl);
}


function add_code() {
  var ctrl=$(#"codice");
  var verifica=$("#verifica");
  var lista=$("#lista");
  var hidden=$("#codici");
  var codice=ctrl.val();
  var add=false;

  var suona_ad_ok = true;

  if (codice.length==12) {
      codice=(new Array("0",codice)).join("");
  }

  if (codice=="")
      return;

  if (codice=="+" || codice=="*") {
      // Cambio collo
      
      ctrl.value="";
      verifica.className="tab_magazzino_ok";
      verifica.innerHTML="Cambio collo";
      audiofx.letturaok.currentTime=0;
      audiofx.letturaok.play();
      add=true;
  } else if (!isObject(expected_codes[codice])) {
      var suono = verificaStatoNonRichiesto(codice, verifica);

      gotoBcr(ctrl);

      suono.currentTime=0;
      suono.play();
      add=true;
  } else {
      //TODO: utilizzare le info dell'articolo per identificarlo
      var art=expected_codes[codice];
    
      var aggiunta=art.marca();
      var fine=false;
      if (aggiunta) {
          fine=true;
          for (bcr in expected_codes) {
              if (expected_codes[bcr].mancanti()!=0) {
                  fine=false;
                  break;
              }
          }
      }

      var endsound = { 
      onfinish:function() {
              audiofx.letturacompleto.currentTime=0;
              audiofx.letturacompleto.play();
          }
      }
    
      if (aggiunta==false) {
          //Eccesso;
          verifica.className="tab_magazzino_more";
          descrizione_aggiuntiva="Articolo in eccedenza";
          audiofx.letturaesubero.currentTime=0;
          audiofx.letturaesubero.play();
          // Aggiungilo comunque alla lista
          add=true;
      } else if (art.mancanti()>0) {
          verifica.className="tab_magazzino_some";
          descrizione_aggiuntiva="Da caricare altri "+ art.mancanti().toString() +" pezzi";
          if (suona_ad_ok) {
              audiofx.letturaok.currentTime=0;
              audiofx.letturaok.play(); // Accodare endsound
          } else if (fine) {
              audiofx.letturacompleto.currentTime=0;
              audiofx.letturacompleto.play();
          }
          add=true;
      } else {
          verifica.className="tab_magazzino_ok";
          descrizione_aggiuntiva="Completamente soddisfatta";
          if (suona_ad_ok) {
              audiofx.letturaartcompleto.currentTime=0;
              audiofx.letturaartcompleto.play(); // accodare endsound
          } else if (fine) {
              audiofx.letturacompleto.currentTime=0;
              audiofx.letturacompleto.play();
          }
          add=true;
      }
    
      if (!add) {
          art.cancella();
      } 
      if (fine) {
          descrizione_aggiuntiva=descrizione_aggiuntiva+"<br/><b>Ordine completato</b>";
      }

      verifica.innerHTML=testata_codice_lettura(art,false)+descrizione_aggiuntiva;
  }
  if (add) {
      letture.push(codice);
      lista.appendChild(document.createTextNode(codice));
      lista.appendChild(document.createElement("BR"));
      
      lista.scrollTop=lista.scrollHeight;
      hidden.value=letture.join("\n");
  }

  gotoBcr(ctrl);

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
    lista.html("Lista dei codici letti:<br/>"+letture.join("<br/>")+"<br/>").scrollTop(lista.height);
    $("#codici").val(letture.join("\n"));

    $("#codice").keypress(conferma_bcr);
}

$(document).ready(setup);
