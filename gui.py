import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# =========================================================
# SHOP NAME
# =========================================================

SHOP_NAME = "SHREE BHOJ BABA BUILDINGS MATERIALS"

PRODUCT_FILE = "products.json"
SALES_FILE = "sales.json"


# =========================================================
# LOAD / SAVE DATA
# =========================================================

def load_products():
    if os.path.exists(PRODUCT_FILE):
        try:
            with open(PRODUCT_FILE, "r") as file:
                data = json.load(file)

                if isinstance(data, dict):
                    return data

        except:
            return {}

    return {}


def save_products():
    with open(PRODUCT_FILE, "w") as file:
        json.dump(products, file, indent=4)


def load_sales():
    if os.path.exists(SALES_FILE):
        try:
            with open(SALES_FILE, "r") as file:
                data = json.load(file)

                if isinstance(data, list):
                    return data

        except:
            return []

    return []


def save_sales():
    with open(SALES_FILE, "w") as file:
        json.dump(sales, file, indent=4)


products = load_products()
sales = load_sales()


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()

root.title(SHOP_NAME)

root.geometry("950x760")

root.configure(bg="#f2f2f2")


# =========================================================
# DASHBOARD VARIABLES
# =========================================================

total_products = tk.StringVar()
total_stock_var = tk.StringVar()
total_sales_var = tk.StringVar()
low_stock_var = tk.StringVar()


# =========================================================
# UPDATE DASHBOARD
# =========================================================

def update_dashboard():

    total_products.set(
        str(len(products))
    )

    total_stock = sum(
        item.get("quantity", 0)
        for item in products.values()
    )

    total_stock_var.set(
        str(total_stock)
    )

    total_sales = 0

    for sale in sales:

        try:
            total_sales += float(
                sale.get("total", 0)
            )

        except:
            pass

    total_sales_var.set(
        f"Rs. {total_sales:.2f}"
    )

    low_stock = sum(
        1
        for item in products.values()
        if item.get("quantity", 0) <= 10
    )

    low_stock_var.set(
        str(low_stock)
    )


# =========================================================
# NEXT BILL NUMBER
# =========================================================

def get_next_bill_number():

    bill_numbers = []

    for sale in sales:

        try:
            bill_number = int(
                sale.get("bill_no", 0)
            )

            bill_numbers.append(
                bill_number
            )

        except:
            continue

    if bill_numbers:

        return max(bill_numbers) + 1

    return 1


# =========================================================
# PDF INVOICE
# =========================================================

def generate_invoice(sale):

    file_name = f"Invoice_{sale['bill_no']}.pdf"

    pdf = canvas.Canvas(
        file_name,
        pagesize=A4
    )

    width, height = A4

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawCentredString(
        width / 2,
        height - 60,
        SHOP_NAME
    )

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawCentredString(
        width / 2,
        height - 80,
        "BUILDING MATERIALS SHOP"
    )

    pdf.line(
        40,
        height - 95,
        width - 40,
        height - 95
    )

    pdf.setFont(
        "Helvetica-Bold",
        11
    )

    pdf.drawString(
        50,
        height - 125,
        f"Bill No: {sale['bill_no']}"
    )

    pdf.drawString(
        350,
        height - 125,
        f"Date: {sale['date']}"
    )

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawString(
        50,
        height - 155,
        f"Customer Name: {sale.get('customer', '')}"
    )

    pdf.drawString(
        50,
        height - 175,
        f"Mobile: {sale.get('mobile', '')}"
    )

    y = height - 220

    pdf.setFont(
        "Helvetica-Bold",
        11
    )

    pdf.drawString(
        45,
        y,
        "Product"
    )

    pdf.drawString(
        280,
        y,
        "Qty"
    )

    pdf.drawString(
        350,
        y,
        "Price"
    )

    pdf.drawString(
        450,
        y,
        "Total"
    )

    pdf.line(
        40,
        y - 10,
        width - 40,
        y - 10
    )

    y -= 35

    pdf.setFont(
        "Helvetica",
        10
    )

    items = sale.get(
        "items",
        []
    )

    # Old sales support

    if not items and "product" in sale:

        items = [
            {
                "product": sale.get(
                    "product",
                    ""
                ),
                "quantity": sale.get(
                    "quantity",
                    0
                ),
                "price": sale.get(
                    "price",
                    0
                ),
                "total": sale.get(
                    "total",
                    0
                )
            }
        ]

    for item in items:

        product_name = str(
            item.get(
                "product",
                ""
            )
        )

        if len(product_name) > 30:

            product_name = (
                product_name[:27]
                + "..."
            )

        pdf.drawString(
            45,
            y,
            product_name
        )

        pdf.drawString(
            280,
            y,
            str(
                item.get(
                    "quantity",
                    0
                )
            )
        )

        try:
            price = float(
                item.get(
                    "price",
                    0
                )
            )
        except:
            price = 0

        try:
            item_total = float(
                item.get(
                    "total",
                    0
                )
            )
        except:
            item_total = 0

        pdf.drawString(
            350,
            y,
            f"Rs. {price:.2f}"
        )

        pdf.drawString(
            450,
            y,
            f"Rs. {item_total:.2f}"
        )

        y -= 25

        if y < 100:

            pdf.showPage()

            y = height - 60

            pdf.setFont(
                "Helvetica",
                10
            )

    y -= 20

    pdf.line(
        40,
        y + 20,
        width - 40,
        y + 20
    )

    try:
        grand_total = float(
            sale.get(
                "total",
                0
            )
        )
    except:
        grand_total = 0

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawString(
        350,
        y,
        f"Grand Total: Rs. {grand_total:.2f}"
    )

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawCentredString(
        width / 2,
        60,
        "Thank you for visiting!"
    )

    pdf.drawCentredString(
        width / 2,
        42,
        SHOP_NAME
    )

    pdf.save()

    return file_name


# =========================================================
# ADD PRODUCT
# =========================================================

def add_product():

    window = tk.Toplevel(root)

    window.title("Add Product")

    window.geometry("450x420")

    window.configure(bg="white")

    tk.Label(
        window,
        text="ADD NEW PRODUCT",
        font=("Arial", 18, "bold"),
        bg="white"
    ).pack(
        pady=20
    )

    tk.Label(
        window,
        text="Product Name",
        bg="white"
    ).pack()

    name_entry = tk.Entry(
        window,
        width=35
    )

    name_entry.pack(
        pady=8
    )

    tk.Label(
        window,
        text="Quantity",
        bg="white"
    ).pack()

    quantity_entry = tk.Entry(
        window,
        width=35
    )

    quantity_entry.pack(
        pady=8
    )

    tk.Label(
        window,
        text="Selling Price",
        bg="white"
    ).pack()

    price_entry = tk.Entry(
        window,
        width=35
    )

    price_entry.pack(
        pady=8
    )

    def save():

        name = name_entry.get().strip()

        quantity_text = quantity_entry.get().strip()

        price_text = price_entry.get().strip()

        if not name or not quantity_text or not price_text:

            messagebox.showerror(
                "Error",
                "Please fill all fields."
            )

            return

        try:

            quantity = int(
                quantity_text
            )

            price = float(
                price_text
            )

        except ValueError:

            messagebox.showerror(
                "Error",
                "Quantity and price must be numbers."
            )

            return

        if quantity < 0 or price < 0:

            messagebox.showerror(
                "Error",
                "Values cannot be negative."
            )

            return

        existing_product = None

        for product in products:

            if product.lower() == name.lower():

                existing_product = product

                break

        if existing_product:

            products[
                existing_product
            ]["quantity"] += quantity

            products[
                existing_product
            ]["price"] = price

        else:

            products[name] = {

                "quantity": quantity,

                "price": price
            }

        save_products()

        update_dashboard()

        messagebox.showinfo(
            "Success",
            "Product added successfully!"
        )

        window.destroy()

    tk.Button(
        window,
        text="SAVE PRODUCT",
        width=25,
        height=2,
        command=save
    ).pack(
        pady=25
    )


# =========================================================
# VIEW PRODUCTS
# =========================================================

def view_products():

    window = tk.Toplevel(root)

    window.title("Product Inventory")

    window.geometry("750x500")

    window.configure(bg="white")

    tk.Label(
        window,
        text="PRODUCT INVENTORY",
        font=("Arial", 20, "bold"),
        bg="white"
    ).pack(
        pady=20
    )

    if not products:

        tk.Label(
            window,
            text="No products available.",
            font=("Arial", 13),
            bg="white"
        ).pack(
            pady=30
        )

        return

    frame = tk.Frame(
        window,
        bg="white"
    )

    frame.pack()

    headers = [
        "Product",
        "Quantity",
        "Price"
    ]

    for column, header in enumerate(headers):

        tk.Label(
            frame,
            text=header,
            width=25 if column == 0 else 15,
            font=("Arial", 11, "bold"),
            bg="white"
        ).grid(
            row=0,
            column=column,
            pady=8
        )

    row = 1

    for name, details in products.items():

        tk.Label(
            frame,
            text=name,
            width=25,
            bg="white"
        ).grid(
            row=row,
            column=0,
            pady=5
        )

        tk.Label(
            frame,
            text=details.get(
                "quantity",
                0
            ),
            width=15,
            bg="white"
        ).grid(
            row=row,
            column=1
        )

        tk.Label(
            frame,
            text=f"Rs. {float(details.get('price', 0)):.2f}",
            width=15,
            bg="white"
        ).grid(
            row=row,
            column=2
        )

        row += 1


# =========================================================
# EDIT PRODUCT
# =========================================================

def edit_product():

    window = tk.Toplevel(root)

    window.title("Edit Product")

    window.geometry("500x500")

    window.configure(bg="white")

    tk.Label(
        window,
        text="EDIT PRODUCT",
        font=("Arial", 20, "bold"),
        bg="white"
    ).pack(
        pady=20
    )

    tk.Label(
        window,
        text="Search Product Name",
        bg="white"
    ).pack()

    search_entry = tk.Entry(
        window,
        width=35
    )

    search_entry.pack(
        pady=8
    )

    # New product name

    tk.Label(
        window,
        text="New Product Name",
        bg="white"
    ).pack()

    name_entry = tk.Entry(
        window,
        width=35
    )

    name_entry.pack(
        pady=8
    )

    # Quantity

    tk.Label(
        window,
        text="Quantity",
        bg="white"
    ).pack()

    quantity_entry = tk.Entry(
        window,
        width=35
    )

    quantity_entry.pack(
        pady=8
    )

    # Price

    tk.Label(
        window,
        text="Selling Price",
        bg="white"
    ).pack()

    price_entry = tk.Entry(
        window,
        width=35
    )

    price_entry.pack(
        pady=8
    )

    def find_product():

        search_name = (
            search_entry.get().strip()
        )

        if not search_name:

            messagebox.showerror(
                "Error",
                "Enter product name."
            )

            return

        found = None

        for product in products:

            if product.lower() == search_name.lower():

                found = product

                break

        if found is None:

            messagebox.showerror(
                "Error",
                "Product not found."
            )

            return

        # Fill existing data

        name_entry.delete(
            0,
            tk.END
        )

        name_entry.insert(
            0,
            found
        )

        quantity_entry.delete(
            0,
            tk.END
        )

        quantity_entry.insert(
            0,
            str(
                products[found].get(
                    "quantity",
                    0
                )
            )
        )

        price_entry.delete(
            0,
            tk.END
        )

        price_entry.insert(
            0,
            str(
                products[found].get(
                    "price",
                    0
                )
            )
        )
    def save_changes():

        old_name = (
            search_entry.get().strip()
        )

        new_name = (
            name_entry.get().strip()
        )

        quantity_text = (
            quantity_entry.get().strip()
        )

        price_text = (
            price_entry.get().strip()
        )

        if not old_name:

            messagebox.showerror(
                "Error",
                "Search product first."
            )

            return

        found = None

        for product in products:

            if product.lower() == old_name.lower():

                found = product

                break

        if found is None:

            messagebox.showerror(
                "Error",
                "Product not found."
            )

            return

        if not new_name or not quantity_text or not price_text:

            messagebox.showerror(
                "Error",
                "Fill all fields."
            )

            return

        try:

            quantity = int(
                quantity_text
            )

            price = float(
                price_text
            )

        except ValueError:

            messagebox.showerror(
                "Error",
                "Quantity must be integer and price must be number."
            )

            return

        if quantity < 0 or price < 0:

            messagebox.showerror(
                "Error",
                "Values cannot be negative."
            )

            return

        # If product name changed

        if new_name != found:

            for product in products:

                if product.lower() == new_name.lower():

                    messagebox.showerror(
                        "Error",
                        "Another product with this name already exists."
                    )

                    return

            products[new_name] = {

                "quantity": quantity,

                "price": price
            }

            del products[found]

        else:

            products[found][
                "quantity"
            ] = quantity

            products[found][
                "price"
            ] = price

        save_products()

        update_dashboard()

        messagebox.showinfo(
            "Success",
            "Product updated successfully!"
        )

        window.destroy()

    tk.Button(
        window,
        text="FIND PRODUCT",
        width=22,
        height=2,
        command=find_product
    ).pack(
        pady=10
    )

    tk.Button(
        window,
        text="SAVE CHANGES",
        width=22,
        height=2,
        font=("Arial", 10, "bold"),
        command=save_changes
    ).pack(
        pady=15
    )


# =========================================================
# DELETE PRODUCT
# =========================================================

def delete_product():

    window = tk.Toplevel(root)

    window.title("Delete Product")

    window.geometry("450x350")

    window.configure(bg="white")

    tk.Label(
        window,
        text="DELETE PRODUCT",
        font=("Arial", 20, "bold"),
        bg="white"
    ).pack(
        pady=25
    )

    tk.Label(
        window,
        text="Product Name",
        bg="white"
    ).pack()

    name_entry = tk.Entry(
        window,
        width=35
    )

    name_entry.pack(
        pady=12
    )

    def delete():

        name = name_entry.get().strip()

        if not name:

            messagebox.showerror(
                "Error",
                "Enter product name."
            )

            return

        found = None

        for product in products:

            if product.lower() == name.lower():

                found = product

                break

        if found is None:

            messagebox.showerror(
                "Error",
                "Product not found."
            )

            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n\n{found}?"
        )

        if not confirm:

            return

        del products[found]

        save_products()

        update_dashboard()

        messagebox.showinfo(
            "Deleted",
            f"{found} deleted successfully!"
        )

        window.destroy()

    tk.Button(
        window,
        text="DELETE PRODUCT",
        width=22,
        height=2,
        font=("Arial", 10, "bold"),
        command=delete
    ).pack(
        pady=25
    )


# =========================================================
# SEARCH PRODUCT
# =========================================================

def search_product():

    window = tk.Toplevel(root)

    window.title("Search Product")

    window.geometry("500x400")

    window.configure(bg="white")

    tk.Label(
        window,
        text="SEARCH PRODUCT",
        font=("Arial", 20, "bold"),
        bg="white"
    ).pack(
        pady=20
    )

    entry = tk.Entry(
        window,
        width=35
    )

    entry.pack(
        pady=10
    )

    result = tk.Label(
        window,
        text="",
        font=("Arial", 12),
        bg="white"
    )

    result.pack(
        pady=30
    )

    def search():

        name = entry.get().strip()

        found = None

        for product in products:

            if product.lower() == name.lower():

                found = product

                break

        if found:

            data = products[found]

            result.config(
                text=(
                    f"Product: {found}\n\n"
                    f"Quantity: {data.get('quantity', 0)}\n"
                    f"Price: Rs. {float(data.get('price', 0)):.2f}"
                )
            )

        else:

            result.config(
                text="Product not found."
            )

    tk.Button(
        window,
        text="SEARCH",
        width=20,
        height=2,
        command=search
    ).pack()


# =========================================================
# UPDATE STOCK
# =========================================================

def update_stock():

    window = tk.Toplevel(root)

    window.title("Update Stock")

    window.geometry("500x400")

    window.configure(bg="white")

    tk.Label(
        window,
        text="UPDATE STOCK",
        font=("Arial", 20, "bold"),
        bg="white"
    ).pack(
        pady=20
    )

    tk.Label(
        window,
        text="Product Name",
        bg="white"
    ).pack()

    name_entry = tk.Entry(
        window,
        width=35
    )

    name_entry.pack(
        pady=8
    )

    tk.Label(
        window,
        text="Quantity to Add",
        bg="white"
    ).pack()

    quantity_entry = tk.Entry(
        window,
        width=35
    )

    quantity_entry.pack(
        pady=8
    )

    def update():

        name = name_entry.get().strip()

        try:

            quantity = int(
                quantity_entry.get()
            )

        except ValueError:

            messagebox.showerror(
                "Error",
                "Enter a valid quantity."
            )

            return

        if quantity <= 0:

            messagebox.showerror(
                "Error",
                "Quantity must be greater than 0."
            )

            return

        found = None

        for product in products:

            if product.lower() == name.lower():

                found = product

                break

        if found is None:

            messagebox.showerror(
                "Error",
                "Product not found."
            )

            return

        products[
            found
        ]["quantity"] += quantity

        save_products()

        update_dashboard()

        messagebox.showinfo(
            "Success",
            "Stock updated successfully!"
        )

        window.destroy()

    tk.Button(
        window,
        text="UPDATE STOCK",
        width=20,
        height=2,
        command=update
    ).pack(
        pady=25
    )


# =========================================================
# SELL PRODUCT - MULTIPLE PRODUCTS
# =========================================================

def sell_product():

    window = tk.Toplevel(root)

    window.title("New Sale")

    window.geometry("850x700")

    window.configure(bg="white")

    tk.Label(
        window,
        text="NEW SALE / INVOICE",
        font=("Arial", 20, "bold"),
        bg="white"
    ).pack(
        pady=15
    )

    customer_frame = tk.Frame(
        window,
        bg="white"
    )

    customer_frame.pack(
        pady=5
    )

    tk.Label(
        customer_frame,
        text="Customer Name:",
        bg="white"
    ).grid(
        row=0,
        column=0,
        padx=5
    )

    customer_entry = tk.Entry(
        customer_frame,
        width=25
    )

    customer_entry.grid(
        row=0,
        column=1,
        padx=10
    )

    tk.Label(
        customer_frame,
        text="Mobile:",
        bg="white"
    ).grid(
        row=0,
        column=2,
        padx=5
    )

    mobile_entry = tk.Entry(
        customer_frame,
        width=20
    )

    mobile_entry.grid(
        row=0,
        column=3,
        padx=10
    )

    product_frame = tk.Frame(
        window,
        bg="white"
    )

    product_frame.pack(
        pady=20
    )

    tk.Label(
        product_frame,
        text="Product:",
        bg="white"
    ).grid(
        row=0,
        column=0,
        padx=5
    )

    product_entry = tk.Entry(
        product_frame,
        width=25
    )

    product_entry.grid(
        row=0,
        column=1,
        padx=5
    )

    tk.Label(
        product_frame,
        text="Quantity:",
        bg="white"
    ).grid(
        row=0,
        column=2,
        padx=5
    )

    quantity_entry = tk.Entry(
        product_frame,
        width=10
    )

    quantity_entry.grid(
        row=0,
        column=3,
        padx=5
    )

    cart = []

    cart_frame = tk.Frame(
        window,
        bg="white"
    )

    cart_frame.pack(
        pady=10
    )

    headers = [
        "Product",
        "Quantity",
        "Price",
        "Total"
    ]

    for col, header in enumerate(headers):

        tk.Label(
            cart_frame,
            text=header,
            width=20 if col == 0 else 12,
            font=("Arial", 10, "bold"),
            bg="#e5e7eb"
        ).grid(
            row=0,
            column=col,
            padx=1,
            pady=1
        )

    grand_total_label = tk.Label(
        window,
        text="Grand Total: Rs. 0.00",
        font=("Arial", 16, "bold"),
        bg="white"
    )

    grand_total_label.pack(
        pady=15
    )

    def refresh_cart():

        for widget in cart_frame.winfo_children():

            try:

                row_number = int(
                    widget.grid_info()["row"]
                )

                if row_number > 0:
                    widget.destroy()

            except:
                pass

        for row, item in enumerate(
            cart,
            start=1
        ):

            tk.Label(
                cart_frame,
                text=item["product"],
                width=20,
                bg="white"
            ).grid(
                row=row,
                column=0,
                pady=3
            )

            tk.Label(
                cart_frame,
                text=item["quantity"],
                width=12,
                bg="white"
            ).grid(
                row=row,
                column=1
            )

            tk.Label(
                cart_frame,
                text=f"Rs. {item['price']:.2f}",
                width=12,
                bg="white"
            ).grid(
                row=row,
                column=2
            )

            tk.Label(
                cart_frame,
                text=f"Rs. {item['total']:.2f}",
                width=12,
                bg="white"
            ).grid(
                row=row,
                column=3
            )

        total = sum(
            item["total"]
            for item in cart
        )

        grand_total_label.config(
            text=f"Grand Total: Rs. {total:.2f}"
        )

    def add_item():

        name = product_entry.get().strip()

        quantity_text = quantity_entry.get().strip()

        if not name or not quantity_text:

            messagebox.showerror(
                "Error",
                "Enter product name and quantity."
            )

            return

        try:

            quantity = int(
                quantity_text
            )

        except ValueError:

            messagebox.showerror(
                "Error",
                "Quantity must be a number."
            )

            return

        if quantity <= 0:

            messagebox.showerror(
                "Error",
                "Quantity must be greater than 0."
            )

            return

        found = None

        for product in products:

            if product.lower() == name.lower():

                found = product

                break

        if found is None:

            messagebox.showerror(
                "Error",
                "Product not found."
            )

            return

        stock = products[
            found
        ].get(
            "quantity",
            0
        )

        price = float(
            products[
                found
            ].get(
                "price",
                0
            )
        )

        already_added = sum(
            item["quantity"]
            for item in cart
            if item["product"] == found
        )

        if already_added + quantity > stock:

            messagebox.showerror(
                "Error",
                f"Available stock: {stock}\n"
                f"Already added: {already_added}"
            )

            return

        existing = None

        for item in cart:

            if item["product"] == found:

                existing = item

                break

        if existing:

            existing["quantity"] += quantity

            existing["total"] = (
                existing["quantity"]
                * existing["price"]
            )

        else:

            cart.append({

                "product": found,

                "quantity": quantity,

                "price": price,

                "total": quantity * price
            })

        product_entry.delete(
            0,
            tk.END
        )

        quantity_entry.delete(
            0,
            tk.END
        )

        product_entry.focus()

        refresh_cart()

    tk.Button(
        window,
        text="ADD PRODUCT",
        width=20,
        height=2,
        command=add_item
    ).pack(
        pady=5
    )

    def complete_sale():

        customer = customer_entry.get().strip()

        mobile = mobile_entry.get().strip()

        if not customer:

            messagebox.showerror(
                "Error",
                "Enter customer name."
            )

            return

        if not mobile:

            messagebox.showerror(
                "Error",
                "Enter mobile number."
            )

            return

        if not cart:

            messagebox.showerror(
                "Error",
                "Add at least one product."
            )

            return

        # Final stock check

        for item in cart:

            product_name = item["product"]

            required_quantity = item["quantity"]

            available_quantity = products[
                product_name
            ].get(
                "quantity",
                0
            )

            if required_quantity > available_quantity:

                messagebox.showerror(
                    "Error",
                    f"Not enough stock for "
                    f"{product_name}.\n\n"
                    f"Available: {available_quantity}\n"
                    f"Required: {required_quantity}"
                )

                return

        # Reduce stock

        for item in cart:

            products[
                item["product"]
            ]["quantity"] -= item["quantity"]

        bill_no = get_next_bill_number()

        date_time = datetime.now().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )

        grand_total = sum(
            item["total"]
            for item in cart
        )

        sale = {

            "bill_no": bill_no,

            "date": date_time,

            "customer": customer,

            "mobile": mobile,

            "items": cart.copy(),

            "total": grand_total
        }

        sales.append(
            sale
        )

        save_products()

        save_sales()

        update_dashboard()

        invoice_file = generate_invoice(
            sale
        )

        messagebox.showinfo(
            "SALE SUCCESSFUL",

            f"Bill No: {bill_no}\n\n"
            f"Customer: {customer}\n"
            f"Items: {len(cart)}\n"
            f"Grand Total: Rs. {grand_total:.2f}\n\n"
            f"PDF Invoice Created:\n"
            f"{invoice_file}"
        )

        window.destroy()

    tk.Button(
        window,
        text="COMPLETE SALE & CREATE BILL",
        width=30,
        height=2,
        font=("Arial", 10, "bold"),
        command=complete_sale
    ).pack(
        pady=15
    )


# =========================================================
# SALES HISTORY
# =========================================================

def sales_history():

    window = tk.Toplevel(root)

    window.title("Sales History")

    window.geometry("950x550")

    window.configure(bg="white")

    tk.Label(
        window,
        text="SALES HISTORY",
        font=("Arial", 20, "bold"),
        bg="white"
    ).pack(
        pady=20
    )

    if not sales:

        tk.Label(
            window,
            text="No sales available.",
            font=("Arial", 13),
            bg="white"
        ).pack(
            pady=30
        )

        return

    frame = tk.Frame(
        window,
        bg="white"
    )

    frame.pack()

    headers = [
        "Bill",
        "Date",
        "Customer",
        "Mobile",
        "Items",
        "Total"
    ]

    widths = [
        8,
        20,
        20,
        15,
        10,
        15
    ]

    for col, header in enumerate(headers):

        tk.Label(
            frame,
            text=header,
            width=widths[col],
            font=("Arial", 10, "bold"),
            bg="#e5e7eb"
        ).grid(
            row=0,
            column=col,
            padx=1,
            pady=2
        )

    row = 1

    for sale in reversed(sales):

        items = sale.get(
            "items",
            []
        )

        if not items and "product" in sale:

            items = [

                {
                    "product": sale.get(
                        "product",
                        ""
                    ),

                    "quantity": sale.get(
                        "quantity",
                        0
                    ),

                    "price": sale.get(
                        "price",
                        0
                    ),

                    "total": sale.get(
                        "total",
                        0
                    )
                }
            ]

        values = [

            sale.get(
                "bill_no",
                ""
            ),

            sale.get(
                "date",
                ""
            ),

            sale.get(
                "customer",
                ""
            ),

            sale.get(
                "mobile",
                ""
            ),

            len(items),

            f"Rs. {float(sale.get('total', 0)):.2f}"
        ]

        for col, value in enumerate(values):

            tk.Label(
                frame,
                text=value,
                width=widths[col],
                bg="white"
            ).grid(
                row=row,
                column=col,
                pady=4
            )

        row += 1


# =========================================================
# LOW STOCK
# =========================================================

def low_stock_alert():

    window = tk.Toplevel(root)

    window.title("Low Stock Alert")

    window.geometry("500x450")

    window.configure(bg="white")

    tk.Label(
        window,
        text="LOW STOCK ALERT",
        font=("Arial", 20, "bold"),
        bg="white"
    ).pack(
        pady=20
    )

    found = False

    for name, details in products.items():

        quantity = details.get(
            "quantity",
            0
        )

        if quantity <= 10:

            found = True

            tk.Label(
                window,
                text=(
                    f"{name} → "
                    f"{quantity} units"
                ),
                font=("Arial", 12),
                bg="white"
            ).pack(
                pady=5
            )

    if not found:

        tk.Label(
            window,
            text="No low-stock products.",
            font=("Arial", 12),
            bg="white"
        ).pack(
            pady=20
        )


# =========================================================
# SHOP REPORT
# =========================================================

def shop_report():

    window = tk.Toplevel(root)

    window.title("Shop Report")

    window.geometry("500x450")

    window.configure(bg="white")

    tk.Label(
        window,
        text="SHOP REPORT",
        font=("Arial", 20, "bold"),
        bg="white"
    ).pack(
        pady=25
    )

    total_products_count = len(
        products
    )

    total_stock_count = sum(
        item.get(
            "quantity",
            0
        )
        for item in products.values()
    )

    low_stock_count = sum(
        1
        for item in products.values()
        if item.get(
            "quantity",
            0
        ) <= 10
    )

    total_sales_count = 0

    for sale in sales:

        try:
            total_sales_count += float(
                sale.get(
                    "total",
                    0
                )
            )

        except:
            pass

    total_bills_count = len(
        sales
    )

    report = (

        f"Total Products     : "
        f"{total_products_count}\n\n"

        f"Total Stock        : "
        f"{total_stock_count}\n\n"

        f"Low Stock Products : "
        f"{low_stock_count}\n\n"

        f"Total Bills        : "
        f"{total_bills_count}\n\n"

        f"Total Sales        : "
        f"Rs. {total_sales_count:.2f}"
    )

    tk.Label(
        window,
        text=report,
        font=("Arial", 13),
        justify="left",
        bg="white"
    ).pack(
        pady=20
    )


# =========================================================
# HEADER
# =========================================================

header = tk.Frame(
    root,
    bg="#1f2937",
    height=100
)

header.pack(
    fill="x"
)

tk.Label(
    header,
    text=SHOP_NAME,
    font=("Arial", 24, "bold"),
    fg="white",
    bg="#1f2937"
).pack(
    pady=15
)

tk.Label(
    header,
    text="Management System",
    font=("Arial", 11),
    fg="white",
    bg="#1f2937"
).pack()


# =========================================================
# DASHBOARD
# =========================================================

dashboard = tk.Frame(
    root,
    bg="#f2f2f2"
)

dashboard.pack(
    pady=25
)


def create_card(
    parent,
    title,
    variable,
    row,
    column
):

    card = tk.Frame(
        parent,
        bg="white",
        width=190,
        height=100,
        relief="solid",
        borderwidth=1
    )

    card.grid(
        row=row,
        column=column,
        padx=8
    )

    card.grid_propagate(
        False
    )

    tk.Label(
        card,
        text=title,
        font=("Arial", 10, "bold"),
        bg="white"
    ).pack(
        pady=10
    )

    tk.Label(
        card,
        textvariable=variable,
        font=("Arial", 17, "bold"),
        bg="white"
    ).pack()


# =========================================================
# DASHBOARD CARDS
# =========================================================

create_card(
    dashboard,
    "TOTAL PRODUCTS",
    total_products,
    0,
    0
)

create_card(
    dashboard,
    "TOTAL STOCK",
    total_stock_var,
    0,
    1
)

create_card(
    dashboard,
    "TOTAL SALES",
    total_sales_var,
    0,
    2
)

create_card(
    dashboard,
    "LOW STOCK",
    low_stock_var,
    0,
    3
)


# =========================================================
# BUTTON AREA
# =========================================================

buttons = tk.Frame(
    root,
    bg="#f2f2f2"
)

buttons.pack(
    pady=10
)

button_style = {

    "width": 22,

    "height": 2,

    "font": (
        "Arial",
        10,
        "bold"
    )
}


# Add Product

tk.Button(
    buttons,
    text="Add Product",
    command=add_product,
    **button_style
).grid(
    row=0,
    column=0,
    padx=8,
    pady=8
)


# View Products

tk.Button(
    buttons,
    text="View Products",
    command=view_products,
    **button_style
).grid(
    row=0,
    column=1,
    padx=8,
    pady=8
)


# Edit Product

tk.Button(
    buttons,
    text="Edit Product",
    command=edit_product,
    **button_style
).grid(
    row=1,
    column=0,
    padx=8,
    pady=8
)


# Delete Product

tk.Button(
    buttons,
    text="Delete Product",
    command=delete_product,
    **button_style
).grid(
    row=1,
    column=1,
    padx=8,
    pady=8
)


# Search Product

tk.Button(
    buttons,
    text="Search Product",
    command=search_product,
    **button_style
).grid(
    row=2,
    column=0,
    padx=8,
    pady=8
)


# Update Stock

tk.Button(
    buttons,
    text="Update Stock",
    command=update_stock,
    **button_style
).grid(
    row=2,
    column=1,
    padx=8,
    pady=8
)


# Sell Product

tk.Button(
    buttons,
    text="Sell Product",
    command=sell_product,
    **button_style
).grid(
    row=3,
    column=0,
    padx=8,
    pady=8
)


# Sales History

tk.Button(
    buttons,
    text="Sales History",
    command=sales_history,
    **button_style
).grid(
    row=3,
    column=1,
    padx=8,
    pady=8
)


# Low Stock

tk.Button(
    buttons,
    text="Low Stock Alert",
    command=low_stock_alert,
    **button_style
).grid(
    row=4,
    column=0,
    padx=8,
    pady=8
)


# Shop Report

tk.Button(
    buttons,
    text="Shop Report",
    command=shop_report,
    **button_style
).grid(
    row=4,
    column=1,
    padx=8,
    pady=8
)


# Exit

tk.Button(
    buttons,
    text="EXIT",
    command=root.destroy,
    width=48,
    height=2,
    font=("Arial", 10, "bold")
).grid(
    row=5,
    column=0,
    columnspan=2,
    pady=15
)


# =========================================================
# START
# =========================================================

update_dashboard()

root.mainloop()
        