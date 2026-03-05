from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import models
from db import get_db, init_db
from pydantic import BaseModel
import base64

app = FastAPI()

# CORS - Allow all origins for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────── Pydantic Models ────────────────────

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class BillingEntry(BaseModel):
    username: str          # DATA ISOLATION
    customer_name: str
    item_name: str
    cost: float
    quantity: int

class WorkerCreate(BaseModel):
    username: str          # DATA ISOLATION
    name: str
    email: str
    phone: str
    address: str
    worker_type: str
    salary: float

class AttendanceEntry(BaseModel):
    id: int
    name: str
    type: str
    status: str

class AttendanceBulk(BaseModel):
    username: str          # DATA ISOLATION
    entries: List[AttendanceEntry]

class ExpenseCreate(BaseModel):
    username: str          # DATA ISOLATION
    category: str
    description: str
    amount: float

class SalesOrderCreate(BaseModel):
    username: str          # DATA ISOLATION
    customer: str
    amount: float
    status: str

class CampaignCreate(BaseModel):
    username: str          # DATA ISOLATION
    name: str
    audience: str
    budget: float
    status: str

class RentalBookingCreate(BaseModel):
    username: str          # DATA ISOLATION
    name: str
    room: str
    rent: float
    deposit: float
    phone: str

class RestaurantSaleCreate(BaseModel):
    username: str          # DATA ISOLATION
    table_no: int
    items: str
    amount: float
    mode: str

class LeadCreate(BaseModel):
    username: str          # DATA ISOLATION
    name: str
    email: str
    source: str
    status: str

class LeaveRequestCreate(BaseModel):
    username: str          # DATA ISOLATION
    name: str
    l_type: str
    days: int

class PayrollCreate(BaseModel):
    username: str          # DATA ISOLATION
    name: str
    month: str
    amount: float

class InvoiceCreate(BaseModel):
    username: str          # DATA ISOLATION
    customer: str
    amount: float
    due_date: str
    status: str

# ──────────────────── Startup ────────────────────

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"message": "API is running"}

# ──────────────────── Auth ────────────────────

@app.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db.add(models.User(username=user.username, email=user.email, password=user.password))
    db.commit()
    return {"message": "User registered"}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.email == user.email,
        models.User.password == user.password
    ).first()
    if db_user:
        return {"username": db_user.username}
    raise HTTPException(status_code=400, detail="Invalid credentials")

# ──────────────────── CRM ────────────────────

@app.post("/crm/instance")
def create_crm_instance(
    username: str = Form(...),
    brand_name: str = Form(...),
    brand_color: str = Form(...),
    logo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    logo_bytes = logo.file.read() if logo else None
    db.add(models.CRMInstance(
        instance_user=username,
        brand_name=brand_name,
        brand_color=brand_color,
        logo=logo_bytes
    ))
    db.commit()
    return {"message": "CRM Instance Created"}

@app.get("/crm/instance/{username}")
def get_crm_instance(username: str, db: Session = Depends(get_db)):
    instance = db.query(models.CRMInstance).filter(
        models.CRMInstance.instance_user == username
    ).order_by(models.CRMInstance.id.desc()).first()
    if instance:
        logo_b64 = base64.b64encode(instance.logo).decode() if instance.logo else None
        return {"brand_name": instance.brand_name, "brand_color": instance.brand_color, "logo": logo_b64}
    return {}

# ──────────────────── Billing ────────────────────

@app.post("/billing")
def add_billing(entry: BillingEntry, db: Session = Depends(get_db)):
    db.add(models.Billing(
        username=entry.username,
        customer_name=entry.customer_name,
        item_name=entry.item_name,
        cost=entry.cost,
        quantity=entry.quantity,
    ))
    db.commit()
    return {"message": "Bill Saved"}

@app.get("/billing")
def get_billing(username: str = Query(...), db: Session = Depends(get_db)):
    bills = db.query(models.Billing).filter(
        models.Billing.username == username
    ).order_by(models.Billing.date_of_entering.desc()).all()
    return bills

# ──────────────────── Workers ────────────────────

@app.post("/workers")
def add_worker(worker: WorkerCreate, db: Session = Depends(get_db)):
    new_worker = models.Worker(
        username=worker.username,
        name=worker.name,
        email=worker.email,
        phone_number=worker.phone,
        address=worker.address,
        worker_type=worker.worker_type,
        salary=worker.salary
    )
    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)
    return {"message": f"Worker Added! ID: {new_worker.worker_id}"}

@app.get("/workers")
def get_workers(username: str = Query(...), only_active: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.Worker).filter(models.Worker.username == username)
    if only_active:
        query = query.filter(models.Worker.removed_date == None)
    return query.all()

@app.put("/workers/{worker_id}/fire")
def fire_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = db.query(models.Worker).filter(models.Worker.worker_id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    worker.removed_date = datetime.now()
    db.commit()
    return {"message": "Worker Fired"}

# ──────────────────── Attendance ────────────────────

@app.post("/attendance")
def save_attendance(data: AttendanceBulk, db: Session = Depends(get_db)):
    for row in data.entries:
        db.add(models.Attendance(
            username=data.username,
            worker_id=row.id,
            worker_name=row.name,
            worker_type=row.type,
            status=row.status
        ))
    db.commit()
    return {"message": f"Marked attendance for {len(data.entries)} workers"}

@app.get("/attendance")
def get_attendance(username: str = Query(...), db: Session = Depends(get_db)):
    return db.query(models.Attendance).filter(
        models.Attendance.username == username
    ).order_by(models.Attendance.date.desc()).all()

# ──────────────────── Expenses ────────────────────

@app.post("/expenses")
def add_expense(exp: ExpenseCreate, db: Session = Depends(get_db)):
    db.add(models.Expense(
        username=exp.username,
        category=exp.category,
        description=exp.description,
        amount=exp.amount,
        submitted_by=exp.username
    ))
    db.commit()
    return {"message": "Expense Logged"}

@app.get("/expenses")
def get_expenses(username: str = Query(...), db: Session = Depends(get_db)):
    return db.query(models.Expense).filter(
        models.Expense.username == username
    ).order_by(models.Expense.expense_date.desc()).all()

# ──────────────────── Sales ────────────────────

@app.post("/sales")
def add_sale(sale: SalesOrderCreate, db: Session = Depends(get_db)):
    db.add(models.SalesOrder(
        username=sale.username,
        customer_name=sale.customer,
        amount=sale.amount,
        status=sale.status
    ))
    db.commit()
    return {"message": "Order Created"}

@app.get("/sales")
def get_sales(username: str = Query(...), db: Session = Depends(get_db)):
    return db.query(models.SalesOrder).filter(
        models.SalesOrder.username == username
    ).order_by(models.SalesOrder.order_date.desc()).all()

# ──────────────────── Ledger ────────────────────

@app.get("/ledger")
def get_ledger(username: str = Query(...), db: Session = Depends(get_db)):
    return db.query(models.Ledger).filter(models.Ledger.username == username).all()

# ──────────────────── Campaigns ────────────────────

@app.post("/campaigns")
def add_campaign(camp: CampaignCreate, db: Session = Depends(get_db)):
    db.add(models.Campaign(
        username=camp.username,
        campaign_name=camp.name,
        target_audience=camp.audience,
        budget=camp.budget,
        status=camp.status
    ))
    db.commit()
    return {"message": "Campaign Launched"}

@app.get("/campaigns")
def get_campaigns(username: str = Query(...), db: Session = Depends(get_db)):
    return db.query(models.Campaign).filter(
        models.Campaign.username == username
    ).all()

# ──────────────────── Rental ────────────────────

@app.post("/rental")
def add_rental(booking: RentalBookingCreate, db: Session = Depends(get_db)):
    db.add(models.RentalBooking(
        username=booking.username,
        tenant_name=booking.name,
        room_number=booking.room,
        monthly_rent=booking.rent,
        security_deposit=booking.deposit,
        phone=booking.phone
    ))
    db.commit()
    return {"message": "Tenant Booked"}

@app.post("/rental/vacate")
def vacate_rental(room_number: str, username: str = Query(...), db: Session = Depends(get_db)):
    booking = db.query(models.RentalBooking).filter(
        models.RentalBooking.username == username,
        models.RentalBooking.room_number == room_number,
        models.RentalBooking.status == 'Occupied'
    ).first()
    if booking:
        booking.status = 'Vacated'
        booking.vacate_date = datetime.now()
        db.commit()
        return {"message": f"Room {room_number} Vacated"}
    raise HTTPException(status_code=404, detail="Room not found or already vacated")

@app.get("/rental")
def get_rental(username: str = Query(...), status: str = "All", db: Session = Depends(get_db)):
    query = db.query(models.RentalBooking).filter(models.RentalBooking.username == username)
    if status != "All":
        query = query.filter(models.RentalBooking.status == status)
    return query.order_by(models.RentalBooking.join_date.desc()).all()

# ──────────────────── Restaurant ────────────────────

@app.post("/restaurant/sales")
def add_restaurant_sale(sale: RestaurantSaleCreate, db: Session = Depends(get_db)):
    db.add(models.RestaurantSale(
        username=sale.username,
        table_number=sale.table_no,
        items_ordered=sale.items,
        total_amount=sale.amount,
        payment_mode=sale.mode
    ))
    db.commit()
    return {"message": "Bill Saved"}

@app.get("/restaurant/sales")
def get_restaurant_sales(username: str = Query(...), db: Session = Depends(get_db)):
    return db.query(models.RestaurantSale).filter(
        models.RestaurantSale.username == username
    ).order_by(models.RestaurantSale.sale_date.desc()).all()

# ──────────────────── Leads ────────────────────

@app.post("/leads")
def add_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    db.add(models.Lead(
        username=lead.username,
        lead_name=lead.name,
        email=lead.email,
        source=lead.source,
        status=lead.status
    ))
    db.commit()
    return {"message": "Lead Added"}

@app.get("/leads")
def get_leads(username: str = Query(...), db: Session = Depends(get_db)):
    return db.query(models.Lead).filter(
        models.Lead.username == username
    ).order_by(models.Lead.created_date.desc()).all()

# ──────────────────── HR Leaves ────────────────────

@app.post("/hr/leaves")
def add_leave(leave: LeaveRequestCreate, db: Session = Depends(get_db)):
    db.add(models.LeaveRequest(
        username=leave.username,
        worker_name=leave.name,
        leave_type=leave.l_type,
        days=leave.days
    ))
    db.commit()
    return {"message": "Leave Request Sent"}

@app.get("/hr/leaves")
def get_leaves(username: str = Query(...), db: Session = Depends(get_db)):
    return db.query(models.LeaveRequest).filter(
        models.LeaveRequest.username == username
    ).order_by(models.LeaveRequest.request_date.desc()).all()

# ──────────────────── HR Payroll ────────────────────

@app.post("/hr/payroll")
def add_payroll(pay: PayrollCreate, db: Session = Depends(get_db)):
    db.add(models.Payroll(
        username=pay.username,
        worker_name=pay.name,
        salary_month=pay.month,
        amount_paid=pay.amount
    ))
    db.commit()
    return {"message": "Salary Processed"}

@app.get("/hr/payroll")
def get_payroll(username: str = Query(...), db: Session = Depends(get_db)):
    return db.query(models.Payroll).filter(
        models.Payroll.username == username
    ).order_by(models.Payroll.payment_date.desc()).all()

# ──────────────────── Invoices ────────────────────

@app.post("/invoices")
def add_invoice(inv: InvoiceCreate, db: Session = Depends(get_db)):
    db.add(models.Invoice(
        username=inv.username,
        customer_name=inv.customer,
        amount=inv.amount,
        due_date=inv.due_date,
        status=inv.status
    ))
    db.commit()
    return {"message": "Invoice Created"}

@app.get("/invoices")
def get_invoices(username: str = Query(...), db: Session = Depends(get_db)):
    return db.query(models.Invoice).filter(
        models.Invoice.username == username
    ).order_by(models.Invoice.created_date.desc()).all()
