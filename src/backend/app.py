from flask import Flask, render_template, redirect, jsonify, request, session, flash
import re
import os
from gaming import gaming_bp, get_gaming_build
from office import office_bp, get_office_build
from editing import editing_bp, get_editing_build
from dotenv import load_dotenv 
from flask_login import current_user
from google_auth_oauthlib.flow import Flow
import pathlib  # For handling file paths
import cachecontrol  # For caching session
import google.auth.transport.requests  # For Google OAuth requests
from google.oauth2 import id_token  # For verifying ID tokens
from requests import Session  # Correct import
from kategori import CPU, CPUCoolers, VideoCard, InternalHardDrive, Keyboard, Memory, Headphones, Monitor, Motherboard, Mouse, PowerSupply, Wishlist, User
from models import db
from functools import wraps
import hashlib
from datetime import datetime,timedelta
from sqlalchemy.exc import IntegrityError
import logging


load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")  # PostgreSQL Database URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
client_id = os.environ.get("GOOGLE_CLIENT_ID")
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
db.init_app(app)  # Initialize the db with the app

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
app.permanent_session_lifetime = timedelta(days=7)

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"  # Corrected parameter name
)

# Atur konfigurasi logging
logging.basicConfig(level=logging.DEBUG)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect('/logins')  # Directly using the login URL
        return f(*args, **kwargs)
    return decorated_function

@app.route('/wishlist/remove', methods=['DELETE'])
@login_required
def remove_wishlist_item():
    user_id = session.get('user_id')
    name = request.args.get('name')
    price = request.args.get('price')
    category = request.args.get('category')

    # Ensure all parameters are provided
    if not all([name, price, category]):
        return jsonify({'error': 'Missing item data'}), 400

    # Find the item in the wishlist
    wishlist_item = Wishlist.query.filter_by(user_id=user_id, name=name, price=price, category=category).first()

    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({'message': 'Item removed from wishlist'}), 200
    else:
        return jsonify({'error': 'Item not found or not authorized'}), 404
    
@app.route('/wishlist', methods=['GET'])
@login_required
def get_wishlist():
    user_id = session.get('user_id')
    print("User ID:", user_id)  # Debug statement
    wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()

    if not wishlist_items:
        return jsonify({'wishlist': [], 'message': "You don't have a wishlist yet"}), 200

    items = [{
        'name': item.name,
        'price': float(item.price),
        'category': item.category,
        'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for item in wishlist_items]

    return jsonify({'wishlist': items}), 200

@app.route('/wishlist/add', methods=['POST'])
@login_required
def add_to_wishlist():
    data = request.json
    logging.debug(f"Received data: {data}")  # Log data yang diterima

    name = data.get('name')
    price = data.get('price')
    category = data.get('category')
    user_id = session.get('user_id')

    # Check if all required data is present
    if not all([name, price, category]):
        logging.error('Missing item data: name=%s, price=%s, category=%s', name, price, category)
        return jsonify({'error': 'Invalid item data'}), 400

    # Check if the item is already in the wishlist
    existing_item = Wishlist.query.filter_by(user_id=user_id, name=name, price=price, category=category).first()
    if existing_item:
        logging.warning('Item already in wishlist: %s', name)
        return jsonify({'error': 'Item already in wishlist'}), 409

    # Add new item to wishlist
    wishlist_item = Wishlist(
        user_id=user_id,
        name=name,
        price=price,
        category=category
    )

    try:
        db.session.add(wishlist_item)
        db.session.commit()
        logging.info('Item added to wishlist: %s', name)
        return jsonify({'message': 'Item added to wishlist!'}), 200
    except IntegrityError as e:
        db.session.rollback()
        logging.error('Failed to add item to wishlist: %s', str(e))
        return jsonify({'error': 'Failed to add item to wishlist'}), 500


@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    username = request.form.get('username')
    address = request.form.get('address')
    city = request.form.get('city')
    country = request.form.get('country')
    state = request.form.get('state')
    zipcode = request.form.get('zipcode')
    password = request.form.get('password')

    # Check if username or email already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing_user:
        return jsonify({'message': 'Username or Email already exists.'}), 400

    # Hash the password using hashlib
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Create a new user instance
    new_user = User(
        email=email,
        username=username,
        password=hashed_password,
        address=address,
        city=city,
        country=country,
        state=state,
        zipcode=zipcode
    )

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect('/logins') 

@app.route('/api/cpu')
@login_required
def cpu_api():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.select(CPU).distinct(CPU.name).order_by(CPU.name)  # Ensuring distinct CPUs
    cpus = db.paginate(query, page=page, per_page=per_page, error_out=False)
    return {
        'cpus': [
            {
                'name': cpu.name,
                'price': str(cpu.price),
                'core_count': cpu.core_count,
                'core_clock': str(cpu.core_clock),
                'boost_clock': str(cpu.boost_clock),
                'tdp': cpu.tdp,
                'graphics': cpu.graphics,
                'smt': cpu.smt
            }
            for cpu in cpus.items
        ],
        'has_prev': cpus.has_prev,
        'has_next': cpus.has_next,
        'page': cpus.page,
        'pages': cpus.pages
    }

@app.route('/api/power_supply')
@login_required
def power_supply_api():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.select(PowerSupply).distinct(PowerSupply.name).order_by(PowerSupply.name)  # Ensure distinct power supplies
    power_supplies = db.paginate(query, page=page, per_page=per_page, error_out=False)

    return {
        'power_supplies': [
            {
                'name': ps.name,
                'price': str(ps.price),
                'type': ps.type or 'N/A',
                'efficiency': ps.efficiency or 'N/A',
                'wattage': ps.wattage,
                'modular': ps.modular or 'N/A',
                'color': ps.color or 'N/A'
            }
            for ps in power_supplies.items
        ],
        'has_prev': power_supplies.has_prev,
        'has_next': power_supplies.has_next,
        'page': power_supplies.page,
        'pages': power_supplies.pages
    }

@app.route('/api/mouse')
@login_required
def mouse_api():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.select(Mouse).distinct(Mouse.name).order_by(Mouse.name)  # Ensure distinct mice
    mice = db.paginate(query, page=page, per_page=per_page, error_out=False)

    return {
        'mice': [
            {
                'name': mouse.name,
                'price': str(mouse.price),
                'tracking_method': mouse.tracking_method or 'N/A',
                'connection_type': mouse.connection_type or 'N/A',
                'max_dpi': mouse.max_dpi or 'N/A',
                'hand_orientation': mouse.hand_orientation or 'N/A',
                'color': mouse.color or 'N/A'
            }
            for mouse in mice.items
        ],
        'has_prev': mice.has_prev,
        'has_next': mice.has_next,
        'page': mice.page,
        'pages': mice.pages
    }


@app.route('/api/memory')
@login_required
def memory_api():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.select(Memory).distinct(Memory.name).order_by(Memory.name)  # Ensuring distinct memories
    memories = db.paginate(query, page=page, per_page=per_page, error_out=False)
    
    return {
        'memories': [
            {
                'name': memory.name,
                'price': str(memory.price),
                'speed_min': memory.speed_min,
                'speed_max': memory.speed_max,
                'module_count': memory.module_count,
                'module_size': memory.module_size,
                'price_per_gb': str(memory.price_per_gb),
                'color': memory.color or 'N/A',
                'first_word_latency': memory.first_word_latency or 'N/A',
                'cas_latency': memory.cas_latency or 'N/A'
            }
            for memory in memories.items
        ],
        'has_prev': memories.has_prev,
        'has_next': memories.has_next,
        'page': memories.page,
        'pages': memories.pages
    }


@app.route('/api/coolers')
@login_required
def coolers_api():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.select(CPUCoolers).distinct(CPUCoolers.name).order_by(CPUCoolers.name)  # Ensuring distinct coolers
    coolers = db.paginate(query, page=page, per_page=per_page, error_out=False)
    
    return {
        'coolers': [
            {
                'name': cooler.name,
                'price': str(cooler.price),
                'rpm': cooler.rpm,  # RPM is an array
                'noise_level': cooler.noise_level,  # Noise level is also an array
                'color': cooler.color,
                'size': cooler.size
            }
            for cooler in coolers.items
        ],
        'has_prev': coolers.has_prev,
        'has_next': coolers.has_next,
        'page': coolers.page,
        'pages': coolers.pages
    }

@app.route('/api/video_cards')
@login_required
def video_cards_api():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.select(VideoCard).distinct(VideoCard.name).order_by(VideoCard.name)  # Ensuring distinct video cards
    video_cards = db.paginate(query, page=page, per_page=per_page, error_out=False)
    
    return {
        'video_cards': [
            {
                'name': video_card.name,
                'price': str(video_card.price),
                'chipset': video_card.chipset,
                'memory': video_card.memory,
                'core_clock': video_card.core_clock,
                'boost_clock': video_card.boost_clock,
                'color': video_card.color,
                'length': video_card.length
            }
            for video_card in video_cards.items
        ],
        'has_prev': video_cards.has_prev,
        'has_next': video_cards.has_next,
        'page': video_cards.page,
        'pages': video_cards.pages
    }

@app.route('/api/internal_hard_drives')
@login_required
def internal_hard_drives_api():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.select(InternalHardDrive).distinct(InternalHardDrive.name).order_by(InternalHardDrive.name)  # Ensuring distinct internal hard drives
    internal_hard_drives = db.paginate(query, page=page, per_page=per_page, error_out=False)
    
    return {
        'internal_hard_drives': [
            {
                'name': drive.name,
                'price': str(drive.price),
                'capacity': drive.capacity,
                'price_per_gb': str(drive.price_per_gb),
                'tipe': drive.tipe,
                'form_factor': drive.form_factor,
                'interface': drive.interface,
                'cache': drive.cache
            }
            for drive in internal_hard_drives.items
        ],
        'has_prev': internal_hard_drives.has_prev,
        'has_next': internal_hard_drives.has_next,
        'page': internal_hard_drives.page,
        'pages': internal_hard_drives.pages
    }

@app.route('/api/keyboard')
@login_required
def keyboard_api():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.select(Keyboard).distinct(Keyboard.name).order_by(Keyboard.name)  # Ensuring distinct keyboards
    keyboards = db.paginate(query, page=page, per_page=per_page, error_out=False)
    
    return {
        'keyboards': [
            {
                'name': keyboard.name,
                'price': str(keyboard.price),
                'style': keyboard.style,
                'switches': keyboard.switches,
                'backlit': keyboard.backlit,
                'tenkeyless': keyboard.tenkeyless,
                'connection_type': keyboard.connection_type,
                'color': keyboard.color
            }
            for keyboard in keyboards.items
        ],
        'has_prev': keyboards.has_prev,
        'has_next': keyboards.has_next,
        'page': keyboards.page,
        'pages': keyboards.pages
    }

@app.route('/api/headphones') 
@login_required
def headphones_api():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.select(Headphones).distinct(Headphones.name).order_by(Headphones.name)  # Ensure distinct headphones
    headphones = db.paginate(query, page=page, per_page=per_page, error_out=False)
    
    return {
        'headphones': [
            {
                'name': headphones.name,
                'price': str(headphones.price),
                'type': headphones.type or 'N/A',
                'frequency_response': headphones.frequency_response,
                'microphone': headphones.microphone,
                'wireless': headphones.wireless,
                'enclosure_type': headphones.enclosure_type or 'N/A',
                'color': headphones.color or 'N/A'
            }
            for headphones in headphones.items
        ],
        'has_prev': headphones.has_prev,
        'has_next': headphones.has_next,
        'page': headphones.page,
        'pages': headphones.pages
    }

@app.route('/api/motherboard')
@login_required
def motherboard_api():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.select(Motherboard).distinct(Motherboard.name).order_by(Motherboard.name)  # Ensure distinct motherboards
    motherboards = db.paginate(query, page=page, per_page=per_page, error_out=False)

    return {
        'motherboards': [
            {
                'name': motherboard.name,
                'price': str(motherboard.price),
                'socket': motherboard.socket or 'N/A',
                'form_factor': motherboard.form_factor or 'N/A',
                'max_memory': motherboard.max_memory or 'N/A',
                'memory_slots': motherboard.memory_slots or 'N/A',
                'color': motherboard.color or 'N/A'
            }
            for motherboard in motherboards.items
        ],
        'has_prev': motherboards.has_prev,
        'has_next': motherboards.has_next,
        'page': motherboards.page,
        'pages': motherboards.pages
    }


@app.route('/api/monitor')
@login_required
def monitor_api():
    page = request.args.get('page', 1, type=int)
    per_page = 30
    query = db.select(Monitor).distinct(Monitor.name).order_by(Monitor.name)  # Ensure distinct monitors
    monitors = db.paginate(query, page=page, per_page=per_page, error_out=False)

    return {
        'monitors': [
            {
                'name': monitor.name,
                'price': str(monitor.price),
                'screen_size': monitor.screen_size or 'N/A',
                'resolution': f"{monitor.resolution_width} x {monitor.resolution_height}" if monitor.resolution_width and monitor.resolution_height else 'N/A',
                'refresh_rate': monitor.refresh_rate or 'N/A',
                'response_time': str(monitor.response_time) or 'N/A',
                'panel_type': monitor.panel_type or 'N/A',
                'aspect_ratio': monitor.aspect_ratio or 'N/A'
            }
            for monitor in monitors.items
        ],
        'has_prev': monitors.has_prev,
        'has_next': monitors.has_next,
        'page': monitors.page,
        'pages': monitors.pages
    }


@app.route("/lugin") #ni buat google
def lugin():
    authorization_url, state = flow.authorization_url()
    session["state"] = state 
    return redirect(authorization_url)

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.password == hashlib.sha256(password.encode()).hexdigest():
        # Store user info in session
        session['user_id'] = user.id
        return redirect('/dashboard')
    else:
        return jsonify({'message': 'Invalid credentials.'}), 401

@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    # Verify the state parameter for security
    if session.get("state") != request.args.get("state"):
        return "Invalid state parameter", 400  # More informative error message

    credentials = flow.credentials
    request_session = Session()
    cached_sessions = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_sessions)

    try:
        # Verify the Google ID token and extract user info
        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=client_id,
            clock_skew_in_seconds=10
        )
    except ValueError as e:
        # Handle invalid token error
        return f"Invalid token: {str(e)}", 400

    # Extract the Google user information
    google_id = id_info.get("sub")  # Google user ID
    email = id_info.get("email")
    name = id_info.get("name")

    if not google_id or not email:  # Validate required fields
        return "Missing Google account information", 400

    # Check if user exists in the database using oauth_id (google_id)
    user = User.query.filter_by(oauth_id=google_id).first()

    if user is None:
        # Create a new user if not found
        new_user = User(
            email=email,
            username=name,  # You can map name to username if you prefer
            oauth_provider='google',  # Marking the provider as Google
            oauth_id=google_id,  # Storing the Google user ID
            # Optionally, set other fields such as created_at, etc.
        )
        db.session.add(new_user)
        try:
            db.session.commit()  # Commit the new user to the database
            session["user_id"] = new_user.id  # Store new user ID in session
        except Exception as e:
            db.session.rollback()  # Rollback if any error occurs
            return f"Error creating user: {str(e)}", 500
    else:
        # Existing user, store their ID in session
        session["user_id"] = user.id

    # Store additional session info
    session["google_id"] = google_id
    session["name"] = name

    # Redirect to dashboard instead of the protected area
    return redirect("/dashboard")

@app.route('/logout')
@login_required
def logout():
    # Clear the user session
    session.pop('user_id', None)  # Remove the user ID from the session
    return redirect('/logins')  # Redirect to the login page or homepage

@app.route('/cpu')
@login_required
def cpu_list():
    return render_template('cpu.html')

@app.route('/services')
@login_required
def services():
    return render_template('service.html')

@app.route('/wishlist/view')
@login_required
def wishlist():
    return render_template('wishlist.html')

@app.route('/compare')
@login_required
def compare():
    return render_template('compare.html')

@app.route('/prebuilts')
@login_required
def prebuilts():
    return render_template('spek_komputer.html')

@app.route('/test')
def a_list():
    return render_template('a.html')

@app.route('/mouse')
@login_required
def mouse_list():
    return render_template('mouse.html')

@app.route('/monitor')
@login_required
def monitor_list():
    return render_template('monitor.html')

@app.route('/motherboard')
@login_required
def motherboard_list():
    return render_template('motherboard.html')

@app.route('/sharing')
@login_required
def share_list():
    return render_template('sharing.html')

@app.route('/psu')
@login_required
def psu_list():
    return render_template('psu.html')

@app.route('/headphones')
@login_required
def headphones_list():
    return render_template('headphones.html')

@app.route('/prebuilt')
@login_required
def prebuilt():
    return render_template('spek_komputer.html')

@app.route('/coolers')
@login_required
def coolers_list():
    return render_template('coolers.html')

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user_list():
    # Simulate user session data (this should be set when the user logs in)
    if 'email' not in session:
        session['email'] = 'user@example.com'
        session['name'] = ''
        session['address'] = ''
        session['city'] = ''
        session['country'] = ''
        session['state'] = ''
        session['zipcode'] = ''

    if request.method == 'POST':
        # Update editable fields
        session['address'] = request.form.get('address', session.get('address', ''))
        session['city'] = request.form.get('city', session.get('city', ''))
        session['country'] = request.form.get('country', session.get('country', ''))
        session['state'] = request.form.get('state', session.get('state', ''))
        session['zipcode'] = request.form.get('zipcode', session.get('zipcode', ''))

        return redirect('/user')

    # Pass session data to the template
    return render_template(
        'user.html',
        email=session.get('email'),
        username=session.get('name'),
        address=session.get('address'),
        city=session.get('city'),
        country=session.get('country'),
        state=session.get('state'),
        zipcode=session.get('zipcode'),
    )


@app.route('/gpu')
@login_required
def gpu_list():
    return render_template('gpu.html')

@app.route('/ssd')
@login_required
def ssd_list():
    return render_template('ssd.html')

@app.route('/keyboard')
@login_required
def keyboard_list():
    return render_template('keyboard.html')

@app.route('/ram')
@login_required
def memory_list():
    return render_template('memory.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/trynow')
@login_required
def input():
    return render_template('input.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/logins')
def logins():
    return render_template('logins.html')

@app.route('/forgot')
def forgotpass():
    return render_template('forgotpass.html')

@app.route('/sign')
def sign():
    return render_template('signup.html')

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    user_input = request.json.get('input', '').strip().lower()
    
    # Default response for unrecognized input
    response = {"message": "I didn't understand that. Please specify a PC type and budget."}
    
    # Check for budget in user input
    budget_match = re.search(r'(\d+)(k|K)?\s*(usd|\$|bucks)?', user_input)
    budget = 0
    if budget_match:
        amount = budget_match.group(1)
        multiplier = 1000 if budget_match.group(2) else 1
        budget = int(amount) * multiplier

    # Check for PC type
    pc_type = None
    if "build" in user_input or "pc" in user_input:
        if "gaming" in user_input:
            pc_type = "gaming"
        elif "editing" in user_input:
            pc_type = "editing"
        elif "office" in user_input:
            pc_type = "office"

    # If both a budget and PC type are found, call the appropriate build logic
    if budget > 0 and pc_type:
        if pc_type == "gaming":
            gaming_build_response = get_gaming_build(budget)  # Call gaming build logic
            if isinstance(gaming_build_response, dict) and "Build Type" in gaming_build_response:
                response = {
                    "Build Type": gaming_build_response.get('Build Type', 'N/A'),
                    "Total Price": float(gaming_build_response.get('Total Price', 0)),
                    "Components": {
                        category: {
                            "name": component.get('name', 'N/A'),
                            "price": float(component.get('price', 0))
                        } for category, component in gaming_build_response.get("Components", {}).items()
                    }
                }
            else:
                response = {"message": "Unable to generate the gaming build. Please try again."}

        elif pc_type == "office":
            office_build_response = get_office_build(budget)
            if isinstance(office_build_response, dict) and "Build Type" in office_build_response:
                response = {
                    "Build Type": office_build_response.get('Build Type', 'N/A'),
                    "Total Price": float(office_build_response.get('Total Price', 0)),
                    "Components": {
                        category: {
                            "name": component.get('name', 'N/A'),
                            "price": float(component.get('price', 0))
                        } for category, component in office_build_response.get("Components", {}).items()
                    }
                }
            else:
                response = {"message": "Unable to generate the office build. Please try again."}

        elif pc_type == "editing":
            editing_build_response = get_editing_build(budget)
            if isinstance(editing_build_response, dict) and "Build Type" in editing_build_response:
                response = {
                    "Build Type": editing_build_response.get('Build Type', 'N/A'),
                    "Total Price": float(editing_build_response.get('Total Price', 0)),
                    "Components": {
                        category: {
                            "name": component.get('name', 'N/A'),
                            "price": float(component.get('price', 0))
                        } for category, component in editing_build_response.get("Components", {}).items()
                    }
                }
            else:
                response = {"message": "Unable to generate the editing build. Please try again."}

    # Custom response for "best group" or similar keywords
    elif "best group" in user_input or "most sigma" in user_input:
        response = {"message": "My creator of course, CoderTampan!"}

    # Return the response as JSON
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True)
