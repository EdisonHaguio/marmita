"""
Sistema de Controle de Licenças - Japão Informática
Gerencia mensalidades e bloqueio de clientes inadimplentes
"""

import os
import json
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

LICENSE_FILE = Path(__file__).parent / ".license"
LICENSE_SERVER = os.environ.get('LICENSE_SERVER_URL', 'https://japao-licencas.herokuapp.com')

class LicenseManager:
    def __init__(self):
        self.license_data = self._load_license()
    
    def _load_license(self):
        """Carrega dados da licença do arquivo local"""
        if LICENSE_FILE.exists():
            try:
                with open(LICENSE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_license(self):
        """Salva dados da licença no arquivo local"""
        with open(LICENSE_FILE, 'w') as f:
            json.dump(self.license_data, f)
    
    def register_client(self, client_name, cnpj_cpf, phone, email):
        """
        Registra um novo cliente no servidor de licenças
        """
        try:
            response = requests.post(
                f"{LICENSE_SERVER}/api/register",
                json={
                    "client_name": client_name,
                    "cnpj_cpf": cnpj_cpf,
                    "phone": phone,
                    "email": email,
                    "system": "Dona Guedes - Marmitaria"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.license_data = {
                    "license_key": data['license_key'],
                    "client_name": client_name,
                    "status": "active",
                    "expires_at": data['expires_at'],
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
                self._save_license()
                return True, "Licença ativada com sucesso!"
            else:
                return False, "Erro ao registrar licença"
        except Exception as e:
            # Se não conseguir conectar ao servidor, permite uso trial de 7 dias
            expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
            self.license_data = {
                "license_key": "TRIAL",
                "client_name": client_name,
                "status": "trial",
                "expires_at": expires_at,
                "last_check": datetime.now(timezone.utc).isoformat()
            }
            self._save_license()
            return True, f"Modo Trial ativado (7 dias). Erro: {str(e)}"
    
    def check_license(self):
        """
        Verifica se a licença está ativa
        Retorna: (is_valid, message, days_remaining)
        """
        if not self.license_data:
            return False, "Sistema não ativado. Entre em contato: (19) 99813-2220", 0
        
        # Verifica data de expiração local
        expires_at = datetime.fromisoformat(self.license_data.get('expires_at', ''))
        now = datetime.now(timezone.utc)
        days_remaining = (expires_at - now).days
        
        if days_remaining < 0:
            return False, f"Licença EXPIRADA há {abs(days_remaining)} dias. Contate: (19) 99813-2220", days_remaining
        
        # Tenta verificar online (a cada 24h)
        last_check = datetime.fromisoformat(self.license_data.get('last_check', ''))
        hours_since_check = (now - last_check).total_seconds() / 3600
        
        if hours_since_check > 24:
            self._check_online()
        
        # Aviso se está próximo do vencimento
        if days_remaining <= 5:
            return True, f"⚠️ Licença vence em {days_remaining} dias. Renove: (19) 99813-2220", days_remaining
        
        return True, "Licença ativa", days_remaining
    
    def _check_online(self):
        """Verifica status da licença no servidor"""
        try:
            response = requests.get(
                f"{LICENSE_SERVER}/api/check",
                params={"license_key": self.license_data.get('license_key')},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.license_data['status'] = data['status']
                self.license_data['expires_at'] = data['expires_at']
                self.license_data['last_check'] = datetime.now(timezone.utc).isoformat()
                self._save_license()
        except:
            # Se não conseguir conectar, usa cache local
            pass
    
    def get_client_info(self):
        """Retorna informações do cliente"""
        if not self.license_data:
            return None
        
        return {
            "client_name": self.license_data.get('client_name'),
            "status": self.license_data.get('status'),
            "expires_at": self.license_data.get('expires_at')
        }


# Instância global
license_manager = LicenseManager()
