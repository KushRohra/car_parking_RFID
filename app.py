from flask import Flask, render_template, request, session, g, redirect, url_for
import mysql.connector
from bubbleSort import *

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="carparking_rfid"
)
mycursor = mydb.cursor()

app = Flask(__name__)
app.secret_key = '1234'

mycursor.execute("SELECT * FROM admintable")
allAdmin = mycursor.fetchall()


@app.before_request
def before_request():
    g.admin = None
    if 'user_id' in session:
        for x in allAdmin:
            if x[0] == session['user_id']:
                g.admin = x


# Index Route
@app.route('/')
def index():
    return render_template("index.html")


# Admin Routes
@app.route('/admin_login', methods=["GET", "POST"])
def admin_login():
    if request.method == 'POST':
        session.pop('admin_id', None)
        shop_id = request.form.get('shop_id')
        shop_email = request.form.get('shop_email')
        shop_password = request.form.get('shop_password')
        query = "SELECT * FROM admintable WHERE shop_id=%s"
        args = (shop_id,)
        mycursor.execute(query, args)
        adminInfo = mycursor.fetchall()
        if len(adminInfo) == 1:
            if adminInfo[0][2] == shop_email and adminInfo[0][3] == shop_password:
                session['admin_id'] = adminInfo[0][0]
                return redirect(url_for('admin_dashboard'))
    return render_template('./admin/admin_login.html')


@app.route('/admin_register', methods=["GET", "POST"])
def admin_register():
    if request.method == 'POST':
        shop_email = request.form.get('shop_email')
        shop_name = request.form.get('shop_name')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')
        wheeler_2 = int(request.form.get('wheeler_2'))
        wheeler_4 = int(request.form.get('wheeler_4'))
        price_2 = int(request.form.get('price_2'))
        price_4 = int(request.form.get('price_4'))
        special_customer = int(request.form.get('special_customer'))
        discount = int(request.form.get('discount'))
        if special_customer == 0:
            discount = 0
        price_2_list = []
        price_4_list = []
        for i in range(price_2):
            hrs = request.form.get('form_2_1_' + str(i + 1))
            price = request.form.get('form_2_2_' + str(i + 1))
            price_2_list.append([hrs, price])
        for i in range(price_4):
            hrs = request.form.get('form_4_1_' + str(i + 1))
            price = request.form.get('form_4_2_' + str(i + 1))
            price_4_list.append([hrs, price])
        bubbleSort(price_2_list)
        bubbleSort(price_4_list)
        query = "INSERT INTO admintable(shop_name, shop_email, shop_password, parking_2, parking_4, pricing_2, pricing_4, special_customers, discount) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        args = (shop_name, shop_email, password, wheeler_2, wheeler_4, price_2, price_4, special_customer, discount,)
        mycursor.execute(query, args)
        mydb.commit()
        mycursor.execute("SELECT shop_id FROM admintable WHERE shop_id=(SELECT MAX(shop_id) FROM admintable)")
        temp_id = mycursor.fetchone()
        id = temp_id[0]

        tableName = str(id) + "_" + "_parking2"
        create_table = "CREATE TABLE " + tableName + "(id INT(11) UNSIGNED AUTO_INCREMENT PRIMARY KEY, lot_no INT(11), parked INT(11), rfid INT(11))"
        mycursor.execute(create_table)
        for i in range(wheeler_2):
            query = "INSERT INTO " + tableName + "(lot_no, parked, rfid) VALUES(%s,%s,%s)"
            args = ((i + 1), 0, 0,)
            mycursor.execute(query, args)
            mydb.commit()

        tableName = str(id) + "_" + "_parking4"
        create_table = "CREATE TABLE " + tableName + "(id INT(11) UNSIGNED AUTO_INCREMENT PRIMARY KEY, lot_no INT(11), parked INT(11), rfid INT(11))"
        mycursor.execute(create_table)
        for i in range(wheeler_4):
            query = "INSERT INTO " + tableName + "(lot_no, parked, rfid) VALUES(%s,%s,%s)"
            args = ((i + 1), 0, 0,)
            mycursor.execute(query, args)
            mydb.commit()

        tableName = str(id) + "_" + "_special"
        create_table = "CREATE TABLE " + tableName + "(id INT(11) UNSIGNED AUTO_INCREMENT PRIMARY KEY, rfid INT(11))"
        mycursor.execute(create_table)

        tableName = str(id) + "_" + "_pricing"
        create_table = "CREATE TABLE " + tableName + "(id INT(11) UNSIGNED AUTO_INCREMENT PRIMARY KEY, hrs INT(11), cost INT(11), flag INT(11))"
        mycursor.execute(create_table)
        for i in range(len(price_2_list)):
            query = "INSERT INTO " + tableName + "(hrs,cost,flag) VALUES(%s,%s,%s)"
            args = (price_2_list[i][0], price_2_list[i][1], 0,)
            mycursor.execute(query, args)
            mydb.commit()
        for i in range(len(price_4_list)):
            query = "INSERT INTO " + tableName + "(hrs,cost,flag) VALUES(%s,%s,%s)"
            args = (price_4_list[i][0], price_4_list[i][1], 1,)
            mycursor.execute(query, args)
            mydb.commit()

        session['admin_id'] = id

        return redirect(url_for('admin_showId'))
    return render_template('./admin/admin_register.html')


@app.route('/admin_showId', methods=['POST', 'GET'])
def admin_showId():
    if request.method == 'POST':
        return redirect(url_for('admin_dashboard'))
    return render_template('./admin/admin_showId.html', id=session['admin_id'])


@app.route('/admin_dashboard')
def admin_dashboard():
    if session['admin_id'] is None:
        return redirect(url_for('admin_login'))
    return render_template('./admin/admin_dashboard.html')


# Special Customers Routes
@app.route('/specialCustomers/addSpecialCustomers', methods=["POST", "GET"])
def addSpecialCustomers():
    if request.method == "POST":
        tableName = str(session['admin_id']) + "__special"
        existingCustomers = []
        mycursor.execute("SELECT rfid FROM " + tableName)
        result = mycursor.fetchall()
        for x in result:
            existingCustomers.append(x[0])
        rfid = int(request.form.get('rfid'))
        # To avoid adding the same entry more than one time
        if rfid not in existingCustomers:
            query = "INSERT INTO " + tableName + "(rfid) VALUES(%s)"
            args = (rfid, )
            mycursor.execute(query, args)
            mydb.commit()
        return redirect(url_for("admin_dashboard"))
    return render_template("./specialCustomers/addSpecialCustomers.html")


@app.route('/specialCustomers/viewSpecialCustomers')
def viewSpecialCustomers():
    tableName = str(session['admin_id']) + "__special"
    mycursor.execute("SELECT rfid FROM " + tableName)
    temp_data = mycursor.fetchall()
    specialCustomers = []
    for x in temp_data:
        specialCustomers.append(x[0])
    return render_template("./specialCustomers/viewSpecialCustomers.html", data=specialCustomers, len=len(specialCustomers))


@app.route('/changePassword')
def changePassword():
    return render_template('./admin/changePassword.html')


# Parking Routes
@app.route('/parking/parkingStatus')
def parkingStatus():
    # 2 wheeler parking details
    tableName = str(session['admin_id']) + "__parking2"
    query = "SELECT * FROM " + tableName
    mycursor.execute(query)
    allSpaces2 = len(mycursor.fetchall())
    query += " WHERE parked=0"
    mycursor.execute(query)
    freeSpaces2 = len(mycursor.fetchall())

    # 4 wheeler parking details
    tableName = str(session['admin_id']) + "__parking4"
    query = "SELECT * FROM " + tableName
    mycursor.execute(query)
    allSpaces4 = len(mycursor.fetchall())
    query += " WHERE parked=0"
    mycursor.execute(query)
    freeSpaces4 = len(mycursor.fetchall())

    return render_template("./parking/parkingStatus.html", free2=freeSpaces2, all2=allSpaces2, free4=freeSpaces4, all4=allSpaces4)


@app.route('/parking/parkingStatus2')
def parkingStatus2():
    tableName = str(session['admin_id']) + "__parking2"
    mycursor.execute("SELECT * FROM " + tableName)
    parking2 = mycursor.fetchall()
    return render_template('./parking/parkingStatus2.html', data=parking2, len=len(parking2))


@app.route('/parking/parkingStatus4')
def parkingStatus4():
    tableName = str(session['admin_id']) + "__parking4"
    mycursor.execute("SELECT * FROM " + tableName)
    parking4 = mycursor.fetchall()
    return render_template('./parking/parkingStatus4.html', data=parking4, len=len(parking4))


@app.route('/parking/addParking', methods=["POST","GET"])
def addParking():
    mycursor.execute("SELECT parking_2, parking_4 FROM admintable WHERE shop_id=" + str(session['admin_id']))
    current2, current4 = mycursor.fetchone()
    if request.method == "POST":
        type = request.form.get("parkingType")
        newSlots = int(request.form.get("parkingSlots"))
        if type == "2":
            totalSlots = newSlots + current2
            parkingTableName = "parking_2"
            tableName = str(session['admin_id']) + "__parking2"
            lastSlot = current2
        elif type == "4":
            totalSlots = newSlots + current4
            parkingTableName = "parking_4"
            tableName = str(session['admin_id']) + "__parking4"
            lastSlot = current4
        mycursor.execute("UPDATE admintable SET " + parkingTableName + "=" + str(totalSlots) + " WHERE shop_id=" + str(session['admin_id']))
        mydb.commit()
        query = "INSERT INTO " + tableName + "(lot_no, parked, rfid) VALUES(%s,%s,%s)"
        for i in range(newSlots):
            args = ((i + 1 + lastSlot), 0, 0,)
            mycursor.execute(query, args)
            mydb.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('./parking/addParking.html', current2=current2, current4=current4)


# Pricing Routes
@app.route('/pricing/viewPricing', methods=["GET", "POST"])
def viewPricing():
    pricingDetails = []
    value = " "
    if request.method == 'POST':
        value = request.form.get('type')
        tableName = str(session['admin_id']) + "_" + "_pricing"
        query = " "
        if value == "2":
            query = "SELECT * FROM " + tableName + " WHERE flag=0"
        elif value == "4":
            query = "SELECT * FROM " + tableName + " WHERE flag=1"
        if query != " ":
            mycursor.execute(query)
            pricingDetails = mycursor.fetchall()
    return render_template("./pricing/viewPricing.html", data=pricingDetails, type=value, len=len(pricingDetails))


@app.route('/pricing/changePricing2', methods=["POST", "GET"])
def changePricing2():
    if request.method == "POST":
        noOf2Slots = int(request.form.get("price_2"))
        price2_list = []
        for i in range(noOf2Slots):
            hrs = request.form.get('form_2_1_' + str(i + 1))
            price = request.form.get('form_2_2_' + str(i + 1))
            price2_list.append([hrs, price])
        bubbleSort(price2_list)
        tableName = str(session['admin_id']) + "__pricing"
        mycursor.execute("DELETE FROM " + tableName + " WHERE flag=0")
        mydb.commit()
        query = "INSERT INTO " + tableName + "(hrs,cost,flag) VALUES(%s,%s,%s)"
        for i in range(len(price2_list)):
            args = (price2_list[i][0], price2_list[i][1], 0,)
            mycursor.execute(query, args)
            mydb.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('./pricing/changePricing2.html')


@app.route('/pricing/changePricing4', methods=["POST", "GET"])
def changePricing4():
    if request.method == "POST":
        noOf4Slots = int(request.form.get("price_4"))
        price4_list = []
        for i in range(noOf4Slots):
            hrs = request.form.get('form_4_1_' + str(i + 1))
            price = request.form.get('form_4_2_' + str(i + 1))
            price4_list.append([hrs, price])
        bubbleSort(price4_list)
        tableName = str(session['admin_id']) + "__pricing"
        mycursor.execute("DELETE FROM " + tableName + " WHERE flag=1")
        mydb.commit()
        query = "INSERT INTO " + tableName + "(hrs,cost,flag) VALUES(%s,%s,%s)"
        for i in range(len(price4_list)):
            args = (price4_list[i][0], price4_list[i][1], 1,)
            mycursor.execute(query, args)
            mydb.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('./pricing/changePricing4.html')


# Discount Routes
@app.route('/discount/changeDiscount', methods=["POST", "GET"])
def changeDiscount():
    mycursor.execute("SELECT discount, special_customers FROM admintable WHERE shop_id=" + str(session['admin_id']))
    currentDiscount, specialCustomers = mycursor.fetchone()
    message = "If you don't have special customers there is no need to fill the form"
    if request.method == "POST":
        discountRate = request.form.get("discountRate")
        if specialCustomers == 0:
            discountRate = 0
        mycursor.execute("UPDATE admintable SET discount="+discountRate+" WHERE shop_id="+str(session['admin_id']))
        mydb.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('./discount/changeDiscount.html', message=message, discount=currentDiscount)


# User Routes
@app.route('/user_login', methods=["GET", "POST"])
def user_login():
    return render_template('./user/user_login.html')


# Logout Routes
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


app.run(debug=True, port=5000)
