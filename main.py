
import json
import os
from datetime import datetime


# ==============================
# LOAD PRODUCTS
# ==============================
def load_products():
    if os.path.exists("products.json"):
        try:
            with open("products.json", "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    return {}


# ==============================
# SAVE PRODUCTS
# ==============================
def save_products():
    with open("products.json", "w") as file:
        json.dump(products, file, indent=4)

    print("Data saved successfully!")


# ==============================
# LOAD SALES
# ==============================
def load_sales():
    if os.path.exists("sales.json"):
        try:
            with open("sales.json", "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []
    return []


# ==============================
# SAVE SALES
# ==============================
def save_sales():
    with open("sales.json", "w") as file:
        json.dump(sales, file, indent=4)


# Load data
products = load_products()
sales = load_sales()


# ==============================
# ADD PRODUCT
# ==============================
def add_product():
    name = input("Enter product name: ")
    quantity = int(input("Enter quantity: "))
    price = float(input("Enter selling price: "))

    products[name] = {
        "quantity": quantity,
        "price": price
    }

    save_products()

    print("Product added successfully!")


# ==============================
# VIEW PRODUCTS
# ==============================
def view_products():
    if not products:
        print("No products available.")
        return

    print("\n----- PRODUCT LIST -----")

    for name, details in products.items():
        print(
            f"Product: {name} | "
            f"Quantity: {details['quantity']} | "
            f"Price: ₹{details['price']}"
        )


# ==============================
# SEARCH PRODUCT
# ==============================
def search_product():
    name = input("Enter product name to search: ")

    if name in products:
        details = products[name]

        print("\nProduct Found")
        print("Name:", name)
        print("Quantity:", details["quantity"])
        print("Price: ₹", details["price"])

    else:
        print("Product not found.")


# ==============================
# UPDATE STOCK
# ==============================
def update_stock():
    name = input("Enter product name: ")

    if name in products:
        quantity = int(input("Enter new quantity: "))

        products[name]["quantity"] = quantity
        save_products()

        print("Stock updated successfully!")

    else:
        print("Product not found.")


# ==============================
# SELL PRODUCT
# ==============================
def sell_product():

    customer_name = input("Enter customer name: ")
    mobile = input("Enter mobile number: ")

    name = input("Enter product name: ")

    if name not in products:
        print("Product not found.")
        return

    quantity = int(input("Enter quantity to sell: "))

    if quantity > products[name]["quantity"]:
        print("Not enough stock!")
        return

    price = products[name]["price"]
    total = quantity * price

    # Reduce stock
    products[name]["quantity"] -= quantity

    # Save updated stock
    save_products()

    # Bill number
    bill_number = datetime.now().strftime("%Y%m%d%H%M%S")

    # Current date and time
    date_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

    # Save sale information
    sale = {
        "bill_no": bill_number,
        "date": date_time,
        "customer": customer_name,
        "mobile": mobile,
        "product": name,
        "quantity": quantity,
        "total": total
    }

    sales.append(sale)
    save_sales()

    # ==============================
    # PRINT BILL
    # ==============================

    print("\n================================")
    print("           SHOP BILL")
    print("================================")
    print("Bill No:", bill_number)
    print("Date & Time:", date_time)
    print("--------------------------------")
    print("Customer:", customer_name)
    print("Mobile:", mobile)
    print("Product:", name)
    print("Quantity:", quantity)
    print("Price: ₹", price)
    print("Total: ₹", total)
    print("================================")
    print("Sale completed successfully!")


# ==============================
# SALES HISTORY
# ==============================
def view_sales():
    print("\n========== SALES HISTORY ==========")

    if not sales:
        print("No sales history available.")
        return

    for sale in sales:
        print("-----------------------------------")
        print("Bill No:", sale["bill_no"])
        print("Date:", sale["date"])
        print("Customer:", sale["customer"])
        print("Mobile:", sale["mobile"])
        print("Product:", sale["product"])
        print("Quantity:", sale["quantity"])
        print("Total: ₹", sale["total"])

    print("-----------------------------------")
# ==============================
# LOW STOCK ALERT
# ==============================
def low_stock_alert():
    limit = 10

    print("\n========== LOW STOCK ALERT ==========")

    found = False

    for name, details in products.items():
        if details["quantity"] <= limit:
            print(
                f"Product: {name} | "
                f"Stock: {details['quantity']}"
            )
            found = True

    if not found:
        print("All products have sufficient stock.")
# ==============================
# SHOP REPORT
# ==============================
def shop_report():
    total_products = len(products)
    total_stock = 0
    low_stock = 0
    total_sales = 0

    # Total stock and low stock
    for name, details in products.items():
        total_stock += details["quantity"]

        if details["quantity"] <= 10:
            low_stock += 1

    # Total sales
    for sale in sales:
        total_sales += sale["total"]

    print("\n========== SHOP REPORT ==========")
    print("Total Products:", total_products)
    print("Total Stock:", total_stock)
    print("Total Sales: ₹", total_sales)
    print("Low Stock Products:", low_stock)
    print("=================================")        
# ==============================
# MAIN MENU
# ==============================
# ==============================
# MAIN MENU
# ==============================
def main():

    while True:

        print("\n==============================")
        print("   BUILDING MATERIAL SHOP")
        print("==============================")
        print("1. Add Product")
        print("2. View Products")
        print("3. Search Product")
        print("4. Update Stock")
        print("5. Sell Product")
        print("6. Sales History")
        print("7. Low Stock Alert")
        print("8. Shop Report")
        print("9. Exit")

        choice = input("Enter your choice: ")
        
        if choice == "1":
            add_product()

        elif choice == "2":
            view_products()

        elif choice == "3":
            search_product()

        elif choice == "4":
            update_stock()

        elif choice == "5":
            sell_product()

        elif choice == "6":
            print("Sales History selected")
            view_sales()

        elif choice == "7":
            print("Low Stock Alert selected")
            low_stock_alert()

        elif choice == "8":
            print("Shop Report selected")
            shop_report()

        elif choice == "9":
            print("Thank you!")
            break

        else:
            print("Invalid choice. Try again.")


# Start program
main()