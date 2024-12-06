import datetime
import re
from urllib.parse import quote_plus

from bson import ObjectId   
from flask import Flask, render_template, request, redirect, session
import pymongo
import os.path

username="noSql"
password="Nosqlproject@123"
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)
uri="mongodb+srv://"+encoded_username+":"+encoded_password+"@nosql.b3i7a.mongodb.net/?retryWrites=true&w=majority&appName=noSql"

conn = pymongo.MongoClient(uri, tls=True, tlsAllowInvalidCertificates=True)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

FOOD_ITEMS_PATH = APP_ROOT + "/static/food_items/"
RESTAURANT_PROFILE_PATH = APP_ROOT + "/static/restaurant_profile/"

my_database = conn["restaurant_food_ordering"]
admin_collection = my_database["admin"]
food_categories_collection = my_database["food_categories"]
food_sub_categories_collection = my_database["food_sub_categories"]
locations_collection = my_database["locations"]
restaurant_types_collection = my_database["restaurant_types"]
restaurants_collection = my_database["restaurants"]
customers_collection = my_database["customers"]
menu_collection = my_database["menu"]
orders_collection = my_database["orders"]
order_items_collection = my_database["order_items"]
payment_details_collection = my_database["payment_details"]
delivery_boys_collection = my_database["delivery_boys"]


app = Flask(__name__)
app.secret_key = "restaurant_food_ordering"

query = {}
count = admin_collection.count_documents(query)
if count == 0:
    query = {"username": "admin", "password": "admin"}
    admin_collection.insert_one(query)
    print(query)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    query = {"username": username, "password": password}
    count = admin_collection.count_documents(query)
    if count > 0:
        admin = admin_collection.find_one(query)
        session['admin_id'] = str(admin['_id'])
        session['role'] = "admin"
        return redirect("/admin_home")
    else:
        return render_template("message.html", message="Invalid Login")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/food_categories")
def food_categories():
    message = request.args.get("message")
    query = {}
    food_categories = food_categories_collection.find(query)
    food_categories = list(food_categories)
    print(food_categories)
    return render_template("food_categories.html", food_categories=food_categories, message=message)


@app.route("/food_categories_action", methods=['post'])
def food_categories_action():
    category_name = request.form.get("category_name")
    query = {"category_name": category_name}
    count = food_categories_collection.count_documents(query)
    if count == 0:
        food_categories_collection.insert_one(query)
        return redirect("/food_categories?message=Food Category Add Successfully")
    else:
        return redirect("food_categories?message=Category Already Exists")


@app.route("/food_sub_categories")
def food_sub_categories():
    message = request.args.get("message")
    food_category_id = request.args.get("food_category_id")
    query = {}
    food_categories = food_categories_collection.find(query)
    food_categories = list(food_categories)
    if message== None:
        message = ""
    if food_category_id == None:
        food_category_id = ""
    if food_category_id == "":
        food_sub_categories = food_sub_categories_collection.find({})
    else:
        query = {"food_category_id": ObjectId(food_category_id)}
        food_sub_categories = food_sub_categories_collection.find(query)
    food_sub_categories = list(food_sub_categories)
    print(food_sub_categories)
    return render_template("food_sub_categories.html", food_categories=food_categories, food_sub_categories=food_sub_categories,food_category_id=food_category_id, message=message, str=str,get_food_category_by_category_id=get_food_category_by_category_id)


@app.route("/food_sub_categories_action", methods=['post'])
def food_sub_categories_action():
    food_category_id = request.form.get("food_category_id")
    food_sub_category_name = request.form.get("food_sub_category_name")
    query = {"food_category_id": ObjectId(food_category_id),"food_sub_category_name": food_sub_category_name}
    count = food_sub_categories_collection.count_documents(query)
    if count > 0:
        return redirect("food_sub_categories?message= Duplicate Sub Category")
    else:
        food_sub_categories_collection.insert_one(query)
        return redirect("food_sub_categories?message=Sub Category Added Successfully")
def get_food_category_by_category_id(food_category_id):
    query = {"_id": food_category_id}
    food_categories = food_categories_collection.find_one(query)
    return food_categories


@app.route("/view_restaurants")
def view_restaurants():
    query = {}
    restaurants = restaurants_collection.find(query)
    restaurants = list(restaurants)
    return render_template("view_restaurant.html", restaurants=restaurants, get_location_by_location_id=get_location_by_location_id)


@app.route("/verify")
def verify():
    restaurant_id = request.args.get("restaurant_id")
    query1 = {"_id": ObjectId(restaurant_id)}
    query2 = {"$set": {"status": "Verified"}}
    restaurants_collection.update_one(query1, query2)
    return redirect("/view_restaurants")


@app.route("/verify2")
def verify2():
    restaurant_id = request.args.get("restaurant_id")
    query1 = {"_id": ObjectId(restaurant_id)}
    query2 = {"$set": {"status": "Not verified"}}
    restaurants_collection.update_one(query1, query2)
    return redirect("/view_restaurants")


@app.route("/verify_delivery_boy")
def verify_delivery_boy():
    delivery_boy_id = request.args.get("delivery_boy_id")
    query1 = {"_id": ObjectId(delivery_boy_id)}
    query2 = {"$set": {"status": "Verified"}}
    delivery_boys_collection.update_one(query1, query2)
    return redirect("/view_delivery_boy")


@app.route("/view_customers")
def view_customers():
    query = {}
    customers = customers_collection.find(query)
    customers = list(customers)
    return render_template("view_customers.html", customers=customers, get_location_by_location_id=get_location_by_location_id)


@app.route("/view_delivery_boy")
def view_delivery_boy():
    query = {}
    delivery_boys = delivery_boys_collection.find(query)
    delivery_boys = list(delivery_boys)
    return render_template("view_delivery_boy.html", delivery_boys=delivery_boys, get_location_by_location_id=get_location_by_location_id)


@app.route("/locations")
def locations():
    message = request.args.get("message")
    query = {}
    locations = locations_collection.find(query)
    locations = list(locations)
    print(locations)
    return render_template("location.html", message=message, locations=locations)


@app.route("/location_action", methods=['post'])
def location_action():
    location_name = request.form.get("location_name")
    query = {"location_name": location_name}
    count = locations_collection.count_documents(query)
    if count == 0:
        locations_collection.insert_one(query)
        return redirect("/locations?message=Location Added Successfully")
    else:
        return redirect("locations?message=Location Already Exists")


@app.route("/restaurant_types")
def restaurant_types():
    message = request.args.get("message")
    query = {}
    restaurant_types = restaurant_types_collection.find(query)
    restaurant_types = list(restaurant_types)
    print(restaurant_types)
    return render_template("type_of_restaurant.html", message=message, restaurant_types=restaurant_types)


@app.route("/restaurant_type_action", methods=['post'])
def restaurant_type_action():
    restaurant_type_name = request.form.get("restaurant_type_name")
    query = {"restaurant_type_name": restaurant_type_name}
    count = restaurant_types_collection.count_documents(query)
    if count == 0:
        restaurant_types_collection.insert_one(query)
        return redirect("/restaurant_types?message=Restaurant Type Name Added Successfully")
    else:
        return redirect("restaurant_types?message=Restaurant Type Name Already Exists")


@app.route("/admin_logout")
def admin_logout():
    return redirect("/")


@app.route("/restaurant_login")
def restaurant_login():
    return render_template("restaurant_login.html")


@app.route("/restaurant_login_action",methods=['post'])
def restaurant_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = restaurants_collection.count_documents(query)
    if count > 0:
        restaurant = restaurants_collection.find_one(query)
        if restaurant['status'] == "Not verified":
            return render_template("message.html", message="Restaurant Is Not verified")
        else:
            session['restaurant_id'] = str(restaurant['_id'])
            session['role'] = "restaurant"
            return redirect("/restaurant_home")
    else:
        return render_template("message.html", message="Invalid login Details")
def get_location_by_location_id(location_id):
    query = {"_id": location_id}
    locations = locations_collection.find_one(query)
    return locations


@app.route("/restaurant_home")
def restaurant_home():
    restaurant_id = session['restaurant_id']
    query = {"_id": ObjectId(restaurant_id)}
    restaurant = restaurants_collection.find_one(query)
    return render_template("restaurant_welcome.html", restaurant=restaurant)


@app.route("/restaurant_logout")
def restaurant_logout():
    return redirect("/")


@app.route("/restaurant_registration_action", methods=["post"])
def restaurant_registration_action():
    name =  request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    password = request.form.get("password")
    location_id = request.form.get("location_id")
    restaurant_type_id = request.form.get("restaurant_type_id")
    print(restaurant_type_id)
    address = request.form.get("address")
    about = request.form.get("about")
    status = request.form.get("status")
    restaurant_profile = request.files.get("restaurant_profile")
    path = RESTAURANT_PROFILE_PATH + "" + restaurant_profile.filename
    restaurant_profile.save(path)
    query = {"email": email}
    count = restaurants_collection.count_documents(query)
    if count == 0:
        query = {"name": name, "phone": phone, "email": email, "password": password, "restaurant_profile": restaurant_profile.filename, "location_id": ObjectId(location_id), "restaurant_type_id": ObjectId(restaurant_type_id), "address": address, "about": about, "status": "Not verified"}
        restaurants_collection.insert_one(query)
        return render_template("message.html", message="Restaurant Added Successfully")
    else:
        return render_template("message.html", message="Duplicate Entry")


@app.route("/restaurant_registration")
def restaurant_registration():
    locations = locations_collection.find({})
    locations = list(locations)
    print(locations)
    restaurant_types = restaurant_types_collection.find({})
    restaurant_types = list(restaurant_types)
    return render_template("restaurant_registration.html", locations=locations, restaurant_types=restaurant_types)


@app.route("/add_menu")
def add_menu():
    food_category_id = request.args.get("food_category_id")
    if food_category_id == None:
        food_category_id = ""
    if food_category_id == "":
        query = {}
    else:
        query = {"food_category_id": ObjectId(food_category_id)}

    food_sub_categories = food_sub_categories_collection.find(query)
    food_sub_categories = list(food_sub_categories)

    food_categories = food_categories_collection.find({})
    food_categories = list(food_categories)
    return render_template("add_menu.html", food_categories=food_categories, food_sub_categories=food_sub_categories)


@app.route("/add_menu_action", methods=["post"])
def add_menu_action():
    food_item_name = request.form.get("food_item_name")
    price = request.form.get("price")
    description = request.form.get("description")
    quantity = request.form.get("quantity")
    restaurant_id = session['restaurant_id']
    food_sub_category_id = request.form.get("food_sub_category_id")
    food_item_image = request.files.get("food_item_image")
    path = FOOD_ITEMS_PATH + "" + food_item_image.filename
    food_item_image.save(path)
    query = {"food_item_name": food_item_name, "restaurant_id": restaurant_id}
    count = menu_collection.count_documents(query)
    if count > 0:
        return render_template("menu_message.html", message="This food item for this restaurant is already added")
    else:
        query = {"food_item_name": food_item_name, "price": price, "description": description, "quantity": quantity,
                 "restaurant_id": ObjectId(restaurant_id), "food_sub_category_id": ObjectId(food_sub_category_id),
                 "food_item_image": food_item_image.filename}
        menu_collection.insert_one(query)
        return render_template("menu_message.html", message="Food Items Added Successfully")


@app.route("/view_menu")
def view_menu():
    restaurant_id = request.args.get("restaurant_id")
    food_category_id = request.args.get("food_category_id")
    food_sub_category_id = request.args.get("food_sub_category_id")
    food_item_name = request.args.get("food_item_name")
    if session['role'] == "restaurant":
        restaurant_id = session['restaurant_id']
    if restaurant_id == None:
        restaurant_id = ""
    if food_category_id == None:
        food_category_id = ""
    if food_sub_category_id == None:
        food_sub_category_id = ""
    if food_item_name == None:
        food_item_name = ""
    food_item_name2 = re.compile(".*" + str(food_item_name) + ".*", re.IGNORECASE)
    query = {}
    if restaurant_id == "" and food_category_id == "" and food_sub_category_id == "":
        query = {"food_item_name": food_item_name2}
    elif restaurant_id == "" and food_category_id == "" and food_sub_category_id != "":
        query = {"food_item_name": food_item_name2, "food_sub_category_id": ObjectId(food_sub_category_id)}
    elif restaurant_id == "" and food_category_id != "" and food_sub_category_id == "":
        query= {"food_category_id": ObjectId(food_category_id)}
        food_sub_categories = food_sub_categories_collection.find(query)
        food_sub_categories = list(food_sub_categories)
        food_sub_category_ids = []
        for food_sub_category in food_sub_categories:
            food_sub_category_ids.append(food_sub_category['_id'])
        query = {"food_item_name": food_item_name2, "food_sub_category_id" : {"$in": food_sub_category_ids}}
    elif restaurant_id == "" and food_category_id != "" and food_sub_category_id != "":
        query = {"food_item_name": food_item_name2,"food_sub_category_id": ObjectId(food_sub_category_id)}
    elif restaurant_id != "" and food_category_id == "" and food_sub_category_id == "":
        query = {"food_item_name": food_item_name2, "restaurant_id": ObjectId(restaurant_id)}
    elif restaurant_id != "" and food_category_id == "" and food_sub_category_id != "":
        query = {"food_item_name": food_item_name2, "restaurant_id": ObjectId(restaurant_id), "food_sub_category_id": ObjectId(food_sub_category_id)}
    elif restaurant_id != "" and food_category_id != "" and food_sub_category_id == "":
        query = {"food_category_id": ObjectId(food_category_id)}
        food_sub_categories = food_sub_categories_collection.find(query)
        food_sub_categories = list(food_sub_categories)
        food_sub_category_ids = []
        for food_sub_category in food_sub_categories:
            food_sub_category_ids.append(food_sub_category['_id'])
        query = {"food_item_name": food_item_name2, "restaurant_id": ObjectId(restaurant_id), "food_sub_category_id": {"$in": food_sub_category_ids}}
    elif restaurant_id != "" and food_category_id != "" and food_sub_category_id != "":
        query = {"food_item_name": food_item_name2, "restaurant_id": ObjectId(restaurant_id), "food_sub_category_id": ObjectId(food_sub_category_id)}
    menus = menu_collection.find(query)
    menus = list(menus)
    food_categories = food_categories_collection.find({})
    food_categories = list(food_categories)
    if food_category_id == "":
        food_sub_categories = food_sub_categories_collection.find({})
    else:
        query = {"food_category_id":ObjectId(food_category_id)}
        food_sub_categories = food_sub_categories_collection.find(query)
    restaurants = restaurants_collection.find({})
    return render_template("view_menu.html", menus=menus, food_categories=food_categories, food_sub_categories=food_sub_categories,restaurants=restaurants,restaurant_id=restaurants,food_category_id=food_category_id,food_sub_category_id=food_sub_category_id,food_item_name=food_item_name,str=str)


@app.route("/add_to_cart")
def add_to_cart():
    quantity = request.args.get("quantity")
    menu_id = request.args.get("menu_id")
    print(menu_id)
    query = {"_id": ObjectId(menu_id)}
    menu = menu_collection.find_one(query)
    print(query)
    restaurant_id = menu['restaurant_id']
    customer_id = session['customer_id']
    query = {"customer_id": ObjectId(customer_id), "restaurant_id": ObjectId(restaurant_id), "status": "cart"}
    count = orders_collection.count_documents(query)
    if count > 0:
        order = orders_collection.find_one(query)
        order_id = order['_id']
    else:
        date = datetime.datetime.now()
        query = {"customer_id": ObjectId(customer_id), "restaurant_id": ObjectId(restaurant_id), "date": date, "status": "cart"}
        result = orders_collection.insert_one(query)
        order_id = result.inserted_id
    query = {"menu_id": ObjectId(menu_id), "order_id": order_id}
    count = order_items_collection.count_documents(query)
    if count > 0:
        order_item = order_items_collection.find_one(query)
        query2 = {"$set": {"quantity": int(order_item['quantity'])+int(quantity)}}
        order_items_collection.update_one(query, query2)
        return render_template("add_cart.html", message="Food item Updated In Cart")
    else:
        query = {"menu_id": ObjectId(menu_id), "order_id": order_id, "quantity": quantity}
        order_items_collection.insert_one(query)
        return render_template("add_cart.html", message="Food item is added successfully")


@app.route("/view_order")
def view_order():
    view_type = request.args.get("view_type")
    query = {}
    orders = orders_collection.find(query)
    if session['role'] == 'customer':
        customer_id = session['customer_id']
        if view_type == "cart":
            query={"customer_id": ObjectId(customer_id), "status": 'cart'}
        elif view_type == "processing":
            query={"$or": [{"customer_id": ObjectId(customer_id), "status": 'ordered'}, {"customer_id": ObjectId(customer_id),"status": 'preparing'}, {"customer_id": ObjectId(customer_id), "status":'prepared'}, {"customer_id": ObjectId(customer_id), "status": 'assigned to delivery boy'}, {"customer_id": ObjectId(customer_id), "status": 'dispatched'}]}
        elif view_type == "history":
            query = {"$or": [{"customer_id": ObjectId(customer_id), "status": 'delivered'}, {"customer_id": ObjectId(customer_id), "status": 'cancelled'}]}
    elif session['role'] == 'restaurant':
        restaurant_id = session['restaurant_id']
        if view_type == "ordered":
            query = {"restaurant_id": ObjectId(restaurant_id), "status": 'ordered'}
        elif view_type == "processing":
            query = {"$or": [{"restaurant_id": ObjectId(restaurant_id), "status": 'preparing'}, {"restaurant_id":ObjectId(restaurant_id), "status": 'prepared'},{"restaurant_id": ObjectId(restaurant_id), "status": 'assigned to delivery boy'}, {"restaurant_id": ObjectId(restaurant_id), "status": 'dispatched'}]}
        elif view_type == "history":
            query = {"$or": [{"restaurant_id": ObjectId(restaurant_id), "status": 'cancelled'}, {"restaurant_id": ObjectId(restaurant_id), "status": 'delivered'}]}
    elif session['role'] == "delivery boy":
        delivery_boy_id = session['delivery_boy_id']
        if view_type == "prepared":
            query = {"status": 'prepared'}
        elif view_type == "processing":
            query = {"$or": [{"delivery_boy_id": ObjectId(delivery_boy_id), "status": 'assigned to delivery boy'}, {"delivery_boy_id": ObjectId(delivery_boy_id), "status": 'dispatched'}]}
        elif view_type == "history":
            query = {"delivery_boy_id": ObjectId(delivery_boy_id), "status": 'delivered'}
    orders = orders_collection.find(query)
    orders = list(orders)
    orders.reverse()
    return render_template("view_orders.html", orders=orders, get_restaurant_by_restaurant_id=get_restaurant_by_restaurant_id,get_customers_by_customer_id=get_customers_by_customer_id,get_order_items_by_order_id=get_order_items_by_order_id,get_menu_by_menu_id=get_menu_by_menu_id, int=int, get_delivery_boy_by_delivery_boy_id=get_delivery_boy_by_delivery_boy_id)
def get_restaurant_by_restaurant_id(restaurant_id):
    query = {"_id": ObjectId(restaurant_id)}
    restaurant = restaurants_collection.find_one(query)
    return restaurant
def get_customers_by_customer_id(customer_id):
    query = {"_id": ObjectId(customer_id)}
    customer = customers_collection.find_one(query)
    return customer
def get_order_items_by_order_id(order_id):
    query = {"order_id": ObjectId(order_id)}
    order_items = order_items_collection.find(query)
    return order_items
def get_menu_by_menu_id(menu_id):
    print(menu_id)
    query = {"_id": ObjectId(menu_id)}
    menu = menu_collection.find_one(query)
    return menu


@app.route("/Remove_items")
def Remove_items():
    order_id = request.args.get("order_id")
    order_item_id = request.args.get("order_item_id")
    query ={"_id": ObjectId(order_item_id)}
    order_items_collection.delete_one(query)
    query = {"order_id": ObjectId(order_id)}
    count = order_items_collection.count_documents(query)
    if count == 0:
        query = {"_id": ObjectId(order_id)}
        orders_collection.delete_one(query)
    return redirect("view_order?view_type=cart")


@app.route("/order_now")
def order_now():
    order_id = request.args.get("order_id")
    total_price = request.args.get("total_price")
    query = {"_id": ObjectId(order_id)}
    order = orders_collection.find_one(query)
    return render_template("order_now.html", order_id=order_id, total_price=total_price)


@app.route("/order_now_action", methods=['post'])
def order_now_action():
    order_id = request.form.get("order_id")
    total_price = request.form.get("total_price")
    card_number = request.form.get("card_number")
    card_holder_name = request.form.get("card_holder_name")
    expired_date = request.form.get("expired_date")
    cvv = request.form.get("cvv")
    date = datetime.datetime.now()
    query = {"order_id": ObjectId(order_id), "card_number": card_number, "card_holder_name": card_holder_name, "total_price": total_price, "expired_date": expired_date, "cvv": cvv, "date": date, "status": "transaction successful"}
    payment_details_collection.insert_one(query)
    query1 = {"_id": ObjectId(order_id)}
    query2 = {"$set": {"status": "ordered"}}
    orders_collection.update_one(query1, query2)
    return render_template("payment_message.html", message="Payment Successful")


@app.route("/customer_login")
def customer_login():
    return render_template("customer_login.html")


@app.route("/customer_login_action", methods=['post'])
def customer_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = customers_collection.count_documents(query)
    if count > 0:
        customer = customers_collection.find_one(query)
        session['customer_id'] = str(customer['_id'])
        session['role'] = "customer"
        return redirect("/customer_home")
    else:
        return render_template("message.html", message="Invalid Login")
def get_location_by_location_id(location_id):
    query = {"_id": location_id}
    locations = locations_collection.find_one(query)
    return locations


@app.route("/customer_home")
def customer_home():
    customer_id = session['customer_id']
    query = {"_id": ObjectId(customer_id)}
    customer = customers_collection.find_one(query)
    return render_template("customer_welcome.html", customer=customer)


@app.route("/customer_logout")
def customer_logout():
    return redirect("/")


@app.route("/customer_registration")
def customer_registration():
    locations = locations_collection.find({})
    locations = list(locations)
    return render_template("customer_registration.html", locations=locations)


@app.route("/customer_registration_action", methods=["post"])
def customer_registration_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    password = request.form.get("password")
    conform_password = request.form.get("conform_password")
    location_id = request.form.get("location_id")
    state = request.form.get("state")
    address = request.form.get("address")
    if password != conform_password:
        return render_template("message.html", message="Password is not matched")
    query = {"email": email}
    count = customers_collection.count_documents(query)
    if count == 0:
        query = {"first_name": first_name, "last_name": last_name, "phone": phone, "email": email, "password": password, "location_id": ObjectId(location_id), "state": state,"address": address}
        customers_collection.insert_one(query)
        return render_template("message.html", message="Customer Added Successfully")
    else:
        return render_template("message.html", message="Duplicate Entry")


@app.route("/delivery_boy_login")
def delivery_boy_login():
    return render_template("delivery_boy_login.html")


@app.route("/delivery_boy_login_action", methods=['post'])
def delivery_boy_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = delivery_boys_collection.count_documents(query)
    if count > 0:
        delivery_boy = delivery_boys_collection.find_one(query)
        if delivery_boy['status'] == "Not verified":
            return render_template("message.html", message="Delivery Boy Is Not verified")
        else:
            session['delivery_boy_id'] = str(delivery_boy['_id'])
            session['role'] = "delivery boy"
            return redirect("/delivery_boy_home")
    else:
        return render_template("message.html", message="Invalid Login")
def get_location_by_location_id(location_id):
    query = {"_id": location_id}
    locations = locations_collection.find_one(query)
    return locations


@app.route("/delivery_boy_home")
def delivery_boy_home():
    delivery_boy_id = session['delivery_boy_id']
    query = {"_id": ObjectId(delivery_boy_id)}
    delivery_boy = delivery_boys_collection.find_one(query)
    return render_template("delivery_boy_welcome.html", delivery_boy=delivery_boy)


@app.route("/delivery_boy_logout")
def delivery_boy_logout():
    return redirect("/")


@app.route("/delivery_boy_registration")
def delivery_boy_registration():
    locations = locations_collection.find({})
    locations = list(locations)
    return render_template("delivery_boy_registration.html", locations=locations)


@app.route("/delivery_boy_registration_action", methods=["post"])
def delivery_boy_registration_action():
    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    password = request.form.get("password")
    location_id = request.form.get("location_id")
    address = request.form.get("address")
    status = request.form.get("status")
    query = {"email": email}
    count = delivery_boys_collection.count_documents(query)
    if count == 0:
        query = {"name": name, "phone": phone, "email": email, "password": password, "location_id": ObjectId(location_id), "address": address, "status": "Not verified"}
        delivery_boys_collection.insert_one(query)
        return render_template("message.html", message="Delivery Boy Added Successfully")
    else:
        return render_template("message.html", message="Duplicate Entry")


@app.route("/cancel")
def cancel():
    order_id = request.args.get("order_id")
    status = request.args.get("status")
    view_type = request.args.get("view_type")
    query1 = {"_id": ObjectId(order_id)}
    query2 = {"$set": {"status": status}}
    orders_collection.update_one(query1, query2)
    query1 = {"order_id": ObjectId(order_id)}
    query2 = {"$set": {"status": "Refunded"}}
    payment_details_collection.update_one(query1, query2)
    return redirect("view_order?view_type="+str(view_type))


@app.route("/set_status")
def set_status():
    order_id = request.args.get("order_id")
    status = request.args.get("status")
    view_type = request.args.get("view_type")
    query1 = {"_id": ObjectId(order_id)}
    query2 = {"$set": {"status": status}}
    orders_collection.update_one(query1, query2)
    return redirect("view_order?view_type="+str(view_type))


@app.route("/set_status2")
def set_status2():
    delivery_boy_id = session['delivery_boy_id']
    order_id = request.args.get("order_id")
    status = request.args.get("status")
    view_type = request.args.get("view_type")
    query1 = {"_id": ObjectId(order_id)}
    query2 = {"$set": {"status": status, "delivery_boy_id": ObjectId(delivery_boy_id)}}
    orders_collection.update_one(query1, query2)
    return redirect("view_order?view_type="+str(view_type))


def get_delivery_boy_by_delivery_boy_id(delivery_boy_id):
    query = {"_id": delivery_boy_id}
    delivery_boy = delivery_boys_collection.find_one(query)
    return delivery_boy


@app.route("/view_payments")
def view_payments():
    order_id = request.args.get("order_id")
    query = {"order_id": ObjectId(order_id)}
    payment_details = payment_details_collection.find(query)
    payment_details = list(payment_details)
    return render_template("view_payments.html", payment_details=payment_details, order_id=order_id)

app.run(debug=True)
