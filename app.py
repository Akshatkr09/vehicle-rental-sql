import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

DB_PATH = "rental.db"

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query, params)
    data = cur.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

st.set_page_config(page_title="Vehicle Rental System - KIIT", layout="wide")

st.title("🚗 Vehicle Rental Management System")
st.caption("Bike & Car Rentals for KIIT - Powered by SQLite & Streamlit")

menu = ["View Vehicles", "Add Customer", "New Rental", "Return Vehicle", "Payments", "Reports"]
choice = st.sidebar.radio("📌 Menu", menu)

# --- View Vehicles ---
if choice == "View Vehicles":
    st.subheader("Available Vehicles")
    data = run_query("SELECT vehicle_id, vehicle_type, brand, model, reg_no, rent_per_day, available FROM Vehicles", fetch=True)
    df = pd.DataFrame(data, columns=["ID","Type","Brand","Model","Reg No","Rent/Day","Available"])
    st.dataframe(df)

# --- Add Customer ---
elif choice == "Add Customer":
    st.subheader("Add New Customer")
    with st.form("add_customer"):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        aadhaar = st.text_input("Aadhaar No")
        dl = st.text_input("Driving License No")
        address = st.text_area("Address")
        submit = st.form_submit_button("Add Customer")
    if submit:
        run_query("INSERT INTO Customers (name, phone, email, aadhaar_no, dl_no, address) VALUES (?,?,?,?,?,?)",
                  (name, phone, email, aadhaar, dl, address))
        st.success(f"Customer {name} added successfully!")

# --- New Rental ---
elif choice == "New Rental":
    st.subheader("Book a Vehicle")
    customers = run_query("SELECT customer_id, name FROM Customers", fetch=True)
    vehicles = run_query("SELECT vehicle_id, brand||' '||model FROM Vehicles WHERE available=1", fetch=True)
    
    if customers and vehicles:
        cust = st.selectbox("Select Customer", customers, format_func=lambda x: x[1])
        veh = st.selectbox("Select Vehicle", vehicles, format_func=lambda x: x[1])
        start = st.date_input("Start Date", date.today())
        end = st.date_input("End Date", date.today())
        rent_days = (end - start).days + 1
        rent_amt = run_query("SELECT rent_per_day FROM Vehicles WHERE vehicle_id=?", (veh[0],), fetch=True)[0][0]
        total = rent_days * rent_amt
        st.write(f"💰 Estimated Total = ₹{total}")
        if st.button("Confirm Booking"):
            run_query("INSERT INTO Rentals (customer_id, vehicle_id, start_date, end_date, total_amount) VALUES (?,?,?,?,?)",
                      (cust[0], veh[0], start, end, total))
            run_query("UPDATE Vehicles SET available=0 WHERE vehicle_id=?", (veh[0],))
            st.success("Rental created successfully!")
    else:
        st.warning("Add customers & ensure vehicles are available.")

# --- Return Vehicle ---
elif choice == "Return Vehicle":
    st.subheader("Return Vehicle")
    rentals = run_query("SELECT rental_id, vehicle_id, customer_id, start_date, end_date FROM Rentals WHERE actual_return IS NULL", fetch=True)
    if rentals:
        sel = st.selectbox("Select Rental", rentals, format_func=lambda x: f"Rental {x[0]} (Cust:{x[2]} Veh:{x[1]})")
        today = st.date_input("Return Date", date.today())
        if st.button("Return Now"):
            fine = 0
            if today > date.fromisoformat(sel[4]):
                fine = (today - date.fromisoformat(sel[4])).days * 200
            run_query("UPDATE Rentals SET actual_return=?, fine_amount=? WHERE rental_id=?",
                      (today, fine, sel[0]))
            run_query("UPDATE Vehicles SET available=1 WHERE vehicle_id=?", (sel[1],))
            st.success(f"Vehicle returned. Fine = ₹{fine}")
    else:
        st.info("No active rentals found.")

# --- Payments ---
elif choice == "Payments":
    st.subheader("Record Payment")
    unpaid = run_query("SELECT rental_id, total_amount, fine_amount FROM Rentals WHERE payment_status='Pending'", fetch=True)
    if unpaid:
        sel = st.selectbox("Select Rental", unpaid, format_func=lambda x: f"Rental {x[0]} - Due ₹{x[1]+x[2]}")
        method = st.selectbox("Payment Method", ["Cash","UPI","PayTM","Card"])
        if st.button("Mark Paid"):
            amt = sel[1]+sel[2]
            run_query("INSERT INTO Payments (rental_id, amount, method) VALUES (?,?,?)", (sel[0], amt, method))
            run_query("UPDATE Rentals SET payment_status='Paid' WHERE rental_id=?", (sel[0],))
            st.success("Payment recorded!")
    else:
        st.info("No pending payments.")

# --- Reports ---
elif choice == "Reports":
    st.subheader("Reports")
    revenue = run_query("SELECT SUM(amount) FROM Payments", fetch=True)[0][0]
    rentals = run_query("SELECT COUNT(*) FROM Rentals", fetch=True)[0][0]
    st.metric("Total Revenue", f"₹{revenue if revenue else 0}")
    st.metric("Total Rentals", rentals)
