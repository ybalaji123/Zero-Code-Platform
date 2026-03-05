from sqlalchemy import Column, Integer, String, Float, DateTime, LargeBinary, Text, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "register"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class CRMInstance(Base):
    __tablename__ = "crm_instances"
    id = Column(Integer, primary_key=True, index=True)
    instance_user = Column(String, index=True)
    brand_name = Column(String)
    brand_color = Column(String)
    logo = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Billing(Base):
    __tablename__ = "billing"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    customer_id = Column(Integer)
    customer_name = Column(String)
    item_name = Column(String)
    cost = Column(Float)
    quantity = Column(Integer)
    date_of_entering = Column(DateTime(timezone=True), server_default=func.now())

class Worker(Base):
    __tablename__ = "workers"
    worker_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    name = Column(String)
    email = Column(String, index=True)
    phone_number = Column(String)
    address = Column(Text)
    worker_type = Column(String)
    salary = Column(Float)
    admitted_date = Column(DateTime(timezone=True), server_default=func.now())
    removed_date = Column(DateTime(timezone=True), nullable=True)

class Attendance(Base):
    __tablename__ = "attendance"
    attendance_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    worker_id = Column(Integer)
    worker_name = Column(String)
    worker_type = Column(String)
    status = Column(String)
    date = Column(DateTime(timezone=True), server_default=func.now())

class Expense(Base):
    __tablename__ = "finance_expenses"
    expense_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    category = Column(String)
    description = Column(String)
    amount = Column(Float)
    submitted_by = Column(String)
    expense_date = Column(DateTime(timezone=True), server_default=func.now())

class SalesOrder(Base):
    __tablename__ = "sales_orders"
    order_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    customer_name = Column(String)
    amount = Column(Float)
    status = Column(String)
    order_date = Column(DateTime(timezone=True), server_default=func.now())

class Ledger(Base):
    __tablename__ = "accounting_ledger"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    account_code = Column(String)
    account_name = Column(String)
    account_type = Column(String)
    balance = Column(Float)

class Campaign(Base):
    __tablename__ = "marketing_campaigns"
    campaign_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    campaign_name = Column(String)
    target_audience = Column(String)
    budget = Column(Float)
    status = Column(String)
    start_date = Column(DateTime(timezone=True), server_default=func.now())

class RentalBooking(Base):
    __tablename__ = "rental_bookings"
    booking_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    tenant_name = Column(String)
    room_number = Column(String)
    monthly_rent = Column(Float)
    security_deposit = Column(Float)
    phone = Column(String)
    status = Column(String, default="Occupied")
    join_date = Column(DateTime(timezone=True), server_default=func.now())
    vacate_date = Column(DateTime(timezone=True), nullable=True)

class RestaurantSale(Base):
    __tablename__ = "restaurant_sales"
    sale_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    table_number = Column(Integer)
    items_ordered = Column(Text)
    total_amount = Column(Float)
    payment_mode = Column(String)
    sale_date = Column(DateTime(timezone=True), server_default=func.now())

class Lead(Base):
    __tablename__ = "marketing_leads"
    lead_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    lead_name = Column(String)
    email = Column(String)
    source = Column(String)
    status = Column(String)
    created_date = Column(DateTime(timezone=True), server_default=func.now())

class LeaveRequest(Base):
    __tablename__ = "hr_leaverequests"
    leave_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    worker_name = Column(String)
    leave_type = Column(String)
    days = Column(Integer)
    status = Column(String, default="Pending")
    request_date = Column(DateTime(timezone=True), server_default=func.now())

class Payroll(Base):
    __tablename__ = "hr_payroll"
    payroll_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    worker_name = Column(String)
    salary_month = Column(String)
    amount_paid = Column(Float)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())

class Invoice(Base):
    __tablename__ = "finance_invoices"
    invoice_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # DATA ISOLATION: owner field
    customer_name = Column(String)
    amount = Column(Float)
    due_date = Column(String)
    status = Column(String)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
