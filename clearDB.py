import pyrebase
config = {
	"apiKey": "AIzaSyD5nvLGP014aCjjP-wNe_uwZo3orlLiG9Q",
	"authDomain": "heimdallcen4020.firebaseapp.com",
	"databaseURL": "https://heimdallcen4020.firebaseio.com",
	"storageBucket": "heimdallcen4020.appspot.com"
}
f = pyrebase.initialize_app(config)
db = f.database()
db.child("puts").remove()
db.child("calls").remove()
for item in db.child("stocks").get().each():
    db.child("stocks").child(item.key()).remove()