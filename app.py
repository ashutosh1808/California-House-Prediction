from flask import Flask,render_template,url_for,redirect,session,request
from sqlite3 import *
import pickle

app=Flask(__name__)
app.secret_key="kamalsirrocks"

@app.route("/logout",methods=["GET","POST"])
def logout():
	session.clear()
	return redirect(url_for("login"))

@app.route("/",methods=["GET","POST"])
def home():
	if "username" in session:
		return render_template("home.html",name=session["username"])
	else:
		return redirect(url_for("login"))

@app.route("/login",methods=["GET","POST"])
def login():
	if request.method=="POST":
		un=request.form["un"]
		pw=request.form["pw"]
		con=None
		try:
			con=connect("user_auth.db")
			cursor=con.cursor()
			sql="select * from users where username='%s' and password='%s'"
			cursor.execute(sql%(un,pw))
			data=cursor.fetchall()
			if len(data)==0:
				return render_template("login.html",msg="Invalid Login")
			else:
				session["username"]=un
				return redirect(url_for("home"))
		except UnboundLocalError:
			con.rollback()
		except Exception as e:
			return render_template("login.html",msg=e)
		finally:
			if con is not None:
				con.close()
	else:
		return render_template("login.html")

@app.route("/signup",methods=["GET","POST"])
def signup():
	if request.method=="POST":
		un=request.form["un"]
		pw1=request.form["pw1"]
		pw2=request.form["pw2"]
		if pw1==pw2:
			con=None
			try:
				con=connect("user_auth.db")
				cursor=con.cursor()
				sql="insert into users values('%s','%s')"
				cursor.execute(sql%(un,pw1))
				con.commit()
				return redirect(url_for("login"))
			except IntegrityError:
				con.rollback()
				return render_template("login.html",msg="entered username already exists")
			except UnboundLocalError:
				con.rollback()
			except Exception as e:
				con.rollback()
				return render_template("signup.html",msg=e)
			finally:
				if con is not None:
					con.close()
		else:
			return render_template("signup.html",msg="password does not match")
	else:
		return render_template("signup.html")

@app.route("/find",methods=["POST"])
def find():
	if request.form["exp"] and request.form["ts"] and request.form["isc"]:
		exp=float(request.form["exp"])
		ts=float(request.form["ts"])
		isc=float(request.form["isc"])
		if exp<0:	msg="exp should be positive"
		elif ts<0 or ts>10:	msg="test score should be between 0 and 10 only"	
		elif isc<0 or isc>10:	msg="interview score should be between 0 and 10 only"
		else:
			data=[[exp,ts,isc]]
			with open("sp.model","rb") as f:
				model=pickle.load(f)
			res=model.predict(data)
			sal=str(res[0])
			msg="your estimated sal is Rs. "+sal
		return render_template("home.html",msg=msg)
	else:
		return render_template("home.html")	

if __name__=="__main__":
	app.run(debug=True,use_reloader=True)