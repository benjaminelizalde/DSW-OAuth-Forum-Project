
from flask import Flask, redirect, url_for, session, request, jsonify, Markup
from flask_oauthlib.client import OAuth
from flask import render_template
from time import localtime, strftime

import pprint
import os
import json

app = Flask(__name__)

app.debug = True #Change this to False for production
app.secret_key = os.environ['SECRET_KEY'] #used to sign session cookies
oauth = OAuth(app)

#Set up GitHub as OAuth provider
github = oauth.remote_app(
    'github',
    consumer_key=os.environ['GITHUB_CLIENT_ID'], #your web app's "username" for github's OAuth
    consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],#your web app's "password" for github's OAuth
    request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
)

#TODO: globalVar=postData Create and set a global variable for the name of you JSON file here.  The file will be storedd on Heroku, so you don't need to make it in GitHub
pdata1="static/posts1.json"
pdata2="static/posts2.json"
#TODO: Create the file on Heroku using os.system.  Ex) os.system("echo '[]'>"+myFile) puts '[]' into your file
#os.system("echo '[]'>"+pdata)

def Post_Html1():
    with open(pdata1,"r") as postfile:
        data=json.load(postfile)
        data.reverse()
        mass =""
        for com in data:
            mass += com["user"] + ": "+com["message"] + "<br>"
    return mass

def Post_Html2():
    with open(pdata2,"r") as postfile:
        data=json.load(postfile)
        data.reverse()
        mass =""
        for com in data:
            mass += com["user"] + ": "+com["message"] + "<br>"
    return mass

@app.context_processor
def inject_logged_in():
    return {"logged_in":('github_token' in session)}

@app.route('/')
def Forum1():
    print(strftime("%a, %d %b %Y %H:%M:%S", localtime()))
    with open(pdata1,"r") as postfile:
        data=json.load(postfile)
        data.reverse()
        mass =""
        for com in data:
            mass += com["user"] + ": "+com["message"] + "<br>"
        return render_template('Forum1.html', past_posts1=Markup(mass))

@app.route('/Forum2')
def Forum2():
    redirect='Forum2'
    print(strftime("%a, %d %b %Y %H:%M:%S", localtime()))
    with open(pdata2,"r") as postfile:
        data=json.load(postfile)
        data.reverse()
        mass =""
        for com in data:
            mass += com["user"] + ": "+com["message"] + "<br>"
        return render_template('Forum2.html', past_posts2=Markup(mass))

@app.route('/posted1', methods=['POST'])
def post():
    msg = request.form['message']
    usr = session['user_data']['login'];
    newpost = {}
    if usr == "DaZenMesa" or usr == "benjaminelizalde":
        newpost["user"] = "<font color=#0008ff> <b>" +'[ADMIN]'+" "+ usr + "</b></font>"
    else:
        newpost["user"] = "<font color=#000000> <b>" + usr + "</b></font>"
    newpost["message"] = "<b>" + msg + "</b>" + ' :' + str(strftime( "%H:%M:%S", localtime()))

    #alldata += newpost
    #os.run( json(alldata) > file )
    with open(pdata1,'r') as oldpost:
        data=json.load(oldpost)
        data.append(newpost)
       # oldpost.seek(0)
        #oldpost.truncate()
        #data.append(newpost)

    with open(pdata1,'w') as oldpost:
        json.dump(data,oldpost)

    #return render_template('home.html' )
    print(request.form)
    redirect= ""
    if "Forum1" in request.form:
        redirect= "Forum1"
        return render_template('%s.html' % redirect, past_posts1=Markup(Post_Html1()))
    if "Forum2" in request.form:
        redirect= "Forum2"
        return render_template('%s.html' % redirect, past_posts2=Markup(Post_Html2()))
    print(redirect)

    #return redirect(url_for('.' + redirect))
    #This function should add the new post to the JSON file of posts and then render home.html and display the posts.
    #Every post should include the username of the poster and text of the post.  poststohtml data
    #('filename.JSON','r+')
    # data=json.load(f)
        #JSON.dump(data,f)


#redirect to GitHub's OAuth page and confirm callback URL
@app.route('/login')
def login():
    return github.authorize(callback=url_for('authorized', _external=True, _scheme='http')) #callback URL must match the pre-configured callback URL

@app.route('/logout')
def logout():
    session.clear()
    return render_template('message.html', message='You were logged out')

@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        session.clear()
        message = 'Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args)
    else:
        try:
            session['github_token'] = (resp['access_token'], '') #save the token to prove that the user logged in
            session['user_data']=github.get('user').data
            message='You were successfully logged in as ' + session['user_data']['login']
        except Exception as inst:
            session.clear()
            print(inst)
            message='Unable to login, please try again.  '
    return render_template('message.html', message=message)


#the tokengetter is automatically called to check who is logged in.
@github.tokengetter
def get_github_oauth_token():
    return session.get('github_token')


if __name__ == '__main__':
    os.system("echo json(array) > file")
    app.run()
