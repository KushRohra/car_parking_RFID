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


@app.route('/')
def index():
    return render_template("index.html")


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

        tableName = str(id) + "_" + shop_name + "_parking2"
        create_table = "CREATE TABLE " + tableName + "(id INT(11) UNSIGNED AUTO_INCREMENT PRIMARY KEY, lot_no INT(11), parked INT(11))"
        mycursor.execute(create_table)
        for i in range(wheeler_2):
            query = "INSERT INTO " + tableName + "(lot_no, parked) VALUES(%s,%s)"
            args = ((i + 1), 0,)
            mycursor.execute(query, args)
            mydb.commit()

        tableName = str(id) + "_" + shop_name + "_parking4"
        create_table = "CREATE TABLE " + tableName + "(id INT(11) UNSIGNED AUTO_INCREMENT PRIMARY KEY, lot_no INT(11), parked INT(11))"
        mycursor.execute(create_table)
        for i in range(wheeler_4):
            query = "INSERT INTO " + tableName + "(lot_no, parked) VALUES(%s,%s)"
            args = ((i + 1), 0,)
            mycursor.execute(query, args)
            mydb.commit()

        tableName = str(id) + "_" + shop_name + "_special"
        create_table = "CREATE TABLE " + tableName + "(id INT(11) UNSIGNED AUTO_INCREMENT PRIMARY KEY, rfid INT(11))"
        mycursor.execute(create_table)

        tableName = str(id) + "_" + shop_name + "_pricing"
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
    if session['admin_id'] == None:
        return redirect(url_for('admin_login'))
    return render_template('./admin/admin_dashboard.html')


@app.route('/user_login', methods=["GET", "POST"])
def user_login():
    return render_template('./user/user_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

app.run(debug=True, port=5000)
