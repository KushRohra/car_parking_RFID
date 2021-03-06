import mysql.connector
from flask import Flask, render_template, request, session, g, redirect, url_for
from pymongo import MongoClient
from bubbleSort import *
from flask_pymongo import PyMongo
from datetime import datetime
from takeImage import *

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="carparking_rfid"
)
mycursor = mydb.cursor()

app = Flask(__name__)
app.secret_key = '1234'

cluster = MongoClient(
    "mongodb+srv://KushRohra:kush5255@carparkingrfid.tufes.mongodb.net/car_parking_rfid>?retryWrites=true&w=majority")
db = cluster["car_parking_rfid"]
users = db["users"]

app.config[
    "MONGO_URI"] = "mongodb+srv://KushRohra:kush5255@carparkingrfid.tufes.mongodb.net/car_parking_rfid>?retryWrites=true&w=majority"
mongo = PyMongo(app)

mycursor.execute("SELECT * FROM admintable")
allAdmin = mycursor.fetchall()


@app.before_request
def before_request():
    g.admin = None
    if 'admin_id' in session:
        for x in allAdmin:
            if x[0] == session['admin_id']:
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

        collectionName = str(id) + "_parkingDetails"
        db.create_collection(collectionName)

        collectionName = str(id) + "_passbook"
        db.create_collection(collectionName)

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
    mycursor.execute("SELECT special_customers FROM admintable WHERE shop_id=" + str(session['admin_id']))
    specialCustomerExist = int(mycursor.fetchone()[0])
    return render_template('./admin/admin_dashboard.html', specialCustomerExist=specialCustomerExist)

# Admin Passbook Routes
@app.route('/passbook/seeAdminPassbook')
def seeAdminPassbook():
    id = str(session['admin_id'])
    collectionName = id + "_passbook"
    passbook = db[collectionName]
    passbookDetails = list(passbook.find({}))
    return render_template('./passbook/seeAdminPassbook.html', details=passbookDetails, length=len(passbookDetails))


# Special Customers Routes
@app.route('/specialCustomers/addSpecialCustomers', methods=["POST", "GET"])
def addSpecialCustomers():
    message = ""
    if request.method == "POST":
        tableName = str(session['admin_id']) + "__special"
        existingCustomers = []
        mycursor.execute("SELECT rfid FROM " + tableName)
        result = mycursor.fetchall()
        for x in result:
            existingCustomers.append(x[0])
        rfid = int(request.form.get('rfid'))
        # Check if the rfid of someone entered is actuall valid or not, i.e, it has a entry in user database
        if len(list(users.find({'_id': rfid}))) == 0:
            message = "No such user exists with an RFID of " + str(rfid) + ". Confirm the RFID from your Customer"
            return render_template("./specialCustomers/addSpecialCustomers.html", message=message)
        # To avoid adding the same entry more than one time
        if rfid not in existingCustomers:
            query = "INSERT INTO " + tableName + "(rfid) VALUES(%s)"
            args = (rfid,)
            mycursor.execute(query, args)
            mydb.commit()
        return redirect(url_for("admin_dashboard"))
    return render_template("./specialCustomers/addSpecialCustomers.html", message=message)


@app.route('/specialCustomers/viewSpecialCustomers')
def viewSpecialCustomers():
    tableName = str(session['admin_id']) + "__special"
    mycursor.execute("SELECT rfid FROM " + tableName)
    temp_data = mycursor.fetchall()
    specialCustomers = []
    userNames = []
    for x in temp_data:
        specialCustomers.append(x[0])
        userNames.append(users.find({"_id": x[0]})[0]['user_name'])
    return render_template("./specialCustomers/viewSpecialCustomers.html", data=specialCustomers, userNames=userNames,
                           len=len(specialCustomers))


@app.route('/specialCustomers//deleteSpecialCustomers/<int:rfid>')
def deleteSpecialCustomers(rfid):
    tableName = str(session['admin_id']) + "__special"
    query = "DELETE FROM " + tableName + " WHERE rfid=%s"
    args = (rfid,)
    mycursor.execute(query, args)
    mydb.commit()
    return redirect(url_for("admin_dashboard"))


# Change Password Admin Route
@app.route('/changePassword', methods=["POST", "GET"])
def changeAdminPassword():
    if request.method == "POST":
        password = request.form.get("password")
        repeatPassword = request.form.get("repeat_password")
        if password != repeatPassword:
            return render_template('./admin/changePassword.html')
        else:
            query = "UPDATE admintable SET shop_password=%s" + " WHERE shop_id=" + str(session['admin_id'])
            args = (password,)
            mycursor.execute(query, args)
            mydb.commit()
            return redirect(url_for('admin_dashboard'))
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

    return render_template("./parking/parkingStatus.html", free2=freeSpaces2, all2=allSpaces2, free4=freeSpaces4,
                           all4=allSpaces4)


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


@app.route('/parking/addParking', methods=["POST", "GET"])
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
        mycursor.execute("UPDATE admintable SET " + parkingTableName + "=" + str(totalSlots) + " WHERE shop_id=" + str(
            session['admin_id']))
        mydb.commit()
        query = "INSERT INTO " + tableName + "(lot_no, parked, rfid) VALUES(%s,%s,%s)"
        for i in range(newSlots):
            args = ((i + 1 + lastSlot), 0, 0,)
            mycursor.execute(query, args)
            mydb.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('./parking/addParking.html', current2=current2, current4=current4)


@app.route('/parking/adminParkingDetails')
def adminParkingDetails():
    totalMoneyEarned = 0
    id = str(session['admin_id'])
    collectionName = id + "_parkingDetails"
    parking = db[collectionName]
    parkingDetails = list(parking.find({}))
    for details in parkingDetails:
        print(details)
        try:
            totalMoneyEarned += details['cost']
        except:
            totalMoneyEarned += 0
    return render_template('./parking/parkingDetails.html', parkingDetails=parkingDetails, len=len(parkingDetails),
                           totalMoneyEarned=totalMoneyEarned)


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
        mycursor.execute(
            "UPDATE admintable SET discount=" + discountRate + " WHERE shop_id=" + str(session['admin_id']))
        mydb.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('./discount/changeDiscount.html', message=message, discount=currentDiscount)


# Delete Admin Account
@app.route('/deleteAdminAccount')
def deleteAdminAccount():
    id = str(session['admin_id'])
    mycursor.execute("DROP TABLE " + id + "__parking2")
    mycursor.execute("DROP TABLE " + id + "__parking4")
    mycursor.execute("DROP TABLE " + id + "__pricing")
    mycursor.execute("DROP TABLE " + id + "__special")
    mycursor.execute("DELETE FROM admintable WHERE shop_id=" + id)
    collectionName = id + "_parkingDetails"
    db[collectionName].drop()
    collectionName = id + "_passbook"
    db[collectionName].drop()
    mydb.commit()
    return redirect('/')


@app.route('/entry/vehicleEntry', methods=["POST", "GET"])
def vehicleEntry():
    if request.method == "POST":
        id = str(session['admin_id'])
        mycursor.execute("SELECT shop_name FROM admintable WHERE shop_id=" + id)
        parkingName = mycursor.fetchone()[0]

        # getting all form details
        vehicleType = int(request.form.get("vehicleType"))
        rfid = int(request.form.get("rfid"))
        entryTime = datetime.now()
        if vehicleType == 2:
            tableName = id + "__parking2"
        else:
            tableName = id + "__parking4"
        mycursor.execute("SELECT lot_no, parked FROM " + tableName)
        results = mycursor.fetchall()
        lotNo = -1

        # checking if it is a special customer
        specialCustomersTableName = id + "__special"
        mycursor.execute("SELECT rfid FROM " + specialCustomersTableName)
        data = mycursor.fetchall()
        specialCustomersList = []
        for customer in data:
            specialCustomersList.append(customer[0])
        isSpecialCustomer = 0
        discount = 0

        # assigning parking lot based on the outcome of previous step
        if rfid not in specialCustomersList:
            for x in results:
                if x[1] == 0:
                    lotNo = x[0]
                    break
        else:
            isSpecialCustomer = 1
            mycursor.execute("SELECT discount from admintable WHERE shop_id=" + id)
            discount = mycursor.fetchone()[0]
            for x in reversed(results):
                if x[1] == 0:
                    lotNo = x[0]
                    break

        # Checking if balance of user is positive or restrict him from entering the parking lot
        balance = users.find({"_id": rfid})[0]['balance']

        # checking if space is available or not and showing messages
        if lotNo == -1:
            return render_template('vehicleEntry/vehicleEntry.html',
                                   message="Parking Lot Full for " + str(vehicleType) + " Wheeler Vehicles",
                                   color="red")
        elif balance < 0:
            return render_template('vehicleEntry/vehicleEntry.html',
                                   message="Your balance is less than 0. Recharge your balance to enter the parking lot",
                                   color="red")
        else:
            # Take image of the driver
            takeImage()
            imageName = id + " " + str(entryTime)
            image = open("image.jpg", "rb")
            mongo.save_file(imageName, image)

            # Parking Lot Collection Update
            # SQL TABLE UPDATE
            query = "UPDATE " + tableName + " SET parked=%s, rfid=%s WHERE lot_no=%s"
            args = (1, rfid, lotNo,)
            mycursor.execute(query, args)
            mydb.commit()

            # NoSQL TABLE UPDATE
            collectionName = id + "_parkingDetails"
            parking = db[collectionName]
            details = {"vehicleType": vehicleType, "rfid": rfid, "entryTime": entryTime, "slot": lotNo,
                       "specialCustomer": isSpecialCustomer, "discount": discount, "image": imageName}
            parking.insert_one(details)

            # Getting last entry in mongoDB releated to the particular user
            refer_id = parking.find({"rfid": rfid}).sort([("_id", -1)]).limit(1)[0]['_id']

            # User Parking details Update
            userDetails = users.find({"_id": rfid})[0]
            userParkingDetails = userDetails['parkingDetails']
            details = {"parkingName": parkingName, "slot": lotNo, "entryTime": entryTime, "vehicleType": vehicleType,
                       "referId": refer_id, "image": imageName}
            userParkingDetails.append(details)
            users.find_one_and_update({'_id': rfid}, {'$set': {'parkingDetails': userParkingDetails}})

            return render_template('vehicleEntry/vehicleEntry.html',
                                   message="Parking Slot Allotted = " + str(lotNo) + " for vehicle with RFID = " + str(
                                       rfid), color="green")

    return render_template('vehicleEntry/vehicleEntry.html', message="", color="green")


@app.route('/exit/vehicleExit', methods=["POST", "GET"])
def vehicleExit():
    if request.method == "POST":
        id = str(session['admin_id'])
        mycursor.execute("SELECT shop_name FROM admintable WHERE shop_id=" + id)
        parkingLotName = mycursor.fetchone()[0]
        print(parkingLotName)
        collectionName = id + "_parkingDetails"
        parking = db[collectionName]

        exitTime = datetime.now()

        # Getting all the details from form
        vehicleType = int(request.form.get("vehicleType"))
        rfid = int(request.form.get("rfid"))

        # Calculating Time Diff between entry Time and exit Time
        userDetails = users.find({"_id": rfid})[0]
        userParkingDetails = userDetails['parkingDetails']
        lastEntry = len(userParkingDetails) - 1
        referId = userParkingDetails[lastEntry]['referId']
        details = parking.find({"_id": referId})[0]

        entryTime = details['entryTime']
        timeDiff = (exitTime - entryTime).total_seconds()

        # Getting Cost Details
        costTableName = id + "__pricing"
        if vehicleType == 2:
            mycursor.execute("SELECT hrs, cost FROM " + costTableName + " WHERE flag=0")
        else:
            mycursor.execute("SELECT hrs, cost FROM " + costTableName + " WHERE flag=1")
        costDetails = mycursor.fetchall()

        # Calculating Price User has to pay
        price = -1
        for x in costDetails:
            seconds = x[0] * 60 * 60
            if timeDiff < seconds:
                price = x[1]
                break
        if price == -1:
            price = costDetails[len(costDetails) - 1][1]
        isSpecialCustomer = details['specialCustomer']
        discountPercentage = details['discount']
        price -= float((discountPercentage * price) / 100)

        # Changing Parking Lot Status
        lotNo = details['slot']
        if vehicleType == 2:
            parkingTableName = id + "__parking2"
        else:
            parkingTableName = id + "__parking4"
        mycursor.execute("UPDATE " + parkingTableName + " SET parked=0, rfid=0 WHERE lot_no=" + str(lotNo))
        mydb.commit()

        # Deducting Cost from user's card
        newBalance = userDetails['balance'] - price
        users.find_one_and_update({"_id": rfid}, {'$set': {'balance': newBalance}})

        # Adding some more details to users Parking Details
        userParkingDetails[lastEntry]["cost"] = price
        userParkingDetails[lastEntry]["exitTime"] = exitTime
        users.find_one_and_update({"_id": rfid}, {'$set': {'parkingDetails': userParkingDetails}})

        # Adding more details to parkingDetails of the Parking Lot
        parking.find_one_and_update({"_id": referId}, {'$set': {
            '_id': referId,
            'vehicleType': vehicleType,
            'rfid': rfid,
            'entryTime': entryTime,
            'slot': lotNo,
            'specialCustomer': isSpecialCustomer,
            'discount': discountPercentage,
            'cost': price,
            'exitTime': exitTime
        }})

        # User passbook update
        currentPassbook = userDetails['passbook']
        newEntry = {
            'amount': price,
            'desc': 'Money paid to Parking Lot ' + parkingLotName,
            'balance': newBalance,
            'time': exitTime
        }
        currentPassbook.append(newEntry)
        users.find_one_and_update({"_id": rfid}, {'$set': {'passbook': currentPassbook}})

        # Admin passbook update
        userName = userDetails['user_name']
        collectionName = id + "_passbook"
        passbook = db[collectionName]
        passbookEntry = {
            'rfid': rfid,
            'amount': price,
            'desc': 'Money paid for parking by ' + userName,
            'time': exitTime
        }
        passbook.insert_one(passbookEntry)

        return render_template('vehicleExit/vehicleExit.html', message="Your total price is Rs. " + str(
            price) + " and is deducted from your card balance", color="green")

    return render_template('vehicleExit/vehicleExit.html', message="", color="green")


# User Routes
@app.route('/user_register', methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        mycursor.execute("SELECT count FROM usercount WHERE id=1")
        current_id = mycursor.fetchone()[0]
        query = "UPDATE usercount SET count=%s WHERE id=%s"
        args = (current_id + 1, 1,)
        mycursor.execute(query, args)
        mydb.commit()

        user_name = request.form.get("user_name")
        user_email = request.form.get("user_email")
        password = request.form.get("password")
        customerType = request.form.get("customerType")
        if customerType == "1":
            balance = 500
        else:
            balance = 100
        user_image = request.files.get("user_image", 'rb')
        imageName = request.form.get("imageName")
        mongo.save_file(imageName, user_image)
        userImages = [imageName]
        parkingDetails = []
        passbook = []
        users.insert_one({"_id": current_id, "user_name": user_name, "user_email": user_email, "password": password,
                          "customerType": customerType, "balance": balance, "user_images": userImages,
                          "parkingDetails": parkingDetails, "passbook": passbook})

        session['user_id'] = current_id
        return redirect(url_for('user_showId'))
    return render_template("./user/user_register.html")


@app.route("/user_showId", methods=["POST", "GET"])
def user_showId():
    if request.method == "POST":
        return redirect(url_for('user_dashboard'))
    return render_template('/user/user_showId.html', id=session['user_id'])


@app.route('/user_dashboard')
def user_dashboard():
    user = users.find({"_id": session['user_id']})[0]
    parkingDetails = user['parkingDetails']
    flag = 0
    slot = 0
    length = len(parkingDetails)
    if length != 0 and 'exitTime' not in parkingDetails[length - 1]:
        flag = 1
        slot = parkingDetails[length - 1]['slot']
    return render_template('./user/user_dashboard.html', flag=flag, slot=slot)


@app.route('/user_login', methods=["GET", "POST"])
def user_login():
    message = ""
    if request.method == "POST":
        id = int(request.form.get("id"))
        password = request.form.get("password")
        userDetails = users.find({"_id": id})
        copy = userDetails
        if len(list(copy)) == 0:
            message = "Enter Correct ID Number"
        else:
            userDetails = users.find({"_id": id})[0]
            if password != userDetails['password']:
                message = "Enter Correct Password"
            elif password == userDetails['password']:
                session['user_id'] = id
                return redirect(url_for('user_dashboard'))
    return render_template('./user/user_login.html', message=message)


@app.route('/user/changePassword', methods=["POST", "GET"])
def changeUserPassword():
    if request.method == "POST":
        newPassword = request.form.get("password")
        users.find_one_and_update({'_id': session['user_id']}, {'$set': {'password': newPassword}})
        return redirect(url_for('user_dashboard'))
    return render_template('./user/changePassword.html')


# User Image Related Routes
@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


@app.route('/delete_file/<int:index>')
def deleteImage(index):
    userDetails = users.find({"_id": session['user_id']})[0]
    userImages = userDetails['user_images']
    del userImages[index]
    users.find_one_and_update({'_id': session['user_id']}, {'$set': {'user_images': userImages}})
    return redirect(url_for('user_dashboard'))


@app.route('/user/seeImages')
def seeImages():
    userDetails = users.find({"_id": session['user_id']})[0]
    return render_template('./user/userImages/seeImages.html', images=userDetails['user_images'],
                           len=len(userDetails['user_images']))


@app.route('/user/addImages', methods=["POST", "GET"])
def addImages():
    userDetails = users.find({"_id": session['user_id']})[0]
    userImages = userDetails['user_images']
    if request.method == "POST":
        user_image = request.files.get("user_image", 'rb')
        imageName = request.form.get("imageName")
        mongo.save_file(imageName, user_image)
        userImages = userDetails['user_images']
        userImages.append(imageName)
        users.find_one_and_update({'_id': session['user_id']}, {'$set': {'user_images': userImages}})
        return redirect(url_for('user_dashboard'))
    return render_template('./user/userImages/addImages.html', userImages=userImages)


# See All Parking Details of user
@app.route('/parking/userParkingDetails')
def seeParkingUser():
    user = users.find({"_id": session['user_id']})[0]
    parkingDetails = user['parkingDetails']
    totalMoneySpent = 0
    for details in parkingDetails:
        try:
            totalMoneySpent += details['cost']
        except:
            totalMoneySpent += 0
    flag = 0
    length = len(parkingDetails)
    if length !=0 and 'exitTime' not in parkingDetails[length - 1]:
        flag = 1
    return render_template('./user/parking/parkingDetails.html', parkingDetails=parkingDetails, len=len(parkingDetails),
                           totalMoneySpent=totalMoneySpent)


# User Passbook Route
@app.route('/user/seeUserPassbook')
def seeUserPassbook():
    userDetails = users.find({"_id": session['user_id']})[0]
    passbook = userDetails['passbook']
    return render_template('./user/passbook/seeUserPassbook.html', passbook=passbook, length=len(passbook))


# User Balance Routes
@app.route('/user/addBalance', methods=["POST", "GET"])
def addBalance():
    userDetails = users.find({"_id": session['user_id']})[0]
    balance = userDetails['balance']
    if request.method == "POST":
        balanceToBeAdded = int(request.form.get("addBalance"))
        newBalance = balanceToBeAdded + balance
        currentPassbook = userDetails['passbook']
        newEntry = {
            'amount': balanceToBeAdded,
            'desc': 'Money Added to Account',
            'balance': newBalance,
            'time': datetime.now()
        }
        currentPassbook.append(newEntry)

        # Updating Balance
        users.find_one_and_update({'_id': session['user_id']}, {'$set': {'balance': newBalance}})

        # Updating Passbook
        users.find_one_and_update({'_id': session['user_id']}, {'$set': {'passbook': currentPassbook}})
        return redirect(url_for('user_dashboard'))
    return render_template('./user/userBalance/addBalance.html', balance=balance)


@app.route('/user/transferBalance', methods=["POST", "GET"])
def transferBalance():
    userDetails = users.find({"_id": session['user_id']})[0]
    balance = userDetails['balance']
    userName = userDetails['user_name']
    if request.method == "POST":
        rfid = int(request.form.get("rfid"))
        user = users.find({"_id": rfid})
        money = float(request.form.get("transferBalance"))
        if rfid == session['user_id']:
            return render_template('./user/userBalance/transferBalance.html', balance=balance,
                                   message="You cannot transfer money to your own account", color="red")
        elif len(list(user)) == 0:
            return render_template('./user/userBalance/transferBalance.html', balance=balance,
                                   message="No such user exists, check the rfid again", color="red")
        elif money > balance:
            return render_template('./user/userBalance/transferBalance.html', balance=balance,
                                   message="The amount entered exceeds balance in your account", color="red")
        else:
            otherUser = users.find({"_id": rfid})[0]
            otherUserName = otherUser['user_name']
            otherUserBalance = otherUser['balance']
            otherUserPassbook = otherUser['passbook']
            newEntry = {
                'amount': money,
                'desc': 'Money Received from ' + userName,
                'balance': otherUserBalance + money,
                'time': datetime.now()
            }
            users.find_one_and_update({"_id": rfid}, {'$set': {'balance': otherUserBalance + money}})
            otherUserPassbook.append(newEntry)
            users.find_one_and_update({"_id": rfid}, {'$set': {'passbook': otherUserPassbook}})


            passbook = userDetails['passbook']
            newEntry = {
                'amount': money,
                'desc': 'Money transferred to ' + otherUserName,
                'balance': balance - money,
                'time': datetime.now()
            }
            passbook.append(newEntry)
            users.find_one_and_update({"_id": session['user_id']}, {'$set': {'balance': balance - money}})
            users.find_one_and_update({"_id": session['user_id']}, {'$set': {'passbook': passbook}})

            return redirect(url_for('user_dashboard'))
    return render_template('./user/userBalance/transferBalance.html', balance=balance, message="", color="")


# Delete User Account Route
@app.route('/deleteUserAccount')
def deleteUserAccount():
    users.delete_one({"_id": session['user_id']})
    return redirect('/')


# Logout Routes
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


app.run(debug=True, port=5000)
