from models import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    oauth_provider = db.Column(db.String(50), nullable=True)
    oauth_id = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    zipcode = db.Column(db.String(20), nullable=True)

    # Relasi dengan Review
    reviews = db.relationship('Review', back_populates='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

    
class CPU(db.Model):
    __tablename__ = 'cpu'  # Nama tabel di database

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    core_count = db.Column(db.Integer, nullable=False)
    core_clock = db.Column(db.Numeric(5, 2), nullable=False)
    boost_clock = db.Column(db.Numeric(5, 2), nullable=True)  # Optional field
    tdp = db.Column(db.Integer, nullable=False)
    graphics = db.Column(db.String(255), nullable=True)  # Optional field
    smt = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<CPU {self.name}>'
    
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
        }


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relasi ke User
    user = db.relationship('User', back_populates='reviews')

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
class Headphones(db.Model):
    __tablename__ = 'headphones'  # Name of the table in the database

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(50), nullable=True)  # Optional field
    frequency_response = db.Column(db.ARRAY(db.Integer), nullable=False)  # Not nullable
    microphone = db.Column(db.Boolean, nullable=False)
    wireless = db.Column(db.Boolean, nullable=False)
    enclosure_type = db.Column(db.String(50), nullable=True)  # Optional field
    color = db.Column(db.String(50), nullable=True)  # Optional field

    def __repr__(self):
        return f'<Headphones {self.name}>'

    
class Memory(db.Model):
    __tablename__ = 'memory'  # Name of the table in the database

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    speed_min = db.Column(db.Integer, nullable=True)  # Optional field
    speed_max = db.Column(db.Integer, nullable=True)  # Optional field
    module_count = db.Column(db.Integer, nullable=True)  # Optional field
    module_size = db.Column(db.Integer, nullable=True)  # Optional field, e.g., in GB
    price_per_gb = db.Column(db.Numeric(10, 5), nullable=True)  # Optional field
    color = db.Column(db.String(50), nullable=True)  # Optional field
    first_word_latency = db.Column(db.Integer, nullable=True)  # Optional field
    cas_latency = db.Column(db.Integer, nullable=True)  # Optional field

    def __repr__(self):
        return f'<Memory {self.name}>'

class CPUCoolers(db.Model):
    __tablename__ = 'cpu_coolers'  # Nama tabel di database

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    rpm = db.Column(db.ARRAY(db.Integer), nullable=False)  # RPM stored as array
    noise_level = db.Column(db.ARRAY(db.Numeric(5, 2)), nullable=False)  # Noise levels stored as array
    color = db.Column(db.String(50), nullable=True)  # Optional field
    size = db.Column(db.Integer, nullable=True)  # Optional field

    def __repr__(self):
        return f'<CPUCooler {self.name}>'


class VideoCard(db.Model):
    __tablename__ = 'video_card'  # Table name in the database

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    chipset = db.Column(db.String(100), nullable=True)  # Optional field
    memory = db.Column(db.Integer, nullable=True)  # Optional field
    core_clock = db.Column(db.Integer, nullable=True)  # Optional field
    boost_clock = db.Column(db.Integer, nullable=True)  # Optional field
    color = db.Column(db.String(50), nullable=True)  # Optional field
    length = db.Column(db.Integer, nullable=True)  # Optional field

    def __repr__(self):
        return f'<VideoCard {self.name}>'
    
class InternalHardDrive(db.Model):
    __tablename__ = 'internal_hard_drive'  # Table name in the database

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    price_per_gb = db.Column(db.Numeric(10, 5), nullable=False)
    tipe = db.Column(db.String(50), nullable=True)  # Optional
    form_factor = db.Column(db.String(50), nullable=True)  # Optional
    interface = db.Column(db.String(50), nullable=True)  # Optional
    cache = db.Column(db.Integer, nullable=True)  # Optional

    def __repr__(self):
        return f'<InternalHardDrive {self.name}>'

class Keyboard(db.Model):
    __tablename__ = 'keyboard'  # Nama tabel di database

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    style = db.Column(db.String(100), nullable=False)
    switches = db.Column(db.String(100), nullable=False)
    backlit = db.Column(db.Boolean, default=False)
    tenkeyless = db.Column(db.Boolean, default=False)
    connection_type = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=True)  # Optional field

    def __repr__(self):
        return f'<Keyboard {self.name}>'
    
class Monitor(db.Model):
    __tablename__ = 'monitor'  # Name of the table in the database

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    screen_size = db.Column(db.Integer, nullable=True)  # Optional field
    resolution_width = db.Column(db.Integer, nullable=True)  # Optional field
    resolution_height = db.Column(db.Integer, nullable=True)  # Optional field
    refresh_rate = db.Column(db.Integer, nullable=True)  # Optional field
    response_time = db.Column(db.Numeric(10, 1), nullable=True)  # Optional field
    panel_type = db.Column(db.String(50), nullable=True)  # Optional field
    aspect_ratio = db.Column(db.String(10), nullable=True)  # Optional field

    def __repr__(self):
        return f'<Monitor {self.name}>'

class BestSelling(db.Model):
    __tablename__ = 'best_selling_pc_components'  # Sesuai dengan nama tabel di DB

    id = db.Column(db.Integer, primary_key=True)  # ID sebagai primary key
    country = db.Column(db.String(50), nullable=False)  # Kolom country
    best_selling_cpu = db.Column(db.String(100), nullable=False)  # Kolom best_selling_cpu
    best_selling_gpu = db.Column(db.String(100), nullable=False)  # Kolom best_selling_gpu
    best_selling_ram = db.Column(db.String(100), nullable=False)  # Kolom best_selling_ram
    best_selling_ssd = db.Column(db.String(100), nullable=False)  # Kolom best_selling_ssd
    best_selling_psu = db.Column(db.String(100), nullable=False)  # Kolom best_selling_psu

    def __repr__(self):
        return f'<BestSelling {self.country}>'

class Motherboard(db.Model):
    __tablename__ = 'motherboard'  # Name of the table in the database

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    socket = db.Column(db.String(50), nullable=True)  # Optional field
    form_factor = db.Column(db.String(50), nullable=True)  # Optional field
    max_memory = db.Column(db.Integer, nullable=True)  # Optional field
    memory_slots = db.Column(db.Integer, nullable=True)  # Optional field
    color = db.Column(db.String(50), nullable=True)  # Optional field

    def __repr__(self):
        return f'<Motherboard {self.name}>'
    
class Mouse(db.Model):
    __tablename__ = 'mouse'  # Name of the table in the database

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    tracking_method = db.Column(db.String(50), nullable=True)  # Optional field
    connection_type = db.Column(db.String(50), nullable=True)  # Optional field
    max_dpi = db.Column(db.Integer, nullable=True)  # Optional field
    hand_orientation = db.Column(db.String(50), nullable=True)  # Optional field
    color = db.Column(db.String(50), nullable=True)  # Optional field

    def __repr__(self):
        return f'<Mouse {self.name}>'

class PowerSupply(db.Model):
    __tablename__ = 'power_supply'  # Name of the table in the database

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(50), nullable=True)  # Optional field
    efficiency = db.Column(db.String(50), nullable=True)  # Optional field
    wattage = db.Column(db.Integer, nullable=False)  # Required field
    modular = db.Column(db.String(50), nullable=True)  # Optional field
    color = db.Column(db.String(50), nullable=True)  # Optional field

    def __repr__(self):
        return f'<PowerSupply {self.name}>'

class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)