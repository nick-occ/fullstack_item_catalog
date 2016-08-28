from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc, func,distinct
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from oauth2client.client import AccessTokenCredentials

import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

#client id from client secrets file
CLIENT_ID = json.loads(
    open('client_secrets.json','r').read())['web']['client_id']

#name of application
APPLICATION_NAME = "Online Shopping Catalog"

#connect to db and create session
engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession() #database session object

#get category id category
def getCategories(categories,category):
    for cat in categories:
        if cat.name == category:
            return cat.id
    

#logic for application login page
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    #store state token in login_session object
    login_session['state'] = state
    #render login page
    return render_template('login.html',STATE=state)

#logic for logging into application
@app.route('/gconnect', methods=['POST'])
def gconnect():
    #check if state token matches if not return 401 response
    if request.args.get('state') != login_session['state']:
        #response if state token doesn't match
        response = make_response(json.dumps('Invalid state parameter.'),401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #get auth code
    code = request.data

    try:
        #upgrade auth code into credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        #get code and get credentials
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        #response if authorization code is wrong
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'),401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #check for valid token
    access_token = credentials.access_token
    
    #get user information by passing in token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           %access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])

    #if there was an error in token return 500 response
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')),500)
        response.headers['Content-Type'] = 'application/json'
        return response

    #verify token is for correct user if not return 401 response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        #reponse if token is invalid
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."),401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #verify token is for correct app if not return 401 response
    if result['issued_to'] != CLIENT_ID:
        #response if client id is invalid
        response = make_response(
            json.dumps("Token's client ID does not match app's."),401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    #get credentials and id from login session
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        #resoonse if user is already connected
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    #store the access token in the session for later use
    login_session['credentials'] = credentials.access_token
    credentials = AccessTokenCredentials(login_session['credentials'], 'user-agent-value')
    login_session['gplus_id'] = gplus_id

    #get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)
   
    data = answer.json()

    #store user info in login session
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    #get user id from database
    user_id = getUserId(login_session['email'])
    #create user if they do not exist
    if not user_id:
        user_id = createUser(login_session)
    #store user id in login session
    login_session['user_id'] = user_id

    #html output
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            #del login_session['gplus_id']
            #del login_session['credentials']
        
        #del login_session['username']
        #del login_session['email']
        #del login_session['picture']
        #del login_session['user_id']
        #del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))

#logic to disconnect session from google auth
@app.route('/gdisconnect')
def gdisconnect():
    #get credentials from login session
    credentials = login_session.get('credentials')
    if credentials is None:
        #reponse if user is not connected
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    
    #revoke access token
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    
    if result['status'] == '200':
        print login_session
    #delete login session elements
	del login_session['credentials'] 
	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
        #response if user is successfully disconnected
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:
        #reponse if token cannot be revoked
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response


#show all catgories
@app.route('/')
@app.route('/catalog/')
def showCategories():
    #query category table from database
    categories = session.query(Category).order_by(asc(Category.name))
    
    #query latest items from database
    latestItems = session.query(CategoryItem).order_by(desc(CategoryItem.date_added))[:10]
    
    #if user is not logged in show public page otherwise show CRUD page
    if 'username' not in login_session:
        return render_template('public_catalog.html',categories = categories, latestItems=latestItems)
    else:
        return render_template('catalog.html', categories = categories, latestItems=latestItems)

#show items for a specific category
@app.route('/items/<int:category_id>/')
def showItems(category_id):
    #query category table from database
    category = session.query(Category).filter_by(id = category_id).all()
    category_name = category[0].name
    
    category = session.query(Category).order_by(asc(Category.name))
    #query category items from database
    items = session.query(CategoryItem).filter_by(category_id = category_id).all()
    print 
    #if user is not logged in show public page otherwise show CRUD page
    if 'username' not in login_session:
        return render_template('public_items.html', category=category, category_name=category_name, items=items)
    else:
        return render_template('items.html', category=category, category_name=category_name, items=items)

#JSON output of categories
@app.route('/categories/json')
def categoryJSON():
    #query category table from database
    category = session.query(Category).order_by(asc(Category.name)).all()
    return jsonify(categorys=[c.serialize for c in category])

#JSON output of items for a specific category
@app.route('/items/<int:category_id>/json')
def categoryitemsJSON(category_id):
    #query category items from database
    items = session.query(CategoryItem).filter_by(category_id = category_id).all()
    return jsonify(items=[i.serialize for i in items])

#JSON output of all items in database
@app.route('/itemsall/json')
def itemsJSON():
    #query category table from database
    category = session.query(Category).all()
    store = {}
    for c in category:
        #loop through categories and return all items from the database
        items = session.query(CategoryItem).filter_by(category_id=c.id).all()    
        store[c.id] = {"category":c.name,
        "items": [i.serialize for i in items]
        }
    return(jsonify(store=store))

#show item details
@app.route('/item/<int:item_id>/')
def showItem(item_id):
    #query category item from database
    item = session.query(CategoryItem).filter_by(id=item_id)

    #if user is not logged in show public page otherwise show CRUD page
    if 'username' not in login_session:
        return render_template('public_item.html', item=item)
    else:
        return render_template('item.html', item=item)

#add catalog items in the database
@app.route('/additem/', methods=['GET','POST'])
def addItem():
    #if not logged in then redirect to login screen
    if 'username' not in login_session:
        return redirect('/login')

    #post event when users creates item
    if request.method == 'POST':
        #query category item from database
        categories = session.query(Category).order_by(asc(Category.name))
    
        #get id of selected category
        cat_id = getCategories(categories,request.form['category'])
        
        #create new item in database
        newItem = CategoryItem(name=request.form['name'],description=request.form['description'], category_id = cat_id, user_id = login_session['user_id'], date_added=func.now())
        session.add(newItem)
        session.commit()
        
        #show message confirming item is created and redirect to home page
        flash('New Item %s Successfully Created' % (newItem.name))
        return redirect(url_for('showCategories'))
    else:
        #query category item from database
        categories = session.query(Category.id, Category.name).order_by(asc(Category.name))

        #if user is not logged in goto home page otherwise show CRUD page
        if 'username' not in login_session:
            return redirect(url_for('showCategories'))
        else:
            return render_template('additem.html',categories=categories)

#edit catalog items in the database
@app.route('/item/<int:item_id>/edit/', methods=['GET','POST'])
def editItem(item_id):
    #query category item from database
    editedItem = session.query(CategoryItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        #get data from form and update in database
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        #show message confirming item is created and redirect to home page
        flash('Catalog Item Successfully Edited')
        return redirect(url_for('showCategories'))
    else:
        #if user is not logged in goto home page
        if 'username' not in login_session:
            flash('Please login to edit items')
            return redirect(url_for('showCategories'))
        #if user is not one that created item send message notifying user
        elif login_session['user_id'] != editedItem.user_id:
            flash('Only user that created this item can edit')
            return redirect(url_for('showItem',item_id=editedItem.id))
        #otherwise render edit page
        else:
            return render_template('edititem.html',item=editedItem)

#delete catalog item in the database
@app.route('/item/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    #query category item from database
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    if request.method == 'POST':
        #delete item in database
        session.delete(itemToDelete)
        session.commit()
        #show message confirming item is created and redirect to home page
        flash('Item Successfully Deleted')
        return redirect(url_for('showCategories'))
    else:
        #if user is not logged in goto home page
        if 'username' not in login_session:
            return redirect(url_for('showCategories'))
        #if user is not one that created item send message notifying user
        elif login_session['user_id'] != itemToDelete.user_id:
            flash('Only user that created this item can delete')
            return redirect(url_for('showItem',item_id=itemToDelete.id))
        #otherwise render delete page
        else:
            return render_template('deleteitem.html', item=itemToDelete)

#create user in user database
def createUser(login_session):
    #get user information from login session
    newUser = User(name=login_session['username'],email=login_session['email'],picture=login_session['picture'])
    #write user to database
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

#query user from database
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

#query user id by email in database
def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)