from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.responses import Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import hashlib
from escpos.printer import Network, Dummy
import io
from license_manager import license_manager
import tempfile

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ===== MODELS =====
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    name: str
    role: str = "attendant"  # attendant or admin
    password: Optional[str] = None  # Only for admin
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    code: str
    name: str
    role: str = "attendant"
    password: Optional[str] = None

class LoginRequest(BaseModel):
    code: str
    password: Optional[str] = None

class Customer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # accompaniment, protein, beverage, or salad
    price_p: Optional[float] = 0
    price_m: Optional[float] = 0
    price_g: Optional[float] = 0
    price: Optional[float] = 0  # For beverages and salads (fixed price)
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductCreate(BaseModel):
    name: str
    type: str
    price_p: Optional[float] = 0
    price_m: Optional[float] = 0
    price_g: Optional[float] = 0
    price: Optional[float] = 0

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price_p: Optional[float] = None
    price_m: Optional[float] = None
    price_g: Optional[float] = None
    price: Optional[float] = None
    active: Optional[bool] = None

class OrderItem(BaseModel):
    employee_name: Optional[str] = None  # Nome do funcionário (para empresas)
    size: str  # P, M, G
    protein: Optional[str] = None  # Compatibilidade com formato antigo
    proteins: List[str] = []  # Lista de proteínas (P=1, M/G=2)
    accompaniments: List[str] = []

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_number: int
    customer_name: str  # Nome da empresa ou cliente
    is_company_order: bool = False  # Se é pedido de empresa
    order_type: str  # BALCAO or ENTREGA
    delivery_address: Optional[str] = None
    items: List[OrderItem] = []  # Multiple marmitas
    salads: List[str] = []  # Shared salads
    beverages: List[str] = []  # Shared beverages
    coffees: List[str] = []  # Cafes
    snacks: List[str] = []  # Lanches
    desserts: List[str] = []  # Sobremesas
    others: List[str] = []  # Outros produtos
    observations: Optional[str] = None
    total_price: float
    payment_method: str = "DINHEIRO"  # DINHEIRO, PIX, CARTAO, FIADO
    amount_paid: float = 0  # Valor pago
    change_amount: float = 0  # Troco
    status: str = "pending"
    attendant_code: str
    attendant_name: str
    printed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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

class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "settings"
    store_name: str = "Dona Guedes"
    store_address: str = ""
    store_logo_url: Optional[str] = None
    printer_type: str = "windows"  # "windows" or "thermal"
    printer_ip: Optional[str] = None
    printer_port: int = 9100
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SettingsUpdate(BaseModel):
    store_name: Optional[str] = None
    store_address: Optional[str] = None
    store_logo_url: Optional[str] = None
    printer_type: Optional[str] = None
    printer_ip: Optional[str] = None
    printer_port: Optional[int] = None

# ===== AUTH HELPERS =====
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ===== ROUTES =====
@api_router.get("/")
async def root():
    # Verifica licença
    is_valid, message, days = license_manager.check_license()
    return {
        "message": "Dona Guedes API", 
        "status": "online",
        "license_valid": is_valid,
        "license_message": message,
        "days_remaining": days
    }

@api_router.get("/license/status")
async def get_license_status():
    is_valid, message, days = license_manager.check_license()
    client_info = license_manager.get_client_info()
    
    return {
        "valid": is_valid,
        "message": message,
        "days_remaining": days,
        "client_info": client_info
    }

class LicenseActivation(BaseModel):
    client_name: str
    cnpj_cpf: str
    phone: str
    email: str

@api_router.post("/license/activate")
async def activate_license(data: LicenseActivation):
    success, message = license_manager.register_client(
        data.client_name,
        data.cnpj_cpf,
        data.phone,
        data.email
    )
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

@api_router.post("/auth/login")
async def login(req: LoginRequest):
    user_dict = await db.users.find_one({"code": req.code, "active": True}, {"_id": 0})
    if not user_dict:
        raise HTTPException(status_code=401, detail="Código inválido")
    
    user = User(**user_dict)
    
    # Admin needs password
    if user.role == "admin":
        if not req.password:
            raise HTTPException(status_code=401, detail="Senha necessária para admin")
        if hash_password(req.password) != user.password:
            raise HTTPException(status_code=401, detail="Senha incorreta")
    
    return {"user": user, "token": user.id}

@api_router.get("/users", response_model=List[User])
async def get_users():
    users = await db.users.find({"active": True}, {"_id": 0, "password": 0}).to_list(1000)
    for u in users:
        if isinstance(u['created_at'], str):
            u['created_at'] = datetime.fromisoformat(u['created_at'])
    return users

@api_router.post("/users", response_model=User)
async def create_user(user_input: UserCreate):
    # Check if code already exists
    existing = await db.users.find_one({"code": user_input.code})
    if existing:
        raise HTTPException(status_code=400, detail="Código já existe")
    
    user_dict = user_input.model_dump()
    if user_input.password:
        user_dict['password'] = hash_password(user_input.password)
    
    user_obj = User(**user_dict)
    doc = user_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.users.insert_one(doc)
    return user_obj

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await db.users.update_one({"id": user_id}, {"$set": {"active": False}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário removido"}

@api_router.get("/products", response_model=List[Product])
async def get_products(active_only: bool = False):
    query = {"active": True} if active_only else {}
    products = await db.products.find(query, {"_id": 0}).to_list(1000)
    for p in products:
        if isinstance(p['created_at'], str):
            p['created_at'] = datetime.fromisoformat(p['created_at'])
    return products

@api_router.post("/products", response_model=Product)
async def create_product(product_input: ProductCreate):
    product_dict = product_input.model_dump()
    product_obj = Product(**product_dict)
    doc = product_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.products.insert_one(doc)
    return product_obj

@api_router.patch("/products/{product_id}")
async def update_product(product_id: str, update: ProductUpdate):
    update_dict = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    result = await db.products.update_one({"id": product_id}, {"$set": update_dict})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"message": "Produto atualizado"}

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    result = await db.products.update_one({"id": product_id}, {"$set": {"active": False}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"message": "Produto removido"}

@api_router.delete("/products/{product_id}/permanent")
async def delete_product_permanent(product_id: str):
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return {"message": "Produto excluído permanentemente"}

@api_router.get("/customers", response_model=List[Customer])
async def get_customers():
    customers = await db.customers.find({}, {"_id": 0}).sort("name", 1).to_list(1000)
    for c in customers:
        if isinstance(c['created_at'], str):
            c['created_at'] = datetime.fromisoformat(c['created_at'])
    return customers

@api_router.post("/customers", response_model=Customer)
async def create_customer(customer_input: CustomerCreate):
    customer_dict = customer_input.model_dump()
    customer_obj = Customer(**customer_dict)
    doc = customer_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.customers.insert_one(doc)
    return customer_obj

@api_router.patch("/customers/{customer_id}")
async def update_customer(customer_id: str, update: CustomerUpdate):
    update_dict = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    result = await db.customers.update_one({"id": customer_id}, {"$set": update_dict})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"message": "Cliente atualizado"}

@api_router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str):
    result = await db.customers.delete_one({"id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"message": "Cliente excluído"}

@api_router.get("/orders", response_model=List[Order])
async def get_orders(status: Optional[str] = None):
    query = {"status": status} if status else {}
    orders = await db.orders.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for o in orders:
        if isinstance(o['created_at'], str):
            o['created_at'] = datetime.fromisoformat(o['created_at'])
    return orders

@api_router.post("/orders", response_model=Order)
async def create_order(order_input: OrderCreate):
    # Get next order number
    last_order = await db.orders.find_one({}, {"order_number": 1}, sort=[("order_number", -1)])
    next_number = (last_order['order_number'] + 1) if last_order else 1
    
    order_dict = order_input.model_dump()
    order_dict['order_number'] = next_number
    order_obj = Order(**order_dict)
    doc = order_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.orders.insert_one(doc)
    return order_obj

@api_router.patch("/orders/{order_id}/status")
async def update_order_status(order_id: str, update: OrderStatusUpdate):
    result = await db.orders.update_one({"id": order_id}, {"$set": {"status": update.status}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return {"message": "Status atualizado"}

@api_router.post("/orders/{order_id}/print")
async def print_order(order_id: str):
    order_dict = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order_dict:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    settings_dict = await db.settings.find_one({"id": "settings"}, {"_id": 0})
    settings = Settings(**settings_dict) if settings_dict else Settings()
    
    # Check if it's a company order - print individual receipts
    if order_dict.get('is_company_order'):
        return await print_company_order(order_dict, settings)
    else:
        return await print_single_order(order_dict, settings)

async def print_single_order(order_dict, settings):
    """Print a single receipt for the whole order"""
    receipt_text = generate_receipt_text(order_dict, settings)
    
    if settings.printer_type == "windows":
        # Generate print file for Windows default printer
        return generate_windows_print(receipt_text, order_dict['order_number'])
    else:
        # Use thermal printer
        return send_to_thermal_printer(receipt_text, settings, order_dict['id'])

async def print_company_order(order_dict, settings):
    """Print individual receipts for each employee"""
    receipts = []
    
    for idx, item in enumerate(order_dict['items'], 1):
        employee_name = item.get('employee_name', f"Funcionário {idx}")
        receipt_text = generate_employee_receipt(order_dict, item, employee_name, settings)
        
        if settings.printer_type == "windows":
            receipts.append(generate_windows_print(receipt_text, f"{order_dict['order_number']}-{idx}"))
        else:
            receipts.append(send_to_thermal_printer(receipt_text, settings, order_dict['id']))
    
    await db.orders.update_one({"id": order_dict['id']}, {"$set": {"printed": True}})
    return {"message": f"{len(receipts)} cupons gerados (1 por funcionário)", "printed": True, "count": len(receipts)}

def generate_receipt_text(order_dict, settings):
    """Generate receipt text for full order"""
    lines = []
    lines.append("=" * 40)
    lines.append(settings.store_name.center(40))
    lines.append(settings.store_address.center(40))
    lines.append("=" * 40)
    lines.append(f"Pedido: #{order_dict['order_number']}")
    lines.append(f"Cliente: {order_dict['customer_name']}")
    lines.append(f"Tipo: {order_dict['order_type']}")
    
    if order_dict['order_type'] == 'ENTREGA' and order_dict.get('delivery_address'):
        lines.append(f"Endereco: {order_dict['delivery_address']}")
    
    lines.append("-" * 40)
    
    # Print each marmita
    for idx, item in enumerate(order_dict['items'], 1):
        lines.append(f"\nMarmita {idx} ({item['size']}):")
        if item.get('employee_name'):
            lines.append(f"  Para: {item['employee_name']}")
        # Suporta tanto 'protein' quanto 'proteins'
        proteins = item.get('proteins', [item.get('protein', '')])
        if isinstance(proteins, list):
            lines.append(f"  Mistura: {' + '.join(proteins)}")
        else:
            lines.append(f"  Mistura: {proteins}")
        if item.get('accompaniments'):
            lines.append(f"  Acomp.: {', '.join(item['accompaniments'])}")
    
    lines.append("-" * 40)
    
    if order_dict.get('salads') and len(order_dict['salads']) > 0:
        lines.append(f"Saladas: {', '.join(order_dict['salads'])}")
    
    if order_dict.get('beverages') and len(order_dict['beverages']) > 0:
        lines.append(f"Bebidas: {', '.join(order_dict['beverages'])}")
    
    if order_dict.get('coffees') and len(order_dict['coffees']) > 0:
        lines.append(f"Cafes: {', '.join(order_dict['coffees'])}")
    
    if order_dict.get('snacks') and len(order_dict['snacks']) > 0:
        lines.append(f"Lanches: {', '.join(order_dict['snacks'])}")
    
    if order_dict.get('desserts') and len(order_dict['desserts']) > 0:
        lines.append(f"Sobremesas: {', '.join(order_dict['desserts'])}")
    
    if order_dict.get('others') and len(order_dict['others']) > 0:
        lines.append(f"Outros: {', '.join(order_dict['others'])}")
    
    if order_dict.get('observations'):
        lines.append(f"Obs: {order_dict['observations']}")
    
    lines.append("-" * 40)
    lines.append(f"TOTAL: R$ {order_dict['total_price']:.2f}")
    
    # Pagamento
    payment_method = order_dict.get('payment_method', 'DINHEIRO')
    lines.append(f"Pagamento: {payment_method}")
    
    if payment_method == "DINHEIRO":
        amount_paid = order_dict.get('amount_paid', 0)
        change_amount = order_dict.get('change_amount', 0)
        if amount_paid > 0:
            lines.append(f"Valor Recebido: R$ {amount_paid:.2f}")
            lines.append(f"TROCO: R$ {change_amount:.2f}")
    
    lines.append("-" * 40)
    lines.append(f"Atendente: {order_dict['attendant_name']}")
    lines.append(f"Data: {order_dict.get('created_at', '')[:19]}")
    lines.append("=" * 40)
    lines.append("     Obrigado pela preferencia!")
    lines.append("=" * 40)
    lines.append("\n\n\n")
    
    return "\n".join(lines)

def generate_employee_receipt(order_dict, item, employee_name, settings):
    """Generate individual receipt for one employee"""
    lines = []
    lines.append("=" * 40)
    lines.append(settings.store_name.center(40))
    lines.append("=" * 40)
    lines.append(f"Pedido: #{order_dict['order_number']}")
    lines.append(f"Empresa: {order_dict['customer_name']}")
    lines.append(f"\n>>> PARA: {employee_name} <<<\n")
    lines.append("-" * 40)
    lines.append(f"Tamanho: {item['size']}")
    # Suporta tanto 'protein' quanto 'proteins'
    proteins = item.get('proteins', [item.get('protein', '')])
    if isinstance(proteins, list):
        lines.append(f"Mistura: {' + '.join(proteins)}")
    else:
        lines.append(f"Mistura: {proteins}")
    if item.get('accompaniments'):
        lines.append("Acompanhamentos:")
        for acc in item['accompaniments']:
            lines.append(f"  - {acc}")
    lines.append("=" * 40)
    lines.append("\n\n\n")
    
    return "\n".join(lines)

def generate_windows_print(text, order_number):
    """Generate print file for Windows default printer"""
    import os
    
    # Create temp file with print content
    temp_file = os.path.join(tempfile.gettempdir(), f"pedido_{order_number}.txt")
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Return instructions for Windows printing
    return {
        "message": "Arquivo gerado para impressão",
        "file_path": temp_file,
        "instruction": f"Execute: notepad /p {temp_file}",
        "printed": True,
        "type": "windows"
    }

def send_to_thermal_printer(text, settings, order_id):
    """Send to thermal ESC/POS printer"""
    try:
        from escpos.printer import Network, Dummy
        
        if not settings.printer_ip:
            return {"message": "IP da impressora não configurado", "printed": False}
        
        printer = Network(settings.printer_ip, port=settings.printer_port)
        
        # Convert text to ESC/POS commands
        dummy = Dummy()
        dummy.set(align='left')
        for line in text.split('\n'):
            dummy.text(line + '\n')
        dummy.cut()
        
        printer._raw(dummy.output)
        printer.close()
        
        return {"message": "Impresso em impressora térmica", "printed": True, "type": "thermal"}
    except Exception as e:
        logging.error(f"Erro ao imprimir: {e}")
        return {"message": f"Erro: {str(e)}", "printed": False}

@api_router.get("/settings", response_model=Settings)
async def get_settings():
    settings_dict = await db.settings.find_one({"id": "settings"}, {"_id": 0})
    if not settings_dict:
        # Create default settings
        settings = Settings()
        doc = settings.model_dump()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.settings.insert_one(doc)
        return settings
    
    if isinstance(settings_dict['updated_at'], str):
        settings_dict['updated_at'] = datetime.fromisoformat(settings_dict['updated_at'])
    return Settings(**settings_dict)

@api_router.patch("/settings")
async def update_settings(update: SettingsUpdate):
    update_dict = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    
    update_dict['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.settings.update_one({"id": "settings"}, {"$set": update_dict}, upsert=True)
    return {"message": "Configurações atualizadas"}

# Initialize default admin user
@app.on_event("startup")
async def startup_event():
    # Create default admin if not exists
    admin = await db.users.find_one({"role": "admin"})
    if not admin:
        admin_user = User(
            code="admin",
            name="Administrador",
            role="admin",
            password=hash_password("admin123")
        )
        doc = admin_user.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.users.insert_one(doc)
        logging.info("Admin padrão criado: admin / admin123")

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()