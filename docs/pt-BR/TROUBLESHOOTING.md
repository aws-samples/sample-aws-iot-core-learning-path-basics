# Guia de Solução de Problemas

Este documento fornece orientação abrangente de solução de problemas para o projeto de aprendizagem Amazon Web Services (AWS) AWS IoT Core - Básicos.

## Índice

- [Problemas Comuns](#problemas-comuns)
  - [Credenciais AWS](#credenciais-aws)
  - [Problemas de Ambiente Virtual](#problemas-de-ambiente-virtual)
  - [Problemas de Dependências](#problemas-de-dependências)
  - [Problemas de Permissão](#problemas-de-permissão)
  - [Problemas de Certificado](#problemas-de-certificado)
- [Problemas de Conexão MQTT](#problemas-de-conexão-mqtt)
  - [Problemas MQTT Baseado em Certificado](#problemas-mqtt-baseado-em-certificado)
  - [Problemas MQTT WebSocket](#problemas-mqtt-websocket)
- [Problemas de AWS IoT Device Shadow service](#problemas-de-device-shadow)
  - [Problemas de Conexão Shadow](#problemas-de-conexão-shadow)
  - [Problemas de Arquivo de Estado Shadow](#problemas-de-arquivo-de-estado-shadow)
- [Problemas do Rules Engine](#problemas-do-rules-engine)
  - [Problemas de Criação de Regra](#problemas-de-criação-de-regra)
  - [Problemas de Teste de Regra](#problemas-de-teste-de-regra)
- [Problemas do OpenSSL](#problemas-do-openssl)
  - [Problemas de Instalação](#problemas-de-instalação)
  - [Problemas de Geração de Certificado](#problemas-de-geração-de-certificado)
- [Problemas de Rede e Conectividade](#problemas-de-rede-e-conectividade)
  - [Problemas de Firewall e Proxy](#problemas-de-firewall-e-proxy)
  - [Problemas de Resolução DNS](#problemas-de-resolução-dns)
- [Problemas de Performance e Timing](#problemas-de-performance-e-timing)
  - [Limitação de Taxa de API](#limitação-de-taxa-de-api)
  - [Timeouts de Conexão](#timeouts-de-conexão)
- [Obtendo Ajuda Adicional](#obtendo-ajuda-adicional)
  - [Uso do Modo Debug](#uso-do-modo-debug)
  - [Verificação do Console AWS IoT](#verificação-do-console-aws-iot)
  - [Amazon CloudWatch Logs](#cloudwatch-logs)
  - [Passos Comuns de Resolução](#passos-comuns-de-resolução)
  - [Recursos de Suporte](#recursos-de-suporte)

## Problemas Comuns

### Credenciais AWS

#### Verificar se as Credenciais Estão Definidas
```bash
# Verificar se as credenciais estão configuradas
aws sts get-caller-identity

# Verificar região atual
echo $AWS_DEFAULT_REGION

# Listar variáveis de ambiente
env | grep AWS
```

#### Problemas Comuns de Credenciais

**Problema: "Unable to locate credentials"**
```bash
# Solução 1: Definir variáveis de ambiente
export AWS_ACCESS_KEY_ID=<sua-chave-de-acesso>
export AWS_SECRET_ACCESS_KEY=<sua-chave-secreta>
export AWS_DEFAULT_REGION=us-east-1

# Solução 2: Usar configuração AWS CLI
aws configure

# Solução 3: Verificar configuração existente
aws configure list
```

**Problema: "You must specify a region"**
```bash
# Definir região padrão
export AWS_DEFAULT_REGION=us-east-1

# Ou especificar na configuração AWS CLI
aws configure set region us-east-1
```

**Problema: "The security token included in the request is invalid"**
- **Causa**: Credenciais temporárias expiradas ou token de sessão incorreto
- **Solução**: Atualize suas credenciais ou remova token de sessão expirado
```bash
unset AWS_SESSION_TOKEN
# Então defina novas credenciais
```

### Problemas de Ambiente Virtual

#### Verificar Ambiente Virtual
```bash
# Verificar se venv está ativo
which python
# Deve mostrar: /caminho/para/seu/projeto/venv/bin/python

# Verificar versão do Python
python --version
# Deve ser 3.7 ou superior

# Listar pacotes instalados
pip list
```

#### Problemas de Ambiente Virtual

**Problema: Ambiente virtual não ativado**
```bash
# Ativar ambiente virtual
# No macOS/Linux:
source venv/bin/activate

# No Windows:
venv\Scripts\activate

# Verificar ativação
which python
```

**Problema: Versão errada do Python**
```bash
# Criar novo venv com versão específica do Python
python3.9 -m venv venv
# ou
python3 -m venv venv

# Ativar e verificar
source venv/bin/activate
python --version
```

**Problema: Falha na instalação de pacotes**
```bash
# Atualizar pip primeiro
python -m pip install --upgrade pip

# Instalar requirements
pip install -r requirements.txt

# Se ainda falhar, tentar pacotes individuais
pip install boto3
pip install awsiotsdk
```

### Problemas de Dependências

#### Reinstalar Dependências
```bash
# Atualizar todos os pacotes
pip install --upgrade -r requirements.txt

# Forçar reinstalação
pip install --force-reinstall -r requirements.txt

# Limpar cache do pip e reinstalar
pip cache purge
pip install -r requirements.txt
```

#### Erros Comuns de Dependências

**Problema: "No module named 'boto3'"**
```bash
# Garantir que venv está ativado e instalar
pip install boto3

# Verificar instalação
python -c "import boto3; print(boto3.__version__)"
```

**Problema: "No module named 'awsiot'"**
```bash
# Instalar AWS IoT SDK
pip install awsiotsdk

# Verificar instalação
python -c "import awsiot; print('AWS IoT SDK instalado')"
```

**Problema: Erros de certificado SSL/TLS**
```bash
# No macOS, atualizar certificados
/Applications/Python\ 3.x/Install\ Certificates.command

# Ou instalar pacote de certificados
pip install --upgrade certifi
```

### Problemas de Permissão

#### Permissões AWS Identity and Access Management (AWS IAM)

**Permissões Necessárias para Scripts de Aprendizagem:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:*",
        "iam:CreateRole",
        "iam:CreatePolicy",
        "iam:AttachRolePolicy",
        "iam:GetRole",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

**Permissões Mínimas (se iot:* for muito amplo):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:CreateThing",
        "iot:ListThings",
        "iot:DescribeThing",
        "iot:DeleteThing",
        "iot:CreateThingType",
        "iot:ListThingTypes",
        "iot:DescribeThingType",
        "iot:DeleteThingType",
        "iot:CreateThingGroup",
        "iot:ListThingGroups",
        "iot:DescribeThingGroup",
        "iot:DeleteThingGroup",
        "iot:CreateKeysAndCertificate",
        "iot:ListCertificates",
        "iot:DescribeCertificate",
        "iot:UpdateCertificate",
        "iot:DeleteCertificate",
        "iot:CreatePolicy",
        "iot:ListPolicies",
        "iot:GetPolicy",
        "iot:AttachPolicy",
        "iot:DetachPolicy",
        "iot:AttachThingPrincipal",
        "iot:DetachThingPrincipal",
        "iot:ListThingPrincipals",
        "iot:ListPrincipalThings",
        "iot:Connect",
        "iot:Publish",
        "iot:Subscribe",
        "iot:Receive",
        "iot:GetThingShadow",
        "iot:UpdateThingShadow",
        "iot:CreateTopicRule",
        "iot:ListTopicRules",
        "iot:GetTopicRule",
        "iot:DeleteTopicRule"
      ],
      "Resource": "*"
    }
  ]
}
```

**Erros Comuns de Permissão:**

**Problema: "User is not authorized to perform: iot:CreateThing"**
- **Causa**: Permissões AWS IAM insuficientes
- **Solução**: Adicionar permissões IoT ao seu usuário/função AWS IAM

**Problema: "Access Denied" ao criar funções AWS IAM**
- **Causa**: Permissões AWS IAM ausentes para Rules Engine
- **Solução**: Adicionar permissões AWS IAM ou usar função existente

### Problemas de Certificado

#### Problemas de Arquivo de Certificado

**Problema: Arquivos de certificado não encontrados**
```bash
# Verificar se o diretório certificates existe
ls -la certificates/

# Verificar certificados de Thing específico
ls -la certificates/Vehicle-VIN-001/

# Verificar arquivos de certificado
openssl x509 -in certificates/Vehicle-VIN-001/cert-id.crt -text -noout
```

**Problema: Certificado não anexado ao Thing**
```bash
# Executar explorador de registro para verificar
python iot_registry_explorer.py
# Selecionar opção 5 (Descrever Thing) e verificar se certificados estão listados
```

**Problema: Política não anexada ao certificado**
```bash
# Usar gerenciador de certificados para anexar política
python certificate_manager.py
# Selecionar opção 3 (Anexar Política ao Certificado Existente)
```

#### Problemas de Status de Certificado

**Problema: Certificado está INATIVO**
```bash
# Usar gerenciador de certificados para ativar
python certificate_manager.py
# Selecionar opção 5 (Habilitar/Desabilitar Certificado)
```

**Problema: Validação de certificado falha**
```bash
# Verificar formato do certificado
head -5 certificates/Vehicle-VIN-001/cert-id.crt
# Deve começar com: -----BEGIN CERTIFICATE-----

# Validar certificado
openssl x509 -in certificates/Vehicle-VIN-001/cert-id.crt -noout
# Nenhuma saída significa válido, erro significa inválido
```

## Problemas de Conexão MQTT

### Problemas MQTT Baseado em Certificado

#### Diagnósticos de Conexão
```bash
# Usar modo debug para informações detalhadas de erro
python mqtt_client_explorer.py --debug

# Testar conectividade básica com OpenSSL
openssl s_client -connect <seu-endpoint>:8883 \
  -cert certificates/Vehicle-VIN-001/<cert-id>.crt \
  -key certificates/Vehicle-VIN-001/<cert-id>.key
```

#### Erros Comuns de MQTT

**Problema: "Connection timeout"**
- **Causas**: Conectividade de rede, endpoint incorreto, firewall
- **Soluções**:
  ```bash
  # Verificar endpoint
  python iot_registry_explorer.py
  # Selecionar opção 8 (Descrever Endpoint)
  
  # Testar conectividade de rede
  ping seu-iot-endpoint.amazonaws.com
  
  # Verificar firewall (porta 8883 deve estar aberta)
  telnet seu-iot-endpoint.amazonaws.com 8883
  ```

**Problema: "Authentication failed"**
- **Causas**: Problemas de certificado, problemas de política, Thing não anexado
- **Soluções**:
  1. Verificar se certificado está ATIVO
  2. Verificar se certificado está anexado ao Thing
  3. Verificar se política está anexada ao certificado
  4. Verificar se permissões de política incluem iot:Connect

**Problema: "Subscription/Publish failed"**
- **Causas**: Restrições de política, formato de tópico inválido
- **Soluções**:
  ```bash
  # Verificar permissões de política
  # Política deve incluir: iot:Subscribe, iot:Publish, iot:Receive
  
  # Verificar formato de tópico (sem espaços, caracteres válidos)
  # Válido: device/sensor/temperature
  # Inválido: device sensor temperature
  ```

#### Comandos de Solução de Problemas MQTT

**Dentro do Cliente MQTT:**
```bash
📡 MQTT> debug                    # Mostrar diagnósticos de conexão
📡 MQTT> status                   # Exibir informações de conexão
📡 MQTT> messages                 # Mostrar histórico de mensagens
```

**Exemplo de Saída de Debug:**
```
🔍 Diagnósticos de Conexão:
   Endpoint: a1b2c3d4e5f6g7-ats.iot.us-east-1.amazonaws.com
   Porta: 8883
   ID do Cliente: Vehicle-VIN-001-mqtt-12345678
   Certificado: certificates/Vehicle-VIN-001/abc123.crt
   Chave Privada: certificates/Vehicle-VIN-001/abc123.key
   Status da Conexão: CONECTADO
   Keep Alive: 30 segundos
   Sessão Limpa: True
```

### Problemas MQTT WebSocket

#### Diagnósticos WebSocket
```bash
# Verificar credenciais AWS
aws sts get-caller-identity

# Verificar permissões IAM
aws iam get-user-policy --user-name <seu-nome-de-usuario> --policy-name <nome-da-politica>

# Usar modo debug
python mqtt_websocket_explorer.py --debug
```

#### Erros Comuns de WebSocket

**Problema: "Credential validation failed"**
- **Causa**: Credenciais AWS ausentes ou inválidas
- **Solução**: Definir credenciais AWS adequadas
  ```bash
  export AWS_ACCESS_KEY_ID=<sua-chave>
  export AWS_SECRET_ACCESS_KEY=<sua-chave-secreta>
  export AWS_DEFAULT_REGION=us-east-1
  ```

**Problema: "WebSocket connection failed"**
- **Causas**: Problemas de rede, configurações de proxy, firewall
- **Soluções**:
  ```bash
  # Testar conectividade HTTPS
  curl -I https://seu-endpoint.amazonaws.com
  
  # Verificar configurações de proxy
  echo $HTTP_PROXY
  echo $HTTPS_PROXY
  ```

**Problema: "SigV4 signing error"**
- **Causa**: Desvio de relógio, credenciais inválidas
- **Soluções**:
  ```bash
  # Sincronizar relógio do sistema
  sudo ntpdate -s time.nist.gov  # Linux/macOS
  
  # Verificar se credenciais não expiraram
  aws sts get-caller-identity
  ```

### Problemas de AWS IoT Device Shadow service

#### Problemas de Conexão Shadow

**Problema: Operações shadow falham**
- **Causas**: Permissões shadow ausentes, problemas de certificado
- **Soluções**:
  1. Verificar se política inclui permissões shadow:
     ```json
     {
       "Action": [
         "iot:GetThingShadow",
         "iot:UpdateThingShadow"
       ]
     }
     ```
  2. Verificar se certificado está anexado ao Thing correto
  3. Verificar se nome do Thing corresponde às operações shadow

**Problema: Mensagens delta não recebidas**
- **Causas**: Problemas de assinatura, permissões de tópico
- **Soluções**:
  ```bash
  # Verificar assinaturas de tópico shadow
  🌟 Shadow> status
  
  # Verificar se política permite assinaturas de tópico shadow
  # Tópicos: $aws/things/{thingName}/shadow/update/delta
  ```

#### Problemas de Arquivo de Estado Shadow

**Problema: Arquivo de estado local não encontrado**
- **Causa**: Permissões de criação de arquivo, problemas de caminho
- **Solução**:
  ```bash
  # Verificar permissões do diretório certificates
  ls -la certificates/
  
  # Criar arquivo de estado manualmente se necessário
  echo '{"temperature": 20.0, "status": "online"}' > certificates/Vehicle-VIN-001/device_state.json
  ```

**Problema: JSON inválido no arquivo de estado**
- **Causa**: Erros de edição manual
- **Solução**:
  ```bash
  # Validar formato JSON
  python -m json.tool certificates/Vehicle-VIN-001/device_state.json
  
  # Corrigir ou recriar arquivo
  ```

### Problemas do Rules Engine

#### Problemas de Criação de Regra

**Problema: Falha na criação de função AWS IAM**
- **Causas**: Permissões AWS IAM insuficientes, função já existe
- **Soluções**:
  ```bash
  # Verificar se função existe
  aws iam get-role --role-name IoTRulesEngineRole
  
  # Criar função manualmente se necessário
  aws iam create-role --role-name IoTRulesEngineRole --assume-role-policy-document file://trust-policy.json
  ```

**Problema: Erros de sintaxe SQL**
- **Causas**: Formato SQL inválido, funções não suportadas
- **Soluções**:
  - Usar cláusulas SELECT, FROM, WHERE simples
  - Evitar funções SQL complexas
  - Testar com regras básicas primeiro

#### Problemas de Teste de Regra

**Problema: Regra não dispara**
- **Causas**: Incompatibilidade de tópico, problemas de cláusula WHERE, regra desabilitada
- **Soluções**:
  1. Verificar se padrão de tópico corresponde ao tópico publicado
  2. Verificar lógica da cláusula WHERE
  3. Garantir que regra está HABILITADA
  4. Testar com regra simples primeiro

**Problema: Nenhuma saída de regra recebida**
- **Causas**: Problemas de assinatura, configuração de ação
- **Soluções**:
  ```bash
  # Verificar ações da regra
  python iot_rules_explorer.py
  # Selecionar opção 2 (Descrever Regra)
  
  # Verificar assinatura no tópico de saída
  # Assinar em: processed/* ou alerts/*
  ```

## Problemas do OpenSSL

### Problemas de Instalação

**macOS:**
```bash
# Instalar via Homebrew
brew install openssl

# Adicionar ao PATH se necessário
export PATH="/usr/local/opt/openssl/bin:$PATH"
```

**Ubuntu/Debian:**
```bash
# Atualizar lista de pacotes e instalar
sudo apt-get update
sudo apt-get install openssl

# Verificar instalação
openssl version
```

**Windows:**
```bash
# Baixar de: https://slproweb.com/products/Win32OpenSSL.html
# Ou usar Windows Subsystem for Linux (WSL)

# No WSL:
sudo apt-get install openssl
```

### Problemas de Geração de Certificado

**Problema: Comando OpenSSL não encontrado**
- **Solução**: Instalar OpenSSL ou adicionar ao PATH

**Problema: Permissão negada ao criar arquivos de certificado**
- **Solução**: Verificar permissões de diretório ou executar com privilégios apropriados

**Problema: Formato de certificado inválido**
- **Solução**: Verificar sintaxe e parâmetros do comando OpenSSL

## Problemas de Rede e Conectividade

### Problemas de Firewall e Proxy

**Portas Necessárias:**
- **MQTT sobre TLS**: 8883
- **WebSocket MQTT**: 443
- **HTTPS (chamadas de API)**: 443

**Firewall Corporativo:**
```bash
# Testar conectividade de porta
telnet seu-iot-endpoint.amazonaws.com 8883
telnet seu-iot-endpoint.amazonaws.com 443

# Verificar configurações de proxy
echo $HTTP_PROXY
echo $HTTPS_PROXY
echo $NO_PROXY
```

**Configuração de Proxy:**
```bash
# Definir proxy para HTTPS
export HTTPS_PROXY=http://proxy.empresa.com:8080

# Ignorar proxy para endpoints AWS
export NO_PROXY=amazonaws.com,.amazonaws.com
```

### Problemas de Resolução DNS

**Problema: Não é possível resolver endpoint IoT**
```bash
# Testar resolução DNS
nslookup seu-iot-endpoint.amazonaws.com

# Usar DNS alternativo
export AWS_IOT_ENDPOINT=$(dig +short seu-iot-endpoint.amazonaws.com)
```

## Problemas de Performance e Timing

### Limitação de Taxa de API

**Problema: ThrottlingException**
- **Causa**: Muitas chamadas de API muito rapidamente
- **Solução**: Adicionar atrasos entre operações ou reduzir concorrência

**Problema: Atrasos de consistência eventual**
- **Causa**: Serviços AWS precisam de tempo para propagar mudanças
- **Solução**: Adicionar tempos de espera após criação de recursos

### Timeouts de Conexão

**Problema: Timeouts de keep-alive MQTT**
- **Causa**: Instabilidade de rede, períodos longos de inatividade
- **Soluções**:
  - Reduzir intervalo de keep-alive
  - Implementar lógica de retry de conexão
  - Verificar estabilidade da rede

## Obtendo Ajuda Adicional

### Uso do Modo Debug

**Habilitar modo debug para todos os scripts:**
```bash
python nome_do_script.py --debug
```

**Modo debug fornece:**
- Logging detalhado de requisição/resposta de API
- Diagnósticos de conexão
- Stack traces de erro
- Informações de timing

### Verificação do Console AWS IoT

**Verificar recursos no Console AWS:**
1. **Things**: AWS IoT Core → Gerenciar → Things
2. **Certificados**: AWS IoT Core → Proteger → Certificados
3. **Políticas**: AWS IoT Core → Proteger → Políticas
4. **Regras**: AWS IoT Core → Agir → Regras

### Amazon CloudWatch Logs

**Habilitar logging IoT para debug de produção:**
1. Ir para AWS IoT Core → Configurações
2. Habilitar logging com nível de log apropriado
3. Verificar Amazon CloudWatch Logs para informações detalhadas de erro

### Passos Comuns de Resolução

**Quando tudo mais falhar:**
1. **Começar do zero**: Executar script de limpeza e começar novamente
2. **Verificar status da AWS**: Visitar AWS Service Health Dashboard
3. **Verificar limites da conta**: Verificar cotas de serviço AWS
4. **Testar com configuração mínima**: Usar configuração mais simples possível
5. **Comparar com exemplos funcionais**: Usar dados de exemplo fornecidos

### Recursos de Suporte

- **Documentação AWS IoT**: https://docs.aws.amazon.com/iot/
- **Guia do Desenvolvedor AWS IoT**: https://docs.aws.amazon.com/iot/latest/developerguide/
- **Suporte AWS**: https://aws.amazon.com/support/
- **Fóruns AWS**: https://forums.aws.amazon.com/forum.jspa?forumID=210