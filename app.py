from flask import Flask, request, render_template, redirect, url_for , flash
from werkzeug.security import generate_password_hash
from flask_bootstrap import Bootstrap
from database import db
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required, current_user
import os 
from datetime import datetime
from models import Author, Book , User
from forms.forms import BookForm, AuthorForm , RegisterForm, LoginForm
from werkzeug.utils import secure_filename
from flask_migrate import Migrate




app = Flask(__name__)
app.config['SECRET_KEY'] = "4fa6fc77e9a2506e3415d7c5891970dc"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'   
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/uploads')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


Bootstrap(app)
db.init_app(app) 
Migrate(app,db)
LoginManager(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # تحديد صفحة تسجيل الدخول الافتراضية
login_manager.login_message = "يجب تسجيل الدخول للوصول إلى هذه الصفحة."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()  



@app.route('/', methods=['GET'])
def home():
    books = Book.query.all()
    return render_template('books_from_form.html', books=books)


@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def addbook():
    form = BookForm()
    form.author.choices = [(author.id, author.name) for author in Author.query.all()]
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image_file = form.image.data
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
        new_book = Book(
        name=form.name.data,
        publish_date=datetime.strptime(str(form.publish_date.data), '%Y-%m-%d').date(),
        add_to_site_at=datetime.strptime(str(form.add_to_site_at.data), '%Y-%m-%d').date(),
        author_id=int(form.author.data),  
        price=form.price.data,
        appropriate=form.appropriate.data,
        image_filename=image_filename
        
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('showbooks'))
    
    return render_template('forms.html', form=form)


@app.route('/add_author', methods=['GET', 'POST'])
def addauthor():
    form = AuthorForm()
    
    if form.validate_on_submit():
      author_name = form.name.data  
      existing_author = Author.query.filter_by(name=author_name).first()

      if existing_author:
          flash(" المؤلف موجود بالفعل!", "warning")
          return redirect(url_for('showbooks'))
      new_author = Author(name=form.name.data)
      db.session.add(new_author)
      db.session.commit()
      db.session.close()
      return redirect(url_for('showbooks'))
    
    return render_template('forms.html', form=form)


@app.route('/showbooks', methods=['GET'])
def showbooks():
    books = Book.query.all()
    return render_template('books_from_form.html', books=books)




@app.route('/book/<int:book_id>', methods=['GET'])
@login_required
def bookdetails(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('bookdetails.html', book=book)

@app.route('/author/<int:author_id>', methods=['GET'])
def authordetails(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template('authordetails.html', author=author)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('showbooks'))




@app.route('/book/db/<int:book_id>', methods=['GET'])
@login_required
def bookdetailsdb(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('bookdetailsdb.html', book=book)



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
        user.password = form.password.data 

        user.save_to_db()
        return redirect(url_for('showbooks'))
    
    return render_template('forms.html', form=form)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
    
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and user.verify_password(form.password.data) :
#          return redirect(url_for('showbooks'))
    
#     return render_template('forms.html', form=form)
# from flask_login import login_user, logout_user, login_required, current_user

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)  # تسجيل الدخول
            return redirect(url_for('home'))
        flash("Invalid email or password", "danger")
    
    return render_template('forms.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)


    form.author.choices = [(author.id, author.name) for author in Author.query.all()]

    if form.validate_on_submit():
        book.name = form.name.data
        book.publish_date = datetime.strptime(str(form.publish_date.data), '%Y-%m-%d').date()
        book.add_to_site_at = datetime.strptime(str(form.add_to_site_at.data), '%Y-%m-%d').date()
        book.author_id = int(form.author.data)
        book.price = form.price.data
        book.appropriate = form.appropriate.data

        if form.image.data:
            image_file = form.image.data
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
            book.image_filename = image_filename

        db.session.commit()
        flash("Book updated successfully!", "success")
        return redirect(url_for('showbooks'))

    return render_template('forms.html', form=form)

 
if __name__ == '__main__':
    app.run(debug=True)

