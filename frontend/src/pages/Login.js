import { useState } from "react";
import { axiosInstance } from "../App";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { toast } from "sonner";
import { UtensilsCrossed, LogIn } from "lucide-react";

export default function Login({ onLogin }) {
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axiosInstance.post("/auth/login", {
        code,
        password: isAdmin ? password : undefined,
      });

      onLogin(response.data.user);
      toast.success(`Bem-vindo(a), ${response.data.user.name}!`);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Erro ao fazer login");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #FFF8F0 0%, #FFE0B2 100%)' }}>
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-floating p-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-primary rounded-full mb-4">
              <UtensilsCrossed className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-4xl font-outfit font-bold text-secondary mb-2">Dona Guedes</h1>
            <p className="text-secondary-light">Sistema de Pedidos</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-secondary mb-2">
                {isAdmin ? "Usuário Admin" : "Código do Funcionário"}
              </label>
              <Input
                data-testid="login-code-input"
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder={isAdmin ? "admin" : "001"}
                className="h-12 text-lg border-orange-200 focus:border-primary"
                required
              />
            </div>

            {isAdmin && (
              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Senha
                </label>
                <Input
                  data-testid="login-password-input"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="h-12 text-lg border-orange-200 focus:border-primary"
                  required
                />
              </div>
            )}

            <Button
              data-testid="login-submit-button"
              type="submit"
              disabled={loading}
              className="w-full h-12 text-lg bg-primary hover:bg-primary-hover text-white rounded-xl shadow-lg hover:shadow-xl transition-all active:scale-95"
            >
              <LogIn className="w-5 h-5 mr-2" />
              {loading ? "Entrando..." : "Entrar"}
            </Button>

            <button
              data-testid="toggle-admin-button"
              type="button"
              onClick={() => setIsAdmin(!isAdmin)}
              className="w-full text-sm text-secondary-light hover:text-secondary underline"
            >
              {isAdmin ? "Voltar para login de funcionário" : "Sou administrador"}
            </button>
          </form>
        </div>

        <div className="text-center mt-4 text-sm text-secondary-light">
          <p>Funcionário: use seu código | Admin: admin / admin123</p>
        </div>
      </div>
    </div>
  );
}