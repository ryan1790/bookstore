import flask

class NewBook():
    def __init__(self):
        """ Create the ViewModel with the form data from the request """
        request = flask.request
        self.title = request.form['title']
        self.author = request.form['author']
        self.info = request.form['info']
        self.price = str(request.form['price'])
        self.isbn = request.form['isbn']
        self.image = request.form['image']
        self.published = request.form['published']
        self.lang = request.form['lang']
        self.pages = request.form['pages']
        self.stock = request.form['stock']
        self.genre_id = request.form['genre']
        self.error = None

    def validate(self):
        """ validate the form """
        print('\n\n\n')
        print(type(self.pages), type(self.stock), type(self.genre_id))
        print('\n\n\n')
        if not self.title or not self.title.strip():
            self.error = 'Title is missing'        
        if not self.author or not self.author.strip():
            self.error = 'Author is missing'        
        if not self.info or not self.info.strip():
            self.error = 'Description is missing'        
        if not self.price or not self.price.strip():
            self.error = 'Price is missing'      
        try:
            float(self.price)
        except TypeError:
            self.error = 'Invalid price'  
        if not self.isbn or not self.isbn.strip():
            self.error = 'ISBN is missing'       
        if not self.isbn.isnumeric() or len(self.isbn) != 10 and len(self.isbn) != 13:
            self.error = 'Must be a valid ISBN'
        if not self.image or not self.image.strip():
            self.error = 'Image is missing'      
        if 'http' not in self.image:
            self.error = 'Invalid image url'  
        if not self.lang or not self.lang.strip():
            self.error = 'Language is missing' 
        if not self.genre_id or not self.genre_id.strip():
            self.error = 'Genre is missing'
        if not self.genre_id.isnumeric():
            self.error = 'Invalid genre'
 
    def __str__(self):
        """ create a readable output for the data """
        return f"{self.title}: {self.author}"
 
    def to_dict(self):
        """ turn this object into a dictionary """
        return self.__dict__