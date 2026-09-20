
from flask import Flask, render_template_string, request, redirect, url_for, send_file, flash
import json, os, io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "shop-management-secret"

SHOP_NAME = "SHREE BHOJ BABA BUILDINGS MATERIALS"
PRODUCT_FILE = "products.json"
SALES_FILE = "sales.json"
LOW_STOCK_LIMIT = 10

def load_products():
    if os.path.exists(PRODUCT_FILE):
        try:
            with open(PRODUCT_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}

def save_products(products):
    with open(PRODUCT_FILE, "w") as f:
        json.dump(products, f, indent=4)

def load_sales():
    if os.path.exists(SALES_FILE):
        try:
            with open(SALES_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []

def save_sales(sales):
    with open(SALES_FILE, "w") as f:
        json.dump(sales, f, indent=4)

products = load_products()
sales = load_sales()

BASE = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} - Shop Management</title>
<style>
body{font-family:Arial,sans-serif;margin:0;background:#f3f4f6;color:#111827}
header{background:#1f2937;color:white;padding:22px;text-align:center}
header h1{margin:0;font-size:25px}
nav{background:white;padding:12px;text-align:center;box-shadow:0 2px 6px #ddd}
nav a{display:inline-block;margin:5px;padding:9px 13px;text-decoration:none;color:#111827;border-radius:6px;background:#e5e7eb}
.container{max-width:1100px;margin:25px auto;padding:0 15px}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:15px}
.card{background:white;padding:20px;border-radius:10px;box-shadow:0 2px 8px #ddd}
.card h3{font-size:13px;margin:0 0 10px;color:#6b7280}
.card p{font-size:25px;font-weight:bold;margin:0}
.box{background:white;padding:20px;border-radius:10px;box-shadow:0 2px 8px #ddd;margin-top:20px}
input,select{padding:10px;width:100%;box-sizing:border-box;margin:6px 0 12px;border:1px solid #d1d5db;border-radius:6px}
button,.btn{background:#1f2937;color:white;border:0;padding:10px 15px;border-radius:6px;text-decoration:none;cursor:pointer}
.danger{background:#b91c1c}.success{background:#166534}
table{width:100%;border-collapse:collapse;background:white}
th,td{padding:10px;border-bottom:1px solid #e5e7eb;text-align:left}
th{background:#f3f4f6}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.alert{padding:12px;background:#fef3c7;border-radius:6px;margin-bottom:15px}
@media(max-width:800px){.cards{grid-template-columns:1fr 1fr}.grid2{grid-template-columns:1fr}table{font-size:13px}}
</style>
</head>
<body>
<header><h1>{{ shop_name }}</h1><div>Web Management System</div></header>
<nav>
<a href="{{ url_for('index') }}">Dashboard</a>
<a href="{{ url_for('products_page') }}">Products</a>
<a href="{{ url_for('add_product') }}">Add Product</a>
<a href="{{ url_for('sell') }}">Sell / Invoice</a>
<a href="{{ url_for('sales_history') }}">Sales History</a>
<a href="{{ url_for('report') }}">Shop Report</a>
</nav>
<div class="container">
{% with messages=get_flashed_messages() %}
{% for m in messages %}<div class="alert">{{m}}</div>{% endfor %}
{% endwith %}
{{ body|safe }}
</div>
</body>
</html>
"""

def page(body, title="Dashboard"):
    return render_template_string(BASE, body=body, title=title, shop_name=SHOP_NAME)

@app.route("/")
def index():
    total_products = len(products)
    total_stock = sum(int(v.get("quantity",0)) for v in products.values())
    total_sales = sum(float(s.get("total",0)) for s in sales)
    low_stock = sum(1 for v in products.values() if int(v.get("quantity",0)) <= LOW_STOCK_LIMIT)
    body = f"""
    <h2>Dashboard</h2>
    <div class="cards">
      <div class="card"><h3>TOTAL PRODUCTS</h3><p>{total_products}</p></div>
      <div class="card"><h3>TOTAL STOCK</h3><p>{total_stock}</p></div>
      <div class="card"><h3>TOTAL SALES</h3><p>Rs. {total_sales:.2f}</p></div>
      <div class="card"><h3>LOW STOCK</h3><p>{low_stock}</p></div>
    </div>
    <div class="box">
      <h3>Quick Actions</h3>
      <a class="btn" href="/add-product">Add Product</a>
      <a class="btn success" href="/sell">Create Invoice</a>
      <a class="btn" href="/products">View Products</a>
    </div>
    """
    return page(body)

@app.route("/products")
def products_page():
    rows = ""
    for name, d in products.items():
        qty = int(d.get("quantity",0)); price = float(d.get("price",0))
        rows += f"""<tr><td>{name}</td><td>{qty}</td><td>Rs. {price:.2f}</td>
        <td><a class="btn" href="/edit/{name}">Edit</a>
        <a class="btn danger" href="/delete/{name}" onclick="return confirm('Delete this product?')">Delete</a></td></tr>"""
    if not rows:
        rows = "<tr><td colspan='4'>No products available.</td></tr>"
    body = f"""<h2>Product Inventory</h2><div class="box"><table>
    <tr><th>Product</th><th>Quantity</th><th>Selling Price</th><th>Action</th></tr>{rows}
    </table></div>"""
    return page(body, "Products")

@app.route("/add-product", methods=["GET","POST"])
def add_product():
    if request.method == "POST":
        name = request.form["name"].strip()
        try:
            qty = int(request.form["quantity"]); price = float(request.form["price"])
            if not name or qty < 0 or price < 0: raise ValueError
        except ValueError:
            flash("Enter valid product name, quantity and price.")
            return redirect(url_for("add_product"))
        existing = next((p for p in products if p.lower()==name.lower()), None)
        if existing:
            products[existing]["quantity"] += qty
            products[existing]["price"] = price
        else:
            products[name] = {"quantity": qty, "price": price}
        save_products(products); flash("Product added successfully!")
        return redirect(url_for("products_page"))
    body = """<h2>Add Product</h2><div class="box"><form method="post">
    <label>Product Name</label><input name="name" required>
    <label>Quantity</label><input name="quantity" type="number" min="0" required>
    <label>Selling Price</label><input name="price" type="number" min="0" step="0.01" required>
    <button>Save Product</button></form></div>"""
    return page(body, "Add Product")

@app.route("/edit/<path:name>", methods=["GET","POST"])
def edit(name):
    if name not in products: return "Product not found", 404
    if request.method == "POST":
        new_name=request.form["name"].strip()
        qty=int(request.form["quantity"]); price=float(request.form["price"])
        if new_name != name and any(p.lower()==new_name.lower() for p in products):
            flash("Another product with this name already exists.")
            return redirect(url_for("edit", name=name))
        products[new_name]={"quantity":qty,"price":price}
        if new_name != name: del products[name]
        save_products(products); flash("Product updated successfully!")
        return redirect(url_for("products_page"))
    d=products[name]
    body=f"""<h2>Edit Product</h2><div class="box"><form method="post">
    <label>Product Name</label><input name="name" value="{name}" required>
    <label>Quantity</label><input name="quantity" type="number" min="0" value="{d.get('quantity',0)}" required>
    <label>Selling Price</label><input name="price" type="number" min="0" step="0.01" value="{d.get('price',0)}" required>
    <button>Save Changes</button></form></div>"""
    return page(body, "Edit Product")

@app.route("/delete/<path:name>")
def delete(name):
    if name in products:
        del products[name]; save_products(products); flash(f"{name} deleted successfully!")
    return redirect(url_for("products_page"))

@app.route("/sell", methods=["GET","POST"])
def sell():
    if request.method == "POST":
        customer=request.form["customer"].strip()
        mobile=request.form["mobile"].strip()
        names=request.form.getlist("product")
        qtys=request.form.getlist("quantity")
        items=[]; total=0
        if not customer or not mobile:
            flash("Customer name and mobile are required."); return redirect(url_for("sell"))
        for name, q in zip(names, qtys):
            if not name: continue
            try: q=int(q)
            except: continue
            if q <= 0 or name not in products: continue
            if q > int(products[name].get("quantity",0)):
                flash(f"Not enough stock for {name}."); return redirect(url_for("sell"))
            price=float(products[name].get("price",0))
            item={"product":name,"quantity":q,"price":price,"total":q*price}
            items.append(item); total += q*price
        if not items:
            flash("Add at least one product."); return redirect(url_for("sell"))
        for item in items: products[item["product"]]["quantity"] -= item["quantity"]
        bill=max([int(s.get("bill_no",0)) for s in sales] or [0])+1
        sale={"bill_no":bill,"date":datetime.now().strftime("%d-%m-%Y %I:%M:%S %p"),
              "customer":customer,"mobile":mobile,"items":items,"total":total}
        sales.append(sale); save_products(products); save_sales(sales)
        flash(f"Sale completed. Bill No: {bill}")
        return redirect(url_for("invoice", bill_no=bill))
    options="".join(f"<option value='{name}'>{name} (Stock: {int(d.get('quantity',0))})</option>" for name,d in products.items() if int(d.get("quantity",0))>0)
    body=f"""<h2>New Sale / Invoice</h2><div class="box"><form method="post">
    <label>Customer Name</label><input name="customer" required>
    <label>Mobile</label><input name="mobile" required>
    <div id="items"><div class="grid2 item"><div><label>Product</label><select name="product">{options}</select></div>
    <div><label>Quantity</label><input name="quantity" type="number" min="1" value="1" required></div></div></div>
    <button type="button" onclick="addItem()">+ Add Another Product</button>
    <button class="success" type="submit">Complete Sale & Create Bill</button>
    </form></div>
    <script>
   function addItem(){{let x=document.querySelector('.item').cloneNode(true);x.querySelector('input').value=1;document.getElementById('items').appendChild(x);}}
    </script>"""
    return page(body, "Sell Product")

@app.route("/sales")
def sales_history():
    rows=""
    for s in reversed(sales):
        rows += f"<tr><td>{s.get('bill_no')}</td><td>{s.get('date')}</td><td>{s.get('customer')}</td><td>{s.get('mobile')}</td><td>{len(s.get('items',[]))}</td><td>Rs. {float(s.get('total',0)):.2f}</td><td><a class='btn' href='/invoice/{s.get('bill_no')}'>Invoice</a></td></tr>"
    body=f"""<h2>Sales History</h2><div class="box"><table>
    <tr><th>Bill</th><th>Date</th><th>Customer</th><th>Mobile</th><th>Items</th><th>Total</th><th>Invoice</th></tr>{rows or "<tr><td colspan='7'>No sales available.</td></tr>"}
    </table></div>"""
    return page(body, "Sales History")

@app.route("/invoice/<int:bill_no>")
def invoice(bill_no):
    sale=next((s for s in sales if int(s.get("bill_no",0))==bill_no),None)
    if not sale: return "Invoice not found",404
    body=f"""<h2>Invoice #{bill_no}</h2><div class="box">
    <p><b>Shop:</b> {SHOP_NAME}</p><p><b>Customer:</b> {sale.get('customer')}</p>
    <p><b>Mobile:</b> {sale.get('mobile')}</p><p><b>Date:</b> {sale.get('date')}</p>
    <table><tr><th>Product</th><th>Qty</th><th>Price</th><th>Total</th></tr>
    {''.join(f"<tr><td>{i['product']}</td><td>{i['quantity']}</td><td>Rs. {i['price']:.2f}</td><td>Rs. {i['total']:.2f}</td></tr>" for i in sale.get('items',[]))}
    </table><h2>Grand Total: Rs. {float(sale.get('total',0)):.2f}</h2>
    <a class="btn" href="/invoice/{bill_no}/pdf">Download PDF Invoice</a></div>"""
    return page(body, "Invoice")

@app.route("/invoice/<int:bill_no>/pdf")
def invoice_pdf(bill_no):
    sale=next((s for s in sales if int(s.get("bill_no",0))==bill_no),None)
    if not sale: return "Invoice not found",404
    buf=io.BytesIO(); pdf=canvas.Canvas(buf,pagesize=A4); w,h=A4
    pdf.setFont("Helvetica-Bold",18); pdf.drawCentredString(w/2,h-60,SHOP_NAME)
    pdf.setFont("Helvetica",10); pdf.drawCentredString(w/2,h-80,"BUILDING MATERIALS SHOP")
    pdf.line(40,h-95,w-40,h-95)
    pdf.setFont("Helvetica",11); pdf.drawString(50,h-125,f"Bill No: {sale['bill_no']}")
    pdf.drawString(350,h-125,f"Date: {sale['date']}")
    pdf.drawString(50,h-155,f"Customer: {sale.get('customer','')}")
    pdf.drawString(50,h-175,f"Mobile: {sale.get('mobile','')}")
    y=h-220; pdf.setFont("Helvetica-Bold",11)
    for x,t in [(45,"Product"),(280,"Qty"),(350,"Price"),(450,"Total")]: pdf.drawString(x,y,t)
    pdf.line(40,y-10,w-40,y-10); y-=35; pdf.setFont("Helvetica",10)
    items=sale.get("items",[])
    if not items and "product" in sale:
        items=[{"product":sale.get("product",""),"quantity":sale.get("quantity",0),"price":sale.get("price",0),"total":sale.get("total",0)}]
    for i in items:
        pdf.drawString(45,y,str(i.get("product",""))[:30]); pdf.drawString(280,y,str(i.get("quantity",0)))
        pdf.drawString(350,y,f"Rs. {float(i.get('price',0)):.2f}"); pdf.drawString(450,y,f"Rs. {float(i.get('total',0)):.2f}")
        y-=25
        if y<100: pdf.showPage(); y=h-60
    pdf.setFont("Helvetica-Bold",14); pdf.drawString(350,y-20,f"Grand Total: Rs. {float(sale.get('total',0)):.2f}")
    pdf.setFont("Helvetica",10); pdf.drawCentredString(w/2,60,"Thank you for visiting!")
    pdf.drawCentredString(w/2,42,SHOP_NAME); pdf.save(); buf.seek(0)
    return send_file(buf,as_attachment=True,download_name=f"Invoice_{bill_no}.pdf",mimetype="application/pdf")

@app.route("/low-stock")
def low_stock():
    low=[(n,d) for n,d in products.items() if int(d.get("quantity",0))<=LOW_STOCK_LIMIT]
    body="<h2>Low Stock Alert</h2><div class='box'><table><tr><th>Product</th><th>Stock</th></tr>"
    body += "".join(f"<tr><td>{n}</td><td>{int(d.get('quantity',0))}</td></tr>" for n,d in low)
    body += "</table>" + ("<p>No low-stock products.</p>" if not low else "") + "</div>"
    return page(body,"Low Stock")

@app.route("/report")
def report():
    total_products=len(products); total_stock=sum(int(d.get("quantity",0)) for d in products.values())
    low=sum(1 for d in products.values() if int(d.get("quantity",0))<=LOW_STOCK_LIMIT)
    total_sales=sum(float(s.get("total",0)) for s in sales)
    body=f"""<h2>Shop Report</h2><div class="cards">
    <div class="card"><h3>Total Products</h3><p>{total_products}</p></div>
    <div class="card"><h3>Total Stock</h3><p>{total_stock}</p></div>
    <div class="card"><h3>Low Stock Products</h3><p>{low}</p></div>
    <div class="card"><h3>Total Bills</h3><p>{len(sales)}</p></div>
    </div><div class="box"><h2>Total Sales: Rs. {total_sales:.2f}</h2></div>"""
    return page(body,"Shop Report")

if __name__ == "__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port,debug=True)
