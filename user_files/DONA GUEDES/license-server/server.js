// Servidor de Controle de Licenças - Japão Informática
// Node.js + Express + MongoDB Atlas (Grátis)

const express = require('express');
const cors = require('cors');
const { MongoClient } = require('mongodb');
const crypto = require('crypto');

const app = express();
app.use(cors());
app.use(express.json());

// Conectar ao MongoDB Atlas (grátis 512MB)
const MONGO_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const client = new MongoClient(MONGO_URI);
let db;

// Conectar ao banco
client.connect().then(() => {
  db = client.db('japao_licencas');
  console.log('✅ Conectado ao MongoDB');
});

// ===== ROTAS =====

// Registrar nova licença
app.post('/api/register', async (req, res) => {
  try {
    const { client_name, cnpj_cpf, phone, email, system } = req.body;
    
    // Gerar chave de licença única
    const license_key = crypto.randomBytes(16).toString('hex').toUpperCase();
    
    // Data de expiração: 30 dias
    const expires_at = new Date();
    expires_at.setDate(expires_at.getDate() + 30);
    
    // Salvar no banco
    await db.collection('licenses').insertOne({
      license_key,
      client_name,
      cnpj_cpf,
      phone,
      email,
      system,
      status: 'active',
      expires_at: expires_at.toISOString(),
      created_at: new Date().toISOString(),
      last_payment: new Date().toISOString()
    });
    
    // Notificar você (implementar webhook/email depois)
    console.log(`📝 Nova licença: ${client_name} - ${license_key}`);
    
    res.json({
      success: true,
      license_key,
      expires_at: expires_at.toISOString(),
      message: 'Licença ativada! Validade: 30 dias'
    });
  } catch (error) {
    console.error('Erro ao registrar:', error);
    res.status(500).json({ error: 'Erro ao registrar licença' });
  }
});

// Verificar status da licença
app.get('/api/check', async (req, res) => {
  try {
    const { license_key } = req.query;
    
    if (!license_key) {
      return res.status(400).json({ error: 'license_key obrigatório' });
    }
    
    const license = await db.collection('licenses').findOne({ license_key });
    
    if (!license) {
      return res.status(404).json({ 
        status: 'invalid',
        message: 'Licença não encontrada'
      });
    }
    
    const now = new Date();
    const expires = new Date(license.expires_at);
    const isExpired = now > expires;
    
    res.json({
      status: isExpired ? 'expired' : license.status,
      expires_at: license.expires_at,
      client_name: license.client_name,
      days_remaining: Math.ceil((expires - now) / (1000 * 60 * 60 * 24))
    });
  } catch (error) {
    console.error('Erro ao verificar:', error);
    res.status(500).json({ error: 'Erro ao verificar licença' });
  }
});

// Renovar licença (você usa isso após receber pagamento)
app.post('/api/renew', async (req, res) => {
  try {
    const { license_key, days = 30, admin_key } = req.body;
    
    // Chave de admin para segurança (configure no .env)
    if (admin_key !== process.env.ADMIN_KEY) {
      return res.status(403).json({ error: 'Não autorizado' });
    }
    
    const new_expires = new Date();
    new_expires.setDate(new_expires.getDate() + days);
    
    await db.collection('licenses').updateOne(
      { license_key },
      { 
        $set: { 
          expires_at: new_expires.toISOString(),
          status: 'active',
          last_payment: new Date().toISOString()
        }
      }
    );
    
    res.json({
      success: true,
      new_expires: new_expires.toISOString(),
      message: `Licença renovada por ${days} dias`
    });
  } catch (error) {
    res.status(500).json({ error: 'Erro ao renovar' });
  }
});

// Bloquear licença (inadimplente)
app.post('/api/block', async (req, res) => {
  try {
    const { license_key, admin_key } = req.body;
    
    if (admin_key !== process.env.ADMIN_KEY) {
      return res.status(403).json({ error: 'Não autorizado' });
    }
    
    await db.collection('licenses').updateOne(
      { license_key },
      { $set: { status: 'blocked' } }
    );
    
    res.json({ success: true, message: 'Licença bloqueada' });
  } catch (error) {
    res.status(500).json({ error: 'Erro ao bloquear' });
  }
});

// Listar todas as licenças (painel admin)
app.get('/api/licenses', async (req, res) => {
  try {
    const { admin_key } = req.query;
    
    if (admin_key !== process.env.ADMIN_KEY) {
      return res.status(403).json({ error: 'Não autorizado' });
    }
    
    const licenses = await db.collection('licenses')
      .find({})
      .sort({ created_at: -1 })
      .toArray();
    
    res.json({ licenses });
  } catch (error) {
    res.status(500).json({ error: 'Erro ao listar' });
  }
});

// Página inicial
app.get('/', (req, res) => {
  res.send(`
    <h1>🔐 Servidor de Licenças - Japão Informática</h1>
    <p>Sistema de controle de mensalidades ativo!</p>
    <p>Contato: (19) 99813-2220</p>
  `);
});

// Iniciar servidor
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Servidor rodando na porta ${PORT}`);
  console.log(`📞 Japão Informática - (19) 99813-2220`);
});

module.exports = app;
