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
    type: str  # accompaniment, protein, or beverage
    price_p: Optional[float] = 0
    price_m: Optional[float] = 0
    price_g: Optional[float] = 0
    price: Optional[float] = 0  # For beverages (fixed price)
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

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_number: int
    customer_name: str
    order_type: str  # BALCAO or ENTREGA
    delivery_address: Optional[str] = None
    size: str  # P, M, G
    accompaniments: List[str] = []  # List of accompaniment names
    protein: str  # Protein name
    observations: Optional[str] = None
    total_price: float
    status: str = "pending"  # pending, preparing, ready, delivered
    attendant_code: str
    attendant_name: str
    printed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OrderCreate(BaseModel):
    customer_name: str
    order_type: str
    delivery_address: Optional[str] = None
    size: str
    accompaniments: List[str]
    protein: str
    observations: Optional[str] = None
    total_price: float
    attendant_code: str
    attendant_name: str

class OrderStatusUpdate(BaseModel):
    status: str

class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "settings"
    store_name: str = "Dona Guedes"
    store_address: str = ""
    printer_ip: Optional[str] = None
    printer_port: int = 9100
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SettingsUpdate(BaseModel):
    store_name: Optional[str] = None
    store_address: Optional[str] = None
    printer_ip: Optional[str] = None
    printer_port: Optional[int] = None

# ===== AUTH HELPERS =====
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ===== ROUTES =====
@api_router.get("/")
async def root():
    return {"message": "Dona Guedes API", "status": "online"}

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
    
    # Generate ESC/POS commands
    printer = Dummy()
    printer.set(align='center', width=2, height=2)
    printer.text(settings.store_name + '\n')
    printer.set(align='center', width=1, height=1)
    printer.text(settings.store_address + '\n')
    printer.text('------------------------\n')
    printer.set(align='left')
    printer.text(f"Pedido: {order_dict['order_number']}\n")
    printer.text(f"Cliente: {order_dict['customer_name']}\n")
    printer.text(f"Tipo: {order_dict['order_type']}\n")
    
    if order_dict['order_type'] == 'ENTREGA' and order_dict.get('delivery_address'):
        printer.text(f"End: {order_dict['delivery_address']}\n")
    
    printer.text(f"Tamanho: {order_dict['size']}\n")
    printer.text(f"Acompanhamentos: {', '.join(order_dict['accompaniments'])}\n")
    printer.text(f"Mistura: {order_dict['protein']}\n")
    
    if order_dict.get('observations'):
        printer.text(f"Obs: {order_dict['observations']}\n")
    
    printer.text(f"Valor: R$ {order_dict['total_price']:.2f}\n")
    printer.text(f"Atendente: {order_dict['attendant_name']}\n")
    printer.text('\n\n')
    printer.cut()
    
    # Get ESC/POS data
    escpos_data = printer.output
    
    # Try to print to network printer if configured
    if settings.printer_ip:
        try:
            network_printer = Network(settings.printer_ip, port=settings.printer_port)
            network_printer._raw(escpos_data)
            network_printer.close()
            await db.orders.update_one({"id": order_id}, {"$set": {"printed": True}})
            return {"message": "Impresso com sucesso", "printed": True}
        except Exception as e:
            logging.error(f"Erro ao imprimir: {e}")
            return {"message": f"Erro: {str(e)}", "printed": False}
    
    # Return ESC/POS data for download/manual printing
    return Response(content=escpos_data, media_type="application/octet-stream", 
                    headers={"Content-Disposition": f"attachment; filename=pedido_{order_dict['order_number']}.bin"})

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
    
    result = await db.settings.update_one({"id": "settings"}, {"$set": update_dict}, upsert=True)
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