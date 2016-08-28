#Fullstack Project 03 Item Catalog#

##Introduction##
This web application is a online sports store catalog that allows users
to view items by category, get specific item details and add, edit or delete
items from the application after the user logs into the application.


##Data##
*Python*<br>
\
application.py - Flask application containing the logic for sport store application
database_setup.py - Database tables used to store items from sports store application
catalogwithusers.py - Populates the database with categories, catalog items and users

*HTML*<br>
\templates\
main.html - Loads required libraries to view application.
header.html - HTML for navigation bar.
catalog.html - Main home page for item catalog.
public_catalog.html - Main home page for item catalog without CRUD functionality.
items.html - Page showing items for a specific category.
public_items.html - Page showing items for a specific category without CRUD functionality.
item.html - Page showing specific item details.
public_item.html - Page showing specific item details without CRUD functionality.
login.html - Page that allows the user to login through Google Oauth authentication.
additem.html - Page where users adds items to the database.
deleteitem.html - Page where users delete items they created from the database.
edititem.html - Page where users edit items they created from the database.

*STATIC*<br>
\static\
sports.jpg - background image for web site.
styles.css - CSS controlling the styles for the elements within the application.



##RUNNING APPLICATION##
*Start by running the database_setup.py file with the command python database_setup.py.<br>
*Once that completes you should see a file catalogwithusers.db<br>
*Run the following command python catalog_items.py.  This creates the data in the .DB file.<br>
*Run the following command python application.py.  You should see a message stating:<br>
*"Running on http://0.0.0.0:8000/"<br>
*"Restarting with reloader"<br>
*In your browser navigate to http://localhost:8000 and you should be able to view the application.


##JSON##
*There are a few paths the user can navigate to, to get a JSON output of the data:
'/categories/json' - Gets a JSON listing of all the categories.
'/items/<int:category_id>/json' - Gets a JSON listing of all the items for a specific category.
'/itemsall/json' - Gets a JSON listing for all items in the catalog.

##CREDITS##
Image obtained from:
https://www.google.com/url?sa=i&rct=j&q=&esrc=s&source=images&cd=&ved=0ahUKEwjW17eFoOTOAhWFpR4KHXFMDgAQjBwIBA&url=http%3A%2F%2Faz616578.vo.msecnd.net%2Ffiles%2F2016%2F05%2F02%2F635977531345511541813312376_Sports_ball__twitter_.jpg&psig=AFQjCNFclVHF47GTbztCo2kD2R3DqqfIdg&ust=1472478495945520
