from flask import Flask, render_template, request, session, g, redirect, url_for
import mysql.connector

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/admin_login')
def admin_login():
	return render_template('admin_login.html')

app.run(debug=True, port=5000)
