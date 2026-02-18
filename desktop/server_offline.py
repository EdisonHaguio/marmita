# Backend com SQLite para instalação offline
# Mantém todas as funcionalidades do sistema original

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import uuid
import json
import sqlite3
import os
import hashlib

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), "dona_guedes.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'attendant',
            hashed_password TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            price REAL DEFAULT 0,
            price_p REAL DEFAULT 0,
            price_m REAL DEFAULT 0,
            price_g REAL DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TEXT
        )
    ''')
    
    # Customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            type TEXT DEFAULT 'normal',
            created_at TEXT
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            order_number INTEGER,
            customer_name TEXT,
            is_company_order INTEGER DEFAULT 0,
            order_type TEXT,
            delivery_address TEXT,
            items TEXT,
            salads TEXT,
            beverages TEXT,
            coffees TEXT,
            snacks TEXT,
            desserts TEXT,
            others TEXT,
            observations TEXT,
            total_price REAL,
            payment_method TEXT DEFAULT 'DINHEIRO',
            amount_paid REAL DEFAULT 0,
            change_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'pending',
            attendant_code TEXT,
            attendant_name TEXT,
            printed INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id TEXT PRIMARY KEY,
            store_name TEXT,
            store_address TEXT,
            store_phone TEXT,
            logo_url TEXT,
            printer_type TEXT DEFAULT 'windows',
            printer_ip TEXT,
            software_company TEXT,
            software_phone TEXT
        )
    ''')
    
    # Create default admin user if not exists
    cursor.execute("SELECT * FROM users WHERE code = 'admin'")
    if not cursor.fetchone():
        admin_id = str(uuid.uuid4())
        hashed = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (id, code, name, role, hashed_password, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (admin_id, 'admin', 'Administrador', 'admin', hashed, 1, datetime.now(timezone.utc).isoformat()))
    
    # Create default settings if not exists
    cursor.execute("SELECT * FROM settings WHERE id = 'settings'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO settings (id, store_name, store_address, store_phone, printer_type, software_company, software_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ('settings', 'Dona Guedes', 'Rua Principal, 123', '(19) 99999-9999', 'windows', 'Japao Informatica', '(19) 99813-2220'))
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Pydantic models
class UserCreate(BaseModel):
    code: str
    name: str
    role: str = "attendant"
    password: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    type: str
    price: float = 0
    price_p: float = 0
    price_m: float = 0
    price_g: float = 0

class CustomerCreate(BaseModel):
    name: str
    phone: str = ""
    address: str = ""
    type: str = "normal"

class OrderItem(BaseModel):
    employee_name: Optional[str] = None
    size: str
    protein: Optional[str] = None
    proteins: List[str] = []
    accompaniments: List[str] = []

class OrderCreate(BaseModel):
    customer_name: str
    is_company_order: bool = False
    order_type: str
    delivery_address: Optional[str] = None
    items: List[OrderItem]
    salads: List[str] = []
    beverages: List[str] = []
    coffees: List[str] = []
    snacks: List[str] = []
    desserts: List[str] = []
    others: List[str] = []
    observations: Optional[str] = None
    total_price: float
    payment_method: str = "DINHEIRO"
    amount_paid: float = 0
    change_amount: float = 0
    attendant_code: str
    attendant_name: str

class OrderStatusUpdate(BaseModel):
    status: str

class SettingsUpdate(BaseModel):
    store_name: str
    store_address: str
    store_phone: str
    logo_url: Optional[str] = None
    printer_type: str = "windows"
    printer_ip: Optional[str] = None

class LoginRequest(BaseModel):
    code: str
    password: Optional[str] = None

# FastAPI app
app = FastAPI(title="Dona Guedes API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

# Helper functions
def row_to_dict(row):
    if row is None:
        return None
    return dict(row)

def get_next_order_number():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(order_number) FROM orders")
    result = cursor.fetchone()[0]
    conn.close()
    return (result or 0) + 1

# Auth endpoints
@api_router.post("/auth/login")
def login(data: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE code = ? AND is_active = 1", (data.code,))
    user = row_to_dict(cursor.fetchone())
    conn.close()
    
    if not user:
        raise HTTPException(status_code=401, detail="Usuario nao encontrado")
    
    if user['role'] == 'admin':
        if not data.password:
            raise HTTPException(status_code=401, detail="Senha obrigatoria para admin")
        hashed = hashlib.sha256(data.password.encode()).hexdigest()
        if user['hashed_password'] != hashed:
            raise HTTPException(status_code=401, detail="Senha incorreta")
    
    return {
        "id": user['id'],
        "code": user['code'],
        "name": user['name'],
        "role": user['role']
    }

# Users endpoints
@api_router.get("/users")
def get_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, code, name, role, is_active, created_at FROM users")
    users = [row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

@api_router.post("/users")
def create_user(user: UserCreate):
    conn = get_db()
    cursor = conn.cursor()
    
    user_id = str(uuid.uuid4())
    hashed = hashlib.sha256(user.password.encode()).hexdigest() if user.password else None
    
    try:
        cursor.execute('''
            INSERT INTO users (id, code, name, role, hashed_password, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user.code, user.name, user.role, hashed, 1, datetime.now(timezone.utc).isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Codigo ja existe")
    
    conn.close()
    return {"id": user_id, "message": "Usuario criado"}

@api_router.delete("/users/{user_id}")
def delete_user(user_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "Usuario removido"}

# Products endpoints
@api_router.get("/products")
def get_products():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE active = 1")
    products = [row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return products

@api_router.post("/products")
def create_product(product: ProductCreate):
    conn = get_db()
    cursor = conn.cursor()
    
    product_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO products (id, name, type, price, price_p, price_m, price_g, active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (product_id, product.name, product.type, product.price, product.price_p, product.price_m, product.price_g, 1, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()
    
    return {"id": product_id, "message": "Produto criado"}

@api_router.put("/products/{product_id}/toggle")
def toggle_product(product_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET active = NOT active WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return {"message": "Status alterado"}

@api_router.delete("/products/{product_id}")
def delete_product(product_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return {"message": "Produto removido"}

# Customers endpoints
@api_router.get("/customers")
def get_customers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    customers = [row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return customers

@api_router.post("/customers")
def create_customer(customer: CustomerCreate):
    conn = get_db()
    cursor = conn.cursor()
    
    customer_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO customers (id, name, phone, address, type, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (customer_id, customer.name, customer.phone, customer.address, customer.type, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()
    
    return {"id": customer_id, "message": "Cliente criado"}

@api_router.delete("/customers/{customer_id}")
def delete_customer(customer_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()
    return {"message": "Cliente removido"}

# Orders endpoints
@api_router.get("/orders")
def get_orders():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = []
    for row in cursor.fetchall():
        order = row_to_dict(row)
        # Parse JSON fields
        order['items'] = json.loads(order['items']) if order['items'] else []
        order['salads'] = json.loads(order['salads']) if order['salads'] else []
        order['beverages'] = json.loads(order['beverages']) if order['beverages'] else []
        order['coffees'] = json.loads(order['coffees']) if order['coffees'] else []
        order['snacks'] = json.loads(order['snacks']) if order['snacks'] else []
        order['desserts'] = json.loads(order['desserts']) if order['desserts'] else []
        order['others'] = json.loads(order['others']) if order['others'] else []
        order['is_company_order'] = bool(order['is_company_order'])
        order['printed'] = bool(order['printed'])
        orders.append(order)
    conn.close()
    return orders

@api_router.post("/orders")
def create_order(order: OrderCreate):
    conn = get_db()
    cursor = conn.cursor()
    
    order_id = str(uuid.uuid4())
    order_number = get_next_order_number()
    
    cursor.execute('''
        INSERT INTO orders (id, order_number, customer_name, is_company_order, order_type, delivery_address,
                          items, salads, beverages, coffees, snacks, desserts, others, observations,
                          total_price, payment_method, amount_paid, change_amount, status,
                          attendant_code, attendant_name, printed, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order_id, order_number, order.customer_name, int(order.is_company_order), order.order_type,
        order.delivery_address, json.dumps([item.dict() for item in order.items]),
        json.dumps(order.salads), json.dumps(order.beverages), json.dumps(order.coffees),
        json.dumps(order.snacks), json.dumps(order.desserts), json.dumps(order.others),
        order.observations, order.total_price, order.payment_method, order.amount_paid,
        order.change_amount, 'pending', order.attendant_code, order.attendant_name, 0,
        datetime.now(timezone.utc).isoformat()
    ))
    conn.commit()
    conn.close()
    
    return {"id": order_id, "order_number": order_number, "message": "Pedido criado"}

@api_router.put("/orders/{order_id}/status")
def update_order_status(order_id: str, update: OrderStatusUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (update.status, order_id))
    conn.commit()
    conn.close()
    return {"message": "Status atualizado"}

@api_router.patch("/orders/{order_id}/status")
def patch_order_status(order_id: str, update: OrderStatusUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (update.status, order_id))
    conn.commit()
    conn.close()
    return {"message": "Status atualizado"}

@api_router.get("/orders/{order_id}/receipt")
def get_order_receipt(order_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    
    order = row_to_dict(row)
    order['items'] = json.loads(order['items']) if order['items'] else []
    
    cursor.execute("SELECT * FROM settings WHERE id = 'settings'")
    settings = row_to_dict(cursor.fetchone())
    conn.close()
    
    receipt = generate_receipt(order, settings)
    return {"receipt": receipt, "order_number": order['order_number']}

@api_router.post("/orders/{order_id}/print")
def print_order(order_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    
    order = row_to_dict(row)
    order['items'] = json.loads(order['items']) if order['items'] else []
    
    cursor.execute("SELECT * FROM settings WHERE id = 'settings'")
    settings = row_to_dict(cursor.fetchone())
    
    cursor.execute("UPDATE orders SET printed = 1 WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    
    receipt = generate_receipt(order, settings)
    
    # Try to print
    try:
        print_to_windows(receipt)
        return {"message": "Impresso com sucesso", "receipt": receipt}
    except Exception as e:
        return {"message": f"Cupom gerado (impressao falhou: {str(e)})", "receipt": receipt}

def generate_receipt(order, settings):
    lines = []
    lines.append("=" * 40)
    lines.append(settings['store_name'].center(40))
    lines.append(settings['store_address'].center(40))
    lines.append("=" * 40)
    lines.append(f"Pedido: #{order['order_number']}")
    lines.append(f"Cliente: {order['customer_name']}")
    lines.append(f"Tipo: {order['order_type']}")
    
    if order['order_type'] == 'ENTREGA' and order.get('delivery_address'):
        lines.append(f"Endereco: {order['delivery_address']}")
    
    lines.append("-" * 40)
    
    for idx, item in enumerate(order['items'], 1):
        lines.append(f"\nMarmita {idx} ({item['size']}):")
        if item.get('employee_name'):
            lines.append(f"  Para: {item['employee_name']}")
        proteins = item.get('proteins', [item.get('protein', '')])
        if isinstance(proteins, list) and proteins:
            lines.append(f"  Mistura: {' + '.join([p for p in proteins if p])}")
        elif proteins:
            lines.append(f"  Mistura: {proteins}")
        if item.get('accompaniments'):
            lines.append(f"  Acomp.: {', '.join(item['accompaniments'])}")
    
    lines.append("-" * 40)
    lines.append(f"TOTAL: R$ {order['total_price']:.2f}")
    lines.append(f"Pagamento: {order.get('payment_method', 'DINHEIRO')}")
    
    if order.get('payment_method') == 'DINHEIRO' and order.get('amount_paid', 0) > 0:
        lines.append(f"Recebido: R$ {order['amount_paid']:.2f}")
        lines.append(f"TROCO: R$ {order.get('change_amount', 0):.2f}")
    
    lines.append("-" * 40)
    lines.append(f"Atendente: {order['attendant_name']}")
    lines.append(f"Data: {order['created_at'][:19]}")
    lines.append("=" * 40)
    lines.append("   Obrigado pela preferencia!")
    lines.append("=" * 40)
    
    return "\n".join(lines)

def print_to_windows(text):
    import tempfile
    import subprocess
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(text)
        temp_path = f.name
    
    try:
        subprocess.run(['notepad', '/p', temp_path], check=True, timeout=30)
    finally:
        try:
            os.remove(temp_path)
        except:
            pass

# Settings endpoints
@api_router.get("/settings")
def get_settings():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM settings WHERE id = 'settings'")
    settings = row_to_dict(cursor.fetchone())
    conn.close()
    return settings

@api_router.put("/settings")
def update_settings(settings: SettingsUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE settings SET store_name = ?, store_address = ?, store_phone = ?,
        logo_url = ?, printer_type = ?, printer_ip = ? WHERE id = 'settings'
    ''', (settings.store_name, settings.store_address, settings.store_phone,
          settings.logo_url, settings.printer_type, settings.printer_ip))
    conn.commit()
    conn.close()
    return {"message": "Configuracoes atualizadas"}

# Health check
@api_router.get("/")
def health():
    return {"status": "online", "message": "Dona Guedes API"}

app.include_router(api_router)

# Serve static files (compiled frontend)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    
    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("  DONA GUEDES - Sistema de Marmitaria")
    print("  Acesse: http://localhost:8000")
    print("  Login: admin / admin123")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
