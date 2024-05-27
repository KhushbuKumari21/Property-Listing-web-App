from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# Mock data for properties (replace with database)
properties = [
    {'id': 1, 'area': 'Example Area 1', 'bedrooms': 3, 'bathrooms': 2, 'proximity': 'Nearby hospitals and colleges', 'likes': 0},
    {'id': 2, 'area': 'Example Area 2', 'bedrooms': 2, 'bathrooms': 1, 'proximity': 'Close to amenities', 'likes': 0},
    # Add more properties here
]

# Pagination settings
PER_PAGE = 10

# Flask-WTF form for pagination
class PaginationForm(FlaskForm):
    page = IntegerField('Page', validators=[DataRequired()])
    submit = SubmitField('Go')

# Routes
@app.route('/')
def index():
    # Implement pagination logic here
    form = PaginationForm(request.form)
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    paginated_properties = properties[start:end]
    return render_template('index.html', properties=paginated_properties, form=form)

@app.route('/property/<int:property_id>')
def property_details(property_id):
    property = get_property_by_id(property_id)
    return render_template('property_details.html', property=property)

@app.route('/like', methods=['POST'])
def like_property():
    property_id = request.form['property_id']
    property = get_property_by_id(property_id)
    property['likes'] += 1
    flash('You liked this property!')
    return redirect(url_for('index'))

@app.route('/interest', methods=['POST'])
def express_interest():
    if 'buyer_email' not in session:
        return redirect(url_for('login'))

    property_id = request.form['property_id']
    property = get_property_by_id(property_id)
    send_email_to_seller(property)
    send_email_to_buyer(property)
    flash('Emails sent to buyer and seller with property details!')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['buyer_email'] = request.form['email']
        flash('You are now logged in!')
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('buyer_email', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

# Helper functions
def get_property_by_id(property_id):
    for property in properties:
        if property['id'] == property_id:
            return property
    return None

def send_email_to_seller(property):
    msg = Message('Interest in your property', sender='your_email@example.com', recipients=['seller_email@example.com'])
    msg.body = f"Hello,\n\nA buyer is interested in your property:\nArea: {property['area']}\nBedrooms: {property['bedrooms']}\nBathrooms: {property['bathrooms']}\nProximity: {property['proximity']}\n\nContact the buyer at: {session['buyer_email']}"
    mail.send(msg)

def send_email_to_buyer(property):
    msg = Message('Seller contact details', sender='your_email@example.com', recipients=[session['buyer_email']])
    msg.body = f"Hello,\n\nHere are the seller's contact details for the property you are interested in:\nName: Seller Name\nEmail: seller_email@example.com\nPhone: +1234567890"
    mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)
