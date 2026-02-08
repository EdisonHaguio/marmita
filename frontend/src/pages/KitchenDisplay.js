import { useState, useEffect } from "react";
import { axiosInstance } from "../App";
import { Button } from "../components/ui/button";
import { toast } from "sonner";
import { ChefHat, Clock, PlayCircle, CheckCircle, RefreshCw } from "lucide-react";

const STATUS_CONFIG = {
  pending: { label: "Pendente", color: "bg-orange-100 border-primary", icon: Clock, textColor: "text-primary" },
  preparing: { label: "Preparando", color: "bg-blue-100 border-accent-blue", icon: PlayCircle, textColor: "text-accent-blue" },
  ready: { label: "Pronto", color: "bg-green-100 border-accent-green", icon: CheckCircle, textColor: "text-accent-green" },
};

export default function KitchenDisplay() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadOrders();
    const interval = setInterval(loadOrders, 5000); // Auto refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const loadOrders = async () => {
    try {
      const response = await axiosInstance.get("/orders");
      const filtered = response.data.filter(o => ["pending", "preparing", "ready"].includes(o.status));
      setOrders(filtered);
    } catch (error) {
      console.error("Erro ao carregar pedidos");
    }
  };

  const updateOrderStatus = async (orderId, newStatus) => {
    setLoading(true);
    try {
      await axiosInstance.patch(`/orders/${orderId}/status`, { status: newStatus });
      toast.success("Status atualizado!");
      loadOrders();
    } catch (error) {
      toast.error("Erro ao atualizar status");
    } finally {
      setLoading(false);
    }
  };

  const getNextStatus = (currentStatus) => {
    if (currentStatus === "pending") return "preparing";
    if (currentStatus === "preparing") return "ready";
    if (currentStatus === "ready") return "delivered";
    return currentStatus;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FFF8F0] to-[#FFE0B2] p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-white rounded-2xl p-6 shadow-floating border-b-4 border-primary relative">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="bg-primary rounded-full p-3">
                <ChefHat className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-outfit font-bold text-secondary">Cozinha - Dona Guedes</h1>
                <p className="text-secondary-light">Pedidos em Tempo Real</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right hidden sm:block">
                <p className="text-xs text-secondary-light">Suporte: Japão Informática</p>
                <p className="text-xs text-secondary-light">(19) 99813-2220</p>
              </div>
              <Button
                data-testid="refresh-orders-button"
                onClick={loadOrders}
                variant="outline"
                className="border-primary text-primary hover:bg-primary hover:text-white"
              >
                <RefreshCw className="w-5 h-5 mr-2" />
                Atualizar
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Orders Grid */}
      <div className="max-w-7xl mx-auto">
        {orders.length === 0 ? (
          <div className="bg-white rounded-2xl p-12 shadow-warm text-center">
            <ChefHat className="w-16 h-16 text-secondary-light mx-auto mb-4" />
            <p className="text-xl text-secondary-light">Nenhum pedido pendente no momento</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {orders.map((order) => {
              const config = STATUS_CONFIG[order.status];
              const StatusIcon = config.icon;
              const nextStatus = getNextStatus(order.status);
              
              return (
                <div
                  key={order.id}
                  data-testid={`kitchen-order-${order.order_number}`}
                  className={`${config.color} border-4 rounded-2xl p-6 shadow-lg transition-all hover:scale-102`}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <StatusIcon className={`w-6 h-6 ${config.textColor}`} />
                      <span className={`text-sm font-semibold ${config.textColor}`}>{config.label}</span>
                    </div>
                    <span className="text-3xl font-mono font-bold text-secondary">#{order.order_number}</span>
                  </div>

                  <div className="bg-white rounded-xl p-4 mb-4 space-y-2">
                    <div>
                      <p className="text-xs text-secondary-light">Cliente</p>
                      <p className="text-lg font-semibold text-secondary">{order.customer_name}</p>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <p className="text-xs text-secondary-light">Tipo</p>
                        <p className="text-sm font-medium text-secondary">{order.order_type}</p>
                      </div>
                      <div>
                        <p className="text-xs text-secondary-light">Tamanho</p>
                        <p className="text-sm font-medium text-secondary">{order.size}</p>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-secondary-light">Mistura</p>
                      <p className="text-base font-bold text-primary">{order.protein}</p>
                    </div>
                    <div>
                      <p className="text-xs text-secondary-light">Acompanhamentos</p>
                      <p className="text-sm text-secondary">{order.accompaniments.join(", ")}</p>
                    </div>
                    {order.beverages && order.beverages.length > 0 && (
                      <div>
                        <p className="text-xs text-secondary-light">Bebidas</p>
                        <p className="text-sm text-accent-blue font-medium">{order.beverages.join(", ")}</p>
                      </div>
                    )}
                    {order.observations && (
                      <div className="pt-2 border-t border-orange-200">
                        <p className="text-xs text-secondary-light">Observações</p>
                        <p className="text-sm font-medium text-accent-red">{order.observations}</p>
                      </div>
                    )}
                  </div>

                  <Button
                    data-testid={`update-status-${order.order_number}`}
                    onClick={() => updateOrderStatus(order.id, nextStatus)}
                    disabled={loading}
                    className="w-full h-12 bg-secondary hover:bg-secondary-hover text-white rounded-xl shadow-lg hover:shadow-xl transition-all active:scale-95"
                  >
                    {order.status === "pending" && "Iniciar Preparo"}
                    {order.status === "preparing" && "Marcar como Pronto"}
                    {order.status === "ready" && "Marcar como Entregue"}
                  </Button>

                  <div className="mt-3 text-xs text-center text-secondary-light">
                    Atendente: {order.attendant_name}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}