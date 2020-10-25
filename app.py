from flask import Flask, render_template, request, session, g, redirect, url_for
import mysql.connector

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/admin_login', methods=["GET", "POST"])
def admin_login():
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
		special_customer = request.form.get('special_customer')
		discount = int(request.form.get('discount'))
		if special_customer == '0':
    			discount = 0 
		price_2_list = []
		price_4_list = []
		for i in range(price_2):
				hrs = request.form.get('form_2_1_'+str(i+1))
				price = request.form.get('form_2_2_'+str(i+1))
				print(hrs, price)
				price_2_list.append([hrs, price])
		for i in range(price_4):
				hrs = request.form.get('form_4_1_'+str(i+1))
				price = request.form.get('form_4_2_'+str(i+1))
				print(hrs, price)
				price_4_list.append([hrs, price])
		print(price_2_list)
		print(price_4_list)
		print(shop_email, shop_name, password, repeat_password, wheeler_2, wheeler_4, price_2, price_4, special_customer, discount)
	return render_template('./admin/admin_register.html')

@app.route('/user_login', methods=["GET", "POST"])
def user_login():
	return render_template('./user/user_login.html')

app.run(debug=True, port=5000)
