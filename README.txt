Welcome to the codebase for our simple easy Audit Tool
-Alex Conklin
-Premgith Vidyanandan
-Shannon Mendonca

Directory Structure
|
|-/database
| |
| - /diagrams           Contains the ERD and any other database related diagrams we need to design
| |  
| - /scripts            Contains all the scripts needed to build the database out in order to run the tool
|
|-/requirements
| |
| - /diagrams           Contains all the diagrams designed as part of planning/requirements gathering
|   |
|   - /seq_diagrams     Contains the sequence diagrams in particular
|
|-/templates            Contains the html templates used by flask to build the pages.
|
|-/entity               Contains Entity Classes to model the major objects in the app (see class diagram).
|
|-/service              Contains our service classes which handle passing data back and forth between db tables and entity objects.
|
|-/static
| |
| - /stylesheets        Contains our primary css file 'standard.css'. This folder structure is enforced by Flask.

Running the code-

To run this you will need the following installed (likely through pip)
-Python
-Flask (python library, runs the python web server)
-Psycopg2 (python library, connects to the database)

You will also need to be running a postgresql database (free download from https://www.postgresql.org/)

Step 1 - Database setup
-First, using a tool such as pgAdmin create a new database called 'supplierauditdb'
-Then create a database user with the following username and password: user-'sadb_appuser', password-'appuserpassword'
*NOTE* You will notice those above values are available in dbconfig.py-
    You are free to change them in your db but be sure to update dbconfig or psycopg2 will be unable to make a connection
-Finally run the db scripts found in /database/scripts in their numbered order

Step 2 - Running the application
-Assuming all dependencies are installed running the application is as simple as running app.py in python.
-The command line will give you a url that you can go to in order to visit the site on your browser (usually http://127.0.0.1:5000)
-The test user script you ran earlier created 2 users for you to log in as
        - An auditor named 'admin' who you can login as using 'admin@test.com' with password '123'
        - A supplier user named 'supplier_user' who logs in using 'supplier@test.com' with password '123'
-Use these two users to explore the full application!

