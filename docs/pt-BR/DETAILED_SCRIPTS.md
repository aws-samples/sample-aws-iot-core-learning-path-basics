# Documentação Detalhada dos Scripts

Este documento fornece documentação abrangente para todos os scripts de aprendizagem no projeto AWS IoT Core - Básicos.

## Índice

- [Explorador de API do Registro IoT](#explorador-de-api-do-registro-iot)
- [Gerenciador de Certificados e Políticas](#gerenciador-de-certificados-e-políticas)
- [Comunicação MQTT](#comunicação-mqtt)
- [Explorador de Device Shadow](#explorador-de-device-shadow)
- [Explorador do IoT Rules Engine](#explorador-do-iot-rules-engine)

## Explorador de API do Registro IoT

### Propósito
Ferramenta interativa para aprender APIs do Registro AWS IoT através de chamadas de API reais com explicações detalhadas. Este script ensina as operações do Plano de Controle usadas para gerenciar dispositivos IoT, certificados e políticas.

### Como Executar

**Uso Básico:**
```bash
python iot_registry_explorer.py
```

**Com Modo Debug (detalhes aprimorados da API):**
```bash
python iot_registry_explorer.py --debug
```

### Sistema de Menu Interativo

Quando você executa o script, verá:
```
📋 Operações Disponíveis:
1. Listar Things
2. Listar Certificados
3. Listar Thing Groups
4. Listar Thing Types
5. Descrever Thing
6. Descrever Thing Group
7. Descrever Thing Type
8. Descrever Endpoint
9. Sair

Selecionar operação (1-9):
```

### APIs Suportadas com Detalhes de Aprendizagem

#### 1. Listar Things
- **Propósito**: Recuperar todos os dispositivos IoT em sua conta
- **HTTP**: `GET /things`
- **Aprender**: Descoberta de dispositivos com opções de paginação e filtragem
- **Opções Disponíveis**:
  - **Listagem básica**: Mostra todos os Things
  - **Paginação**: Recuperar Things em lotes menores
  - **Filtrar por Thing Type**: Encontrar veículos de categorias específicas
  - **Filtrar por Atributo**: Encontrar veículos com atributos específicos

#### 2. Listar Certificados
- **Propósito**: Ver todos os certificados X.509 para autenticação de dispositivos
- **HTTP**: `GET /certificates`
- **Aprender**: Ciclo de vida de certificados, gerenciamento de status

#### 3. Listar Thing Groups
- **Propósito**: Ver organização de dispositivos e hierarquias
- **HTTP**: `GET /thing-groups`
- **Aprender**: Estratégias de agrupamento de dispositivos, gerenciamento em escala

#### 4. Listar Thing Types
- **Propósito**: Ver modelos e categorias de dispositivos
- **HTTP**: `GET /thing-types`
- **Aprender**: Classificação de dispositivos, esquemas de atributos

#### 5. Descrever Thing
- **Propósito**: Obter informações detalhadas sobre um dispositivo específico
- **HTTP**: `GET /things/{thingName}`
- **Entrada Necessária**: Nome do Thing (ex: "Vehicle-VIN-001")
- **Aprender**: Metadados de dispositivos, atributos, relacionamentos

#### 6. Descrever Thing Group
- **Propósito**: Ver detalhes e propriedades do grupo
- **HTTP**: `GET /thing-groups/{thingGroupName}`
- **Entrada Necessária**: Nome do grupo (ex: "CustomerFleet")
- **Aprender**: Hierarquias de grupos, políticas, atributos

#### 7. Descrever Thing Type
- **Propósito**: Ver especificações e modelos de tipos
- **HTTP**: `GET /thing-types/{thingTypeName}`
- **Entrada Necessária**: Nome do tipo (ex: "SedanVehicle")
- **Aprender**: Definições de tipos, atributos pesquisáveis

#### 8. Descrever Endpoint
- **Propósito**: Obter URLs de endpoint IoT para sua conta
- **HTTP**: `GET /endpoint`
- **Opções de Entrada**: Tipo de endpoint (iot:Data-ATS, iot:Data, etc.)
- **Aprender**: Diferentes tipos de endpoint e seus propósitos

### Recursos de Aprendizagem

**Para cada chamada de API, você verá:**
- 🔄 **Nome da chamada de API** e descrição
- 🌐 **Requisição HTTP** método e caminho completo
- ℹ️ **Explicação da operação** - o que faz e por quê
- 📥 **Parâmetros de entrada** - quais dados você está enviando
- 💡 **Explicação da resposta** - o que a saída significa
- 📤 **Payload da resposta** - dados JSON reais retornados

## Gerenciador de Certificados e Políticas

### Propósito
Aprender conceitos de segurança AWS IoT através do gerenciamento prático de certificados e políticas. Este script ensina o modelo de segurança completo: identidade do dispositivo (certificados) e autorização (políticas).

### Como Executar

**Uso Básico:**
```bash
python certificate_manager.py
```

**Com Modo Debug (logging detalhado da API):**
```bash
python certificate_manager.py --debug
```

### Menu Principal Interativo

Quando você executa o script, verá:
```
🔐 Gerenciador de Certificados e Políticas AWS IoT
==================================================
Este script ensina conceitos de segurança AWS IoT:
• Certificados X.509 para autenticação de dispositivos
• Anexação de certificado ao Thing
• Políticas IoT para autorização
• Anexação e desanexação de políticas
• Registro de certificados externos
• Detalhes completos da API para cada operação
==================================================

📋 Menu Principal:
1. Criar Certificado AWS IoT e Anexar ao Thing (+ Política Opcional)
2. Registrar Certificado Externo e Anexar ao Thing (+ Política Opcional)
3. Anexar Política ao Certificado Existente
4. Desanexar Política do Certificado
5. Habilitar/Desabilitar Certificado
6. Sair

Selecionar opção (1-6):
```

### Opção 1: Fluxo Completo de Certificado

**O que isso ensina:**
- Ciclo de vida completo do certificado
- Estabelecimento de identidade do dispositivo
- Melhores práticas de segurança

**Processo passo a passo:**

#### Passo 1: Seleção de Thing
- **Seletor interativo de dispositivos** com múltiplas opções
- **Validação** - Confirma que o Thing existe antes de prosseguir
- **Aprendizagem**: Padrões de descoberta e seleção de dispositivos

#### Passo 2: Criação de Certificado
- **Chamada de API**: `create_keys_and_certificate`
- **HTTP**: `POST /keys-and-certificate`
- **O que acontece**: AWS gera certificado X.509 + par de chaves
- **Aprendizagem**: Componentes do certificado e seus propósitos

#### Passo 3: Armazenamento de Arquivo Local
- **Criação automática de pasta**: `certificates/{thing-name}/`
- **Arquivos salvos**:
  - `{cert-id}.crt` - Certificado PEM (para AWS IoT)
  - `{cert-id}.key` - Chave privada (manter segura!)
  - `{cert-id}.pub` - Chave pública (para referência)

#### Passo 4: Anexação Certificado-Thing
- **Chamada de API**: `attach_thing_principal`
- **HTTP**: `PUT /things/{thingName}/principals`
- **Aprendizagem**: Vinculação de identidade do dispositivo

#### Passo 5: Gerenciamento de Política (Opcional)
- **Escolha**: Usar política existente, criar nova política ou pular
- **Aprendizagem**: Autorização vs autenticação, estratégias de reutilização de políticas

### Gerenciamento de Certificados Detalhado

**Criação de Certificado X.509:**
- Conceitos de **Infraestrutura de Chave Pública (PKI)**
- Papel da **Autoridade Certificadora (CA)** no AWS IoT
- **Geração de par de chaves** e princípios criptográficos
- **Ciclo de vida do certificado** - criação, ativação, rotação, revogação

**Estratégia de Armazenamento de Arquivo Local:**
```
certificates/
├── Vehicle-VIN-001/               # Uma pasta por Thing
│   ├── abc123def456.crt          # Certificado PEM
│   ├── abc123def456.key          # Chave privada (NUNCA compartilhar)
│   └── abc123def456.pub          # Chave pública (referência)
├── Vehicle-VIN-002/
│   ├── xyz789uvw012.crt
│   ├── xyz789uvw012.key
│   └── xyz789uvw012.pub
└── MyCustomDevice/
    └── ...
```

### Gerenciamento de Políticas Detalhado

**Modelos de Política Explicados:**

**1. Política Básica de Dispositivo:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "iot:Connect",     # Conectar ao AWS IoT
      "iot:Publish",     # Enviar mensagens
      "iot:Subscribe",   # Escutar tópicos
      "iot:Receive"      # Receber mensagens
    ],
    "Resource": "*"      # Todos os recursos (permissões amplas)
  }]
}
```

**2. Política Somente Leitura:**
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "iot:Connect",     # Apenas conectar
      "iot:Subscribe",   # Apenas escutar
      "iot:Receive"      # Apenas receber (sem publicação)
    ],
    "Resource": "*"
  }]
}
```

## Comunicação MQTT

### Propósito
Experimentar comunicação IoT em tempo real usando o protocolo MQTT. Aprender como dispositivos se conectam ao AWS IoT Core e trocam mensagens com segurança.

### Duas Opções MQTT Disponíveis

#### Opção A: MQTT Baseado em Certificado (Recomendado para Aprendizagem)
**Arquivo**: `mqtt_client_explorer.py`
**Autenticação**: Certificados X.509 (TLS mútuo)
**Melhor para**: Entender segurança IoT de produção

#### Opção B: MQTT WebSocket (Método Alternativo)
**Arquivo**: `mqtt_websocket_explorer.py`
**Autenticação**: Credenciais AWS IAM (SigV4)
**Melhor para**: Aplicações web e conexões amigáveis a firewall

### Cliente MQTT Baseado em Certificado

#### Como Executar

**Uso Básico:**
```bash
python mqtt_client_explorer.py
```

**Com Modo Debug (diagnósticos de conexão):**
```bash
python mqtt_client_explorer.py --debug
```

#### Pré-requisitos
- **Certificados devem existir** - Execute `certificate_manager.py` primeiro
- **Política anexada** - Certificado precisa de permissões IoT
- **Associação Thing** - Certificado deve estar anexado a um Thing

#### Comandos Interativos

Uma vez conectado, use estes comandos:

```bash
# Assinatura de Tópico
📡 MQTT> sub device/+/temperature                  # Assinar com QoS 0
📡 MQTT> sub1 device/alerts/#                      # Assinar com QoS 1
📡 MQTT> unsub device/+/temperature               # Cancelar assinatura

# Publicação de Mensagem
📡 MQTT> pub device/sensor/temperature 23.5        # Publicar com QoS 0
📡 MQTT> pub1 device/alert "Temp alta!"            # Publicar com QoS 1
📡 MQTT> json device/data temp=23.5 humidity=65    # Publicar objeto JSON

# Comandos Utilitários
📡 MQTT> test                                      # Enviar mensagem de teste
📡 MQTT> status                                    # Mostrar info de conexão
📡 MQTT> messages                                  # Mostrar histórico de mensagens
📡 MQTT> help                                      # Mostrar todos os comandos
📡 MQTT> quit                                      # Sair do cliente
```

### Aprendizagem do Protocolo MQTT

#### Conceitos Principais

**Tópicos e Hierarquias:**
- **Estrutura de Tópico**: `device/sensor/temperature`
- **Wildcards**: `device/+/temperature` (nível único), `device/#` (multi-nível)
- **Melhores Práticas**: Nomenclatura hierárquica, evitar espaços

**Qualidade de Serviço (QoS):**
- **QoS 0 (No máximo uma vez)**: Disparar e esquecer, mais rápido
- **QoS 1 (Pelo menos uma vez)**: Entrega garantida, pode duplicar
- **QoS 2 (Exatamente uma vez)**: Não suportado pelo AWS IoT

## Explorador de Device Shadow

### Propósito
Aprender o serviço AWS IoT Device Shadow através da exploração prática da sincronização de estado de dispositivos. Este script ensina o ciclo de vida completo do shadow: estado desejado, estado relatado e processamento de delta.

### Como Executar

**Uso Básico:**
```bash
python device_shadow_explorer.py
```

**Com Modo Debug (análise detalhada de mensagens shadow):**
```bash
python device_shadow_explorer.py --debug
```

### Pré-requisitos
- **Certificados devem existir** - Execute `certificate_manager.py` primeiro
- **Política com permissões shadow** - Certificado precisa de permissões IoT shadow
- **Associação Thing** - Certificado deve estar anexado a um Thing

### Comandos Interativos

Uma vez conectado, use estes comandos:

```bash
# Operações Shadow
🌟 Shadow> get                                    # Solicitar documento shadow atual
🌟 Shadow> report                                 # Relatar estado local ao shadow
🌟 Shadow> desire temperature=25.0 status=active # Definir estado desejado

# Gerenciamento de Dispositivo Local
🌟 Shadow> local                                  # Mostrar estado atual do dispositivo local
🌟 Shadow> edit                                   # Editar estado do dispositivo local

# Comandos Utilitários
🌟 Shadow> status                                 # Mostrar status de conexão e shadow
🌟 Shadow> help                                   # Mostrar todos os comandos
🌟 Shadow> quit                                   # Sair do explorador
```

### Recursos Principais de Aprendizagem

#### Estrutura do Documento Shadow

**Documento Shadow Completo:**
```json
{
  "state": {
    "desired": {
      "temperature": 25.0,
      "status": "active"
    },
    "reported": {
      "temperature": 22.5,
      "status": "online",
      "firmware_version": "1.0.0"
    },
    "delta": {
      "temperature": 25.0,
      "status": "active"
    }
  },
  "metadata": {
    "desired": {
      "temperature": {
        "timestamp": 1642248600
      }
    },
    "reported": {
      "temperature": {
        "timestamp": 1642248500
      }
    }
  },
  "version": 15,
  "timestamp": 1642248600
}
```

#### Sincronização Automática de Estado
**Processamento de Delta:**
1. **Detecção de Delta** - Script detecta automaticamente quando desejado ≠ relatado
2. **Notificação do Usuário** - Mostra diferenças e solicita ação
3. **Atualização Local** - Aplica mudanças ao arquivo de estado do dispositivo local
4. **Relatório Shadow** - Relata estado atualizado de volta ao AWS IoT

## Explorador do IoT Rules Engine

### Propósito
Aprender o AWS IoT Rules Engine através da criação e gerenciamento prático de regras. Este script ensina roteamento de mensagens, filtragem baseada em SQL e configuração de ações com configuração automática de função IAM.

### Como Executar

**Uso Básico:**
```bash
python iot_rules_explorer.py
```

**Com Modo Debug (operações detalhadas de API e IAM):**
```bash
python iot_rules_explorer.py --debug
```

### Pré-requisitos
- **Credenciais AWS** - Permissões IAM para IoT Rules e gerenciamento de função IAM
- **Certificados não necessários** - Rules Engine opera no nível de serviço

### Opções do Menu Principal
Quando você executa o script:
1. **Listar todas as Regras IoT** - Ver regras existentes com status e ações
2. **Descrever Regra IoT específica** - Análise detalhada de regra e decomposição SQL
3. **Criar nova Regra IoT** - Criação guiada de regra com construtor SQL
4. **Gerenciar Regra IoT** - Habilitar, desabilitar ou excluir regras

### Recursos Principais de Aprendizagem

#### Fluxo de Criação de Regra
**Criação Guiada Passo a Passo:**
1. **Nomenclatura de Regra** - Aprender convenções de nomenclatura e requisitos de unicidade
2. **Seleção de Tipo de Evento** - Escolher entre tipos de eventos IoT comuns ou personalizado
3. **Construção de Declaração SQL** - Construção interativa de cláusulas SELECT, FROM, WHERE
4. **Configuração de Ação** - Configurar destinos de republicação com funções IAM adequadas
5. **Configuração Automática de IAM** - Script cria e configura permissões necessárias

#### Construtor de Declaração SQL

**Padrão de Tópico:**
```
testRulesEngineTopic/+/<eventType>
```

**Opções de Tipo de Evento:**
- `temperature` - Leituras de sensor de temperatura
- `humidity` - Medições de umidade
- `pressure` - Dados de sensor de pressão
- `motion` - Eventos de detecção de movimento
- `door` - Status de sensor de porta
- `alarm` - Eventos do sistema de alarme
- `status` - Status geral do dispositivo
- `battery` - Relatórios de nível de bateria
- `Custom` - Tipo de evento definido pelo usuário

#### Exemplos SQL Completos
**Monitoramento de Temperatura:**
```sql
SELECT deviceId, timestamp, value 
FROM 'testRulesEngineTopic/+/temperature' 
WHERE value > 30
```

**Alertas de Bateria:**
```sql
SELECT deviceId, battery, status 
FROM 'testRulesEngineTopic/+/battery' 
WHERE battery < 15
```

**Detecção de Movimento:**
```sql
SELECT * 
FROM 'testRulesEngineTopic/+/motion' 
WHERE value = 'detected'
```

### Configuração Automática de IAM

#### Criação de Função IAM
**Configuração Automática:**
- Cria `IoTRulesEngineRole` se não existir
- Configura política de confiança para `iot.amazonaws.com`
- Anexa permissões necessárias para ações de republicação
- Lida com atrasos de consistência eventual do IAM

### Testando Suas Regras

#### Exemplos de Mensagem de Teste
**Evento de Temperatura:**
```json
{
  "deviceId": "device123",
  "timestamp": 1642248600000,
  "value": 32.5,
  "unit": "celsius"
}
```

**Alerta de Bateria:**
```json
{
  "deviceId": "sensor456",
  "timestamp": 1642248600000,
  "battery": 15,
  "status": "low_battery"
}
```

#### Fluxo de Teste
1. **Criar Regra** - Use o script para criar uma regra com filtragem específica
2. **Publicar Mensagem de Teste** - Enviar mensagem para tópico de origem usando cliente MQTT
3. **Assinar Destino** - Escutar tópico de destino de republicação
4. **Verificar Roteamento** - Confirmar que a mensagem aparece no tópico de destino com filtragem correta

### Cenários de Aprendizagem

#### Cenário 1: Monitoramento de Temperatura
1. Criar regra para eventos de temperatura > 30°C
2. Testar com vários valores de temperatura
3. Observar comportamento de filtragem
4. Monitorar mensagens republicadas

#### Cenário 2: Seleção Multi-Atributo
1. Criar regra selecionando atributos específicos
2. Comparar estrutura de mensagem de entrada vs saída
3. Entender transformação de dados

#### Cenário 3: Filtragem Complexa
1. Criar regra com cláusula WHERE
2. Testar casos extremos e condições de limite
3. Aprender comportamento do operador SQL