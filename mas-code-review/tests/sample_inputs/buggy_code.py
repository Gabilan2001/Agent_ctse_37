# tests/sample_inputs/buggy_code.py
# A sample e-commerce order processing module
# WARNING: This file contains intentional bugs for demo purposes

import os
import md5
import pickle
import subprocess

# Hardcoded credentials (security issue)
DB_PASSWORD = "admin123"
SECRET_KEY = "mysecretkey"

# Global mutable state (code smell)
orders = []
total_revenue = 0


def calculate_discount(price, discount):
    # Bug: no check for division by zero
    # Bug: no validation for negative values
    discounted = price / discount
    return discounted


def hash_password(password):
    # Security: md5 is cryptographically weak
    return md5.new(password).hexdigest()


def process_order(user_id, items, promo_code):
    # Bug: unused variable
    unused_var = "this does nothing"

    # Bug: mutable default argument pattern
    total = 0
    for item in items:
        # Bug: no check if 'price' key exists
        total = total + item["price"] * item["qty"]

    # Security: SQL injection vulnerability
    query = "SELECT * FROM users WHERE id = " + user_id

    # Bug: broad exception handling
    try:
        result = apply_promo(promo_code, total)
    except:
        result = total

    orders.append({
        "user": user_id,
        "total": result
    })

    return result


def apply_promo(code, total):
    # Bug: comparing with == instead of checking membership
    if code == "SAVE10" or code == "SAVE20" or code == "SAVE30":
        if code == "SAVE10":
            discount = total * 0.1
        if code == "SAVE20":
            discount = total * 0.2
        if code == "SAVE30":
            discount = total * 0.3
        return total - discount
    else:
        return total


def get_user_data(username):
    # Security: command injection vulnerability
    output = subprocess.check_output(
        "cat /etc/passwd | grep " + username,
        shell=True
    )
    return output


def save_orders(filename):
    # Security: pickle is unsafe for untrusted data
    with open(filename, "wb") as f:
        pickle.dump(orders, f)


def load_orders(filename):
    # Security: loading untrusted pickle data
    with open(filename, "rb") as f:
        data = pickle.load(f)
    return data


def calculate_tax(amount, rate):
    # Bug: integer division loses decimal precision
    tax = amount * rate / 100
    total = amount + tax
    # Bug: missing return statement
    

def generate_report():
    # Bug: will crash if orders list is empty
    average = total_revenue / len(orders)
    print("Average order value: " + average)
    return average