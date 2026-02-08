import { useState, useEffect } from "react";
import { axiosInstance } from "../App";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { toast } from "sonner";
import { LogOut, Users, UtensilsCrossed, Settings, Plus, Trash2, Eye, EyeOff } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";

export default function AdminDashboard({ user, onLogout }) {
  const [view, setView] = useState("products");
  const [products, setProducts] = useState([]);
  const [users, setUsers] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [view]);

  const loadData = async () => {
    try {
      if (view === "products") {
        const res = await axiosInstance.get("/products");
        setProducts(res.data);
      } else if (view === "users") {
        const res = await axiosInstance.get("/users");
        setUsers(res.data);
      } else if (view === "customers") {
        const res = await axiosInstance.get("/customers");
        setCustomers(res.data);
      } else if (view === "settings") {
        const res = await axiosInstance.get("/settings");
        setSettings(res.data);
      }
    } catch (error) {
      toast.error("Erro ao carregar dados");
    }
  };

  const toggleProductActive = async (productId, currentActive) => {
    try {
      await axiosInstance.patch(`/products/${productId}`, { active: !currentActive });
      toast.success(currentActive ? "Produto desativado" : "Produto ativado");
      loadData();
    } catch (error) {
      toast.error("Erro ao atualizar produto");
    }
  };

  const deleteUser = async (userId) => {
    if (!window.confirm("Tem certeza que deseja remover este funcionário?")) return;
    
    try {
      await axiosInstance.delete(`/users/${userId}`);
      toast.success("Funcionário removido");
      loadData();
    } catch (error) {
      toast.error("Erro ao remover funcionário");
    }
  };

  const updateSettings = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axiosInstance.patch("/settings", settings);
      toast.success("Configurações atualizadas!");
    } catch (error) {
      toast.error("Erro ao atualizar");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FFF8F0] to-[#FFE0B2]">
      {/* Header */}
      <header className="bg-white shadow-md border-b-4 border-primary">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-outfit font-bold text-secondary">Admin - Dona Guedes</h1>
            <p className="text-sm text-secondary-light">Olá, {user.name}</p>
          </div>
          <Button
            data-testid="admin-logout-button"
            onClick={onLogout}
            variant="outline"
            className="border-secondary text-secondary hover:bg-secondary hover:text-white"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Sair
          </Button>
        </div>
      </header>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex gap-2 mb-6 overflow-x-auto">
          <Button
            data-testid="products-tab"
            onClick={() => setView("products")}
            className={`flex-1 h-12 rounded-xl transition-all whitespace-nowrap ${
              view === "products"
                ? "bg-primary text-white shadow-lg"
                : "bg-white text-secondary hover:bg-orange-50"
            }`}
          >
            <UtensilsCrossed className="w-5 h-5 mr-2" />
            Produtos
          </Button>
          <Button
            data-testid="customers-tab"
            onClick={() => setView("customers")}
            className={`flex-1 h-12 rounded-xl transition-all whitespace-nowrap ${
              view === "customers"
                ? "bg-primary text-white shadow-lg"
                : "bg-white text-secondary hover:bg-orange-50"
            }`}
          >
            <Users className="w-5 h-5 mr-2" />
            Clientes
          </Button>
          <Button
            data-testid="users-tab"
            onClick={() => setView("users")}
            className={`flex-1 h-12 rounded-xl transition-all whitespace-nowrap ${
              view === "users"
                ? "bg-primary text-white shadow-lg"
                : "bg-white text-secondary hover:bg-orange-50"
            }`}
          >
            <Users className="w-5 h-5 mr-2" />
            Funcionários
          </Button>
          <Button
            data-testid="settings-tab"
            onClick={() => setView("settings")}
            className={`flex-1 h-12 rounded-xl transition-all whitespace-nowrap ${
              view === "settings"
                ? "bg-primary text-white shadow-lg"
                : "bg-white text-secondary hover:bg-orange-50"
            }`}
          >
            <Settings className="w-5 h-5 mr-2" />
            Configurações
          </Button>
        </div>

        {view === "products" && <ProductsTab products={products} onRefresh={loadData} />}
        {view === "customers" && <CustomersTab customers={customers} onRefresh={loadData} />}
        {view === "users" && <UsersTab users={users} onDelete={deleteUser} onRefresh={loadData} />}
        {view === "settings" && <SettingsTab settings={settings} setSettings={setSettings} onSubmit={updateSettings} loading={loading} />}
      </div>
    </div>
  );
}

function ProductsTab({ products, onRefresh }) {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({ name: "", type: "protein", price_p: 0, price_m: 0, price_g: 0 });

  const toggleProductActive = async (productId, currentActive) => {
    try {
      await axiosInstance.patch(`/products/${productId}`, { active: !currentActive });
      toast.success(currentActive ? "Produto desativado" : "Produto ativado");
      onRefresh();
    } catch (error) {
      toast.error("Erro ao atualizar produto");
    }
  };

  const deleteProductPermanent = async (productId, productName) => {
    if (!window.confirm(`Tem certeza que deseja EXCLUIR PERMANENTEMENTE "${productName}"? Esta ação não pode ser desfeita!`)) return;
    
    try {
      await axiosInstance.delete(`/products/${productId}/permanent`);
      toast.success("Produto excluído permanentemente");
      onRefresh();
    } catch (error) {
      toast.error("Erro ao excluir produto");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axiosInstance.post("/products", formData);
      toast.success("Produto criado!");
      setIsOpen(false);
      setFormData({ name: "", type: "protein", price_p: 0, price_m: 0, price_g: 0 });
      onRefresh();
    } catch (error) {
      toast.error("Erro ao criar produto");
    }
  };

  const accompaniments = products.filter(p => p.type === "accompaniment");
  const proteins = products.filter(p => p.type === "protein");

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-product-button" className="bg-primary hover:bg-primary-hover text-white">
              <Plus className="w-4 h-4 mr-2" />
              Novo Produto
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Novo Produto</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nome</label>
                <Input
                  data-testid="product-name-input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Tipo</label>
                <select
                  data-testid="product-type-select"
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="w-full h-10 border border-gray-300 rounded-lg px-3"
                >
                  <option value="accompaniment">Acompanhamento</option>
                  <option value="protein">Mistura (Proteína)</option>
                </select>
              </div>
              {formData.type === "protein" && (
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="block text-xs font-medium mb-1">Preço P</label>
                    <Input
                      data-testid="product-price-p-input"
                      type="number"
                      step="0.01"
                      value={formData.price_p}
                      onChange={(e) => setFormData({ ...formData, price_p: parseFloat(e.target.value) })}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium mb-1">Preço M</label>
                    <Input
                      data-testid="product-price-m-input"
                      type="number"
                      step="0.01"
                      value={formData.price_m}
                      onChange={(e) => setFormData({ ...formData, price_m: parseFloat(e.target.value) })}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium mb-1">Preço G</label>
                    <Input
                      data-testid="product-price-g-input"
                      type="number"
                      step="0.01"
                      value={formData.price_g}
                      onChange={(e) => setFormData({ ...formData, price_g: parseFloat(e.target.value) })}
                    />
                  </div>
                </div>
              )}
              <Button data-testid="submit-product-button" type="submit" className="w-full bg-primary hover:bg-primary-hover text-white">
                Criar Produto
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="bg-white rounded-2xl p-6 shadow-warm">
        <h3 className="text-xl font-outfit font-semibold text-secondary mb-4">Misturas (Proteínas)</h3>
        <div className="space-y-2">
          {proteins.map((p) => (
            <div key={p.id} data-testid={`product-item-${p.id}`} className="flex items-center justify-between p-4 border border-orange-100 rounded-xl">
              <div>
                <p className="font-semibold text-secondary">{p.name}</p>
                <p className="text-sm text-secondary-light">
                  P: R$ {p.price_p.toFixed(2)} | M: R$ {p.price_m.toFixed(2)} | G: R$ {p.price_g.toFixed(2)}
                </p>
              </div>
              <div className="flex gap-2">
                <Button
                  data-testid={`toggle-product-${p.id}`}
                  onClick={() => toggleProductActive(p.id, p.active)}
                  variant="outline"
                  size="sm"
                  className={p.active ? "border-accent-green text-accent-green" : "border-gray-400 text-gray-400"}
                >
                  {p.active ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                </Button>
                <Button
                  data-testid={`delete-product-${p.id}`}
                  onClick={() => deleteProductPermanent(p.id, p.name)}
                  variant="outline"
                  size="sm"
                  className="border-accent-red text-accent-red hover:bg-accent-red hover:text-white"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-2xl p-6 shadow-warm">
        <h3 className="text-xl font-outfit font-semibold text-secondary mb-4">Acompanhamentos</h3>
        <div className="space-y-2">
          {accompaniments.map((p) => (
            <div key={p.id} data-testid={`accompaniment-item-${p.id}`} className="flex items-center justify-between p-4 border border-orange-100 rounded-xl">
              <p className="font-semibold text-secondary">{p.name}</p>
              <div className="flex gap-2">
                <Button
                  data-testid={`toggle-accompaniment-${p.id}`}
                  onClick={() => toggleProductActive(p.id, p.active)}
                  variant="outline"
                  size="sm"
                  className={p.active ? "border-accent-green text-accent-green" : "border-gray-400 text-gray-400"}
                >
                  {p.active ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                </Button>
                <Button
                  data-testid={`delete-accompaniment-${p.id}`}
                  onClick={() => deleteProductPermanent(p.id, p.name)}
                  variant="outline"
                  size="sm"
                  className="border-accent-red text-accent-red hover:bg-accent-red hover:text-white"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function CustomersTab({ customers, onRefresh }) {
  const [isOpen, setIsOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [formData, setFormData] = useState({ name: "", phone: "", address: "" });

  const openEditDialog = (customer) => {
    setEditingCustomer(customer);
    setFormData({ name: customer.name, phone: customer.phone || "", address: customer.address || "" });
    setIsOpen(true);
  };

  const closeDialog = () => {
    setIsOpen(false);
    setEditingCustomer(null);
    setFormData({ name: "", phone: "", address: "" });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingCustomer) {
        await axiosInstance.patch(`/customers/${editingCustomer.id}`, formData);
        toast.success("Cliente atualizado!");
      } else {
        await axiosInstance.post("/customers", formData);
        toast.success("Cliente criado!");
      }
      closeDialog();
      onRefresh();
    } catch (error) {
      toast.error("Erro ao salvar cliente");
    }
  };

  const deleteCustomer = async (customerId, customerName) => {
    if (!window.confirm(`Tem certeza que deseja excluir o cliente "${customerName}"?`)) return;
    
    try {
      await axiosInstance.delete(`/customers/${customerId}`);
      toast.success("Cliente excluído");
      onRefresh();
    } catch (error) {
      toast.error("Erro ao excluir cliente");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <Dialog open={isOpen} onOpenChange={(open) => !open && closeDialog()}>
          <DialogTrigger asChild>
            <Button data-testid="add-customer-button" className="bg-primary hover:bg-primary-hover text-white">
              <Plus className="w-4 h-4 mr-2" />
              Novo Cliente
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editingCustomer ? "Editar Cliente" : "Novo Cliente"}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nome *</label>
                <Input
                  data-testid="customer-name-input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="João Silva"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Telefone</label>
                <Input
                  data-testid="customer-phone-input"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="(11) 99999-9999"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Endereço</label>
                <Textarea
                  data-testid="customer-address-input"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  placeholder="Rua, número, bairro"
                  className="min-h-20"
                />
              </div>
              <Button data-testid="submit-customer-button" type="submit" className="w-full bg-primary hover:bg-primary-hover text-white">
                {editingCustomer ? "Atualizar Cliente" : "Criar Cliente"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="bg-white rounded-2xl p-6 shadow-warm">
        <h3 className="text-xl font-outfit font-semibold text-secondary mb-4">Clientes Cadastrados</h3>
        {customers.length === 0 ? (
          <p className="text-center text-secondary-light py-8">Nenhum cliente cadastrado</p>
        ) : (
          <div className="space-y-2">
            {customers.map((c) => (
              <div key={c.id} data-testid={`customer-item-${c.id}`} className="flex items-start justify-between p-4 border border-orange-100 rounded-xl hover:border-primary transition-all">
                <div className="flex-1">
                  <p className="font-semibold text-secondary">{c.name}</p>
                  {c.phone && <p className="text-sm text-secondary-light">📞 {c.phone}</p>}
                  {c.address && <p className="text-sm text-secondary-light">📍 {c.address}</p>}
                </div>
                <div className="flex gap-2">
                  <Button
                    data-testid={`edit-customer-${c.id}`}
                    onClick={() => openEditDialog(c)}
                    variant="outline"
                    size="sm"
                    className="border-accent-blue text-accent-blue hover:bg-accent-blue hover:text-white"
                  >
                    <Settings className="w-4 h-4" />
                  </Button>
                  <Button
                    data-testid={`delete-customer-${c.id}`}
                    onClick={() => deleteCustomer(c.id, c.name)}
                    variant="outline"
                    size="sm"
                    className="border-accent-red text-accent-red hover:bg-accent-red hover:text-white"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function UsersTab({ users, onDelete, onRefresh }) {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({ code: "", name: "" });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axiosInstance.post("/users", { ...formData, role: "attendant" });
      toast.success("Funcionário criado!");
      setIsOpen(false);
      setFormData({ code: "", name: "" });
      onRefresh();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erro ao criar funcionário");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-user-button" className="bg-primary hover:bg-primary-hover text-white">
              <Plus className="w-4 h-4 mr-2" />
              Novo Funcionário
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Novo Funcionário</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Código</label>
                <Input
                  data-testid="user-code-input"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  placeholder="001"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Nome</label>
                <Input
                  data-testid="user-name-input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="João Silva"
                  required
                />
              </div>
              <Button data-testid="submit-user-button" type="submit" className="w-full bg-primary hover:bg-primary-hover text-white">
                Criar Funcionário
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="bg-white rounded-2xl p-6 shadow-warm">
        <h3 className="text-xl font-outfit font-semibold text-secondary mb-4">Funcionários Ativos</h3>
        <div className="space-y-2">
          {users.filter(u => u.role === "attendant").map((u) => (
            <div key={u.id} data-testid={`user-item-${u.code}`} className="flex items-center justify-between p-4 border border-orange-100 rounded-xl">
              <div>
                <p className="font-semibold text-secondary">{u.name}</p>
                <p className="text-sm text-secondary-light">Código: {u.code}</p>
              </div>
              <Button
                data-testid={`delete-user-${u.code}`}
                onClick={() => onDelete(u.id)}
                variant="outline"
                size="sm"
                className="border-accent-red text-accent-red hover:bg-accent-red hover:text-white"
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function SettingsTab({ settings, setSettings, onSubmit, loading }) {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-warm">
      <h3 className="text-xl font-outfit font-semibold text-secondary mb-6">Configurações da Loja</h3>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-secondary mb-2">Nome da Loja</label>
          <Input
            data-testid="settings-store-name-input"
            value={settings.store_name || ""}
            onChange={(e) => setSettings({ ...settings, store_name: e.target.value })}
            placeholder="Dona Guedes"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-secondary mb-2">Endereço da Loja</label>
          <Input
            data-testid="settings-store-address-input"
            value={settings.store_address || ""}
            onChange={(e) => setSettings({ ...settings, store_address: e.target.value })}
            placeholder="Rua, número, bairro"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-secondary mb-2">IP da Impressora (Tanca T650)</label>
          <Input
            data-testid="settings-printer-ip-input"
            value={settings.printer_ip || ""}
            onChange={(e) => setSettings({ ...settings, printer_ip: e.target.value })}
            placeholder="192.168.1.100"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-secondary mb-2">Porta da Impressora</label>
          <Input
            data-testid="settings-printer-port-input"
            type="number"
            value={settings.printer_port || 9100}
            onChange={(e) => setSettings({ ...settings, printer_port: parseInt(e.target.value) })}
            placeholder="9100"
          />
        </div>
        <Button
          data-testid="save-settings-button"
          type="submit"
          disabled={loading}
          className="w-full h-12 bg-primary hover:bg-primary-hover text-white rounded-xl shadow-lg"
        >
          {loading ? "Salvando..." : "Salvar Configurações"}
        </Button>
      </form>
    </div>
  );
}