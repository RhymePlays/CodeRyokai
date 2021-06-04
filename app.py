from flask import Flask, request, render_template_string
import time, json, hashlib, threading
from random import choice
from flask.templating import render_template
from markupsafe import Markup

# Initing Flask
app = Flask(__name__)

# Variables
hashSalt = "Ryokai+LongLiveMyAnimeWaifus"
allowedUsernameChars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "_", "."]
autoSave = True

accounts = {}
posts = []


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
    global accounts, posts
    try:
        with open("data.json", "r") as f:
            data = json.loads(f.read())
            accounts = data["accounts"]
            posts = data["posts"]
    except:
        print("Failed to load database")

def autoSaveDatabase():
    while autoSave:
        time.sleep(100)
        try:
            with open("data.json", "w") as f:
                f.write(json.dumps({"accounts" :accounts, "posts": posts}))
            print("Auto-saved database "+str(time.time()))
        except:
            print("Failed to auto-save database "+str(time.time()))

# API Routes
@app.route("/ping", methods=["GET", "POST"])
def ping():
    return "pong"


@app.route("/api/saveData/<code>", methods=["GET"])
def saveDatabase(code):
    if code == "LongLiveMyAnimeWaifus":
        try:
            with open("data.json", "w") as f:
                f.write(json.dumps({"accounts" :accounts, "posts": posts}))
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
                    accounts[username] = {"password": hashlib.sha256((password+hashSalt).encode("ascii")).hexdigest(), "email": email, "joined": time.time(), "posts": [], "following": [], "followers": [], "about": "", "likes": [], "comments": []}
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

            if (username in accounts) and strToIntCheck(fromIndex) and strToIntCheck(toIndex):
                fromIndex=int(fromIndex);toIndex=int(toIndex)
                returnValue=[]
                for index in range(fromIndex, toIndex):
                    try:
                        returnValue.append({"postStr": accounts[username]["posts"][index]["postStr"], "time": accounts[username]["posts"][index]["time"], "id": accounts[username]["posts"][index]["id"], "likes": len(accounts[username]["posts"][index]["likes"]), "comments": len(accounts[username]["posts"][index]["comments"]), "isCommentTo": accounts[username]["posts"][index]["isCommentTo"]})
                    except:
                        return json.dumps(returnValue)
                return json.dumps(returnValue)
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
                accounts[username]["posts"].insert(0 ,{"postStr": postStr, "time": time.time(), "id": f'{username}#{len(accounts[username]["posts"])}', "likes": [], "comments": [], "isCommentTo": None})
                posts.insert(0, f'{username}#{len(accounts[username]["posts"])-1}')
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

            splittedPostId = postId.split("#")
            if len(splittedPostId) == 2:
                if (splittedPostId[0] in accounts) and strToIntCheck(splittedPostId[1]):
                    postIndex = (len(accounts[splittedPostId[0]]["posts"]) - int(splittedPostId[1])) - 1
                    if postIndex >= 0:
                        return {"postStr": accounts[splittedPostId[0]]["posts"][postIndex]["postStr"], "time": accounts[splittedPostId[0]]["posts"][postIndex]["time"], "id": accounts[splittedPostId[0]]["posts"][postIndex]["id"], "likes": len(accounts[splittedPostId[0]]["posts"][postIndex]["likes"]), "comments": len(accounts[splittedPostId[0]]["posts"][postIndex]["comments"]), "isCommentTo": accounts[splittedPostId[0]]["posts"][postIndex]["isCommentTo"]}
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

@app.route("/api/likePost", methods=["POST"])
def likePost():
    if request.method == "POST":
        if ("username" in request.args) and ("password" in request.args) and ("postId" in request.args):
            username = request.args["username"]
            password = request.args["password"]
            postId = request.args["postId"]

            splittedPostId = postId.split("#")
            if authCheck(username, password) and len(splittedPostId) == 2:
                if (splittedPostId[0] in accounts) and strToIntCheck(splittedPostId[1]) and (postId not in accounts[username]["likes"]):
                    postIndex = (len(accounts[splittedPostId[0]]["posts"]) - int(splittedPostId[1])) - 1
                    if postIndex >= 0:
                        accounts[splittedPostId[0]]["posts"][postIndex]["likes"].append(username)
                        accounts[username]["likes"].append(postId)
                        return "success"
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

@app.route("/api/unlikePost", methods=["POST"])
def unlikePost():
    if request.method == "POST":
        if ("username" in request.args) and ("password" in request.args) and ("postId" in request.args):
            username = request.args["username"]
            password = request.args["password"]
            postId = request.args["postId"]

            splittedPostId = postId.split("#")
            if authCheck(username, password) and len(splittedPostId) == 2:
                if (splittedPostId[0] in accounts) and strToIntCheck(splittedPostId[1]) and (postId in accounts[username]["likes"]):
                    postIndex = (len(accounts[splittedPostId[0]]["posts"]) - int(splittedPostId[1])) - 1
                    if postIndex >= 0:
                        accounts[splittedPostId[0]]["posts"][postIndex]["likes"].remove(username)
                        accounts[username]["likes"].remove(postId)
                        return "success"
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

@app.route("/api/isLiked", methods=["POST"])
def isLiked():
    if request.method == "POST":
        if ("username" in request.args) and ("password" in request.args) and ("postId" in request.args):
            username = request.args["username"]
            password = request.args["password"]
            postId = request.args["postId"]

            if authCheck(username, password):
                if postId in accounts[username]["likes"]:
                    return "true"
                else:
                    return "false"
            else:
                return "error"
        else:
            return "error"
    else:
        return "error"

@app.route("/api/comment", methods=["POST"])
def comment():
    if request.method == "POST":
        if ("username" in request.args) and ("password" in request.args) and ("postId" in request.args) and ("commentStr" in request.args):
            username = request.args["username"]
            password = request.args["password"]
            postId = request.args["postId"]
            commentStr = request.args["commentStr"]

            splittedPostId = postId.split("#")
            if authCheck(username, password) and len(splittedPostId) == 2 and (len(commentStr) >= 1):
                if (splittedPostId[0] in accounts) and strToIntCheck(splittedPostId[1]):
                    postIndex = (len(accounts[splittedPostId[0]]["posts"]) - int(splittedPostId[1])) - 1
                    if postIndex >= 0:
                        commentId = f'{username}#{len(accounts[username]["posts"])}'

                        accounts[username]["posts"].insert(0, {"postStr": commentStr, "time": time.time(), "id": commentId, "likes": [], "comments": [], "isCommentTo": postId})

                        if(splittedPostId[0]==username): accounts[splittedPostId[0]]["posts"][postIndex+1]["comments"].insert(0, commentId)
                        else: accounts[splittedPostId[0]]["posts"][postIndex]["comments"].insert(0, commentId)
                        accounts[username]["comments"].insert(0, {"commentOn": postId, "comment": commentId})
                        posts.insert(0, commentId)
                        return "success"
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

@app.route("/api/getPostComments", methods=["GET"])
def getPostComments():
    if request.method == "GET":
        if ("postId" in request.args) and ("fromIndex" in request.args) and ("toIndex" in request.args):
            postId = request.args["postId"]
            fromIndex = request.args["fromIndex"]
            toIndex = request.args["toIndex"]

            splittedPostId = postId.split("#")
            if len(splittedPostId) == 2:
                if (splittedPostId[0] in accounts) and strToIntCheck(splittedPostId[1]) and strToIntCheck(fromIndex) and strToIntCheck(toIndex):
                    postIndex = (len(accounts[splittedPostId[0]]["posts"]) - int(splittedPostId[1])) - 1
                    if postIndex >= 0:

                        allComments = accounts[splittedPostId[0]]["posts"][postIndex]["comments"]

                        fromIndex=int(fromIndex);toIndex=int(toIndex)
                        returnValue=[]
                        for index in range(fromIndex, toIndex):
                            try:

                                splittedCommentId = allComments[index].split("#")
                                if len(splittedCommentId) == 2:
                                    if (splittedCommentId[0] in accounts) and strToIntCheck(splittedCommentId[1]):
                                        commentIndex = (len(accounts[splittedCommentId[0]]["posts"]) - int(splittedCommentId[1])) - 1
                                        if commentIndex >= 0:
                                            returnValue.append({"postStr": accounts[splittedCommentId[0]]["posts"][commentIndex]["postStr"], "time": accounts[splittedCommentId[0]]["posts"][commentIndex]["time"], "id": accounts[splittedCommentId[0]]["posts"][commentIndex]["id"], "likes": len(accounts[splittedCommentId[0]]["posts"][commentIndex]["likes"]), "comments": len(accounts[splittedCommentId[0]]["posts"][commentIndex]["comments"]), "isCommentTo": accounts[splittedCommentId[0]]["posts"][commentIndex]["isCommentTo"]})
                                        else:
                                            return "error"
                                    else:
                                        return "error"
                                else:
                                    return "error"

                            except:
                                return json.dumps(returnValue)
                        return json.dumps(returnValue)
                        
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

@app.route("/api/getTrendingPosts", methods=["GET"])
def getTrendingPosts():
    if request.method == "GET":
        returnValue = []
        try:
            # while len(returnValue) < 10:
            for i in range(10):
                splittedPostId = choice(posts).split("#")
                if len(splittedPostId) == 2:
                    if (splittedPostId[0] in accounts) and strToIntCheck(splittedPostId[1]):
                        commentIndex = (len(accounts[splittedPostId[0]]["posts"]) - int(splittedPostId[1])) - 1
                        if commentIndex >= 0:
                            postObj = {"postStr": accounts[splittedPostId[0]]["posts"][commentIndex]["postStr"], "time": accounts[splittedPostId[0]]["posts"][commentIndex]["time"], "id": accounts[splittedPostId[0]]["posts"][commentIndex]["id"], "likes": len(accounts[splittedPostId[0]]["posts"][commentIndex]["likes"]), "comments": len(accounts[splittedPostId[0]]["posts"][commentIndex]["comments"]), "isCommentTo": accounts[splittedPostId[0]]["posts"][commentIndex]["isCommentTo"]}
                            if postObj not in returnValue:
                                returnValue.append(postObj)

            return json.dumps(returnValue)
        except:
            return "error"
    else:
        return "error"

@app.route("/api/getRecommendedPosts", methods=["GET"])
def getRecommendedPosts():
    if request.method == "GET":
        returnValue = []
        try:
            # while len(returnValue) < 10:
            for i in range(10):
                splittedPostId = choice(posts).split("#")
                if len(splittedPostId) == 2:
                    if (splittedPostId[0] in accounts) and strToIntCheck(splittedPostId[1]):
                        commentIndex = (len(accounts[splittedPostId[0]]["posts"]) - int(splittedPostId[1])) - 1
                        if commentIndex >= 0:
                            postObj = {"postStr": accounts[splittedPostId[0]]["posts"][commentIndex]["postStr"], "time": accounts[splittedPostId[0]]["posts"][commentIndex]["time"], "id": accounts[splittedPostId[0]]["posts"][commentIndex]["id"], "likes": len(accounts[splittedPostId[0]]["posts"][commentIndex]["likes"]), "comments": len(accounts[splittedPostId[0]]["posts"][commentIndex]["comments"]), "isCommentTo": accounts[splittedPostId[0]]["posts"][commentIndex]["isCommentTo"]}
                            if postObj not in returnValue:
                                returnValue.append(postObj)

            return json.dumps(returnValue)
        except:
            return "error"
    else:
        return "error"

# UI Routes
@app.errorhandler(404)
def error404Page(e):
    # return render_template_string(webUI["basePage"], mainSection = Markup(webUI["404Page"]))
    return render_template("base.html", mainSection = Markup(render_template("404.html")))

@app.route("/", methods=["GET", "POST"])
def root():
    return render_template("base.html", mainSection = Markup(render_template("home.html")))

@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("base.html", mainSection = Markup(render_template("about.html")))

@app.route("/user/<username>", methods=["GET", "POST"])
def userPage(username):
    if username in accounts:
        return render_template("base.html", mainSection = Markup(render_template("user.html")))
    else:
        return render_template("base.html", mainSection = Markup(render_template("404.html")))

@app.route("/user/<username>/<postIndexRaw>", methods=["GET", "POST"])
def postPage(username, postIndexRaw):
    if (username in accounts) and strToIntCheck(postIndexRaw):
        postIndex = (len(accounts[username]["posts"]) - int(postIndexRaw)) - 1
        if postIndex >= 0:
            return render_template("base.html", mainSection = Markup(render_template("post.html")))
        else: 
            return render_template("base.html", mainSection = Markup(render_template("404.html")))
    else:
        return render_template("base.html", mainSection = Markup(render_template("404.html")))

# Starting Point
if __name__ == "__main__":
    savingThread = threading.Thread(target=autoSaveDatabase);savingThread.start()
    app.run(port=80, debug=True)