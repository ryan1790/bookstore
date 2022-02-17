import flask
from thelastchapter.utilities import STATES

class NewAddress():
    def __init__(self):
        """ Create the ViewModel with the form data from the request """
        request = flask.request
        form = request.form
        if 'name' in form:
            self.name = form['name']
        else:
            self.name = ''
        self.city = form['city']
        self.address = form['address']
        self.state = form['state']
        self.country = 'US'
        self.zip_code = form['zip-code']
        self.error = None
 
    def validate(self):
        """ validate the form """ 
        if not self.city or not self.city.strip():
            self.error = 'Missing city' 
        if not self.address or not self.address.strip():
            self.error = 'Missing address' 
        if not self.state or not self.state.strip():
            self.error = 'Missing state'
        if not self.state not in STATES:
            self.error = 'Invalid state'
        if len(self.zip_code) != 6 or not self.zip_code.isnumeric():
            self.error = 'Invalid zip code'
 
    def __str__(self):
        """ create a readable output for the data """
        return f"{self.name + ': ' if self.name else ''}{self.address} {self.city}, {self.state} {self.zip}"
 
    def to_dict(self):
        """ turn this object into a dictionary """
        return self.__dict__