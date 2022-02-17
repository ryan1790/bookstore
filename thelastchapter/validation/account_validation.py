import flask
from werkzeug.exceptions import abort

roles = ( 'ADMIN', 'EDITOR', 'USER' )

class LogIn():
    def __init__(self):
        """ Create the ViewModel with the form data from the request """
        request = flask.request
        self.email = request.form['email']
        self.password = request.form['password']
        self.error = None
 
    def validate(self):
        """ validate the form """     
        if not self.email or not self.email.strip() or '@' not in self.email:
            self.error = 'Must use a valid email' 
        if not self.password or not self.password.strip():
            self.error = 'Must have a password' 
 
    def __str__(self):
        """ create a readable output for the data """
        return f"{self.email}"
 
    def to_dict(self):
        """ turn this object into a dictionary """
        return self.__dict__

class UpdateAccount():
    def __init__(self):
        """ Create the ViewModel with the form data from the request """
        request = flask.request
        self.username = request.form['username']
        self.email = request.form['email']
        self.old_password = request.form['old-password']
        self.new_password = request.form['new-password']
        self.check_password = request.form['check-password']
        self.update_password = False
        self.error = None
 
    def validate(self):
        """ validate the form """
        if not self.username or not self.username.strip():
            self.error = 'Must have a display name'        
        if not self.email or not self.email.strip() or '@' not in self.email:
            self.error = 'Must have a valid email' 
        if len(self.old_password) > 0:
            self.update_password = True
            if not self.new_password or not self.new_password.strip():
                self.error = 'Must have a new password entered'
            if self.new_password != self.check_password:
                self.error = 'New password and confirm password must match'
 
    def __str__(self):
        """ create a readable output for the data """
        return f"{self.name} [{self.email}]"
 
    def to_dict(self):
        """ turn this object into a dictionary """
        return self.__dict__

class AlterPermissions():
    def __init__(self):
        """ Create the ViewModel with the form data from the request """
        request = flask.request
        self.email = request.form['email']
        self.role = request.form['role']
        self.error = None
 
    def validate(self):
        """ validate the form """
        if not self.email or not self.email.strip() or '@' not in self.email:
            self.error = 'Enter valid email address'
        if self.role not in roles:
            abort(400)
 
    def __str__(self):
        """ create a readable output for the data """
        return f"{self.name} [{self.email}]: {self.message}"
 
    def to_dict(self):
        """ turn this object into a dictionary """
        return self.__dict__