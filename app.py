from flask import Flask, request, render_template_string
import time, json, hashlib, threading
from markupsafe import Markup

# Initing Flask
app = Flask(__name__)

# Variables
hashSalt = "Ryokai+LongLiveMyAnimeWaifus"
allowedUsernameChars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "_", "."]
accounts = {}
webUI = {}
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

def loadWebUI(pageLoadQueue):
    for page in pageLoadQueue:
        try:
            with open(page["fileLoc"], "r") as f:
                webUI[page["pageTag"]] = f.read()
        except:
            print("Failed to load "+str(page["pageTag"]))

# API Routes
@app.route("/api/saveData/<code>", methods=["GET"])
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

@app.route("/api/login", methods=["POST"])
def login():
    if (request.method == "POST") and ("username" in request.args) and ("password" in request.args):
        username = request.args["username"]
        password = request.args["password"]

        if authCheck(username, password):
            return "success"
        else:
            return "error2"
    else:
        return "error1"


@app.route("/api/signup", methods=["POST"])
def signup():
    if request.method == "POST":
        if ("username" in request.args) and ("password" in request.args) and ("email" in request.args):
            username = request.args["username"]
            password = request.args["password"]
            email = request.args["email"]

            if usernameCharCheck(username) and (username not in accounts) and (len(username) >= 4) and (len(username) <= 18) and (len(email) > 1) and (len(email) <= 320):
                if len(password) >= 8 and len(password) <= 64:
                    accounts[username] = {"password": hashlib.sha256((password+hashSalt).encode("ascii")).hexdigest(), "email": email, "joined": time.time(), "posts": [], "following": [], "followers": [], "about": ""}
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
                return {"username": username, "joined": accounts[username]['joined'], "entries": len(accounts[username]['posts']), "about": accounts[username]['about'], "following": len(accounts[username]['following']), "followers": len(accounts[username]['followers'])}
            else:
                return "error"
        else:
            return "error"
    else:
        return "error"

@app.route("/api/getUserPosts", methods=["GET"])
def getUserPosts():
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
                            returnValue.append(accounts[username]["posts"][index])
                        except:
                            return json.dumps(returnValue)
                    return json.dumps(returnValue)
                except:
                    return "error"
            else:
                return "error"
        else:
            return "error"
    else:
        return "error"

@app.route("/api/addPost", methods=["POST"])
def addPost():
    if request.method == "POST":
        if ("username" in request.args) and ("password" in request.args) and ("postStr" in request.args):
            username = request.args["username"]
            password = request.args["password"]
            postStr = request.args["postStr"]

            if authCheck(username, password) and (len(postStr) >= 1):
                accounts[username]["posts"].insert(0 ,{"postStr": postStr, "time": time.time(), "id": f'{username}#{len(accounts[username]["posts"])}'})
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

@app.route("/api/getPostById", methods=["GET"])
def getPostById():
    if request.method == "GET":
        if "postId" in request.args:
            postId = request.args["postId"]

            splitedPostId = postId.split("#")
            if len(splitedPostId) == 2:
                if (splitedPostId[0] in accounts) and strToIntCheck(splitedPostId[1]):
                    postIndex = (len(accounts[splitedPostId[0]]["posts"]) - int(splitedPostId[1])) - 1
                    if postIndex >= 0:
                        return accounts[splitedPostId[0]]["posts"][postIndex]
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

# UI Routes
@app.errorhandler(404)
def error404Page(e):
    return render_template_string(webUI["basePage"], mainSection = Markup(webUI["404Page"]))

@app.route("/")
def root():
    return render_template_string(webUI["basePage"], mainSection = Markup("""<div class="sectionBG"><div class="sectionTop"><div class="cH1">Konnichiwa Sekai</div></div><hr><div style="margin: 10px">Welcome to CodeRyokai</div></div>"""))

@app.route("/user/<username>", methods=["GET", "POST"])
def userPage(username):
    if username in accounts:
        return render_template_string(webUI["basePage"], mainSection = Markup(webUI["userPage"]))
    else:
        return render_template_string(webUI["basePage"], mainSection = Markup(webUI["404Page"]))

# Starting Point
if __name__ == "__main__":
    loadDatabase();loadWebUI([{"fileLoc": "pages/base.html", "pageTag": "basePage"}, {"fileLoc": "pages/user.html", "pageTag": "userPage"}, {"fileLoc": "pages/404.html", "pageTag": "404Page"}])
    savingThread = threading.Thread(target=autoSaveDatabase);savingThread.start()
    app.run(port=80, debug=True)