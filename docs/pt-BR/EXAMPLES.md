# Exemplos de Uso e Fluxos de Trabalho

Este documento fornece exemplos detalhados e fluxos de trabalho completos para o projeto de aprendizagem AWS IoT Core - Básicos.

## Índice

- [Fluxo de Trabalho Completo de Aprendizagem](#fluxo-de-trabalho-completo-de-aprendizagem)
- [Exemplos de Configuração de Dados de Exemplo](#exemplos-de-configuração-de-dados-de-exemplo)
- [Exemplos do Explorador de API do Registro IoT](#exemplos-do-explorador-de-api-do-registro-iot)
- [Exemplos do Gerenciador de Certificados](#exemplos-do-gerenciador-de-certificados)
- [Exemplos de Comunicação MQTT](#exemplos-de-comunicação-mqtt)
- [Exemplos de Device Shadow](#exemplos-de-device-shadow)
- [Exemplos do Rules Engine](#exemplos-do-rules-engine)
- [Exemplos de Limpeza](#exemplos-de-limpeza)
- [Exemplos de Tratamento de Erros](#exemplos-de-tratamento-de-erros)

## Fluxo de Trabalho Completo de Aprendizagem

### Sequência de Aprendizagem Recomendada

**Caminho de Aprendizagem Completo de Ponta a Ponta:**

```bash
# 1. Configuração do Ambiente
source venv/bin/activate
export AWS_ACCESS_KEY_ID=<sua-chave>
export AWS_SECRET_ACCESS_KEY=<sua-chave-secreta>
export AWS_DEFAULT_REGION=us-east-1

# 2. Criar Recursos IoT de Exemplo
python setup_sample_data.py

# 3. Explorar APIs do Registro AWS IoT
python iot_registry_explorer.py

# 4. Aprender Segurança com Certificados e Políticas
python certificate_manager.py

# 5. Experimentar Comunicação MQTT em Tempo Real
python mqtt_client_explorer.py
# OU
python mqtt_websocket_explorer.py

# 6. Aprender Sincronização de Estado de Dispositivos com Shadows
python device_shadow_explorer.py

# 7. Dominar Roteamento de Mensagens com Rules Engine
python iot_rules_explorer.py

# 8. Limpar Quando Terminar de Aprender
python cleanup_sample_data.py
```

## Exemplos de Configuração de Dados de Exemplo

### Experiência Interativa Passo a Passo

**Quando você executa `python setup_sample_data.py`, verá:**

```
🚀 Configuração de Dados de Exemplo AWS IoT
==========================================
Este script criará recursos IoT de exemplo para aprendizagem:
• 3 Thing Types (categorias de veículos)
• 4 Thing Groups (categorias de frota)  
• 20 Things (veículos simulados)

⚠️  Isso criará recursos reais da AWS que incorrem em custos.
Custo estimado: ~$0.05 para armazenamento de Things

Deseja continuar? (y/N): y

🔄 Passo 1: Criando Thing Types
✅ Thing Type criado: SedanVehicle
✅ Thing Type criado: SUVVehicle  
✅ Thing Type criado: TruckVehicle

🔄 Passo 2: Criando Thing Groups
✅ Thing Group criado: CustomerFleet
✅ Thing Group criado: TestFleet
✅ Thing Group criado: MaintenanceFleet
✅ Thing Group criado: DealerFleet

🔄 Passo 3: Criando Things (20 veículos)
✅ Thing criado: Vehicle-VIN-001 (SedanVehicle → CustomerFleet)
✅ Thing criado: Vehicle-VIN-002 (SUVVehicle → TestFleet)
...
✅ Thing criado: Vehicle-VIN-020 (TruckVehicle → DealerFleet)

📊 Resumo:
   Thing Types: 3 criados
   Thing Groups: 4 criados  
   Things: 20 criados
   
🎉 Configuração de dados de exemplo concluída!
```

### Exemplo do Modo Debug

**Com `python setup_sample_data.py --debug`:**

```
🔍 DEBUG: Criando Thing Type 'SedanVehicle'
📥 Chamada de API: create_thing_type
📤 Requisição: {
  "thingTypeName": "SedanVehicle",
  "thingTypeProperties": {
    "description": "Veículos sedan de passageiros",
    "searchableAttributes": ["customerId", "country", "manufacturingDate"]
  }
}
📨 Resposta: {
  "thingTypeName": "SedanVehicle",
  "thingTypeArn": "arn:aws:iot:us-east-1:123456789012:thingtype/SedanVehicle"
}
⏱️  Duração: 0.45 segundos
```

## Exemplos do Explorador de API do Registro IoT

### Navegação do Menu Interativo

**Menu Principal:**
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

Selecionar operação (1-9): 1
```

### Exemplo de Listar Things

**Listagem Básica:**
```
🔄 Chamada de API: list_things
🌐 Requisição HTTP: GET https://iot.us-east-1.amazonaws.com/things
ℹ️  Descrição: Recupera todos os Things IoT em sua conta AWS
📥 Parâmetros de Entrada: Nenhum (listagem básica)
💡 Explicação da Resposta: Retorna array de objetos Thing com nomes, tipos e atributos

📤 Payload da Resposta:
Encontrados 20 Things:
1. Vehicle-VIN-001 (Tipo: SedanVehicle)
   Atributos: customerId=a1b2c3d4-e5f6-7890, country=US, manufacturingDate=2024-03-15
2. Vehicle-VIN-002 (Tipo: SUVVehicle)  
   Atributos: customerId=b2c3d4e5-f6g7-8901, country=Germany, manufacturingDate=2024-07-22
...
```

### Exemplo de Descrever Thing

**Seleção de Thing:**
```
Digite o nome do Thing: Vehicle-VIN-001

🔄 Chamada de API: describe_thing
🌐 Requisição HTTP: GET https://iot.us-east-1.amazonaws.com/things/Vehicle-VIN-001
📥 Parâmetros de Entrada: {"thingName": "Vehicle-VIN-001"}

📤 Payload da Resposta:
{
  "thingName": "Vehicle-VIN-001",
  "thingId": "12345678-1234-1234-1234-123456789012",
  "thingArn": "arn:aws:iot:us-east-1:123456789012:thing/Vehicle-VIN-001",
  "thingTypeName": "SedanVehicle",
  "attributes": {
    "customerId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "country": "US", 
    "manufacturingDate": "2024-03-15"
  },
  "version": 1
}
```

## Exemplos do Gerenciador de Certificados

### Fluxo Completo de Certificado

**Opção 1: Criar Certificado AWS IoT e Anexar ao Thing**

```
📋 Menu Principal:
1. Criar Certificado AWS IoT e Anexar ao Thing (+ Política Opcional)
2. Registrar Certificado Externo e Anexar ao Thing (+ Política Opcional)  
3. Anexar Política ao Certificado Existente
4. Desanexar Política do Certificado
5. Habilitar/Desabilitar Certificado
6. Sair

Selecionar opção (1-6): 1

📚 MOMENTO DE APRENDIZAGEM: Criação de Certificado e Anexação ao Thing
Criar um certificado AWS IoT estabelece uma identidade digital única para seu dispositivo...

Pressione Enter para continuar...

📱 Things Disponíveis (20 encontrados):
   1. Vehicle-VIN-001 (Tipo: SedanVehicle)
   2. Vehicle-VIN-002 (Tipo: SUVVehicle)
   ...
   10. Vehicle-VIN-010 (Tipo: TruckVehicle)
   ... e mais 10

📋 Opções:
   • Digite número (1-20) para selecionar Thing
   • Digite 'all' para ver todos os Things  
   • Digite 'manual' para inserir nome do Thing manualmente

Sua escolha: 1
✅ Thing selecionado: Vehicle-VIN-001
```

**Processo de Criação de Certificado:**
```
🔐 Passo 1: Criando Certificado X.509
--------------------------------------------------
ℹ️  Certificados X.509 são usados para autenticação de dispositivos no AWS IoT
ℹ️  Cada certificado contém um par de chaves pública/privada

🔍 Detalhes da API:
   Operação: create_keys_and_certificate
   Método HTTP: POST
   Caminho da API: /keys-and-certificate
   Descrição: Cria um novo certificado X.509 com par de chaves pública/privada
   Parâmetros de Entrada: setAsActive: true (ativa certificado imediatamente)
   Saída Esperada: certificateArn, certificateId, certificatePem, keyPair

🔄 Criando certificado e par de chaves...
📥 Entrada: {"setAsActive": true}
✅ Criação de certificado e par de chaves concluída com sucesso

📋 Detalhes do Certificado:
   ID do Certificado: abc123def456789ghi012jkl345mno678pqr901stu234vwx567yz890
   ARN do Certificado: arn:aws:iot:us-east-1:123456789012:cert/abc123def456789ghi012jkl345mno678pqr901stu234vwx567yz890
   Status: ATIVO

   📄 Certificado: certificates/Vehicle-VIN-001/abc123def456789ghi012jkl345mno678pqr901stu234vwx567yz890.crt
   🔐 Chave Privada: certificates/Vehicle-VIN-001/abc123def456789ghi012jkl345mno678pqr901stu234vwx567yz890.key
   🔑 Chave Pública: certificates/Vehicle-VIN-001/abc123def456789ghi012jkl345mno678pqr901stu234vwx567yz890.pub

💾 Arquivos de certificado salvos em: certificates/Vehicle-VIN-001
```

**Anexação Certificado-Thing:**
```
🔐 Passo 2: Anexando Certificado ao Thing
--------------------------------------------------
ℹ️  Certificados devem ser anexados aos Things para autenticação de dispositivos
ℹ️  Isso cria uma relação segura entre o certificado e o dispositivo IoT
ℹ️  Certificado será anexado a: Vehicle-VIN-001

🔗 Anexando certificado ao Thing: Vehicle-VIN-001

🔍 Detalhes da API:
   Operação: attach_thing_principal
   Método HTTP: PUT
   Caminho da API: /things/Vehicle-VIN-001/principals
   Descrição: Anexa um certificado (principal) a um Thing para autenticação
   Parâmetros de Entrada: thingName: Vehicle-VIN-001, principal: arn:aws:iot:...
   Saída Esperada: Resposta vazia em caso de sucesso

🔄 Anexando certificado ao Vehicle-VIN-001...
✅ Anexação de certificado ao Vehicle-VIN-001 concluída
✅ Certificado anexado com sucesso ao Vehicle-VIN-001
   ℹ️  O Thing agora pode usar este certificado para autenticação
```

## Exemplos de Comunicação MQTT

### Sessão MQTT Baseada em Certificado

**Seleção de Dispositivo:**
```
🔍 Descobrindo Things com certificados...
📋 Encontrados 3 Things com certificados:
   1. Vehicle-VIN-001 → Certificado: abc123def456...
   2. Vehicle-VIN-002 → Certificado: def456ghi789...
   3. Vehicle-VIN-003 → Certificado: ghi789jkl012...

Selecionar Thing (1-3): 1
✅ Selecionado: Vehicle-VIN-001

🔍 Validação de certificado:
   📄 Arquivo de certificado: ✅ Encontrado
   🔐 Arquivo de chave privada: ✅ Encontrado
   📱 Anexação ao Thing: ✅ Verificada
```

**Estabelecimento de Conexão:**
```
🔐 Passo 1: Estabelecendo Conexão MQTT para Operações Shadow
--------------------------------------------------
🔗 Parâmetros de Conexão Shadow:
   ID do Cliente: Vehicle-VIN-001-mqtt-a1b2c3d4
   Nome do Thing: Vehicle-VIN-001
   Endpoint: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com
   Porta: 8883
   Protocolo: MQTT 3.1.1 sobre TLS
   Autenticação: Certificado X.509
   Tipo de Shadow: Classic Shadow

🔄 Conectando ao AWS IoT Core...
✅ Conectado com sucesso ao AWS IoT Core

======================================================================
🔔 CONEXÃO SHADOW ESTABELECIDA [14:30:10.123]
======================================================================
Status: Conectado com sucesso ao AWS IoT Core
ID do Cliente: Vehicle-VIN-001-mqtt-a1b2c3d4
Nome do Thing: Vehicle-VIN-001
Endpoint: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com
Tipo de Shadow: Classic Shadow
Sessão Limpa: True
Keep Alive: 30 segundos
Versão TLS: 1.2
Autenticação de Certificado: TLS mútuo X.509
======================================================================
```

**Comandos MQTT Interativos:**
```
📡 Cliente MQTT Conectado - Digite 'help' para comandos

📡 MQTT> help
Comandos disponíveis:
  sub <tópico>              - Assinar tópico (QoS 0)
  sub1 <tópico>             - Assinar tópico (QoS 1)
  unsub <tópico>            - Cancelar assinatura do tópico
  pub <tópico> <mensagem>   - Publicar mensagem (QoS 0)
  pub1 <tópico> <mensagem>  - Publicar mensagem (QoS 1)
  json <tópico> chave=val... - Publicar mensagem JSON
  test                      - Enviar mensagem de teste
  status                    - Mostrar status da conexão
  messages                  - Mostrar histórico de mensagens
  debug                     - Diagnósticos de conexão
  quit                      - Sair do cliente

📡 MQTT> sub device/+/temperature
✅ [14:30:15.456] ASSINADO em device/+/temperature (QoS: 0)

📡 MQTT> pub device/sensor/temperature 23.5
✅ [14:30:20.789] PUBLICADO
   📤 Tópico: device/sensor/temperature
   🏷️  QoS: 0 | ID do Pacote: 1
   📊 Tamanho: 4 bytes

======================================================================
🔔 MENSAGEM RECEBIDA #1 [14:30:20.890]
======================================================================
📥 Tópico: device/sensor/temperature
🏷️  QoS: 0 (No máximo uma vez)
📊 Tamanho do Payload: 4 bytes
💬 Mensagem: 23.5
======================================================================
```

## Exemplos de Device Shadow

### Sincronização de Estado Shadow

**Configuração Inicial do Shadow:**
```
🌟 Explorador de Device Shadow
=============================
🔍 Descobrindo Things com certificados...
✅ Thing selecionado: Vehicle-VIN-001

📱 Configuração de Estado Local do Dispositivo:
   📄 Arquivo de estado: certificates/Vehicle-VIN-001/device_state.json
   📊 Estado inicial: {
     "temperature": 22.5,
     "humidity": 45.0,
     "status": "online",
     "firmware_version": "1.0.0"
   }

🔄 Conectando ao AWS IoT para operações shadow...
✅ Conexão shadow estabelecida

🌟 Passo 2: Assinando Tópicos Shadow
--------------------------------------------------
📋 Tópicos Classic Shadow:
   ✅ $aws/things/Vehicle-VIN-001/shadow/get/accepted
   ✅ $aws/things/Vehicle-VIN-001/shadow/get/rejected
   ✅ $aws/things/Vehicle-VIN-001/shadow/update/accepted
   ✅ $aws/things/Vehicle-VIN-001/shadow/update/rejected
   ✅ $aws/things/Vehicle-VIN-001/shadow/update/delta

✅ Assinado com sucesso em todos os 5 tópicos shadow
```

**Operações Shadow:**
```
🌟 Shadow> get
🔄 Solicitando documento shadow atual...

======================================================================
🌟 MENSAGEM SHADOW RECEBIDA [14:40:10.123]
======================================================================
✅ SHADOW GET ACEITO
   📊 Versão: 1
   ⏰ Timestamp: 1642248610
   📡 Shadow Atual: {
     "state": {
       "reported": {
         "temperature": 22.5,
         "humidity": 45.0,
         "status": "online"
       }
     },
     "metadata": {
       "reported": {
         "temperature": {"timestamp": 1642248500},
         "humidity": {"timestamp": 1642248500},
         "status": {"timestamp": 1642248500}
       }
     },
     "version": 1,
     "timestamp": 1642248610
   }
======================================================================

🌟 Shadow> desire temperature=25.0 status=active
🔄 Definindo estado desejado (simulando solicitação da nuvem/app)...

======================================================================
🌟 MENSAGEM SHADOW RECEBIDA [14:40:15.456]
======================================================================
🔄 DELTA SHADOW RECEBIDO
   📝 Descrição: Estado desejado difere do estado relatado
   📊 Versão: 2
   🔄 Mudanças Necessárias: {
     "temperature": 25.0,
     "status": "active"
   }

🔍 Comparação de Estado:
   📱 Estado Local: {
     "temperature": 22.5,
     "status": "online"
   }
   🔄 Delta: {
     "temperature": 25.0,
     "status": "active"
   }

⚠️  Diferenças Encontradas:
   • temperature: 22.5 → 25.0
   • status: online → active

Aplicar essas mudanças ao dispositivo local? (y/N): y
✅ Estado local atualizado com sucesso
📡 Relatando automaticamente estado atualizado ao shadow...
======================================================================
```

## Exemplos do Rules Engine

### Fluxo de Criação de Regra

**Menu de Criação de Regra:**
```
⚙️ Explorador do IoT Rules Engine
================================
📋 Menu Principal:
1. Listar todas as Regras IoT
2. Descrever Regra IoT específica
3. Criar nova Regra IoT
4. Gerenciar Regra IoT (habilitar/desabilitar/excluir)
5. Testar Regra IoT com MQTT
6. Sair

Selecionar opção (1-6): 3

🔧 Assistente de Criação de Regra
================================
Digite o nome da regra: TemperatureAlert
✅ Nome da regra 'TemperatureAlert' está disponível

📊 Seleção de Tipo de Evento:
1. temperature - Leituras de sensor de temperatura
2. humidity - Medições de umidade
3. pressure - Dados de sensor de pressão
4. motion - Eventos de detecção de movimento
5. door - Status de sensor de porta
6. alarm - Eventos do sistema de alarme
7. status - Status geral do dispositivo
8. battery - Relatórios de nível de bateria
9. Custom - Tipo de evento definido pelo usuário

Selecionar tipo de evento (1-9): 1
✅ Tipo de evento selecionado: temperature
```

**Construção de Declaração SQL:**
```
🔧 Construtor de Declaração SQL
==============================
📥 Padrão de Tópico: testRulesEngineTopic/+/temperature

📝 Opções de Cláusula SELECT:
1. SELECT * (todos os atributos)
2. SELECT deviceId, timestamp, value (atributos específicos)
3. SELECT deviceId, timestamp, temperature, humidity (múltiplos sensores)
4. Cláusula SELECT personalizada

Selecionar opção (1-4): 2
✅ Cláusula SELECT: deviceId, timestamp, value

🔍 Cláusula WHERE (opcional):
Digite condição WHERE (ou pressione Enter para nenhum filtro): value > 30
✅ Cláusula WHERE: value > 30

📝 Declaração SQL Completa:
SELECT deviceId, timestamp, value 
FROM 'testRulesEngineTopic/+/temperature' 
WHERE value > 30

🎯 Configuração de Ação:
📤 Tópico de destino de republicação: processed/temperature
🔑 Função IAM: IoTRulesEngineRole (será criada se necessário)

Confirmar criação da regra? (y/N): y
```

### Exemplo de Teste de Regra

**Configuração de Teste:**
```
📋 Menu Principal:
5. Testar Regra IoT com MQTT

Selecionar opção (1-6): 5

🧪 Modo de Teste de Regra
========================
📋 Regras Disponíveis:
1. TemperatureAlert - HABILITADA
2. BatteryMonitor - DESABILITADA

Selecionar regra para testar (1-2): 1
✅ Regra selecionada: TemperatureAlert

📖 Análise da Regra:
   SQL: SELECT deviceId, timestamp, value FROM 'testRulesEngineTopic/+/temperature' WHERE value > 30
   📥 Padrão de Tópico: testRulesEngineTopic/+/temperature
   🔍 Condição WHERE: value > 30
   📤 Tópico de Saída: processed/temperature

🔗 Estabelecendo conexão MQTT para teste...
✅ Conectado ao AWS IoT com autenticação de certificado
✅ Assinado no tópico de saída: processed/temperature
```

**Teste Interativo de Mensagem:**
```
🧪 Gerador de Mensagem de Teste
==============================
🧪 Mensagem de Teste #1

📥 Padrão de Tópico: testRulesEngineTopic/+/temperature
Esta mensagem deve CORRESPONDER ao padrão de tópico? (y/n): y

🔍 Condição WHERE: value > 30
Esta mensagem deve CORRESPONDER à condição WHERE? (y/n): y

📝 Mensagem de Teste Gerada:
📡 Tópico: testRulesEngineTopic/device123/temperature
💬 Payload: {
  "deviceId": "test-device-123",
  "timestamp": 1642248600000,
  "value": 35.0,
  "unit": "celsius"
}

🔮 Previsão: Regra DEVE disparar (tópico corresponde E value > 30)

📤 Publicando mensagem de teste...
⏳ Aguardando 3 segundos para processamento da regra...

======================================================================
🔔 SAÍDA DA REGRA RECEBIDA [14:45:10.123]
======================================================================
📤 Tópico de Saída: processed/temperature
💬 Mensagem Processada: {
  "deviceId": "test-device-123",
  "timestamp": 1642248600000,
  "value": 35.0
}
✅ Regra 'TemperatureAlert' processou e encaminhou a mensagem!
======================================================================
```

## Exemplos de Limpeza

### Limpeza Segura de Recursos

**Confirmação de Limpeza:**
```
🧹 Limpeza de Dados de Exemplo AWS IoT
======================================
Este script removerá com segurança APENAS os recursos de exemplo criados por setup_sample_data.py:

✅ Seguro para Excluir:
   • 20 Things: Vehicle-VIN-001 até Vehicle-VIN-020
   • 3 Thing Types: SedanVehicle, SUVVehicle, TruckVehicle
   • 4 Thing Groups: CustomerFleet, TestFleet, MaintenanceFleet, DealerFleet
   • Certificados associados e arquivos locais

❌ NÃO Excluirá:
   • Seus Things, Thing Types ou Thing Groups existentes
   • Certificados anexados a Things não-exemplo
   • Políticas IoT (requerem revisão manual)

⚠️  Esta ação não pode ser desfeita.
Deseja continuar? (y/N): y
```

**Processo de Limpeza:**
```
🔍 Passo 1: Descobrindo recursos de exemplo...
📋 Recursos Encontrados:
   Things: 20 Things de exemplo encontrados
   Thing Types: 3 Thing Types de exemplo encontrados
   Thing Groups: 4 Thing Groups de exemplo encontrados
   Certificados: 15 certificados anexados a Things de exemplo

🧹 Passo 2: Limpeza de certificados...
🔄 Processando Thing: Vehicle-VIN-001
   🔍 Encontrado 1 certificado anexado
   🔓 Desanexando políticas do certificado abc123def456...
   🔗 Desanexando certificado do Thing...
   🔴 Desativando certificado...
   🗑️  Excluindo certificado...
   📁 Removendo arquivos de certificado locais...
   ✅ Limpeza de certificado concluída

🧹 Passo 3: Limpeza de Things...
🔄 Excluindo Thing: Vehicle-VIN-001...
✅ Thing excluído com sucesso
...
✅ Todos os 20 Things excluídos com sucesso

📊 Resumo da Limpeza:
   ✅ Things excluídos: 20
   ✅ Certificados excluídos: 15
   ✅ Thing Groups excluídos: 4
   ✅ Thing Types excluídos: 3
   ✅ Arquivos locais removidos: 45

🎉 Limpeza concluída! Todos os recursos de exemplo foram removidos.
💡 Sua conta AWS agora está limpa e não está mais incorrendo em custos para esses recursos.
```

## Exemplos de Tratamento de Erros

### Cenários de Erro Comuns

**Erro de Certificado Não Encontrado:**
```
❌ Erro na configuração de conexão MQTT
Arquivos de certificado não encontrados para Thing: Vehicle-VIN-001

💡 Solução:
1. Execute certificate_manager.py primeiro
2. Crie e anexe um certificado a este Thing
3. Certifique-se de que os arquivos de certificado existem em certificates/Vehicle-VIN-001/

🔍 Passos de debug:
   ls -la certificates/Vehicle-VIN-001/
   python certificate_manager.py
```

**Erro de Permissão Negada:**
```
❌ Erro: AccessDeniedException - Usuário não está autorizado a executar: iot:CreateThing

💡 Solução:
Suas credenciais AWS precisam de permissões IoT. Adicione esta política ao seu usuário IAM:
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "iot:*",
    "Resource": "*"
  }]
}

🔍 Verificar permissões atuais:
   aws sts get-caller-identity
   aws iam list-attached-user-policies --user-name <seu-nome-de-usuario>
```

**Timeout de Conexão MQTT:**
```
❌ Falha na Conexão MQTT: Timeout de conexão

💡 Passos de solução de problemas:
1. Verificar conectividade de rede:
   ping a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com

2. Verificar se o certificado está ativo:
   python iot_registry_explorer.py
   # Selecionar opção 2 (Listar Certificados)

3. Verificar firewall (porta 8883 deve estar aberta):
   telnet a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com 8883

4. Verificar anexação certificado-Thing:
   python iot_registry_explorer.py
   # Selecionar opção 5 (Descrever Thing)
```

Esses exemplos demonstram a jornada completa de aprendizagem desde a configuração até a limpeza, mostrando interações reais e saídas que você verá ao usar os scripts.