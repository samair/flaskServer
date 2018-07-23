from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base,Vendor,Items,User

from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

engine = create_engine("sqlite:///geekshack.db")
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)


@app.route("/login",  methods=['GET','POST'])
def login():
    if request.method == "POST":
        dbSession = DBSession()
        emailid = request.form['emailid']
        password = request.form['pwd']
        error = False
        if dbSession.query(User).filter_by(email_id = emailid).first() is None:
            error=True
        else:
            user=dbSession.query(User).filter_by(email_id = emailid).first()
            if user.verify_password(password) is True:
                session['username'] = emailid
                session['logged_in'] = True
                return redirect(url_for('account',email_id=emailid))
        if error is True:
            abort(400)
    else:
        return render_template("login.html")

@app.route("/logout",  methods=['GET','POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('vendorList'))

@app.route("/account/<string:email_id>",  methods=['GET','POST'])
def account(email_id):
    #   session['logged_in'] = False
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
    if request.method == "POST":
        session = DBSession()
        emailid = request.form['emailid']
        password = request.form['pwd']
        name = request.form['Name']
        if emailid is None or password is None or name is None:
            abort(400) # missing arguments
        if session.query(User).filter_by(email_id = emailid).first() is not None:
            abort(400) # existing user
        user = User(email_id = emailid, Name=name)
        user.hash_password(password)
        session.add(user)
        session.commit()
        user = session.query(User).filter_by(email_id = emailid).one()
        print("user id {}".format(user.id))
        vendor_name = Vendor(name=name,user_id=user.id)
        session.add(vendor_name)
        session.commit()
        print("Added new vendor")

        return  redirect(url_for('vendorList'))
    else:
        print("HIT GET")
        return render_template("register.html")

@app.route("/")
def index():
    dbSession = DBSession()
    vendors = dbSession.query(Vendor).order_by(Vendor.id.desc()).limit(4)
    return render_template("index.html",vendors=vendors)

@app.route("/vendor/")
def vendorList():
    session = DBSession()
    vendors = session.query(Vendor).all()
    return render_template("vendorList.html",vendors=vendors)

@app.route("/vendor/<int:vendor_id>")
def vendor(vendor_id):
    session = DBSession()
    vendor = session.query(Vendor).filter_by(id=vendor_id).one()
    items = session.query(Items).filter_by(vendor_id=vendor_id).all()
    return render_template("vendor.html", items=items, vendrName=vendor.name)

@app.route("/item/new/<string:vendor_name>" , methods=['GET','POST'])
def addItem(vendor_name):
    if request.method == "POST":
        session = DBSession()
        # get vendor id from vendor Name
        vendor=session.query(Vendor).filter_by(name=vendor_name).one()
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
        session.add(item)
        session.commit()
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
                return "Not authorised to edit this item"

        except:
            return "Not authorised to edit this item"


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
            if session['logged_in']==True and session['username'] == user.email_id:
                Item = dbSession.query(Items).filter_by(id=item_id).one()
                return render_template("deleteItem.html",item_id=item_id,item_name=Item.name)
            else:
                return "Not authorised to delete this item"
        except:
            return "Not authorised to delete this item"

if __name__ == "__main__":
    app.debug = True
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host = '0.0.0.0', port=5000)
