import pyodbc
import streamlit as st
import random 

# SSMS configuration
SERVER = "YEMINENIBALAJI\\SQLEXPRESS"
DATABASE = "sequal_ai"
USERNAME = "sa"
PASSWORD = "yemineni@123"

# SSMS connection
def get_connection():
    """Establishes connection to SQL Server"""
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
    )
    try:
        return pyodbc.connect(connection_string)
    except Exception as e:
        st.error(f"❌ Connection Failed: {e}")
        return None

# Registeration table
def register_user(username, email, password):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Email FROM register WHERE Email = ?", (email,))
            if cursor.fetchone():
                st.warning("⚠️ Email already registered.")
                return False
            else:
                cursor.execute("INSERT INTO register (Username, Email, Password) VALUES (?, ?, ?)", 
                               (username, email, password))
                conn.commit()
                return True
        except Exception as e:
            st.error(f"❌ Database Error: {e}")
            return False
        finally:
            conn.close()
    return False

# login table
def login_user(email, password):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Username FROM register WHERE Email = ? AND Password = ?", (email, password))
            result = cursor.fetchone()
            if result:
                return True, result[0]
            else:
                return False, None
        except Exception as e:
            return False, None
        finally:
            conn.close()
    return False, None

# CRM store table
def add_crm_instance(instance_user, brand_name, brand_color, logo_bytes):
    """Creates a new instance in CRM_Instances table"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            insert_query = """
            INSERT INTO CRM_Instances (InstanceUser, BrandName, BrandColor, Logo) 
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(insert_query, (instance_user, brand_name, brand_color, logo_bytes))
            conn.commit()
            return True, "CRM Instance Created Successfully!"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    return False, "Connection Failed"

# CRM get table
def get_crm_for_user(username):
    """Checks if a user already has a CRM instance and returns it"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Get the most recent instance for this user
            query = "SELECT TOP 1 BrandName, BrandColor, Logo FROM CRM_Instances WHERE InstanceUser = ?"
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            
            if row:
                # Returns: (BrandName, BrandColor, LogoBytes)
                return True, row 
            else:
                return False, None
        except Exception as e:
            return False, None
        finally:
            conn.close()
    return False, None

# store bill details in table
def add_billing_entry(customer_name, item_name, cost, quantity):
    """Inserts data into the billing table"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Generate random ID since CustomerID is not IDENTITY
            cust_id = random.randint(10000, 99999)
            
            # Note: We do NOT insert 'Dateofentering'. SQL fills it automatically.
            query = "INSERT INTO billing (CustomerID, Customername, Itemname, cost, quantity) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (cust_id, customer_name, item_name, cost, quantity))
            conn.commit()
            return True, "Bill Saved Successfully!"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    return False, "Connection Error"

# get details from table
def get_all_billing_data():
    """Retrieves all rows including the Date"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Select the new column
            cursor.execute("""SELECT 
                           CustomerID, Customername, Itemname, cost, Dateofentering, quantity, days, years 
                           FROM billing
                           ORDER BY Dateofentering DESC""")
            
            rows = cursor.fetchall()
            
            data = []
            for row in rows:
                data.append((row.CustomerID, row.Customername, row.Itemname, row.cost, row.Dateofentering, row.quantity, row.days, row.years))
            
            return data
        except Exception as e:
            return []
        finally:
            conn.close()
    return []

# workers details table
def add_new_worker(name, email, phone, address, w_type, salary):
    """Inserts a new worker into the Workers table"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            worker_id = random.randint(10000, 99999) # Generate ID
            
            # AdmittedDate is automatic (GETDATE) in SQL
            query = """
            INSERT INTO Workers (WorkerID, Name, Email, PhoneNumber, Address, WorkerType, Salary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query, (worker_id, name, email, phone, address, w_type, salary))
            conn.commit()
            return True, f"Worker Added! ID: {worker_id}"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    return False, "Connection Error"

# get worker details
def get_all_workers(only_active=False):
    """Fetches workers. If only_active is True, hides fired workers."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if only_active:
                query = "SELECT WorkerID, Name, WorkerType FROM Workers WHERE RemovedDate IS NULL"
            else:
                query = "SELECT WorkerID, Name, Email, PhoneNumber, Address, WorkerType, Salary, AdmittedDate, RemovedDate FROM Workers"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Return list of tuples
            return [tuple(row) for row in rows]
        except Exception as e:
            return []
        finally:
            conn.close()
    return []

# fire workers
def fire_worker(worker_id):
    """Updates the RemovedDate for a worker"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Set RemovedDate to Current Time
            query = "UPDATE Workers SET RemovedDate = GETDATE() WHERE WorkerID = ?"
            cursor.execute(query, (worker_id,))
            conn.commit()
            return True, "Worker Status Updated (Fired/Removed)"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    return False, "Connection Error"

# save attendance data in table
def save_attendance_bulk(attendance_data):
    """
    Expects a list of dicts: [{'ID': 123, 'Name': 'John', 'Type': 'Full', 'Status': 'Present'}]
    """
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "INSERT INTO Attendance (AttendanceID, WorkerID, WorkerName, WorkerType, Status) VALUES (?, ?, ?, ?, ?)"
            
            count = 0
            for row in attendance_data:
                att_id = random.randint(100000, 999999)
                cursor.execute(query, (att_id, row['ID'], row['Name'], row['Type'], row['Status']))
                count += 1
            
            conn.commit()
            return True, f"Marked attendance for {count} workers."
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    return False, "Connection Error"

#get data
def get_attendance_history():
    """Fetches all attendance logs"""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT WorkerID, WorkerName, Status, Date FROM Attendance ORDER BY Date DESC"
            cursor.execute(query)
            return [tuple(row) for row in cursor.fetchall()]
        except:
            return []
        finally:
            conn.close()
    return []

# --- 1. FINANCE: EXPENSES ---
def add_expense(category, desc, amount, user):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            exp_id = random.randint(10000, 99999)
            query = "INSERT INTO Finance_Expenses (ExpenseID, Category, Description, Amount, SubmittedBy) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (exp_id, category, desc, amount, user))
            conn.commit()
            return True, "Expense Logged!"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    return False, "Conn Error"

def get_expenses():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ExpenseID, Category, Description, Amount, ExpenseDate, SubmittedBy FROM Finance_Expenses ORDER BY ExpenseDate DESC")
            return [tuple(row) for row in cursor.fetchall()]
        except: return []
        finally: conn.close()
    return []


# --- SALES FUNCTIONS ---
def add_sales_order(customer, amount, status):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            oid = random.randint(1000, 9999)
            query = "INSERT INTO Sales_Orders (OrderID, CustomerName, Amount, Status) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (oid, customer, amount, status))
            conn.commit()
            return True, "Order Created Successfully"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    return False, "Connection Error"

def get_sales_orders():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT OrderID, CustomerName, Amount, Status, OrderDate FROM Sales_Orders ORDER BY OrderDate DESC")
            return [tuple(row) for row in cursor.fetchall()]
        except: return []
        finally: conn.close()
    return []

# --- FINANCE FUNCTIONS ---
def get_ledger():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT AccountCode, AccountName, AccountType, Balance FROM Accounting_Ledger")
            return [tuple(row) for row in cursor.fetchall()]
        except: return []
        finally: conn.close()
    return []

# --- MARKETING FUNCTIONS ---
def add_campaign(name, audience, budget, status):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cid = random.randint(1000, 9999)
            query = "INSERT INTO Marketing_Campaigns (CampaignID, CampaignName, TargetAudience, Budget, Status) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (cid, name, audience, budget, status))
            conn.commit()
            return True, "Campaign Launched!"
        except Exception as e:
            return False, str(e)
        finally:
            conn.close()
    return False, "Connection Error"

def get_campaigns():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT CampaignID, CampaignName, TargetAudience, Budget, Status, StartDate FROM Marketing_Campaigns")
            return [tuple(row) for row in cursor.fetchall()]
        except: return []
        finally: conn.close()
    return []

def add_rental_booking(name, room, rent, deposit, phone):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            bid = random.randint(10000, 99999)
            query = """INSERT INTO Rental_Bookings 
                       (BookingID, TenantName, RoomNumber, MonthlyRent, SecurityDeposit, Phone, Status) 
                       VALUES (?, ?, ?, ?, ?, ?, 'Occupied')"""
            cursor.execute(query, (bid, name, room, rent, deposit, phone))
            conn.commit()
            return True, "Tenant Booked Successfully!"
        except Exception as e: return False, str(e)
        finally: conn.close()
    return False, "Connection Error"

def vacate_rental(room_number):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Update status and set vacate date to now
            query = "UPDATE Rental_Bookings SET Status = 'Vacated', VacateDate = GETDATE() WHERE RoomNumber = ? AND Status = 'Occupied'"
            cursor.execute(query, (room_number,))
            if cursor.rowcount > 0:
                conn.commit()
                return True, f"Room {room_number} Marked as Vacated."
            else:
                return False, "Room not found or already vacated."
        except Exception as e: return False, str(e)
        finally: conn.close()
    return False, "Connection Error"

def get_rental_data(status="All"):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            if status == "All":
                query = "SELECT TenantName, RoomNumber, MonthlyRent, Status, JoinDate, VacateDate FROM Rental_Bookings ORDER BY JoinDate DESC"
            else:
                query = f"SELECT TenantName, RoomNumber, MonthlyRent, Status, JoinDate, VacateDate FROM Rental_Bookings WHERE Status = '{status}' ORDER BY JoinDate DESC"
            
            cursor.execute(query)
            return [tuple(row) for row in cursor.fetchall()]
        except: return []
        finally: conn.close()
    return []

# ==========================================
#       RESTAURANT MODULE FUNCTIONS
# ==========================================
def add_restaurant_sale(table_no, items, amount, mode):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            sid = random.randint(10000, 99999)
            query = "INSERT INTO Restaurant_Sales (SaleID, TableNumber, ItemsOrdered, TotalAmount, PaymentMode) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (sid, table_no, items, amount, mode))
            conn.commit()
            return True, "Order Bill Saved!"
        except Exception as e: return False, str(e)
        finally: conn.close()
    return False, "Connection Error"

def get_restaurant_sales():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT SaleID, TableNumber, ItemsOrdered, TotalAmount, PaymentMode, SaleDate FROM Restaurant_Sales ORDER BY SaleDate DESC")
            return [tuple(row) for row in cursor.fetchall()]
        except: return []
        finally: conn.close()
    return []

# ==========================================
#       MARKETING MODULE FUNCTIONS
# ==========================================
def add_lead(name, email, source, status):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            lid = random.randint(10000, 99999)
            query = "INSERT INTO Marketing_Leads (LeadID, LeadName, Email, Source, Status) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (lid, name, email, source, status))
            conn.commit()
            return True, "Lead Added!"
        except Exception as e: return False, str(e)
        finally: conn.close()
    return False, "Error"

def get_leads():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT LeadID, LeadName, Email, Source, Status, CreatedDate FROM Marketing_Leads ORDER BY CreatedDate DESC")
            return [tuple(row) for row in cursor.fetchall()]
        except: return []
        finally: conn.close()
    return []

# ==========================================
#       HR MODULE FUNCTIONS
# ==========================================
def add_leave_request(name, l_type, days):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            lid = random.randint(10000, 99999)
            query = "INSERT INTO HR_LeaveRequests (LeaveID, WorkerName, LeaveType, Days, Status) VALUES (?, ?, ?, ?, 'Pending')"
            cursor.execute(query, (lid, name, l_type, days))
            conn.commit()
            return True, "Leave Request Sent"
        except Exception as e: return False, str(e)
        finally: conn.close()
    return False, "Error"

def get_leave_requests():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT LeaveID, WorkerName, LeaveType, Days, Status, RequestDate FROM HR_LeaveRequests ORDER BY RequestDate DESC")
            return [tuple(row) for row in cursor.fetchall()]
        except: return []
        finally: conn.close()
    return []

def add_payroll(name, month, amount):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            pid = random.randint(10000, 99999)
            query = "INSERT INTO HR_Payroll (PayrollID, WorkerName, SalaryMonth, AmountPaid) VALUES (?, ?, ?, ?)"
            cursor.execute(query, (pid, name, month, amount))
            conn.commit()
            return True, "Salary Processed"
        except Exception as e: return False, str(e)
        finally: conn.close()
    return False, "Error"

def get_payroll_history():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT PayrollID, WorkerName, SalaryMonth, AmountPaid, PaymentDate FROM HR_Payroll ORDER BY PaymentDate DESC")
            return [tuple(row) for row in cursor.fetchall()]
        except: return []
        finally: conn.close()
    return []

# ==========================================
#       FINANCE MODULE EXTRA FUNCTIONS
# ==========================================
def add_invoice(customer, amount, due_date, status):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            iid = random.randint(10000, 99999)
            query = "INSERT INTO Finance_Invoices (InvoiceID, CustomerName, Amount, DueDate, Status) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (iid, customer, amount, due_date, status))
            conn.commit()
            return True, "Invoice Created Successfully!"
        except Exception as e: return False, str(e)
        finally: conn.close()
    return False, "Connection Error"

def get_invoices():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT InvoiceID, CustomerName, Amount, DueDate, Status, CreatedDate FROM Finance_Invoices ORDER BY CreatedDate DESC")
            return [tuple(row) for row in cursor.fetchall()]
        except: return []
        finally: conn.close()
    return []