@app.route('/')
def index():
    featured = Product.query.filter_by(is_featured=True).limit(6).all()
    recent = Product.query.order_by(Product.created_at.desc()).limit(8).all()
    return render_template('index.html', featured=featured, recent=recent)

@app.route('/catalog')
def catalog():
    brand = request.args.get('brand')
    query = Product.query
    if brand:
        query = query.filter_by(brand=brand)
    products = query.order_by(Product.created_at.desc()).all()
    brands = db.session.query(Product.brand).distinct().all()
    return render_template('catalog.html', products=products, brands=[b[0] for b in brands])

@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    related = Product.query.filter(Product.brand == product.brand, Product.id != id).limit(4).all()
    return render_template('product.html', product=product, related=related)