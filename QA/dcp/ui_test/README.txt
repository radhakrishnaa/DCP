#To run this testing, install protractor in your laptop firstly(your company laptap need add "sudo" before this command to get enough permission)
$npm install -g protractor

$webdriver-manager update

#Start selenium standalone server before test execution;(your company laptap need add "sudo" before this command to get enough permission)
$webdriver-manager start

#Run the local application or set the external environment like a QA

#Run local
python manage.py runserver

#Run local environment test
#This environment will create the empty database for testing and in the end the database is drop
#The initial_data.json is a object that contains all objects to be insert in database based on models of this project

python manage.py testrunserver fixture=../fixtures/initial_data.json

#Test Execution
$protractor config.js
