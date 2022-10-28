import datetime
from distutils.log import error
from google.cloud import datastore
from flask import Flask, render_template, request, url_for, session, redirect
import google.cloud.datastore
import random
#from polyglot import PolyglotForm
import wtforms
from wtforms import Form, BooleanField, StringField, validators, IntegerField, SelectField, widgets, SelectMultipleField, ValidationError, RadioField, DecimalField
from wtforms.validators import NumberRange
from flask_wtf import FlaskForm
import json
from authlib.integrations.flask_client import OAuth


app = Flask(__name__)

app.secret_key = '"\xf9$T\x88\xefT8[\xf1\xc4Y-r@\t\xec!5d\xf9\xcc\xa2\xaa'
app.config.from_object('config')

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.route('/')
def homepage():
    user = session.get('user')
    return render_template('home.html', user=user)
    

@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    session['user'] = token['access_token']
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/data')
def datatesti():
    datastore_client = google.cloud.datastore.Client() 

    # Tallennettava tyyppi
    kind = "Testi"
    # id/nimi
    name = "mallitietue3"
    # Datastoren avain lisättävälle objektille
    testi_key = datastore_client.key(kind, name)

    # Varsinaisen objektin luominen
    testi = google.cloud.datastore.Entity(key=testi_key) 
    testi["kuvaus"] = "Testiteksti"

    # Saves the entity
    datastore_client.put(testi)

    return f"Tallennettiin {testi.key.name}: {testi['kuvaus']}"

#@app.route('/alustus')
#def alustus():
#    kilpailut = [
#        {"id": 1, "kisanimi":"Jäärogaining", "loppuaika": "2019-03-17 20:00:00", "alkuaika": "2019-03-15 09:00:00"}, 
#        {"id": 2, "kisanimi":"Fillarirogaining", "loppuaika": "2016-03-17 20:00:00", "alkuaika": "2016-03-15 09:00:00"}, 
#        {"id": 3, "kisanimi":"Kintturogaining", "loppuaika": "2017-03-18 20:00:00", "alkuaika": "2017-03-18 09:00:00"},
#        {"id": 99, "kisanimi":"Jäärogaining", "loppuaika": "2021-05-01 20:00:00", "alkuaika": "2021-05-01 12:00:00"}]
#    sarjat = [
#        {"sarjanimi":"4 h", "kilpailu": 1, "kesto": 4},
#        {"sarjanimi":"2 h", "kilpailu": 1, "kesto": 2}, 
#        {"sarjanimi":"8 h", "kilpailu": 1, "kesto": 8},
#        {"sarjanimi":"Pikkusarja", "kilpailu": 3, "kesto": 4},
#        {"sarjanimi":"8 h", "kilpailu": 3, "kesto": 8},
#        {"sarjanimi":"Isosarja", "kilpailu": 3, "kesto": 8},
#        {"sarjanimi":"Pääsarja", "kilpailu": 2, "kesto": 4},
#        {"sarjanimi":"2 h", "kilpailu": 2, "kesto": 2}]
#
#    client = google.cloud.datastore.Client()
#
#    for x in kilpailut:
#        id = random.randint(10000, 99999)
#        kaytetytIdt = []
#        
#        while id in kaytetytIdt:
#            id = random.randint(10000, 99999)
#        
#        kaytetytIdt.append(id)
#
#        vanhempikey = client.key("Kilpailu", str(id)) #id täytyy antaa, että voidaan käyttää parentina
#        vanhempi_entity = google.cloud.datastore.Entity(key=vanhempikey)
#        vanhempi_entity.update( { "kisanimi": x["kisanimi"], "id": x["id"], "alkuaika": x["alkuaika"], "loppuaika": x["loppuaika"] } )
#        client.put_multi( [vanhempi_entity] )
#
#        for y in sarjat:
#            if (x["id"] == y["kilpailu"]):
#                lapsikey = client.key("Sarja", parent=vanhempikey) # datastore keksii itse id:n
#                lapsi_entity = google.cloud.datastore.Entity(key=lapsikey)
#                lapsi_entity.update ({"sarjanimi": y["sarjanimi"], "kilpailu": y["kilpailu"], "kesto": y["kesto"]} )
#                client.put_multi( [lapsi_entity] ) #put_multi-metodilla voidaan tallentaa useampi kerralla. Nopeaa ja säästää kuluissa
#
#    return f"Tallennettiin"

@app.route('/kyselyt', methods=['GET', 'POST'])
def kyselyt():

    try:
        laheta = request.form.get('laheta', "")
    except:
        laheta = ""



    try:
        valitunSarjanNimi = ""
        if (laheta == "Lisää joukkue"):
            valitunSarjanNimi = request.form.get('edellinenSarja', "")
        if (laheta == "Valitse kilpailu"):
            valitunSarjanNimi = ""
        if (laheta == "Valitse sarja"):
            valitunSarjanNimi = request.form.get('sarjat', "")
    except:
        valitunSarjanNimi = ""

    try:
        if (laheta == "Lisää joukkue"):
            valitunKisanId = int(request.form.get('edellinenKisa', "")) 
        else: 
            valitunKisanId = int(request.form.get('kilpailut', ""))           
    except:
        valitunKisanId = None



    try:
        edellinenKisa = int(request.form.get('edellinenKisa', ""))
    except:
        edellinenKisa = None

    try:
        edellinenSarja = request.form.get('edellinenSarja', "")
    except:
        edellinenSarja = ""


    client = google.cloud.datastore.Client()

    query = client.query(kind="Kilpailu")
    results = list( query.fetch() )




    if valitunSarjanNimi != "" and valitunKisanId != edellinenKisa:
        #valitunKisanId = None
        valitunSarjanNimi = ""


    valitunKisanNimi = ""
    try:
        for r in results:
            if r["id"] == valitunKisanId:
                valitunKisanNimi = r["kisanimi"]
    except:
        pass

    kisat = []
    for r in results:
        try:
            kisa = {
                "nimi": r["kisanimi"],
                "id": r["id"]
            }
            kisat.append(kisa)
        except:
            pass

    query = client.query(kind="Sarja")
    query.add_filter("kilpailu", "=", valitunKisanId)
    results = list( query.fetch() )

    sarjat = []
    for r in results:
        try:
            sarja = {
                "nimi": r["sarjanimi"],
                "kilpailu": r["kilpailu"]
            }
            sarjat.append(sarja)
        except:
            pass

    uudetJasenet = []
    tuplanaOlevaNimi = ""
    ekaTyhja = ""

    for i in range(5):
        if request.form.get('jasen'+str(i+1), "") in uudetJasenet:
            tuplanaOlevaNimi = request.form.get('jasen'+str(i+1), "")
        if request.form.get('jasen'+str(i+1), "") != "":
            uudetJasenet.append(request.form.get('jasen'+str(i+1), ""))
        elif ekaTyhja == "":
            ekaTyhja = int(i+1)

    #poista tää lopullisesta!!!!!!!!!!
    


    try:
        uudenJoukkueenNimi = request.form.get('nimi', "")
    except:
        uudenJoukkueenNimi = ""

    testailu = [uudetJasenet, tuplanaOlevaNimi, ekaTyhja, uudenJoukkueenNimi]

    ##if tuplanaOlevaNimi == "" and len(uudetJasenet) > 1 and uudenJoukkueenNimi.strip() != "":
    ##    lapsikey = client.key("Joukkue", "123")
    ##    lapsi_entity = google.cloud.datastore.Entity(key=lapsikey)
    ##    lapsi_entity.update( { "joukkuenimi": uudenJoukkueenNimi, "jäsenet": uudetJasenet } )
    ##    client.put_multi( [lapsi_entity] )

    # tässä testailen vaan ottaa entityn käytettäväks tohon alempaan

    lisaysilmoitus = ""
    if tuplanaOlevaNimi == "" and len(uudetJasenet) > 1 and uudenJoukkueenNimi.strip() != "" and laheta == "Lisää joukkue":

        lisaysilmoitus = "Joukkue lisätty!"

        try:
            query = client.query(kind="Sarja")
            query.add_filter("kilpailu", "=", edellinenKisa)
            query.add_filter("sarjanimi", "=", edellinenSarja)
            vanhempi = list( query.fetch() )
        except:
            vanhempi = "Epäonnistui"

        try:
            vanhempiAvain = vanhempi[0].key
        except:
            vanhempiAvain = "Epäonnistui"

        try:
            for r in vanhempi:
                vanhempiNimi = r["sarjanimi"]
        except:
            vanhempiNimi = "Epäonnistui"

        #Vanhempi: [<Entity('Kilpailu', '10784', 'Sarja', 5679095853613056) {'kilpailu': 1, 'sarjanimi': '4 h', 'kesto': 4}>]

        #lapsikey = client.key("Joukkue", "123")

        try:
            lapsikey = client.key("Joukkue", parent=vanhempiAvain)
            lapsi_entity = google.cloud.datastore.Entity(key=lapsikey)
            lapsi_entity.update( { "joukkuenimi": uudenJoukkueenNimi, "jäsenet": uudetJasenet, "sarja": edellinenSarja,"kilpailu": edellinenKisa } )
            client.put_multi( [lapsi_entity] )
        except:
            lapsikey = "Epäonnistui"

    else:
        lapsikey = "Epäonnistui2"
        vanhempiAvain = "Epäonnistui2"
        vanhempiNimi = "Epäonnistui2"
        vanhempi = "Epäonnistui2"

    def nimiTarkistus():
        message = "Kenttä ei saa olla tyhjä"
        def _length(form, field):
            if len(field.data) < 1 or field.data.strip() == "":
                raise ValidationError(message)
        return _length

    def jasenTarkistus(jasenNro=0):
        def _length(form, field):
            #if len(field.data) < 1:
            #    raise ValidationError("Anna jäsen")
            if tuplanaOlevaNimi != "" and tuplanaOlevaNimi == field.data:
                raise ValidationError("Ei saa olla saman nimisiä jäseniä.")
            if len(uudetJasenet) < 2 and jasenNro == 2:
                raise ValidationError("Anna vähintään kaksi jäsentä")

        return _length

    class Arvosanalaskuri(FlaskForm):
    
        nimi = StringField('Joukkueen nimi: ', [nimiTarkistus()], default="")

        jasen1 = StringField('Jäsen 1: ', [jasenTarkistus(jasenNro=1)], default="")
        jasen2 = StringField('Jäsen 2: ', [jasenTarkistus(jasenNro=2)], default="")
        jasen3 = StringField('Jäsen 3: ', [jasenTarkistus(jasenNro=3)], default="")
        jasen4 = StringField('Jäsen 4: ', [jasenTarkistus(jasenNro=4)], default="")
        jasen5 = StringField('Jäsen 5: ', [jasenTarkistus(jasenNro=5)], default="")

    form = Arvosanalaskuri()
    if request.method == 'POST' and laheta == "Lisää joukkue":
        form.validate()

    errorit = []
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            errorit.append(err)

    try:
        if len(errorit) == 0 or (len(errorit) == 1 and errorit[0] == 'The CSRF token is missing.') and laheta == "Lisää joukkue":
            form.nimi.data = ''
            form.jasen1.data = ''
            form.jasen2.data = ''
            form.jasen3.data = ''
            form.jasen4.data = ''
            form.jasen5.data = ''
    except:
        pass



    return render_template('index.html', errorit=errorit, lisaysilmoitus=lisaysilmoitus, laheta=laheta, edellinenKisa=edellinenKisa, edellinenSarja=edellinenSarja,valitunKisanNimi=valitunKisanNimi, vanhempiAvain=vanhempiAvain, vanhempiNimi=vanhempiNimi, vanhempi=vanhempi,kisat=kisat, sarjat=sarjat, valitunKisanId=valitunKisanId, form=form, testailu=testailu, valitunSarjanNimi=valitunSarjanNimi, lapsikey=lapsikey)


@app.route('/listaus', methods=['GET', 'POST'])
def listaus():

    client = google.cloud.datastore.Client()

    query = client.query(kind="Kilpailu")
    results = list( query.fetch() )

    kisat = []
    for r in results:
        try:
            kisa = {
                "nimi": r["kisanimi"],
                "id": r["id"],
                "alkuaika" : r["alkuaika"],
                "sarjat": []
            }
        except:
            pass

        valitunKisanId = r["id"]

        query = client.query(kind="Sarja")
        query.add_filter("kilpailu", "=", valitunKisanId)
        results2 = list( query.fetch() )

        sarjat = []
        for r in results2:
            try:
                sarja = {
                    "nimi": r["sarjanimi"],
                    "kilpailu": r["kilpailu"],
                    "joukkueet": []
                }

                query = client.query(kind="Joukkue")
                query.add_filter("kilpailu", "=", valitunKisanId)
                query.add_filter("sarja", "=", r["sarjanimi"])
                results3 = list( query.fetch() )


                joukkueet = []

                try:
                    for r in results3:
                        joukkue = {
                            "nimi": r["joukkuenimi"],
                            "jäsenet": r["jäsenet"]
                        }
                        joukkue['jäsenet'].sort(key=str.lower)
                        joukkueet.append(joukkue)
                except:
                    pass

                joukkueet = sorted(joukkueet, key=lambda d: d['nimi'].lower()) 
                sarja['joukkueet'] = joukkueet
                sarjat.append(sarja)
            except:
                pass

        sarjat = sorted(sarjat, key=lambda d: d['nimi'].lower()) 
        kisa["sarjat"] = sarjat
        kisat.append(kisa)
        kisat = sorted(kisat, key=lambda d: d['alkuaika'].lower(), reverse=True) 
    

    return render_template('listaus.html', kisat=kisat, sarjat=sarjat, joukkueet=joukkueet)