import os
import uuid
import requests
import asyncio
from datetime import datetime
from flask import (
    Flask, render_template, redirect, url_for, request,
    flash, session, send_from_directory
)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Admin, Product, Setting, Testimonial, HeroSlide
from dotenv import load_dotenv

# Pyrogram untuk MTProto
from pyrogram import Client
from pyrogram.types import InputMediaPhoto
from pyrogram.errors import RPCError

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gantilah-ini-dengan-kunci-rahasia-kuat')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

UPLOAD_PRODUCTS = os.path.join(app.config['UPLOAD_FOLDER'], 'products')
UPLOAD_LOGO = os.path.join(app.config['UPLOAD_FOLDER'], 'logo')
UPLOAD_HERO = os.path.join(app.config['UPLOAD_FOLDER'], 'hero')
UPLOAD_TESTIMONIAL = os.path.join(app.config['UPLOAD_FOLDER'], 'testimonials')
for folder in [UPLOAD_PRODUCTS, UPLOAD_LOGO, UPLOAD_HERO, UPLOAD_TESTIMONIAL]:
    os.makedirs(folder, exist_ok=True)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not Admin.query.first():
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin default: admin / admin123")

# ==================== SETTINGS HELPER ====================
def get_setting(key, default=None):
    setting = Setting.query.filter_by(key=key).first()
    return setting.value if setting else default

# ==================== MULTI BAHASA ====================
TRANSLATIONS = {
    'en': {
        'home': 'Home',
        'catalog': 'Catalog',
        'about': 'About',
        'contact': 'Contact',
        'cart': 'Cart',
        'dashboard': 'Dashboard',
        'logout': 'Logout',
        'login': 'Login',
        'featured_products': 'Featured Products',
        'new_arrivals': 'New Arrivals',
        'view_catalog': 'View Catalog',
        'add_to_cart': 'Add to Cart',
        'buy_whatsapp': 'Buy via WhatsApp',
        'description': 'Description',
        'stock': 'Stock',
        'condition': 'Condition',
        'related_products': 'Related Products',
        'total': 'Total',
        'checkout': 'Proceed to Checkout',
        'empty_cart': 'Your cart is empty',
        'start_shopping': 'Start Shopping',
        'filter': 'Filter',
        'brand': 'Brand',
        'all': 'All',
        'contact_us': 'Contact Us',
        'address': 'Address',
        'email': 'Email',
        'phone': 'Phone',
        'about_us': 'About Us',
        'our_story': 'Our Story',
        'operating_hours': 'Operating Hours',
        'follow_us': 'Follow Us',
        'newsletter': 'Newsletter',
        'your_email': 'Your email',
        'subscribe': 'Subscribe',
        'copyright': '© 2025 Handphone Second. All rights reserved.',
        'checkout_title': 'Checkout',
        'full_name': 'Full Name',
        'phone_number': 'Phone Number',
        'shipping_address': 'Shipping Address',
        'order_summary': 'Order Summary',
        'place_order': 'Place Order',
        'order_success': 'Your order has been placed successfully! We will contact you soon.',
        'what_our_customers_say': 'What Our Customers Say',
        'settings': 'Settings',
        'hero_slider': 'Hero Slider',
        'testimonials': 'Testimonials',
        'add_new': 'Add New',
        'edit': 'Edit',
        'delete': 'Delete',
        'save': 'Save',
        'cancel': 'Cancel',
        'active': 'Active',
        'inactive': 'Inactive',
        'order': 'Order',
        'image': 'Image',
        'title': 'Title',
        'subtitle': 'Subtitle',
        'button_text': 'Button Text',
        'button_url': 'Button URL',
        'name': 'Name',
        'location': 'Location',
        'rating': 'Rating',
        'text': 'Text',
        'site_name': 'Site Name',
        'logo': 'Logo',
        'telegram_bot_token': 'Telegram Bot Token',
        'telegram_chat_id': 'Telegram Chat ID',
        'telegram_api_id': 'Telegram API ID',
        'telegram_api_hash': 'Telegram API Hash',
        'telegram_phone': 'Telegram Phone Number',
        'telegram_session_string': 'Telegram Session String',
        'telegram_group_link': 'Telegram Group Invite Link',
        'settings_updated': 'Settings updated successfully',
        'currency': 'Currency',
        'price': 'Price',
        'clear_all': 'Clear All',
        'grid': 'Grid',
        'list': 'List',
        'products': 'Products',
        'all_products': 'All Products',
        'in_stock': 'In Stock',
        'sort_by': 'Sort by',
        'newest': 'Newest',
        'price_low_high': 'Price: Low to High',
        'price_high_low': 'Price: High to Low',
        'apply': 'Apply',
    },
    'id': {
        'home': 'Beranda',
        'catalog': 'Katalog',
        'about': 'Tentang',
        'contact': 'Kontak',
        'cart': 'Keranjang',
        'dashboard': 'Dasbor',
        'logout': 'Keluar',
        'login': 'Masuk',
        'featured_products': 'Produk Unggulan',
        'new_arrivals': 'Baru Ditambahkan',
        'view_catalog': 'Lihat Katalog',
        'add_to_cart': 'Tambah ke Keranjang',
        'buy_whatsapp': 'Beli via WhatsApp',
        'description': 'Deskripsi',
        'stock': 'Stok',
        'condition': 'Kondisi',
        'related_products': 'Produk Terkait',
        'total': 'Total',
        'checkout': 'Lanjut ke Checkout',
        'empty_cart': 'Keranjang belanja Anda kosong',
        'start_shopping': 'Mulai Belanja',
        'filter': 'Filter',
        'brand': 'Merek',
        'all': 'Semua',
        'contact_us': 'Hubungi Kami',
        'address': 'Alamat',
        'email': 'Email',
        'phone': 'Telepon',
        'about_us': 'Tentang Kami',
        'our_story': 'Cerita Kami',
        'operating_hours': 'Jam Operasional',
        'follow_us': 'Ikuti Kami',
        'newsletter': 'Buletin',
        'your_email': 'Email Anda',
        'subscribe': 'Langganan',
        'copyright': '© 2025 Handphone Second. Hak cipta dilindungi.',
        'checkout_title': 'Checkout',
        'full_name': 'Nama Lengkap',
        'phone_number': 'Nomor Telepon',
        'shipping_address': 'Alamat Pengiriman',
        'order_summary': 'Ringkasan Pesanan',
        'place_order': 'Buat Pesanan',
        'order_success': 'Pesanan Anda berhasil dibuat! Kami akan segera menghubungi Anda.',
        'what_our_customers_say': 'Kata Pelanggan Kami',
        'settings': 'Pengaturan',
        'hero_slider': 'Slider Hero',
        'testimonials': 'Testimoni',
        'add_new': 'Tambah Baru',
        'edit': 'Edit',
        'delete': 'Hapus',
        'save': 'Simpan',
        'cancel': 'Batal',
        'active': 'Aktif',
        'inactive': 'Tidak Aktif',
        'order': 'Urutan',
        'image': 'Gambar',
        'title': 'Judul',
        'subtitle': 'Subjudul',
        'button_text': 'Teks Tombol',
        'button_url': 'URL Tombol',
        'name': 'Nama',
        'location': 'Lokasi',
        'rating': 'Penilaian',
        'text': 'Teks',
        'site_name': 'Nama Situs',
        'logo': 'Logo',
        'telegram_bot_token': 'Token Bot Telegram',
        'telegram_chat_id': 'ID Chat Telegram',
        'telegram_api_id': 'ID API Telegram',
        'telegram_api_hash': 'Hash API Telegram',
        'telegram_phone': 'Nomor Telepon Telegram',
        'telegram_session_string': 'String Sesi Telegram',
        'telegram_group_link': 'Tautan Undangan Grup Telegram',
        'settings_updated': 'Pengaturan berhasil diperbarui',
        'currency': 'Mata Uang',
        'price': 'Harga',
        'clear_all': 'Hapus Semua',
        'grid': 'Grid',
        'list': 'Daftar',
        'products': 'Produk',
        'all_products': 'Semua Produk',
        'in_stock': 'Tersedia',
        'sort_by': 'Urutkan',
        'newest': 'Terbaru',
        'price_low_high': 'Harga: Rendah ke Tinggi',
        'price_high_low': 'Harga: Tinggi ke Rendah',
        'apply': 'Terapkan',
    }
}

def get_text(key):
    lang = session.get('lang', 'en')
    return TRANSLATIONS.get(lang, {}).get(key, key)

app.jinja_env.globals.update(_=get_text)

@app.context_processor
def inject_global_settings():
    return {
        'site_name': get_setting('site_name', 'Handphone Second'),
        'logo_url': get_setting('logo_url'),
        'testimonials': Testimonial.query.filter_by(is_active=True).order_by(Testimonial.order).all(),
        'hero_slides': HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.order).all()
    }

@app.route('/lang/<lang>')
def set_language(lang):
    if lang in ['en', 'id']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

# ==================== FORMAT HARGA ====================
def format_price(price_in_cents):
    """Format harga dalam Rupiah (integer dalam sen)"""
    rupiah = price_in_cents / 100
    return f"Rp {rupiah:,.0f}".replace(',', '.')

app.jinja_env.globals.update(format_price=format_price)

# ==================== TELEGRAM BOT (DENGAN ERROR HANDLING) ====================
def send_telegram_message(message):
    """
    Mengirim pesan teks ke Telegram.
    Mengembalikan tuple (success, error_message)
    """
    bot_token = get_setting('telegram_bot_token')
    chat_id = get_setting('telegram_chat_id')
    if not bot_token or not chat_id:
        error_msg = "Token bot atau Chat ID belum diatur di pengaturan."
        print(error_msg)
        return False, error_msg

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            return True, "OK"
        else:
            error_msg = f"Telegram API error (HTTP {r.status_code}): {r.text}"
            print(error_msg)
            return False, error_msg
    except requests.exceptions.Timeout:
        error_msg = "Koneksi timeout ke API Telegram."
        print(error_msg)
        return False, error_msg
    except requests.exceptions.ConnectionError:
        error_msg = "Gagal terhubung ke API Telegram. Periksa koneksi internet."
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error tidak dikenal: {str(e)}"
        print(error_msg)
        return False, error_msg

def send_telegram_media_group(media_list, chat_id=None):
    """
    Mengirim grup media (foto) ke Telegram.
    Mengembalikan tuple (success, error_message)
    """
    bot_token = get_setting('telegram_bot_token')
    if not bot_token:
        return False, "Token bot tidak ditemukan."
    if not chat_id:
        chat_id = get_setting('telegram_chat_id')
    if not chat_id:
        return False, "Chat ID tidak ditemukan."

    url = f"https://api.telegram.org/bot{bot_token}/sendMediaGroup"
    payload = {
        'chat_id': chat_id,
        'media': media_list
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            return True, "OK"
        else:
            error_msg = f"Telegram API error (HTTP {r.status_code}): {r.text}"
            print(error_msg)
            return False, error_msg
    except Exception as e:
        error_msg = f"Error saat mengirim media group: {str(e)}"
        print(error_msg)
        return False, error_msg

# ==================== TELEGRAM MTPROTO ====================
mtproto_client = None

def get_mtproto_client():
    global mtproto_client
    if mtproto_client is not None:
        return mtproto_client
    api_id = get_setting('telegram_api_id')
    api_hash = get_setting('telegram_api_hash')
    session_string = get_setting('telegram_session_string')
    if not api_id or not api_hash or not session_string:
        return None
    try:
        mtproto_client = Client(
            name="mtproto_session",
            api_id=int(api_id),
            api_hash=api_hash,
            session_string=session_string,
            in_memory=True
        )
        return mtproto_client
    except Exception as e:
        print(f"MTProto client error: {e}")
        return None

async def send_mtproto_media_group(chat_id, media_list):
    client = get_mtproto_client()
    if not client:
        return False
    try:
        await client.start()
        await client.send_media_group(
            chat_id=chat_id,
            media=media_list
        )
        await client.stop()
        return True
    except RPCError as e:
        print(f"MTProto send error: {e}")
        return False
    except Exception as e:
        print(f"MTProto error: {e}")
        return False

def send_product_notification(product, action='new'):
    """Kirim notifikasi produk via MTProto jika tersedia, fallback ke bot"""
    caption_lines = []
    if action == 'new':
        caption_lines.append("<b>🆕 Produk Baru Ditambahkan!</b>\n")
    else:
        caption_lines.append("<b>✏️ Produk Diperbarui!</b>\n")
    
    caption_lines.append(f"<b>Nama:</b> {product.name}")
    caption_lines.append(f"<b>Merek:</b> {product.brand}")
    if product.model:
        caption_lines.append(f"<b>Model:</b> {product.model}")
    caption_lines.append(f"<b>Harga:</b> {format_price(product.price)}")
    if product.condition:
        caption_lines.append(f"<b>Kondisi:</b> {product.condition}")
    caption_lines.append(f"<b>Stok:</b> {product.stock}")
    if product.description:
        short_desc = product.description[:200] + "..." if len(product.description) > 200 else product.description
        caption_lines.append(f"\n{short_desc}")
    
    product_url = url_for('product_detail', id=product.id, _external=True)
    caption_lines.append(f"\n<a href='{product_url}'>🔗 Lihat Produk</a>")
    
    full_caption = "\n".join(caption_lines)

    # Kumpulkan gambar
    img_fields = ['image_filename', 'image_filename2', 'image_filename3', 'image_filename4']
    media_urls = []
    for field in img_fields:
        img = getattr(product, field)
        if img:
            img_url = url_for('uploaded_product_file', filename=img, _external=True)
            media_urls.append(img_url)
    
    if not media_urls:
        return send_telegram_message(full_caption)[0]  # hanya return boolean
    
    chat_id_str = get_setting('telegram_chat_id')
    if not chat_id_str:
        return False
    try:
        chat_id = int(chat_id_str)
    except:
        chat_id = chat_id_str

    media_list = []
    for i, url in enumerate(media_urls):
        if i == 0:
            media_list.append(InputMediaPhoto(media=url, caption=full_caption, parse_mode='html'))
        else:
            media_list.append(InputMediaPhoto(media=url))
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(send_mtproto_media_group(chat_id, media_list))
        if success:
            return True
    except Exception as e:
        print(f"MTProto failed, falling back to bot: {e}")
    
    bot_media_list = []
    for i, url in enumerate(media_urls):
        item = {'type': 'photo', 'media': url}
        if i == 0:
            item['caption'] = full_caption
            item['parse_mode'] = 'HTML'
        bot_media_list.append(item)
    success, _ = send_telegram_media_group(bot_media_list, chat_id_str)
    return success

# ==================== HALAMAN PUBLIK ====================
@app.route('/')
def index():
    brand = request.args.get('brand')
    query = Product.query
    if brand and brand != 'all':
        query = query.filter_by(brand=brand)
    products = query.order_by(Product.created_at.desc()).all()
    brands = db.session.query(Product.brand).distinct().all()
    brands = [b[0] for b in brands]
    featured = Product.query.filter_by(is_featured=True).limit(6).all()
    recent = Product.query.order_by(Product.created_at.desc()).limit(8).all()
    return render_template(
        'index.html',
        featured=featured,
        recent=recent,
        products=products,
        brands=brands
    )

@app.route('/catalog')
def catalog():
    brand = request.args.get('brand')
    query = Product.query
    if brand:
        query = query.filter_by(brand=brand)
    products = query.order_by(Product.created_at.desc()).all()
    brands = db.session.query(Product.brand).distinct().all()
    brands = [b[0] for b in brands]
    return render_template('catalog.html', products=products, brands=brands)

@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    related = Product.query.filter(Product.brand == product.brand, Product.id != id).limit(4).all()
    return render_template('product.html', product=product, related=related)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ==================== KERANJANG ====================
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total = 0
    for item in cart_items:
        total += item['price'] * item['quantity']
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = session.get('cart', [])
    found = False
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += 1
            found = True
            break
    if not found:
        cart.append({
            'product_id': product.id,
            'name': product.name,
            'brand': product.brand,
            'model': product.model,
            'price': product.price,
            'image': product.image_filename,
            'quantity': 1
        })
    session['cart'] = cart
    flash(get_text('add_to_cart'), 'success')
    return redirect(request.referrer or url_for('cart'))

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    cart = session.get('cart', [])
    quantity = int(request.form.get('quantity', 1))
    if quantity < 1:
        quantity = 1
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] = quantity
            break
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart
    flash('Item removed from cart', 'success')
    return redirect(url_for('cart'))

# ==================== CHECKOUT ====================
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart_items = session.get('cart', [])
    if not cart_items:
        flash(get_text('empty_cart'), 'error')
        return redirect(url_for('cart'))

    if request.method == 'POST':
        name = request.form.get('name')
        telegram = request.form.get('telegram')
        email = request.form.get('email')
        address = request.form.get('address')

        if not name or not telegram or not address:
            flash('Harap isi semua field yang wajib', 'error')
            return redirect(url_for('checkout'))

        total = 0
        for item in cart_items:
            total += item['price'] * item['quantity']

        lines = ["<b>🛒 PESANAN BARU DARI HANDPHONE SECOND</b>\n"]
        lines.append(f"<b>Nama:</b> {name}")
        lines.append(f"<b>Telegram:</b> {telegram}")
        if email:
            lines.append(f"<b>Email:</b> {email}")
        lines.append(f"<b>Alamat:</b> {address}\n")
        lines.append("<b>Detail Pesanan:</b>")
        for item in cart_items:
            lines.append(f"{item['name']} - {item['brand']} {item['model']} x {item['quantity']}")
            lines.append(f"  {format_price(item['price'] * item['quantity'])}")
        lines.append(f"\n<b>Total:</b> {format_price(total)}")
        lines.append(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        message = "\n".join(lines)

        success, error_msg = send_telegram_message(message)
        if success:
            session['cart'] = []
            flash(get_text('order_success'), 'success')
            return redirect(url_for('order_success'))
        else:
            flash(f'Gagal mengirim pesanan: {error_msg}', 'error')
            return redirect(url_for('checkout'))

    total = 0
    for item in cart_items:
        total += item['price'] * item['quantity']
    group_link = get_setting('telegram_group_link')
    return render_template('checkout.html', cart_items=cart_items, total=total, telegram_group_link=group_link)

@app.route('/order-success')
def order_success():
    return render_template('order_success.html')

# ==================== ADMIN: DASHBOARD ====================
@app.route('/admin')
@login_required
def admin_index():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    total_products = Product.query.count()
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', total=total_products, recent=recent_products)

# ==================== ADMIN: PRODUCTS ====================
@app.route('/admin/products')
@login_required
def admin_products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)

def save_uploaded_image(file, prefix='', subfolder='products'):
    if file and file.filename:
        filename = secure_filename(file.filename)
        unique = str(uuid.uuid4())[:8]
        new_filename = f"{unique}_{prefix}{filename}"
        folder = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
        file.save(os.path.join(folder, new_filename))
        return new_filename
    return None

@app.route('/admin/product/new', methods=['GET', 'POST'])
@login_required
def admin_product_new():
    if request.method == 'POST':
        name = request.form.get('name')
        brand = request.form.get('brand')
        model = request.form.get('model')
        price = float(request.form.get('price')) * 100  # simpan dalam sen
        condition = request.form.get('condition')
        description = request.form.get('description')
        is_featured = 'is_featured' in request.form
        stock = request.form.get('stock', 1)

        image = request.files.get('image')
        filename = save_uploaded_image(image, 'main_', 'products')
        image2 = request.files.get('image2')
        filename2 = save_uploaded_image(image2, 'img2_', 'products') if image2 else None
        image3 = request.files.get('image3')
        filename3 = save_uploaded_image(image3, 'img3_', 'products') if image3 else None
        image4 = request.files.get('image4')
        filename4 = save_uploaded_image(image4, 'img4_', 'products') if image4 else None

        product = Product(
            name=name, brand=brand, model=model,
            price=int(price),
            condition=condition, description=description,
            is_featured=is_featured, stock=stock,
            image_filename=filename,
            image_filename2=filename2,
            image_filename3=filename3,
            image_filename4=filename4
        )
        db.session.add(product)
        db.session.commit()

        send_product_notification(product, action='new')

        flash('Product added successfully', 'success')
        return redirect(url_for('admin_products'))
    return render_template('admin/product_form.html')

@app.route('/admin/product/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_product_edit(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.brand = request.form.get('brand')
        product.model = request.form.get('model')
        product.price = int(float(request.form.get('price')) * 100)
        product.condition = request.form.get('condition')
        product.description = request.form.get('description')
        product.is_featured = 'is_featured' in request.form
        product.stock = request.form.get('stock', 1)

        def update_image_field(file, field_name, prefix):
            if file and file.filename:
                old = getattr(product, field_name)
                if old:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], 'products', old)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                new_filename = save_uploaded_image(file, prefix, 'products')
                setattr(product, field_name, new_filename)

        update_image_field(request.files.get('image'), 'image_filename', 'main_')
        update_image_field(request.files.get('image2'), 'image_filename2', 'img2_')
        update_image_field(request.files.get('image3'), 'image_filename3', 'img3_')
        update_image_field(request.files.get('image4'), 'image_filename4', 'img4_')

        db.session.commit()

        send_product_notification(product, action='update')

        flash('Product updated', 'success')
        return redirect(url_for('admin_products'))

    product.price_display = product.price / 100
    return render_template('admin/product_form.html', product=product)

@app.route('/admin/product/delete/<int:id>')
@login_required
def admin_product_delete(id):
    product = Product.query.get_or_404(id)
    for img_field in ['image_filename', 'image_filename2', 'image_filename3', 'image_filename4']:
        img = getattr(product, img_field)
        if img:
            path = os.path.join(app.config['UPLOAD_FOLDER'], 'products', img)
            if os.path.exists(path):
                os.remove(path)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted', 'success')
    return redirect(url_for('admin_products'))

# ==================== ADMIN: SETTINGS ====================
@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if request.method == 'POST':
        site_name = request.form.get('site_name')
        telegram_bot_token = request.form.get('telegram_bot_token')
        telegram_chat_id = request.form.get('telegram_chat_id')
        telegram_api_id = request.form.get('telegram_api_id')
        telegram_api_hash = request.form.get('telegram_api_hash')
        telegram_phone = request.form.get('telegram_phone')
        telegram_session_string = request.form.get('telegram_session_string')
        telegram_group_link = request.form.get('telegram_group_link')

        def update_setting(key, value):
            setting = Setting.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                setting = Setting(key=key, value=value)
                db.session.add(setting)

        update_setting('site_name', site_name)
        update_setting('telegram_bot_token', telegram_bot_token)
        update_setting('telegram_chat_id', telegram_chat_id)
        update_setting('telegram_api_id', telegram_api_id)
        update_setting('telegram_api_hash', telegram_api_hash)
        update_setting('telegram_phone', telegram_phone)
        update_setting('telegram_session_string', telegram_session_string)
        update_setting('telegram_group_link', telegram_group_link)

        logo = request.files.get('logo')
        if logo and logo.filename:
            filename = save_uploaded_image(logo, 'logo_', 'logo')
            if filename:
                old_logo = get_setting('logo_url')
                if old_logo:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], 'logo', old_logo)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                update_setting('logo_url', filename)

        db.session.commit()
        flash(get_text('settings_updated'), 'success')
        return redirect(url_for('admin_settings'))

    settings = {
        'site_name': get_setting('site_name', 'Handphone Second'),
        'telegram_bot_token': get_setting('telegram_bot_token', ''),
        'telegram_chat_id': get_setting('telegram_chat_id', ''),
        'telegram_api_id': get_setting('telegram_api_id', ''),
        'telegram_api_hash': get_setting('telegram_api_hash', ''),
        'telegram_phone': get_setting('telegram_phone', ''),
        'telegram_session_string': get_setting('telegram_session_string', ''),
        'telegram_group_link': get_setting('telegram_group_link', ''),
        'logo_url': get_setting('logo_url', '')
    }
    return render_template('admin/settings.html', settings=settings)

# ==================== ADMIN: HERO SLIDER ====================
@app.route('/admin/hero')
@login_required
def admin_hero():
    slides = HeroSlide.query.order_by(HeroSlide.order).all()
    return render_template('admin/hero_slides.html', slides=slides)

@app.route('/admin/hero/new', methods=['GET', 'POST'])
@login_required
def admin_hero_new():
    if request.method == 'POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        button_text = request.form.get('button_text')
        button_url = request.form.get('button_url')
        order = request.form.get('order', 0)
        is_active = 'is_active' in request.form

        image = request.files.get('image')
        if not image or not image.filename:
            flash('Image is required', 'error')
            return redirect(request.url)

        filename = save_uploaded_image(image, 'hero_', 'hero')

        slide = HeroSlide(
            image_filename=filename,
            title=title,
            subtitle=subtitle,
            button_text=button_text,
            button_url=button_url,
            order=order,
            is_active=is_active
        )
        db.session.add(slide)
        db.session.commit()
        flash('Slide added successfully', 'success')
        return redirect(url_for('admin_hero'))

    return render_template('admin/hero_form.html')

@app.route('/admin/hero/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_hero_edit(id):
    slide = HeroSlide.query.get_or_404(id)
    if request.method == 'POST':
        slide.title = request.form.get('title')
        slide.subtitle = request.form.get('subtitle')
        slide.button_text = request.form.get('button_text')
        slide.button_url = request.form.get('button_url')
        slide.order = request.form.get('order', 0)
        slide.is_active = 'is_active' in request.form

        image = request.files.get('image')
        if image and image.filename:
            if slide.image_filename:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], 'hero', slide.image_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = save_uploaded_image(image, 'hero_', 'hero')
            slide.image_filename = filename

        db.session.commit()
        flash('Slide updated', 'success')
        return redirect(url_for('admin_hero'))

    return render_template('admin/hero_form.html', slide=slide)

@app.route('/admin/hero/delete/<int:id>')
@login_required
def admin_hero_delete(id):
    slide = HeroSlide.query.get_or_404(id)
    if slide.image_filename:
        path = os.path.join(app.config['UPLOAD_FOLDER'], 'hero', slide.image_filename)
        if os.path.exists(path):
            os.remove(path)
    db.session.delete(slide)
    db.session.commit()
    flash('Slide deleted', 'success')
    return redirect(url_for('admin_hero'))

# ==================== ADMIN: TESTIMONIALS ====================
@app.route('/admin/testimonials')
@login_required
def admin_testimonials():
    testimonials = Testimonial.query.order_by(Testimonial.order).all()
    return render_template('admin/testimonials.html', testimonials=testimonials)

@app.route('/admin/testimonial/new', methods=['GET', 'POST'])
@login_required
def admin_testimonial_new():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        rating = request.form.get('rating', 5)
        text = request.form.get('text')
        order = request.form.get('order', 0)
        is_active = 'is_active' in request.form

        image = request.files.get('image')
        filename = None
        if image and image.filename:
            filename = secure_filename(image.filename)
            unique = str(uuid.uuid4())[:8]
            filename = f"{unique}_{filename}"
            image.save(os.path.join(UPLOAD_TESTIMONIAL, filename))

        testimonial = Testimonial(
            name=name,
            location=location,
            rating=int(rating),
            text=text,
            image_filename=filename,
            order=int(order),
            is_active=is_active
        )
        db.session.add(testimonial)
        db.session.commit()
        flash('Testimonial added successfully', 'success')
        return redirect(url_for('admin_testimonials'))

    return render_template('admin/testimonial_form.html')

@app.route('/admin/testimonial/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_testimonial_edit(id):
    testimonial = Testimonial.query.get_or_404(id)
    if request.method == 'POST':
        testimonial.name = request.form.get('name')
        testimonial.location = request.form.get('location')
        testimonial.rating = int(request.form.get('rating', 5))
        testimonial.text = request.form.get('text')
        testimonial.order = int(request.form.get('order', 0))
        testimonial.is_active = 'is_active' in request.form

        image = request.files.get('image')
        if image and image.filename:
            if testimonial.image_filename:
                old_path = os.path.join(UPLOAD_TESTIMONIAL, testimonial.image_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            filename = secure_filename(image.filename)
            unique = str(uuid.uuid4())[:8]
            filename = f"{unique}_{filename}"
            image.save(os.path.join(UPLOAD_TESTIMONIAL, filename))
            testimonial.image_filename = filename

        db.session.commit()
        flash('Testimonial updated', 'success')
        return redirect(url_for('admin_testimonials'))

    return render_template('admin/testimonial_form.html', testimonial=testimonial)

@app.route('/admin/testimonial/delete/<int:id>')
@login_required
def admin_testimonial_delete(id):
    testimonial = Testimonial.query.get_or_404(id)
    if testimonial.image_filename:
        path = os.path.join(UPLOAD_TESTIMONIAL, testimonial.image_filename)
        if os.path.exists(path):
            os.remove(path)
    db.session.delete(testimonial)
    db.session.commit()
    flash('Testimonial deleted', 'success')
    return redirect(url_for('admin_testimonials'))

# ==================== ADMIN LOGIN/LOGOUT ====================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

# ==================== STATIC FILES ====================
@app.route('/static/uploads/products/<filename>')
def uploaded_product_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), filename)

@app.route('/static/uploads/logo/<filename>')
def uploaded_logo_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'logo'), filename)

@app.route('/static/uploads/hero/<filename>')
def uploaded_hero_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'hero'), filename)

@app.route('/static/uploads/testimonials/<filename>')
def uploaded_testimonial_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'testimonials'), filename)

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)