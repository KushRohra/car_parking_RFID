from flask import Flask, render_template, request, session, g, redirect, url_for
import mysql.connector

app = Flask(__name__)

@app.route('/')
def index():
	return "Hello World!!"

app.run(debug=True, port=5000)
