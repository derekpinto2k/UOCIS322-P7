# UOCIS322 - Project 7 #
Adding authentication and user interface to brevet time calculator service

# UOCIS322 - Project 7 #
Brevet time calculator with AJAX, MongoDB, and a RESTful API!

Maintainer - Derek Pinto dpinto@uoregon.edu

Brevet time calculator.

## Overview

Reimplement the RUSA ACP controle time calculator with Flask and AJAX.

### ACP controle times

That's *"controle"* with an *e*, because it's French, although "control" is also accepted. Controls are points where a rider must obtain proof of passage, and control[e] times are the minimum and maximum times by which the rider must arrive at the location.

The algorithm for calculating controle times is described here [https://rusa.org/pages/acp-brevet-control-times-calculator](https://rusa.org/pages/acp-brevet-control-times-calculator). Additional background information is given here [https://rusa.org/pages/rulesForRiders](https://rusa.org/pages/rulesForRiders). The description is ambiguous, but the examples help. Part of finishing this project is clarifying anything that is not clear about the requirements, and documenting it clearly.  

We are essentially replacing the calculator here [https://rusa.org/octime_acp.html](https://rusa.org/octime_acp.html). We can also use that calculator to clarify requirements and develop test data.  

Inserts and retrieves times using mongo database with implemented Submit and Display buttons

### Functionality added

## API ##

 * Three basic APIs (JSON is the default representation for these):
    * "http://<host:port>/listAll" should return all open and close times in the database
    * "http://<host:port>/listOpenOnly" should return open times only
    * "http://<host:port>/listCloseOnly" should return close times only

* You will also design two different representations JSON & CSV:
    * "http://<host:port>/listAll/csv" should return all open and close times in CSV format
    * "http://<host:port>/listOpenOnly/csv" should return open times only in CSV format
    * "http://<host:port>/listCloseOnly/csv" should return close times only in CSV format

    * "http://<host:port>/listAll/json" should return all open and close times in JSON format
    * "http://<host:port>/listOpenOnly/json" should return open times only in JSON format
    * "http://<host:port>/listCloseOnly/json" should return close times only in JSON format

* Query parameter 'top' to find the k = top times for the given api.

    * "http://<host:port>/listOpenOnly/csv?top=3" should return top 3 open times only (in ascending order) in CSV format
    * "http://<host:port>/listOpenOnly/json?top=5" should return top 5 open times only (in ascending order) in JSON format
    * "http://<host:port>/listCloseOnly/csv?top=6" should return top 5 close times only (in ascending order) in CSV format
    * "http://<host:port>/listCloseOnly/json?top=4" should return top 4 close times only (in ascending order) in JSON format

## Website
* Consumer program to service these api requests. This service does not have access to the brevet time calculator

### ADDED FUNCTIONALITES
- POST **/register**

Registers a new user. On success a status code 201 is returned. The body of the response contains a JSON object with the newly added user. On failure status code 400 (bad request) is returned. Note: The password is hashed before it is stored in the database. Once hashed, the original password is discarded. Your database should have three fields: id (unique index), username and password for storing the credentials.

- GET **/token**

Returns a token. This request must be authenticated using a HTTP Basic Authentication. On success a JSON object is returned with a field `token` set to the authentication token for the user and a field `duration` set to the (approximate) number of seconds the token is valid. On failure status code 401 (unauthorized) is returned.

- GET **/RESOURCE**

Return a protected <resource>, which is basically what you created in project 6. This request must be authenticated using token-based authentication only. HTTP password-based (basic) authentication is not allowed. On success a JSON object with data for the authenticated user is returned. On failure status code 401 (unauthorized) is returned.

####  User interface
 a) registration
    registration form for user

 b) login
    log in form a registered user

 c) remember me
    remembers user in case browser is closed

 d) logout.
    log out button the user
## Credits

Michal Young, Ram Durairajan, Steven Walton, Joe Istas.
