import streamlit as st
import time
import database as db
import pandas as pd
from io import BytesIO
import base64

# session state
if 'page' not in st.session_state: 
    st.session_state['page'] = 'login'
if 'logged_in' not in st.session_state: 
    st.session_state['logged_in'] = False
if 'username' not in st.session_state: 
    st.session_state['username'] = ""
if 'current_module' not in st.session_state: 
    st.session_state['current_module'] = ""
if 'admin_user' not in st.session_state: 
    st.session_state['admin_user'] = ""
if 'admin_brand' not in st.session_state: 
    st.session_state['admin_brand'] = ""
if 'admin_logo' not in st.session_state: 
    st.session_state['admin_logo'] = None

# --- 2. NAVIGATION HELPERS ---
def switch_page(page_name):
    st.session_state['page'] = page_name
    st.rerun()

# MODULES (Redirect to specific dashboards)
def navigate_to(module_name):
    if module_name == "CRM" and st.session_state['admin_brand']:
        st.session_state['page'] = 'admin_dashboard'
        st.rerun()
    elif module_name == "Rental":
        st.session_state['page'] = 'rental_dashboard'
        st.rerun()
    elif module_name == "Restaurant":
        st.session_state['page'] = 'restaurant_dashboard'
        st.rerun()
    elif module_name in ["Invoicing", "Accounting", "Expenses"]:
        st.session_state['page'] = 'finance_dashboard'
        st.rerun()
    elif module_name in ["Email Marketing", "SMS Marketing", "Social Marketing", "Survey"]:
        st.session_state['page'] = 'marketing_dashboard'
        st.rerun()
    elif module_name in ["Employee Directory", "Recruitment", "Attendance", "Attendance / Payroll"]:
        st.session_state['page'] = 'hr_dashboard'
        st.rerun()
    elif module_name in ["Project", "Timesheets", "Field Service"]:
        st.session_state['page'] = 'services_dashboard'
        st.rerun()
    else:
        st.session_state['current_module'] = module_name
        st.session_state['page'] = 'module_view'
        st.rerun()


# Shared components
def render_admin_sidebar():
    """Renders the logo and navigation for all Admin pages"""
    with st.sidebar:
        st.header(f"🔧 {st.session_state['admin_brand']}")
        
        # Display Logo
        if st.session_state['admin_logo']:
            try:
                b64_logo = base64.b64encode(st.session_state['admin_logo']).decode()
                logo_html = f"""
                    <div style="display: flex; justify-content: left; margin-bottom: 20px;">
                        <img src="data:image/png;base64,{b64_logo}" 
                             style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 3px solid #ccc;">
                    </div>
                """
                st.markdown(logo_html, unsafe_allow_html=True)
            except:
                st.info("Logo Error")
        else:
            st.info("No Logo")
            
        st.divider()
        if st.button("🏠 Module Hub"):
            switch_page('main')
        if st.button("⬅️ Back to General Stores"):
            switch_page('admin_dashboard')
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.session_state['admin_brand'] = "" 
            st.session_state['page'] = 'login'
            st.rerun()


# ==========================================
#        NEW MODULE: RENTAL MANAGEMENT
# ==========================================
def render_rental_dashboard():
    render_admin_sidebar()
    st.title("🏠 Rental Management System")
    st.button("⬅️ Back to Hub", on_click=lambda: switch_page('main'))

    tab1, tab2 = st.tabs(["🔑 New Tenant Entry", "🚪 Vacated / History"])

    # TAB 1: NEW ENTRY
    with tab1:
        st.subheader("Book a Room")
        with st.form("rental_entry"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Tenant Name")
            phone = c2.text_input("Phone Number")
            
            c3, c4 = st.columns(2)
            room = c3.text_input("Room Number/ID")
            rent = c4.number_input("Monthly Rent ($)", min_value=0.0)
            deposit = st.number_input("Security Deposit ($)", min_value=0.0)
            
            if st.form_submit_button("Save Booking"):
                if name and room:
                    success, msg = db.add_rental_booking(name, room, rent, deposit, phone)
                    if success: st.success(msg)
                    else: st.error(msg)
                else:
                    st.warning("Name and Room Number are required.")
        
        st.divider()
        st.subheader("Current Occupants")
        data = db.get_rental_data("Occupied")
        if data:
            st.dataframe(pd.DataFrame(data, columns=["Name", "Room", "Rent", "Status", "Join Date", "Vacated Date"]), use_container_width=True)

    # TAB 2: VACATED DATA
    with tab2:
        st.subheader("Vacate a Room")
        with st.form("vacate_form"):
            v_room = st.text_input("Enter Room Number to Vacate")
            if st.form_submit_button("Mark as Vacated"):
                success, msg = db.vacate_rental(v_room)
                if success: st.success(msg)
                else: st.error(msg)
        
        st.divider()
        st.subheader("Rental History (All)")
        hist_data = db.get_rental_data("All")
        if hist_data:
            st.dataframe(pd.DataFrame(hist_data, columns=["Name", "Room", "Rent", "Status", "Join Date", "Vacated Date"]), use_container_width=True)



# ==========================================
#        NEW MODULE: RESTAURANT MANAGEMENT
# ==========================================
def render_restaurant_dashboard():
    render_admin_sidebar()
    st.title("🍴 Restaurant Management")
    st.button("⬅️ Back to Hub", on_click=lambda: switch_page('main'))

    tab1, tab2 = st.tabs(["👨‍🍳 Worker Details", "🍔 Sales & Billing"])

    # TAB 1: WORKERS
    with tab1:
        st.subheader("Restaurant Staff")
        with st.expander("Add New Chef/Waiter"):
            with st.form("rest_worker"):
                n=st.text_input("Name"); e=st.text_input("Email"); p=st.text_input("Phone")
                role=st.selectbox("Role", ["Chef", "Waiter", "Cleaner", "Manager"])
                s=st.number_input("Salary")
                a=st.text_area("Address")
                if st.form_submit_button("Add Staff"):
                    db.add_new_worker(n,e,p,a,role,s) 
                    st.success("Staff Added")
        
        # --- FIX: Manually filter columns to avoid mismatch error ---
        workers = db.get_all_workers(only_active=False)
        
        if workers:
            df = pd.DataFrame(workers, columns=["ID", "Name", "Email", "Phone", "Addr", "Role", "Salary", "Joined", "Removed"])
            
            active_df = df[df['Removed'].isnull()]
        
            st.dataframe(active_df[["ID", "Name", "Role", "Phone", "Salary"]], use_container_width=True)
        else:
            st.info("No staff found.")

    # TAB 2: SALES
    with tab2:
        st.subheader("New Table Order")
        with st.form("rest_sales"):
            c1, c2 = st.columns(2)
            tbl = c1.number_input("Table Number", min_value=1, step=1)
            pay = c2.selectbox("Payment Mode", ["Cash", "Card", "Online"])
            
            items = st.text_area("Items Ordered (e.g. 2x Biryani, 1x Coke)")
            amt = st.number_input("Total Bill Amount", min_value=0.0)
            
            if st.form_submit_button("Generate Bill"):
                if amt > 0:
                    db.add_restaurant_sale(tbl, items, amt, pay)
                    st.success("Bill Saved!")
                else:
                    st.warning("Enter amount.")
        
        st.divider()
        st.subheader("Daily Sales Report")
        sales = db.get_restaurant_sales()
        if sales:
            st.dataframe(pd.DataFrame(sales, columns=["ID", "Table No", "Items", "Amount", "Mode", "Time"]), use_container_width=True)



# ==========================================
#        EXISTING MODULES (GENERAL STORES)
# ==========================================

def render_module_page():
    module = st.session_state['current_module']
    
    with st.sidebar:
        st.header(f"📂 {module}")
        if st.button("⬅️ Back to Dashboard"):
            switch_page('main')
        st.divider()

    if module == "CRM":
        st.title("🤝 General Stores Portal")
        st.info("Provision a new General Stores instance.")
        
        with st.form("crm_form"):
            st.subheader("Instance Details")
            st.write(f"**Creating Instance for:** {st.session_state['username']}")
            brand_name = st.text_input("Brand Name")
            brand_color = st.color_picker("Brand Color", "#00f9d9")
            logo_file = st.file_uploader("Upload Logo", type=['png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("Generate Instance"):
                if brand_name:
                    logo_bytes = logo_file.read() if logo_file else None
                    success, msg = db.add_crm_instance(st.session_state['username'], brand_name, brand_color, logo_bytes)
                    if success:
                        st.success(f"✅ {msg}")
                        st.session_state['admin_user'] = st.session_state['username']
                        st.session_state['admin_brand'] = brand_name
                        st.session_state['admin_logo'] = logo_bytes
                        time.sleep(1)
                        switch_page('admin_dashboard')
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("Brand Name is required.")
                    
    elif module == "invoicing":
        st.title("🧾 Invoicing (Generic)")
        st.text_input("Items Sold")
        st.number_input("Quantities")
        st.number_input("Total Amount")
        st.button("Generate Invoice")
        
    else:
        st.title(f"🛠️ {module}")
        st.warning("🚧 This module is currently under construction.")


#adim render
def render_admin_dashboard():
    render_admin_sidebar()
    st.title(f"🚀 {st.session_state['admin_brand']} Admin Dashboard")
    st.success(f"Instance Active | User: {st.session_state['admin_user']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🤖 AI Analysis Simulation", use_container_width=True):
            switch_page('ai_analysis')
    with col2:
        if st.button("⚙️ Optional Modules", use_container_width=True):
            switch_page('optional_modules')
            
    col3, col4 = st.columns(2)
    with col3:
        if st.button("👷 Worker Details", use_container_width=True):
            switch_page('worker_details')
    with col4:
        if st.button("📅 Worker Attendance", use_container_width=True):
            switch_page('worker_attendance')

def render_ai_analysis():
    render_admin_sidebar()
    st.title("🤖 AI Analysis Simulation")
    st.file_uploader("Upload Dataset (CSV/Excel)")
    st.chat_input("Ask something about your data...")

def render_optional_modules():
    render_admin_sidebar()
    st.title("⚙️ Optional Modules")
    col1, col2 = st.columns(2)
    with col1:
        st.info("📦 **Inventory Flow**")
        if st.button("Open Inventory Flow", use_container_width=True):
            switch_page('inventory_flow')
    with col2:
        st.info("💳 **Intelligent Billing**")
        if st.button("Open Billing System", use_container_width=True):
            switch_page('intelligent_billing')

def render_inventory_flow():
    render_admin_sidebar()
    st.title("📦 Inventory Flow")
    st.button("⬅️ Back to Options", on_click=lambda: switch_page('optional_modules'))
    st.file_uploader("Upload Inventory Records")
    st.chat_input("Ask about stock levels...")

def render_billing():
    render_admin_sidebar()
    st.title("💳 Intelligent Billing")
    st.button("⬅️ Back to Options", on_click=lambda: switch_page('optional_modules'))
    
    st.subheader("New Bill Entry")
    with st.form("billing_form"):
        c_name = st.text_input("Customer Name")
        item = st.text_input("Item Name")
        cost = st.number_input("Total Cost ($)", min_value=0.0, step=0.01)
        quantity = st.number_input("Enter Quantity", min_value=0)
        
        if st.form_submit_button("Update Data"):
            if c_name and item:
                success, msg = db.add_billing_entry(c_name, item, cost, quantity) 
                if success:
                    st.success(msg)
                else:
                    st.error(f"Error: {msg}")
            else:
                st.warning("Please fill in fields.")
    
    st.divider()
    st.subheader("Database Records")
    if st.button("Preview Full Billing Data"):
        data = db.get_all_billing_data()
        if data:
            df = pd.DataFrame(data, columns=["Customer ID", "Customer Name", "Item Name", "Cost", "Date", "Quantity", "Days", "Years"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No records found.")

def render_worker_details():
    render_admin_sidebar()
    st.title("👷 Worker Details Management")
    st.button("⬅️ Back to Dashboard", on_click=lambda: switch_page('admin_dashboard'))
    
    tab1, tab2 = st.tabs(["📋 Worker List", "➕ Add New Worker"])
    
    with tab1:
        st.subheader("Current Workforce")
        workers = db.get_all_workers(only_active=False)
        if workers:
            df = pd.DataFrame(workers, columns=["ID", "Name", "Email", "Phone", "Address", "Type", "Salary", "Joined", "Removed"])
            st.dataframe(df, use_container_width=True)
            st.divider()
            c1, c2 = st.columns([3, 1])
            with c1:
                fire_id = st.number_input("Enter Worker ID to Remove", step=1, min_value=0)
            with c2:
                st.write(""); st.write("") 
                if st.button("🚫 Remove Worker"):
                    if fire_id:
                        db.fire_worker(fire_id)
                        st.rerun()
        else:
            st.info("No workers found.")

    with tab2:
        st.subheader("Onboard New Worker")
        with st.form("add_worker_form"):
            col1, col2 = st.columns(2)
            with col1:
                w_name = st.text_input("Full Name")
                w_email = st.text_input("Email")
                w_phone = st.text_input("Phone Number")
            with col2:
                w_type = st.selectbox("Worker Type", ["Full-Time", "Part-Time", "Contract", "Intern"])
                w_salary = st.number_input("Salary Per Month", min_value=0.0, step=100.0)
                w_address = st.text_area("Address")
            
            if st.form_submit_button("Add Worker"):
                if w_name and w_salary:
                    success, msg = db.add_new_worker(w_name, w_email, w_phone, w_address, w_type, w_salary)
                    if success: st.success(msg)
                    else: st.error(msg)
                else:
                    st.warning("Name and Salary are required.")


def render_worker_attendance():
    render_admin_sidebar()
    st.title("📅 Worker Attendance")
    st.button("⬅️ Back to Dashboard", on_click=lambda: switch_page('admin_dashboard'))
    
    st.subheader("Mark Today's Attendance")
    active_workers = db.get_all_workers(only_active=True)
    
    if active_workers:
        data = []
        for w in active_workers:
            data.append({"ID": w[0], "Name": w[1], "Type": w[2], "Present?": False})
        df_input = pd.DataFrame(data)
        edited_df = st.data_editor(
            df_input,
            column_config={"Present?": st.column_config.CheckboxColumn("Is Present?", default=False)},
            disabled=["ID", "Name", "Type"], 
            hide_index=True,
            use_container_width=True
        )
        if st.button("💾 Save Attendance"):
            attendance_list = []
            for index, row in edited_df.iterrows():
                status = "Present" if row["Present?"] else "Absent"
                attendance_list.append({"ID": row["ID"], "Name": row["Name"], "Type": row["Type"], "Status": status})
            success, msg = db.save_attendance_bulk(attendance_list)
            if success:
                st.success(msg)
                time.sleep(1)
                st.rerun()
            else:
                st.error(msg)
    else:
        st.warning("No active workers found.")

    st.divider()
    st.subheader("Attendance History")
    history = db.get_attendance_history()
    if history:
        df_hist = pd.DataFrame(history, columns=["Worker ID", "Name", "Status", "Date"])
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("No attendance records yet.")


# ==========================================
#        MODULE 4: FINANCE 
# ==========================================
def render_finance_dashboard():
    render_admin_sidebar()
    st.title("📒 Finance & Accounting")
    st.button("⬅️ Back to Hub", on_click=lambda: switch_page('main'))
    
    tab1, tab2, tab3 = st.tabs(["🧾 Invoicing", "📊 General Ledger", "💸 Expense Tracker"])

    # TAB 1: INVOICING
    with tab1:
        st.subheader("Create New Invoice")
        with st.form("new_invoice_form"):
            c1, c2 = st.columns(2)
            cust = c1.text_input("Customer Name")
            amt = c2.number_input("Invoice Amount ($)", min_value=0.0)
            
            c3, c4 = st.columns(2)
            d_date = c3.date_input("Due Date")
            stat = c4.selectbox("Status", ["Pending", "Paid", "Overdue"])
            
            if st.form_submit_button("Generate Invoice"):
                if cust and amt > 0:
                    # NOTE: Ensure db.add_invoice exists in database.py
                    try:
                        db.add_invoice(cust, amt, d_date, stat)
                        st.success("Invoice Created!")
                    except Exception as e:
                        st.error("Database function missing: add_invoice")
                else:
                    st.warning("Required fields missing.")
        
        st.divider()
        st.subheader("Invoice History")
        try:
            inv_data = db.get_invoices()
            if inv_data:
                df = pd.DataFrame(inv_data, columns=["Invoice ID", "Customer", "Amount", "Due Date", "Status", "Created On"])
                st.dataframe(df, use_container_width=True)
        except:
            st.info("No invoices found.")

    # TAB 2: GENERAL LEDGER
    with tab2:
        st.subheader("Chart of Accounts")
        ledger = db.get_ledger()
        if ledger: 
            st.dataframe(pd.DataFrame(ledger, columns=["Code", "Account Name", "Type", "Balance"]), use_container_width=True)
        else: 
            st.info("Ledger is empty.")

    # TAB 3: EXPENSES
    with tab3:
        st.subheader("Log Company Expense")
        with st.form("exp_form"):
            c1, c2 = st.columns(2)
            cat = c1.text_input("Category")
            amt = c2.number_input("Amount ($)", min_value=0.0)
            desc = st.text_input("Description")
            
            if st.form_submit_button("Log Expense"): 
                db.add_expense(cat, desc, amt, st.session_state['username'])
                st.success("Expense Logged Successfully")
        
        st.divider()
        st.subheader("Recent Expenses")
        if hasattr(db, 'get_expenses'):
            expenses = db.get_expenses()
            if expenses:
                st.dataframe(pd.DataFrame(expenses, columns=["ID", "Category", "Description", "Amount", "Date", "User"]), use_container_width=True)


# ==========================================
#        MODULE 5: MARKETING
# ==========================================
def render_marketing_dashboard():
    render_admin_sidebar()
    st.title("📢 Marketing Hub")
    st.button("⬅️ Back to Hub", on_click=lambda: switch_page('main'))
    
    tab1, tab2 = st.tabs(["🚀 Campaigns", "🎯 Leads"])

    with tab1:
        st.subheader("Active Campaigns")
        camps = db.get_campaigns()
        if camps: 
            st.dataframe(pd.DataFrame(camps, columns=["ID", "Name", "Audience", "Budget", "Status", "Date"]), use_container_width=True)
        
        with st.expander("Launch New Campaign"):
            with st.form("mc"):
                n=st.text_input("Name"); t=st.text_input("Target Audience"); b=st.number_input("Budget")
                if st.form_submit_button("Launch"): 
                    db.add_campaign(n, t, b, "Active")
                    st.rerun()

    with tab2:
        st.subheader("Lead Capture")
        with st.form("lead_form"):
            n=st.text_input("Lead Name"); e=st.text_input("Email"); s=st.selectbox("Source", ["Web", "Social"])
            if st.form_submit_button("Add Lead"):
                try: 
                    db.add_lead(n, e, s)
                    st.success("Lead Added")
                except: st.error("DB Error: add_lead missing")
        
        try:
            leads = db.get_leads()
            if leads: st.dataframe(pd.DataFrame(leads, columns=["ID", "Name", "Email", "Source", "Status", "Date"]), use_container_width=True)
        except: st.info("No leads.")



# ==========================================
#        MODULE 6: HR
# ==========================================
def render_hr_dashboard():
    render_admin_sidebar()
    st.title("👥 Human Resources")
    st.button("⬅️ Back to Hub", on_click=lambda: switch_page('main'))
    
    tab1, tab2, tab3 = st.tabs(["📂 Directory", "📅 Leave Management", "💰 Payroll"])

    with tab1:
        if st.button("Manage Workers Table", use_container_width=True): switch_page('worker_details')
        workers = db.get_all_workers(True)
        if workers: st.dataframe(pd.DataFrame(workers, columns=["ID", "Name", "Role", "Phone", "Salary"]), use_container_width=True)

    with tab2:
        with st.form("leave"):
            n=st.text_input("Employee Name"); t=st.selectbox("Type", ["Sick", "Vacation"]); d=st.number_input("Days", min_value=1)
            if st.form_submit_button("Request Leave"):
                try: db.add_leave_request(n, t, d); st.success("Sent")
                except: st.error("DB Error")
        
        try:
            leaves = db.get_leave_requests()
            if leaves: st.dataframe(pd.DataFrame(leaves, columns=["ID", "Name", "Type", "Days", "Status", "Date"]), use_container_width=True)
        except: st.info("No requests")

    with tab3:
        with st.form("pay"):
            n=st.text_input("Employee"); m=st.text_input("Month"); a=st.number_input("Amount")
            if st.form_submit_button("Process Pay"):
                try: db.add_payroll(n, m, a); st.success("Paid")
                except: st.error("DB Error")
        
        try:
            pay = db.get_payroll_history()
            if pay: st.dataframe(pd.DataFrame(pay, columns=["ID", "Name", "Month", "Amount", "Date"]), use_container_width=True)
        except: st.info("No history")



# ==========================================
#        MODULE 7: SERVICES
# ==========================================
def render_services_dashboard():
    render_admin_sidebar()
    st.title("🛠️ Services & Support")
    st.button("⬅️ Back to Hub", on_click=lambda: switch_page('main'))
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Ticket Queue")
        tickets = db.get_tickets()
        if tickets: st.dataframe(pd.DataFrame(tickets, columns=["ID", "Customer", "Priority", "Status", "Date", "Issue"]), use_container_width=True)
    
    with col2:
        with st.form("ticket"):
            st.subheader("New Ticket")
            n=st.text_input("Customer"); i=st.text_area("Issue"); p=st.selectbox("Priority", ["High", "Medium", "Low"])
            if st.form_submit_button("Create"):
                db.add_ticket(n, i, p)
                st.rerun()


# ==========================================
#        EXCEL BULK UPLOAD LOGIC 
# ==========================================
def render_excel_upload_page():
    render_admin_sidebar()
    st.title("📂 Bulk Data Upload")
    if st.button("⬅️ Back to Hub"): switch_page('main')
    
    st.write("---")
    
    # 1. File Uploader
    uploaded_file = st.file_uploader("Upload Excel (Billing)", type=['xlsx'])
    
    # 2. Process Logic
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            
            # Check if Excel has correct columns
            required_cols = {'Customer', 'Item', 'Cost', 'Quantity'}
            if required_cols.issubset(df.columns):
                
                st.success(f"{len(df)} rows found.")
                st.dataframe(df.head())
                
                if st.button("📥 Import Data", use_container_width=True):
                    progress_bar = st.progress(0)
                    
                    for index, row in df.iterrows():
                        # Call your existing database function
                        db.add_billing_entry(
                            row['Customer'], 
                            row['Item'], 
                            float(row['Cost']), 
                            int(row['Quantity'])
                        )
                        # Update progress
                        progress_bar.progress((index + 1) / len(df))
                    
                    st.success("Data Imported Successfully!")
                    time.sleep(1)
                    switch_page('admin_dashboard')
            else:
                st.error("Excel must have columns: Customer, Item, Cost, Quantity")
        except Exception as e:
            st.error(f"Error reading file: {e}")

# ==========================================
#        ABOUT PAGE
# ==========================================
def render_about_page():
    render_admin_sidebar()
    st.title("ℹ️ About Zero-Code Portal")
    st.button("⬅️ Back to Hub", on_click=lambda: switch_page('main'))
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🚀 The Future of Business Management
        
        The **Zero-Code ERP Portal** is a comprehensive Enterprise Resource Planning solution designed to streamline daily operations without writing a single line of code.
        
        It integrates disparate business functions into a single, unified interface, allowing business owners to focus on growth rather than logistics.
        """)
    
    with col2:
        st.info("**Version:** 1.0.0\n\n**Status:** Production Ready\n\n**Tech:** Streamlit & SQL")

    st.subheader("📦 Integrated Modules")
    
    c1, c2 = st.columns(2)
    with c1:
        st.success("**🤝 General Stores:** Complete Inventory & Billing.")
        st.success("**🏠 Rental System:** Tenant Booking & Vacancy Tracking.")
        st.success("**🍴 Restaurant:** Table Orders & Staff Management.")
        st.success("**📒 Finance:** Invoicing, Ledger & Expense Tracking.")
    with c2:
        st.info("**👥 Human Resources:** Payroll, Leave & Attendance.")
        st.info("**📢 Marketing:** Lead Generation & Campaign Management.")
        st.info("**🛠️ Services:** Ticketing & Customer Support.")
        
    st.markdown("---")
    st.caption("© 2026 Zero-Code ERP Solutions. All Rights Reserved.")


# ==========================================
#        MAIN ROUTING LOGIC
# ==========================================
if st.session_state['logged_in']:
    
    if st.session_state['page'] == 'main':
        st.sidebar.markdown(f"**User:** {st.session_state['username']}")
        if st.sidebar.button("ℹ️ About Portal", use_container_width=True):
            st.session_state['page'] = 'about'
            st.rerun()  
        # FIX: Button switches to NEW PAGE so main grid disappears
        if st.sidebar.button("Generate sample data", use_container_width=True):
            st.session_state['page'] = 'excel_upload'
            st.rerun()
            
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['admin_brand'] = "" 
            st.session_state['page'] = 'login'
            st.rerun()

        st.title("🚀 Zero-Code ERP Portal")
        
        # --- SALES SECTION ---
        st.subheader("Sales & Properties")
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button("🤝 General Stores", use_container_width=True): navigate_to("CRM")
        with c2: 
            if st.button("🏠 Rental Management", use_container_width=True): navigate_to("Rental")
        with c3: 
            if st.button("🍴 Restaurant", use_container_width=True): navigate_to("Restaurant")
        
        # --- FINANCE SECTION ---
        st.subheader("Finance")
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button("Invoicing", use_container_width=True): navigate_to("Invoicing")
        with c2: 
            if st.button("Accounting", use_container_width=True): navigate_to("Accounting")
        with c3: 
            if st.button("Expenses", use_container_width=True): navigate_to("Expenses")

        # --- SERVICES SECTION ---
        st.subheader("Services")
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button("Project", use_container_width=True): navigate_to("Project")
        with c2: 
            if st.button("Timesheets", use_container_width=True): navigate_to("Timesheets")
        with c3: 
            if st.button("Field Service", use_container_width=True): navigate_to("Field Service")

        # --- MARKETING SECTION ---
        st.subheader("Marketing")
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button("Email Marketing", use_container_width=True): navigate_to("Email Marketing")
        with c2: 
            if st.button("SMS Marketing", use_container_width=True): navigate_to("SMS Marketing")
        with c3: 
            if st.button("Survey", use_container_width=True): navigate_to("Survey")
        
        if st.button("Social Marketing", use_container_width=True): navigate_to("Social Marketing")

        # --- HUMAN RESOURCES SECTION ---
        st.subheader("Human Resources")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Employee Directory", use_container_width=True): navigate_to("Employee Directory")
        with c2:
            if st.button("Recruitment", use_container_width=True): navigate_to("Recruitment")
        with c3:
            if st.button("Attendance / Payroll", use_container_width=True): navigate_to("Attendance / Payroll")

    # --- PAGE ROUTING ---
    elif st.session_state['page'] == 'module_view': 
        render_module_page()
    elif st.session_state['page'] == 'admin_dashboard': 
        render_admin_dashboard()
    elif st.session_state['page'] == 'ai_analysis': 
        render_ai_analysis()
    elif st.session_state['page'] == 'optional_modules': 
        render_optional_modules()
    elif st.session_state['page'] == 'inventory_flow': 
        render_inventory_flow()
    elif st.session_state['page'] == 'intelligent_billing': 
        render_billing()
    elif st.session_state['page'] == 'worker_details': 
        render_worker_details()
    elif st.session_state['page'] == 'worker_attendance':
        render_worker_attendance()
    elif st.session_state['page'] == 'rental_dashboard':
        render_rental_dashboard()
    elif st.session_state['page'] == 'restaurant_dashboard': 
        render_restaurant_dashboard()
    elif st.session_state['page'] == 'finance_dashboard': 
        render_finance_dashboard()
    elif st.session_state['page'] == 'marketing_dashboard': 
        render_marketing_dashboard()
    elif st.session_state['page'] == 'hr_dashboard': 
        render_hr_dashboard()
    elif st.session_state['page'] == 'services_dashboard': 
        render_services_dashboard()
    elif st.session_state['page'] == 'excel_upload': 
        render_excel_upload_page()
    elif st.session_state['page'] == 'about': 
        render_about_page()

else:
    # --- LOGIN LOGIC ---
    if st.session_state['page'] == 'login':
        st.title("🔐 Login")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                success, name = db.login_user(email, password)
                if success:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = name
                    has_crm, crm_data = db.get_crm_for_user(name)
                    if has_crm:
                        st.session_state['admin_user'] = name
                        st.session_state['admin_brand'] = crm_data[0]
                        st.session_state['admin_logo'] = crm_data[2]
                        st.toast(f"Welcome back! {crm_data[0]} loaded.")
                    st.session_state['page'] = 'main'
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        st.write("---")
        if st.button("Register"):
            st.session_state['page'] = 'register'
            st.rerun()

    # registeration logic
    elif st.session_state['page'] == 'register':
        st.title("📝 Register")
        with st.form("register_form"):
            u = st.text_input("Username")
            e = st.text_input("Email")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Sign Up"):
                if db.register_user(u, e, p):
                    st.success("Registered! Login now.")
                    time.sleep(1)
                    st.session_state['page'] = 'login'
                    st.rerun()
        st.write("---")
        if st.button("Back"):
            st.session_state['page'] = 'login'
            st.rerun()