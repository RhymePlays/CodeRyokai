from flask import Flask, request
import time, json, hashlib, threading
# from markupsafe import escape

# Initing Flask
app = Flask(__name__)

# Variables
hashSalt = "Ryokai+LongLiveMyAnimeWaifus"
allowedUsernameChars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "_", "."]
accounts = {}
autoSave = True

# Function
def usernameCharCheck(username):
    username=username.lower()
    for char in username:
        if char not in allowedUsernameChars:
            return False
    return True

def strToIntCheck(string):
    intChars = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    for char in string:
        if char not in intChars:
            return False
    return True

def authCheck(username, password):
    if username in accounts:
        if accounts[username]["password"] == hashlib.sha256((password+hashSalt).encode("ascii")).hexdigest():
            return True
        else:
            return False
    else:
        return False

def loadDatabase():
    global accounts
    try:
        with open("data.json", "r") as f:
            data = json.loads(f.read())
            accounts = data
    except:
        print("Failed to load database")

def autoSaveDatabase():
    while autoSave:
        time.sleep(100)
        try:
            with open("data.json", "w") as f:
                f.write(json.dumps(accounts))
            print("Auto-saved database "+str(time.time()))
        except:
            print("Failed to auto-save database "+str(time.time()))

# Routes
@app.route("/")
def root():
    return "<h2>Konnichiwa Sekai</h2><p>Welcome to Magic Notes</p>"

@app.route("/saveData/<code>", methods=["GET"])
def saveDatabase(code):
    if code == "LongLiveMyAnimeWaifus":
        try:
            with open("data.json", "w") as f:
                f.write(json.dumps(accounts))
            return "success"
        except:
            return "error"
    else:
        return "error"

@app.route("/api/signup", methods=["POST"])
def signup():
    if request.method == "POST":
        if ("username" in request.args) and ("password" in request.args) and ("email" in request.args):
            username = request.args["username"]
            password = request.args["password"]
            email = request.args["email"]

            if usernameCharCheck(username) and (username not in accounts) and (len(username) >= 4) and (len(username) <= 18) and (len(email) > 1) and (len(email) <= 320):
                if len(password) >= 8 and len(password) <= 64:
                    accounts[username] = {"password": hashlib.sha256((password+hashSalt).encode("ascii")).hexdigest(), "email": email, "joined": time.time(), "notes": [], "following": [], "followers": [], "about": ""}
                    return "success"
                else:
                    return "error"
            else:
                return "error"
        else:
            return "error"
    else:
        return "error"

@app.route("/api/addAbout", methods=["POST"])
def addAbout():
    if request.method == "POST":
        if ("username" in request.args) and ("password" in request.args) and ("aboutStr" in request.args):
            username = request.args["username"]
            password = request.args["password"]
            aboutStr = request.args["aboutStr"]

            if authCheck(username, password) and (len(aboutStr) >= 1):
                accounts[username]["about"] = aboutStr
                return "success"
            else:
                return "error"
        else:
            return "error"
    else:
        return "error"

@app.route("/api/getUserInfo", methods=["GET"])
def getUserInfo():
    if request.method == "GET":
        if ("username" in request.args):
            username = request.args["username"]

            if username in accounts:
                return {"username": username, "joined": accounts[username]['joined'], "entries": len(accounts[username]['notes']), "about": accounts[username]['about'], "following": len(accounts[username]['following']), "followers": len(accounts[username]['followers'])}
            else:
                return "error"
        else:
            return "error"
    else:
        return "error"

@app.route("/api/getUserNotes", methods=["GET"])
def getUserNotes():
    if request.method == "GET":
        if ("username" in request.args) and ("fromIndex" in request.args) and ("toIndex" in request.args):
            username = request.args["username"]
            fromIndex = request.args["fromIndex"]
            toIndex = request.args["toIndex"]

            if username in accounts:
                try:
                    fromIndex=int(fromIndex);toIndex=int(toIndex)
                    returnValue=[]
                    for index in range(fromIndex, toIndex):
                        try:
                            returnValue.append(accounts[username]["notes"][index])
                        except:
                            return returnValue
                    return returnValue
                except:
                    return "error"
            else:
                return "error"
        else:
            return "error"
    else:
        return "error"

@app.route("/api/addNote", methods=["POST"])
def addNote():
    if request.method == "POST":
        if ("username" in request.args) and ("password" in request.args) and ("noteStr" in request.args):
            username = request.args["username"]
            password = request.args["password"]
            noteStr = request.args["noteStr"]

            if authCheck(username, password) and (len(noteStr) >= 1):
                accounts[username]["notes"].insert(0 ,{"noteStr": noteStr, "time": time.time(), "id": f'{username}#{len(accounts[username]["notes"])}'})
                return "success"
            else:
                return "error"
        else:
            return "error"
    else:
        return "error"

@app.route("/api/followUser", methods=["POST"])
def followUser():
    if request.method == "POST":
        if ("username" in request.args) and ("password" in request.args) and ("userToFollow" in request.args):
            username = request.args["username"]
            password = request.args["password"]
            userToFollow = request.args["userToFollow"]

            if authCheck(username, password) and (userToFollow in accounts):
                if userToFollow not in accounts[username]["following"]:
                    accounts[username]["following"].append(userToFollow)
                    accounts[userToFollow]["followers"].append(username)
                    return "success"
                else: 
                    return "error"
            else:
                return "error"
        else:
            return "error"
    else:
        return "error"

@app.route("/api/unfollowUser", methods=["POST"])
def unfollowUser():
    if request.method == "POST":
        if ("username" in request.args) and ("password" in request.args) and ("userToUnfollow" in request.args):
            username = request.args["username"]
            password = request.args["password"]
            userToUnfollow = request.args["userToUnfollow"]

            if authCheck(username, password) and (userToUnfollow in accounts):
                if userToUnfollow in accounts[username]["following"]:
                    accounts[username]["following"].remove(userToUnfollow)
                    accounts[userToUnfollow]["followers"].remove(username)
                    return "success"
                else: 
                    return "error"
            else:
                return "error"
        else:
            return "error"
    else:
        return "error"

@app.route("/api/isFollowingUser", methods=["POST"])
def isFollowingUser():
    if request.method == "POST":
        if ("username" in request.args) and ("password" in request.args) and ("userToCheck" in request.args):
            username = request.args["username"]
            password = request.args["password"]
            userToCheck = request.args["userToCheck"]

            if authCheck(username, password) and (userToCheck in accounts):
                if userToCheck in accounts[username]["following"]:
                    return "true"
                else: 
                    return "false"
            else:
                return "error"
        else:
            return "error"
    else:
        return "error"

@app.route("/api/getNoteById", methods=["GET"])
def getNoteById():
    if request.method == "GET":
        if "noteId" in request.args:
            noteId = request.args["noteId"]

            splitedNoteId = noteId.split("#")
            if len(splitedNoteId) == 2:
                if (splitedNoteId[0] in accounts) and strToIntCheck(splitedNoteId[1]):
                    noteIndex = (len(accounts[splitedNoteId[0]]["notes"]) - int(splitedNoteId[1])) - 1
                    if noteIndex >= 0:
                        return accounts[splitedNoteId[0]]["notes"][noteIndex]
                    else:
                        return "error"
                else:
                    return "error"
            else:
                return "error"
        else:
            return "error"
    else:
        return "error"

# Starting Point
if __name__ == "__main__":
    loadDatabase()
    savingThread = threading.Thread(target=autoSaveDatabase);savingThread.start()
    app.run(port=80, debug=True)