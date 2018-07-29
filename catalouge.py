from flask import Flask, render_template, flash, request, redirect, url_for, session, abort, g,jsonify
app = Flask(__name__)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,Vendor,Items,User
import random
import string
import codecs



from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

engine = create_engine("sqlite:///geekshack.db")
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Geek Shack"


@auth.verify_password
def verify_password(email_id, password):
    ''' Checks if the username and password are proper or not
        Used for API Access.
    '''
    dbSession = DBSession()
    user = dbSession.query(User).filter_by(email_id = email_id).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

@app.route('/gconnect', methods=['POST'])

def gconnect():
    ''' Method called by GOOGLE API to validate and store information
        about the users
    '''
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    #h = httplib2.Http()
    #result = json.loads((h.request(url, 'GET')[1]).decode('utf8'))
    result= requests.get(url).json()
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        print(session['email'])
        print(session['access_token'])
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['name'] = data['name']
    session['picture'] = data['picture']
    session['username'] = data['email']
    session['logged_in'] = True

    return session['username']

@app.route("/login",  methods=['GET','POST'])
def login():
    '''
    Routine to handle login requests
    For GET renders a form
    for POST queries data base to validate the information.

   '''
    if request.method == "POST":
        dbSession = DBSession()
        emailid = request.form['emailid']
        password = request.form['pwd']
        error = False

        if dbSession.query(User).filter_by(email_id = emailid).first() is None:
            abort(400)
        else:
            user=dbSession.query(User).filter_by(email_id = emailid).first()
            if user.verify_password(password) is True:
                session['username'] = emailid
                session['logged_in'] = True
                return redirect(url_for('account',email_id=emailid))
            else:
                abort(400)
    else:
        print("Request came from {}".format(request.remote_addr))
        return render_template("login.html")

@app.route("/logout",  methods=['GET','POST'])
def logout():
    '''
    Routine to handle logout requests
   '''
    # once the users clicks logout set the session "logged_in" to false.
    session['logged_in'] = False
    if 'picture' in session:
        # picture is only populated for google login , this is used to diver the flow.
        gdisconnect()
        return redirect(url_for('vendorList',message=session['logout_msg']))
    else:
        return redirect(url_for('vendorList',message=" "))

@app.route("/account/<string:email_id>",  methods=['GET','POST'])
def account(email_id):
    '''
    Routine to handle request to get account information

    '''
    dbSession = DBSession()
    user = dbSession.query(User).filter_by(email_id=email_id).one()
    items=""
    vendorName = ""
    try:
        vendor = dbSession.query(Vendor).filter_by(user_id=user.id).one()
        vendorName =vendor.name
        items = dbSession.query(Items).filter_by(vendor_id=vendor.id).all()
    except:
        print("Error no vendor for this id")
    return render_template("account.html",items=items,vendrName=vendorName)

@app.route("/register" , methods=['GET','POST'])
def register():
    '''
    Routine to handle new user registration
    First check if the user is already logged in, then redirect the users
    else display a form.

    '''
    if not isUserLoggedIn():
        if request.method == "POST":
            dbSession = DBSession()
            emailid = request.form['emailid']
            password = request.form['pwd']
            name = request.form['Name']
            if emailid is None or password is None or name is None:
                abort(400) # missing arguments
            if dbSession.query(User).filter_by(email_id = emailid).first() is not None:
                abort(400) # existing user
            user = User(email_id = emailid, Name=name)
            user.hash_password(password)
            dbSession.add(user)
            dbSession.commit()
            user = dbSession.query(User).filter_by(email_id = emailid).one()
            print("user id {}".format(user.id))
            vendor_name = Vendor(name=name,user_id=user.id)
            dbSession.add(vendor_name)
            dbSession.commit()
            print("Added new vendor")

            return  redirect(url_for('vendorList',message=" "))
        else:
            print("HIT GET")
            return render_template("register.html")
    else:
        #flash('You are already a registered user!')
        return render_template("123.html")

@app.route("/registerOauth", methods=['GET','POST'])
def registerOauth():
    '''
    Routine to handle OAuth user registration
    '''
    if request.method == "GET":
        # first check if the user has registered ?
        dbSession = DBSession()
        try:
            user = dbSession.query(User).filter_by(email_id=session["username"]).one()
            return redirect(url_for('account',email_id=session["username"]))
        except NoResultFound:
            # user is not a registered one, ask to register with a vendor name

            return render_template("registerOauth.html")
    else:
        askVendorName()
        return redirect(url_for('account',email_id=session["username"]))

def askVendorName():
    dbSession = DBSession()
    newUser=User()
    newUser.email_id = session["username"]
    newUser.hash_password("nopassword")
    newUser.Name = "googleSignin"
    newVendor=Vendor()
    newVendor.name =  request.form['vendorName']
    newVendor.user = newUser
    dbSession.add(newUser)
    dbSession.add(newVendor)
    dbSession.commit()

@app.route("/")
def index():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    session['state'] = state
    dbSession = DBSession()
    vendors = dbSession.query(Vendor).order_by(Vendor.id.desc()).limit(4)
    return render_template("index.html",vendors=vendors)

@app.route("/vendorList/<string:message>")
def vendorList(message):
    dbSession = DBSession()
    vendors = dbSession.query(Vendor).all()
    return render_template("vendorList.html",vendors=vendors,message=message)

@app.route("/vendor/<int:vendor_id>")
def vendor(vendor_id):
    dbSession = DBSession()
    vendor = dbSession.query(Vendor).filter_by(id=vendor_id).one()
    items = dbSession.query(Items).filter_by(vendor_id=vendor_id).all()
    return render_template("vendor.html", items=items, vendrName=vendor.name)

@app.route("/item/new/<string:vendor_name>" , methods=['GET','POST'])
def addItem(vendor_name):
    if request.method == "POST":
        dbSession = DBSession()
        # get vendor id from vendor Name
        vendor=dbSession.query(Vendor).filter_by(name=vendor_name).one()
        item = ""
        error = False
        if (request.form['name'] !=""):
            item=Items(name=request.form['name'])
        else:
            error=True
            #redirect(url_for("error",))
        if (request.form['price'] !=""):
            item.price = request.form['price']
        if (request.form['stock'] !=""):
            item.stock = request.form['stock']
        if (request.form['desc'] !=""):
            item.description = request.form['desc']
        item.vendor_id =vendor.id
        dbSession.add(item)
        dbSession.commit()
        return redirect(url_for("vendor", vendor_id= vendor.id))
    else:
        dbSession = DBSession()
        return render_template("addItem.html",vendor_name=vendor_name)

@app.route("/vendor/<int:item_id>/edit/" , methods=['GET','POST'])
def editItem(item_id):
    if request.method == "POST":
        dbSession = DBSession()
        item = dbSession.query(Items).filter_by(id=item_id).one()
        #vendor = session.query(Vendor).filter_by(name=vendor_name).one()
        #if request.form.get('name')
        if (request.form['name'] !=""):
            item.name = request.form['name']
        if (request.form['price'] !=""):
            item.price = request.form['price']
        if (request.form['stock'] !=""):
            item.stock = request.form['stock']
        if (request.form['desc'] !=""):
            item.description = request.form['desc']
        dbSession.add(item)
        dbSession.commit()
        return redirect(url_for("vendor", vendor_id= item.vendor_id))
    else:
        dbSession = DBSession()

        try:

            Item = dbSession.query(Items).filter_by(id=item_id).one()
            vendor = dbSession.query(Vendor).filter_by(id=Item.vendor_id).one()
            user = dbSession.query(User).filter_by(id=vendor.user_id).one()
            print("username is {}".format(session['username']))
            if session['logged_in']==True and session['username'] == user.email_id:
                Item = dbSession.query(Items).filter_by(id=item_id).one()
                return render_template("editItem.html",item_id=item_id,item_name=Item.name)
            else:
                abort(403)

        except:
            abort(403)


@app.route("/vendor/<int:item_id>/delete/" , methods=['GET','POST'])
def deleteItem(item_id):
    if request.method == "POST":
        dbSession = DBSession()
        item = dbSession.query(Items).filter_by(id=item_id).one()
        dbSession.delete(item)
        dbSession.commit()
        return redirect(url_for("vendor", vendor_id= item.vendor_id))
    else:
        dbSession = DBSession()
        try:
            Item = dbSession.query(Items).filter_by(id=item_id).one()
            vendor = dbSession.query(Vendor).filter_by(id=Item.vendor_id).one()
            user = dbSession.query(User).filter_by(id=vendor.user_id).one()
            print("username is {}".format(session['username']))
            print("DB User name is {}".format(user.email_id))
            print("Logged in > {}".format(session['logged_in']))
        except:
            abort(403)
        if session['logged_in']==True and session['username'] == user.email_id:
            Item = dbSession.query(Items).filter_by(id=item_id).one()
            print("Item name {}".format(Item.name))
            return render_template("deleteItem.html",item_id=item_id,item_name=Item.name)
        else:
            abort(403)
                #return "Not authorised to delete this item"


@app.errorhandler(400)
def notAuthorized(error):
    return render_template("400.html")

@app.errorhandler(403)
def notAuthorized(error):
    return render_template("403.html")


def isUserLoggedIn():
    if session.get('logged_in'):
        return True
    else:
        return False

@app.route('/gdisconnect')
def gdisconnect():
    access_token = session['access_token']
    print("access token : {}".format(access_token))
    if access_token is None:
        print("Access Token is None")
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        session['logout_msg'] = response
    print("In gdisconnect access token is {}".format(access_token))
    print("User name is: ")
    print(session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del session['access_token']
        del session['gplus_id']
        del session['username']
        del session['picture']
        response = 'Successfully disconnected.'
        session.clear()

        session['logout_msg'] = response
    else:
        response = 'Failed to revoke token for given user.'
        session.clear()
        session['logout_msg'] = response
    #return session['logged_in']

def isOauthLogin():
    #check if picture is present in sessions
    if 'picture' in session:
        return True
    else:
        return False

@app.route('/api/v1.0/vendors.json')
@auth.login_required
def getVendors():
    dbSession = DBSession()
    vendors = dbSession.query(Vendor).all()
    vendorList=[]
    for v in vendors:
        vendorList.append(v.serialize)

    return jsonify(Vendors=vendorList)

@app.route('/api/v1.0/products.json')
@auth.login_required
def getProducts():
    dbSession = DBSession()
    products = dbSession.query(Items).all()
    productList=[]
    for p in products:
        productList.append(p.serialize)

    return jsonify(Products=productList)

if __name__ == "__main__":
    app.debug = True
    app.secret_key = 'H6HGOZ1OMXGG0NVIDZZGR3USJCR7UUQC'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host = '0.0.0.0', port=5000)
