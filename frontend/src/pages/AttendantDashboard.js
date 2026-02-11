import { useState, useEffect } from "react";
import { axiosInstance } from "../App";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { toast } from "sonner";
import { LogOut, Plus, ShoppingBag, Bike, Check, Printer, Clock, Trash2 } from "lucide-react";

const SIZES = [
  { value: "P", label: "P", color: "bg-accent-green" },
  { value: "M", label: "M", color: "bg-accent-blue" },
  { value: "G", label: "G", color: "bg-primary" },
];

const ORDER_TYPES = [
  { value: "BALCAO", label: "Balcão", icon: ShoppingBag },
  { value: "ENTREGA", label: "Entrega", icon: Bike },
];

export default function AttendantDashboard({ user, onLogout }) {
  const [view, setView] = useState("new");
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [myOrders, setMyOrders] = useState([]);
  
  // Order form state
  const [customerName, setCustomerName] = useState("");
  const [isCompanyOrder, setIsCompanyOrder] = useState(false);
  const [showCustomerSuggestions, setShowCustomerSuggestions] = useState(false);
  const [orderType, setOrderType] = useState("BALCAO");
  const [deliveryAddress, setDeliveryAddress] = useState("");
  
  // Current marmita being added
  const [size, setSize] = useState("M");
  const [selectedAccompaniments, setSelectedAccompaniments] = useState([]);
  const [selectedProtein, setSelectedProtein] = useState("");
  const [employeeName, setEmployeeName] = useState("");  // Para pedidos de empresa
  
  // Cart of marmitas
  const [cartItems, setCartItems] = useState([]);
  
  // Shared items
  const [selectedSalads, setSelectedSalads] = useState([]);
  const [selectedBeverages, setSelectedBeverages] = useState([]);
  const [observations, setObservations] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProducts();
    loadCustomers();
    if (view === "orders") {
      loadMyOrders();
    }
  }, [view]);

  const loadProducts = async () => {
    try {
      const response = await axiosInstance.get("/products?active_only=true");
      setProducts(response.data);
    } catch (error) {
      toast.error("Erro ao carregar produtos");
    }
  };

  const loadCustomers = async () => {
    try {
      const response = await axiosInstance.get("/customers");
      setCustomers(response.data);
    } catch (error) {
      console.error("Erro ao carregar clientes");
    }
  };

  const loadMyOrders = async () => {
    try {
      const response = await axiosInstance.get("/orders");
      const filtered = response.data.filter(o => o.attendant_code === user.code);
      setMyOrders(filtered);
    } catch (error) {
      toast.error("Erro ao carregar pedidos");
    }
  };

  const toggleAccompaniment = (name) => {
    setSelectedAccompaniments(prev => 
      prev.includes(name) ? prev.filter(a => a !== name) : [...prev, name]
    );
  };

  const toggleSalad = (name) => {
    setSelectedSalads(prev => 
      prev.includes(name) ? prev.filter(s => s !== name) : [...prev, name]
    );
  };

  const toggleBeverage = (name) => {
    setSelectedBeverages(prev => 
      prev.includes(name) ? prev.filter(b => b !== name) : [...prev, name]
    );
  };

  const selectCustomer = (customer) => {
    setCustomerName(customer.name);
    if (customer.address) {
      setDeliveryAddress(customer.address);
    }
    setShowCustomerSuggestions(false);
  };

  const filteredCustomers = customers.filter(c => 
    c.name.toLowerCase().includes(customerName.toLowerCase())
  ).slice(0, 5);

  const calculateTotal = () => {
    let total = 0;
    
    // Calculate marmitas prices
    cartItems.forEach(item => {
      const proteinProduct = products.find(p => p.name === item.protein);
      if (proteinProduct) {
        const priceKey = `price_${item.size.toLowerCase()}`;
        total += proteinProduct[priceKey] || 0;
      }
    });
    
    // Add salad prices
    selectedSalads.forEach(saladName => {
      const salad = products.find(p => p.name === saladName && p.type === "salad");
      if (salad) {
        total += salad.price || 0;
      }
    });
    
    // Add beverage prices
    selectedBeverages.forEach(bevName => {
      const beverage = products.find(p => p.name === bevName && p.type === "beverage");
      if (beverage) {
        total += beverage.price || 0;
      }
    });
    
    return total;
  };

  const addMarmitaToCart = () => {
    if (!selectedProtein || selectedAccompaniments.length === 0) {
      toast.error("Selecione proteína e acompanhamentos");
      return;
    }

    if (isCompanyOrder && !employeeName) {
      toast.error("Digite o nome do funcionário");
      return;
    }

    const newItem = {
      size,
      protein: selectedProtein,
      accompaniments: selectedAccompaniments,
      employee_name: isCompanyOrder ? employeeName : null,
    };

    setCartItems([...cartItems, newItem]);
    
    // Reset marmita form
    setSize("M");
    setSelectedAccompaniments([]);
    setSelectedProtein("");
    setEmployeeName("");
    
    toast.success(isCompanyOrder ? `Marmita para ${employeeName} adicionada!` : "Marmita adicionada!");
  };

  const removeMarmitaFromCart = (index) => {
    setCartItems(cartItems.filter((_, i) => i !== index));
  };

  const handleCreateOrder = async () => {
    if (!customerName || cartItems.length === 0) {
      toast.error("Adicione pelo menos uma marmita ao pedido");
      return;
    }

    if (orderType === "ENTREGA" && !deliveryAddress) {
      toast.error("Endereço de entrega é obrigatório");
      return;
    }

    setLoading(true);

    try {
      const orderData = {
        customer_name: customerName,
        is_company_order: isCompanyOrder,
        order_type: orderType,
        delivery_address: orderType === "ENTREGA" ? deliveryAddress : null,
        items: cartItems,
        salads: selectedSalads,
        beverages: selectedBeverages,
        observations,
        total_price: calculateTotal(),
        attendant_code: user.code,
        attendant_name: user.name,
      };

      const response = await axiosInstance.post("/orders", orderData);
      
      // Try to print
      try {
        await axiosInstance.post(`/orders/${response.data.id}/print`);
        toast.success(`Pedido #${response.data.order_number} criado e enviado para impressão!`);
      } catch (printError) {
        toast.success(`Pedido #${response.data.order_number} criado!`);
        toast.warning("Não foi possível imprimir. Verifique a impressora.");
      }

      // Reset form
      setCustomerName("");
      setDeliveryAddress("");
      setCartItems([]);
      setSelectedAccompaniments([]);
      setSelectedProtein("");
      setSelectedSalads([]);
      setSelectedBeverages([]);
      setObservations("");
      setOrderType("BALCAO");
      setSize("M");
    } catch (error) {
      toast.error("Erro ao criar pedido");
    } finally {
      setLoading(false);
    }
  };

  const handlePrintOrder = async (orderId) => {
    try {
      await axiosInstance.post(`/orders/${orderId}/print`);
      toast.success("Pedido enviado para impressão!");
    } catch (error) {
      toast.error("Erro ao imprimir");
    }
  };

  const accompaniments = products.filter(p => p.type === "accompaniment");
  const proteins = products.filter(p => p.type === "protein");
  const salads = products.filter(p => p.type === "salad");
  const beverages = products.filter(p => p.type === "beverage");

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FFF8F0] to-[#FFE0B2]">
      {/* Header */}
      <header className="bg-white shadow-md border-b-4 border-primary relative">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-outfit font-bold text-secondary">Dona Guedes</h1>
            <p className="text-sm text-secondary-light">Olá, {user.name} (#{user.code})</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <p className="text-xs text-secondary-light">Suporte: Japão Informática</p>
              <p className="text-xs text-secondary-light">(19) 99813-2220</p>
            </div>
            <Button
              data-testid="logout-button"
              onClick={onLogout}
              variant="outline"
              className="border-secondary text-secondary hover:bg-secondary hover:text-white"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Sair
            </Button>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex gap-2 mb-6">
          <Button
            data-testid="new-order-tab"
            onClick={() => setView("new")}
            className={`flex-1 h-12 rounded-xl transition-all ${
              view === "new"
                ? "bg-primary text-white shadow-lg"
                : "bg-white text-secondary hover:bg-orange-50"
            }`}
          >
            <Plus className="w-5 h-5 mr-2" />
            Novo Pedido
          </Button>
          <Button
            data-testid="my-orders-tab"
            onClick={() => setView("orders")}
            className={`flex-1 h-12 rounded-xl transition-all ${
              view === "orders"
                ? "bg-primary text-white shadow-lg"
                : "bg-white text-secondary hover:bg-orange-50"
            }`}
          >
            <Clock className="w-5 h-5 mr-2" />
            Meus Pedidos
          </Button>
        </div>

        {view === "new" ? (
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Product Selection */}
            <div className="lg:col-span-2 space-y-6">
              {/* Customer Info */}
              <div className="bg-white rounded-2xl p-6 shadow-warm">
                <h2 className="text-xl font-outfit font-semibold text-secondary mb-4">Informações do Cliente</h2>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="relative">
                    <label className="block text-sm font-medium text-secondary mb-2">Nome do Cliente *</label>
                    <Input
                      data-testid="customer-name-input"
                      value={customerName}
                      onChange={(e) => {
                        setCustomerName(e.target.value);
                        setShowCustomerSuggestions(e.target.value.length > 0);
                      }}
                      onFocus={() => setShowCustomerSuggestions(customerName.length > 0)}
                      placeholder="Digite o nome"
                      className="h-12 border-orange-200"
                    />
                    {showCustomerSuggestions && filteredCustomers.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white border border-orange-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                        {filteredCustomers.map((customer) => (
                          <button
                            key={customer.id}
                            type="button"
                            onClick={() => selectCustomer(customer)}
                            className="w-full text-left px-4 py-2 hover:bg-orange-50 transition-colors border-b border-orange-100 last:border-b-0"
                          >
                            <p className="font-medium text-secondary">{customer.name}</p>
                            {customer.phone && <p className="text-xs text-secondary-light">📞 {customer.phone}</p>}
                            {customer.address && <p className="text-xs text-secondary-light">📍 {customer.address}</p>}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">Tipo de Pedido *</label>
                    <div className="flex gap-2">
                      {ORDER_TYPES.map((type) => (
                        <button
                          key={type.value}
                          data-testid={`order-type-${type.value.toLowerCase()}`}
                          onClick={() => setOrderType(type.value)}
                          className={`flex-1 h-12 rounded-xl border-2 transition-all flex items-center justify-center gap-2 ${
                            orderType === type.value
                              ? "border-primary bg-primary text-white"
                              : "border-orange-200 hover:border-primary bg-white text-secondary"
                          }`}
                        >
                          <type.icon className="w-5 h-5" />
                          {type.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
                {orderType === "ENTREGA" && (
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-secondary mb-2">Endereço de Entrega *</label>
                    <Input
                      data-testid="delivery-address-input"
                      value={deliveryAddress}
                      onChange={(e) => setDeliveryAddress(e.target.value)}
                      placeholder="Rua, número, bairro"
                      className="h-12 border-orange-200"
                    />
                  </div>
                )}
              </div>

              {/* Size Selection */}
              <div className="bg-white rounded-2xl p-6 shadow-warm">
                <h2 className="text-xl font-outfit font-semibold text-secondary mb-4">Tamanho da Marmita *</h2>
                <div className="grid grid-cols-3 gap-3">
                  {SIZES.map((s) => (
                    <button
                      key={s.value}
                      data-testid={`size-${s.value.toLowerCase()}`}
                      onClick={() => setSize(s.value)}
                      className={`h-20 rounded-xl border-2 transition-all font-semibold text-2xl ${
                        size === s.value
                          ? `${s.color} text-white border-transparent shadow-lg scale-105`
                          : "bg-white text-secondary border-orange-200 hover:border-primary"
                      }`}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Accompaniments */}
              <div className="bg-white rounded-2xl p-6 shadow-warm">
                <h2 className="text-xl font-outfit font-semibold text-secondary mb-4">Acompanhamentos *</h2>
                <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {accompaniments.map((acc) => (
                    <button
                      key={acc.id}
                      data-testid={`accompaniment-${acc.name.toLowerCase().replace(/\s/g, '-')}`}
                      onClick={() => toggleAccompaniment(acc.name)}
                      className={`h-16 rounded-xl border-2 transition-all flex items-center justify-center gap-2 font-medium ${
                        selectedAccompaniments.includes(acc.name)
                          ? "border-accent-green bg-accent-green text-white shadow-lg"
                          : "border-orange-200 bg-white text-secondary hover:border-primary"
                      }`}
                    >
                      {selectedAccompaniments.includes(acc.name) && <Check className="w-5 h-5" />}
                      {acc.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* Salads */}
              {salads.length > 0 && (
                <div className="bg-white rounded-2xl p-6 shadow-warm">
                  <h2 className="text-xl font-outfit font-semibold text-secondary mb-4">Saladas (Opcional)</h2>
                  <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
                    {salads.map((salad) => (
                      <button
                        key={salad.id}
                        data-testid={`salad-${salad.name.toLowerCase().replace(/\s/g, '-')}`}
                        onClick={() => toggleSalad(salad.name)}
                        className={`h-16 rounded-xl border-2 transition-all flex items-center justify-between px-4 font-medium ${
                          selectedSalads.includes(salad.name)
                            ? "border-accent-green bg-accent-green text-white shadow-lg"
                            : "border-orange-200 bg-white text-secondary hover:border-primary"
                        }`}
                      >
                        <span>{salad.name}</span>
                        <span className="text-sm opacity-80">+ R$ {(salad.price || 0).toFixed(2)}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Proteins */}
              <div className="bg-white rounded-2xl p-6 shadow-warm">
                <h2 className="text-xl font-outfit font-semibold text-secondary mb-4">Mistura (Proteína) *</h2>
                <div className="grid sm:grid-cols-2 gap-3">
                  {proteins.map((protein) => {
                    const priceKey = `price_${size.toLowerCase()}`;
                    const price = protein[priceKey] || 0;
                    return (
                      <button
                        key={protein.id}
                        data-testid={`protein-${protein.name.toLowerCase().replace(/\s/g, '-')}`}
                        onClick={() => setSelectedProtein(protein.name)}
                        className={`h-20 rounded-xl border-2 transition-all flex flex-col items-center justify-center font-medium ${
                          selectedProtein === protein.name
                            ? "border-primary bg-primary text-white shadow-lg"
                            : "border-orange-200 bg-white text-secondary hover:border-primary"
                        }`}
                      >
                        <span className="text-lg">{protein.name}</span>
                        <span className="text-sm opacity-80">R$ {price.toFixed(2)}</span>
                      </button>
                    );
                  })}
                </div>
                <Button
                  data-testid="add-marmita-to-cart"
                  onClick={addMarmitaToCart}
                  disabled={!selectedProtein || selectedAccompaniments.length === 0}
                  className="w-full mt-4 h-12 bg-accent-green hover:bg-green-700 text-white rounded-xl"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Adicionar Marmita ao Pedido
                </Button>
              </div>

              {/* Cart */}
              {cartItems.length > 0 && (
                <div className="bg-white rounded-2xl p-6 shadow-warm border-2 border-primary">
                  <h2 className="text-xl font-outfit font-semibold text-secondary mb-4">
                    Marmitas no Pedido ({cartItems.length})
                  </h2>
                  <div className="space-y-2">
                    {cartItems.map((item, index) => {
                      const proteinProduct = products.find(p => p.name === item.protein);
                      const priceKey = `price_${item.size.toLowerCase()}`;
                      const price = proteinProduct?.[priceKey] || 0;
                      return (
                        <div
                          key={index}
                          data-testid={`cart-item-${index}`}
                          className="flex items-center justify-between p-4 bg-orange-50 rounded-xl"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-mono font-bold text-primary">#{index + 1}</span>
                              <span className="font-semibold text-secondary">Tamanho {item.size}</span>
                              <span className="text-sm text-secondary-light">R$ {price.toFixed(2)}</span>
                            </div>
                            <p className="text-sm text-secondary">{item.protein}</p>
                            <p className="text-xs text-secondary-light">{item.accompaniments.join(", ")}</p>
                          </div>
                          <Button
                            data-testid={`remove-marmita-${index}`}
                            onClick={() => removeMarmitaFromCart(index)}
                            variant="outline"
                            size="sm"
                            className="border-accent-red text-accent-red hover:bg-accent-red hover:text-white"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Beverages */}
              {beverages.length > 0 && (
                <div className="bg-white rounded-2xl p-6 shadow-warm">
                  <h2 className="text-xl font-outfit font-semibold text-secondary mb-4">Bebidas (Opcional)</h2>
                  <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3">
                    {beverages.map((beverage) => (
                      <button
                        key={beverage.id}
                        data-testid={`beverage-${beverage.name.toLowerCase().replace(/\s/g, '-')}`}
                        onClick={() => toggleBeverage(beverage.name)}
                        className={`h-16 rounded-xl border-2 transition-all flex items-center justify-between px-4 font-medium ${
                          selectedBeverages.includes(beverage.name)
                            ? "border-accent-blue bg-accent-blue text-white shadow-lg"
                            : "border-orange-200 bg-white text-secondary hover:border-primary"
                        }`}
                      >
                        <span>{beverage.name}</span>
                        <span className="text-sm opacity-80">+ R$ {(beverage.price || 0).toFixed(2)}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Observations */}
              <div className="bg-white rounded-2xl p-6 shadow-warm">
                <h2 className="text-xl font-outfit font-semibold text-secondary mb-4">Observações</h2>
                <Textarea
                  data-testid="observations-input"
                  value={observations}
                  onChange={(e) => setObservations(e.target.value)}
                  placeholder="Exemplo: sem cebola, molho à parte..."
                  className="min-h-24 border-orange-200"
                />
              </div>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-2xl p-6 shadow-warm sticky top-4">
                <h2 className="text-xl font-outfit font-semibold text-secondary mb-4">Resumo do Pedido</h2>
                <div className="space-y-3 mb-6">
                  <div className="pb-2 border-b border-orange-100">
                    <p className="text-sm text-secondary-light">Cliente</p>
                    <p className="font-medium text-secondary">{customerName || "-"}</p>
                  </div>
                  <div className="pb-2 border-b border-orange-100">
                    <p className="text-sm text-secondary-light">Tipo</p>
                    <p className="font-medium text-secondary">{orderType}</p>
                  </div>
                  <div className="pb-2 border-b border-orange-100">
                    <p className="text-sm text-secondary-light">Marmitas</p>
                    <p className="font-medium text-secondary">
                      {cartItems.length > 0 ? `${cartItems.length} marmita${cartItems.length > 1 ? 's' : ''}` : "-"}
                    </p>
                  </div>
                  {selectedSalads.length > 0 && (
                    <div className="pb-2 border-b border-orange-100">
                      <p className="text-sm text-secondary-light">Saladas</p>
                      <p className="font-medium text-secondary">{selectedSalads.join(", ")}</p>
                    </div>
                  )}
                  {selectedBeverages.length > 0 && (
                    <div className="pb-2 border-b border-orange-100">
                      <p className="text-sm text-secondary-light">Bebidas</p>
                      <p className="font-medium text-secondary">{selectedBeverages.join(", ")}</p>
                    </div>
                  )}
                  {observations && (
                    <div className="pb-2 border-b border-orange-100">
                      <p className="text-sm text-secondary-light">Observações</p>
                      <p className="font-medium text-secondary text-sm">{observations}</p>
                    </div>
                  )}
                </div>
                <div className="bg-orange-50 rounded-xl p-4 mb-4">
                  <p className="text-sm text-secondary-light mb-1">Valor Total</p>
                  <p className="text-3xl font-outfit font-bold text-primary">R$ {calculateTotal().toFixed(2)}</p>
                </div>
                <Button
                  data-testid="create-order-button"
                  onClick={handleCreateOrder}
                  disabled={loading}
                  className="w-full h-14 text-lg bg-primary hover:bg-primary-hover text-white rounded-xl shadow-lg hover:shadow-xl transition-all active:scale-95"
                >
                  {loading ? "Criando..." : "Criar Pedido"}
                </Button>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl p-6 shadow-warm">
            <h2 className="text-2xl font-outfit font-semibold text-secondary mb-6">Meus Pedidos</h2>
            <div className="space-y-3">
              {myOrders.length === 0 ? (
                <p className="text-center text-secondary-light py-8">Nenhum pedido ainda</p>
              ) : (
                myOrders.map((order) => (
                  <div key={order.id} data-testid={`order-item-${order.order_number}`} className="border-2 border-orange-100 rounded-xl p-4 hover:border-primary transition-all">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-xl font-mono font-bold text-primary">#{order.order_number}</span>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            order.status === "pending" ? "bg-orange-100 text-primary" :
                            order.status === "preparing" ? "bg-blue-100 text-accent-blue" :
                            order.status === "ready" ? "bg-green-100 text-accent-green" :
                            "bg-gray-100 text-gray-600"
                          }`}>
                            {order.status === "pending" ? "Pendente" :
                             order.status === "preparing" ? "Preparando" :
                             order.status === "ready" ? "Pronto" : "Entregue"}
                          </span>
                        </div>
                        <p className="font-semibold text-secondary">{order.customer_name}</p>
                        <p className="text-sm text-secondary-light">
                          {order.size} | {order.protein} | {order.order_type}
                        </p>
                        <p className="text-sm font-medium text-primary mt-1">R$ {order.total_price.toFixed(2)}</p>
                      </div>
                      <Button
                        data-testid={`print-order-${order.order_number}`}
                        onClick={() => handlePrintOrder(order.id)}
                        size="sm"
                        variant="outline"
                        className="border-primary text-primary hover:bg-primary hover:text-white"
                      >
                        <Printer className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}