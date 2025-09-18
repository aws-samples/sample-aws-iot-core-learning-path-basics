# AWS IoT Core - Caminho de Aprendizagem - Conceitos Básicos

> 🌍 **Idiomas Disponíveis** | **Available Languages** | **利用可能な言語** | **可用语言**
> 
> - [English](README.md) | [Español](README.es.md) | [中文](README.zh-CN.md) | [日本語](README.ja.md) | **Português** (Atual)
> - **Documentação**: [English](docs/en/) | [Español](docs/es/) | [中文](docs/zh-CN/) | [日本語](docs/ja/) | [Português](docs/pt-BR/)

Um conjunto abrangente de ferramentas em Python para aprender os conceitos básicos do Amazon Web Services (AWS) IoT Core através de exploração prática. Scripts interativos demonstram gerenciamento de dispositivos, segurança, operações de API e comunicação MQTT com explicações detalhadas.

## 🚀 Início Rápido - Caminho de Aprendizagem Completo

```bash
# 1. Clonar e configurar
git clone https://github.com/aws-samples/sample-aws-iot-core-learning-path-basics.git
cd sample-aws-iot-core-learning-path-basics

# 2. Configurar ambiente
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar credenciais AWS
export AWS_ACCESS_KEY_ID=<sua-chave>
export AWS_SECRET_ACCESS_KEY=<sua-chave-secreta>
export AWS_DEFAULT_REGION=<sua-regiao (ex. us-east-1)>

# 4. Opcional: Definir preferência de idioma
export AWS_IOT_LANG=pt-BR  # 'en' para inglês, 'es' para espanhol, 'ja' para japonês

# 5. Sequência completa de aprendizagem
python scripts/setup_sample_data.py          # Criar recursos IoT de exemplo
python scripts/iot_registry_explorer.py      # Explorar APIs do AWS IoT
python scripts/certificate_manager.py        # Aprender segurança IoT
python scripts/mqtt_client_explorer.py       # Comunicação MQTT em tempo real
python scripts/device_shadow_explorer.py     # Sincronização de estado de dispositivos
python scripts/iot_rules_explorer.py         # Roteamento e processamento de mensagens
python scripts/cleanup_sample_data.py        # Limpar recursos (IMPORTANTE!)
```

**⚠️ Aviso de Custos**: Isso cria recursos reais da AWS (~$0.17 total). Execute a limpeza quando terminar!

## Público-Alvo

**Público Principal:** Desenvolvedores cloud, arquitetos de soluções, engenheiros DevOps novos no AWS IoT Core

**Pré-requisitos:** Conhecimento básico de AWS, fundamentos de Python, uso de linha de comando

**Nível de Aprendizagem:** Nível associado com abordagem prática

## 🔧 Construído com SDKs da AWS

Este projeto aproveita os SDKs oficiais da AWS para fornecer experiências autênticas do AWS IoT Core:

### **Boto3 - SDK da AWS para Python**
- **Propósito**: Alimenta todas as operações do Registro AWS IoT, gerenciamento de certificados e interações do Rules Engine
- **Versão**: `>=1.26.0`
- **Documentação**: [Documentação do Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- **APIs do IoT Core**: [Cliente IoT do Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot.html)

### **SDK de Dispositivos AWS IoT para Python**
- **Propósito**: Permite comunicação MQTT autêntica com AWS IoT Core usando certificados X.509
- **Versão**: `>=1.11.0`
- **Documentação**: [SDK de Dispositivos AWS IoT para Python v2](https://aws.github.io/aws-iot-device-sdk-python-v2/)
- **GitHub**: [aws-iot-device-sdk-python-v2](https://github.com/aws/aws-iot-device-sdk-python-v2)

**Por Que Esses SDKs Importam:**
- **Prontos para Produção**: Os mesmos SDKs usados em aplicações IoT reais
- **Segurança**: Suporte integrado para melhores práticas de segurança do AWS IoT
- **Confiabilidade**: Bibliotecas oficiais mantidas pela AWS com tratamento abrangente de erros
- **Valor de Aprendizagem**: Experimente padrões autênticos de desenvolvimento AWS IoT

## Índice

- 🚀 [Início Rápido](#-início-rápido---caminho-de-aprendizagem-completo)
- ⚙️ [Instalação e Configuração](#️-instalação-e-configuração)
- 📚 [Scripts de Aprendizagem](#-scripts-de-aprendizagem)
- 🧹 [Limpeza de Recursos](#-limpeza-de-recursos)
- 🛠️ [Solução de Problemas](#-solução-de-problemas)
- 📖 [Documentação Avançada](#-documentação-avançada)

## ⚙️ Instalação e Configuração

### Pré-requisitos
- Python 3.10+
- Conta AWS com permissões IoT
- Acesso a terminal/linha de comando
- OpenSSL (para recursos de certificados)

### Informações de Custo

**Este projeto cria recursos reais da AWS que incorrerão em custos (~$0.17 total).**

| Serviço | Uso | Custo Estimado (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~100 mensagens, 20 dispositivos | $0.10 |
| **IoT Device Shadow** | ~30 operações shadow | $0.04 |
| **IoT Rules Engine** | ~50 execuções de regras | $0.01 |
| **Armazenamento de Certificados** | 20 certificados por 1 dia | $0.01 |
| **Amazon CloudWatch Logs** | Logging básico | $0.01 |
| **Total Estimado** | **Sessão completa de aprendizagem** | **~$0.17** |

**⚠️ Importante**: Sempre execute o script de limpeza quando terminar para evitar custos contínuos.

### Instalação Detalhada

**1. Clonar Repositório:**
```bash
git clone https://github.com/aws-samples/sample-aws-iot-core-learning-path-basics.git
cd sample-aws-iot-core-learning-path-basics
```

**2. Instalar OpenSSL:**
- **macOS:** `brew install openssl`
- **Ubuntu/Debian:** `sudo apt-get install openssl`
- **Windows:** Baixar do [site do OpenSSL](https://www.openssl.org/)

**3. Ambiente Virtual (Recomendado):**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

**4. Configuração de Idioma (Opcional):**
```bash
# Definir preferência de idioma para todos os scripts
export AWS_IOT_LANG=pt-BR  # Português (recomendado)
export AWS_IOT_LANG=en     # Inglês
export AWS_IOT_LANG=es     # Espanhol
export AWS_IOT_LANG=ja     # Japonês
export AWS_IOT_LANG=zh-CN  # Chinês

# Alternativa: Scripts perguntarão pelo idioma se não estiver definido
```

**Idiomas Suportados:**
- **Português** (`pt-BR`, `portuguese`, `português`, `pt`) - Tradução completa disponível
- **Inglês** (`en`, `english`) - Padrão
- **Espanhol** (`es`, `spanish`, `español`) - Tradução completa disponível
- **Japonês** (`ja`, `japanese`, `日本語`, `jp`) - Tradução completa disponível
- **Chinês** (`zh-CN`, `chinese`, `中文`, `zh`) - Tradução completa disponível

## 🌍 Suporte Multi-Idioma

Todos os scripts de aprendizagem suportam interfaces em inglês, espanhol, japonês, chinês e português. O idioma afeta:

**✅ O que é Traduzido:**
- Mensagens de boas-vindas e conteúdo educacional
- Opções de menu e prompts do usuário
- Momentos de aprendizagem e explicações
- Mensagens de erro e confirmações
- Indicadores de progresso e mensagens de status

**❌ O que Permanece no Idioma Original:**
- Respostas da API AWS (dados JSON)
- Nomes e valores de parâmetros técnicos
- Métodos HTTP e endpoints
- Informações de debug e logs
- Nomes de recursos AWS e identificadores

**Opções de Uso:**

**Opção 1: Variável de Ambiente (Recomendada)**
```bash
# Definir preferência de idioma para todos os scripts
export AWS_IOT_LANG=pt-BR  # Português
export AWS_IOT_LANG=en     # Inglês
export AWS_IOT_LANG=es     # Espanhol
export AWS_IOT_LANG=ja     # Japonês
export AWS_IOT_LANG=zh-CN  # Chinês

# Executar qualquer script - idioma será aplicado automaticamente
python scripts/iot_registry_explorer.py
```

**Opção 2: Seleção Interativa**
```bash
# Executar sem variável de ambiente - script perguntará pelo idioma
python scripts/setup_sample_data.py

# Exemplo de saída:
# 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma
# 1. English
# 2. Español (Spanish)
# 3. 日本語 (Japanese)
# 4. 中文 (Chinese)
# 5. Português (Portuguese)
# Selecionar idioma (1-5): 5
```

**Scripts Suportados:**
- ✅ `setup_sample_data.py` - Criação de dados de exemplo
- ✅ `iot_registry_explorer.py` - Exploração de API
- ✅ `certificate_manager.py` - Gerenciamento de certificados
- ✅ `mqtt_client_explorer.py` - Comunicação MQTT
- ✅ `mqtt_websocket_explorer.py` - MQTT WebSocket
- ✅ `device_shadow_explorer.py` - Operações Device Shadow
- ✅ `iot_rules_explorer.py` - Exploração Rules Engine
- ✅ `cleanup_sample_data.py` - Limpeza de recursos

**Todos os scripts agora suportam o idioma português (pt-BR)!**

## 📚 Scripts de Aprendizagem

**Caminho de Aprendizagem Recomendado:**

### 1. 📊 Configuração de Dados de Exemplo
**Arquivo**: `scripts/setup_sample_data.py`
**Propósito**: Cria recursos IoT realistas para aprendizagem prática
**Cria**: 20 Things, 3 Thing Types, 4 Thing Groups

### 2. 🔍 Explorador de API do Registro IoT
**Arquivo**: `scripts/iot_registry_explorer.py`
**Propósito**: Ferramenta interativa para aprender APIs do Registro AWS IoT
**Recursos**: 8 APIs principais com explicações detalhadas e chamadas de API reais

### 3. 🔐 Gerenciador de Certificados e Políticas
**Arquivo**: `scripts/certificate_manager.py`
**Propósito**: Aprender segurança AWS IoT através do gerenciamento de certificados e políticas
**Recursos**: Criação de certificados, anexação de políticas, registro de certificados externos

### 4. 📡 Comunicação MQTT
**Arquivos**: 
- `scripts/mqtt_client_explorer.py` (Baseado em certificados, recomendado)
- `scripts/mqtt_websocket_explorer.py` (Alternativa baseada em WebSocket)

**Propósito**: Experimentar comunicação IoT em tempo real usando protocolo MQTT
**Recursos**: Interface de linha de comando interativa, assinatura de tópicos, publicação de mensagens

### 5. 🌟 Explorador de Device Shadow
**Arquivo**: `scripts/device_shadow_explorer.py`
**Propósito**: Aprender sincronização de estado de dispositivos com AWS IoT Device Shadow
**Recursos**: Gerenciamento interativo de shadow, atualizações de estado, processamento de delta

### 6. ⚙️ Explorador do IoT Rules Engine
**Arquivo**: `scripts/iot_rules_explorer.py`
**Propósito**: Aprender roteamento e processamento de mensagens com IoT Rules Engine
**Recursos**: Criação de regras, filtragem SQL, configuração automática de IAM

### 7. 🧹 Limpeza de Dados de Exemplo
**Arquivo**: `scripts/cleanup_sample_data.py`
**Propósito**: Limpar todos os recursos de aprendizagem para evitar custos
**Recursos**: Limpeza segura com tratamento de dependências

## 🧹 Limpeza de Recursos

**⚠️ IMPORTANTE**: Sempre execute a limpeza quando terminar de aprender para evitar custos contínuos da AWS.

```bash
python scripts/cleanup_sample_data.py
```

**O que é limpo:**
- ✅ Things de exemplo (Vehicle-VIN-001, Vehicle-VIN-002, etc.)
- ✅ Certificados e políticas associados
- ✅ Thing Types e Thing Groups
- ✅ Arquivos de certificados locais
- ✅ Regras IoT (se alguma foi criada)

**O que é protegido:**
- ❌ Recursos IoT de produção existentes
- ❌ Certificados e políticas não-exemplo
- ❌ Recursos não criados pelos scripts de aprendizagem

## 🛠️ Solução de Problemas

### Problemas Comuns

**Credenciais AWS:**
```bash
# Definir credenciais
export AWS_ACCESS_KEY_ID=<sua-chave>
export AWS_SECRET_ACCESS_KEY=<sua-chave-secreta>
export AWS_DEFAULT_REGION=us-east-1
```

**Dependências Python:**
```bash
pip install -r requirements.txt
```

**Problemas com OpenSSL:**
- **macOS**: `brew install openssl`
- **Ubuntu**: `sudo apt-get install openssl`

### Modo Debug

Todos os scripts suportam modo debug para logging detalhado da API:
```bash
python scripts/<nome_do_script>.py --debug
```

## 📖 Documentação Avançada

### Documentação Detalhada
- **[Guia Detalhado de Scripts](docs/pt-BR/DETAILED_SCRIPTS.md)** - Documentação aprofundada dos scripts
- **[Exemplos Completos](docs/pt-BR/EXAMPLES.md)** - Fluxos de trabalho completos e saídas de exemplo
- **[Guia de Solução de Problemas](docs/pt-BR/TROUBLESHOOTING.md)** - Problemas comuns e soluções

### Recursos de Aprendizagem

#### Documentação do AWS IoT Core
- **[Guia do Desenvolvedor AWS IoT Core](https://docs.aws.amazon.com/iot/latest/developerguide/)**
- **[Referência da API AWS IoT Core](https://docs.aws.amazon.com/iot/latest/apireference/)**

#### SDKs da AWS Usados Neste Projeto
- **[Documentação do Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)** - Documentação completa do SDK Python
- **[Referência do Cliente IoT do Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot.html)** - Métodos de API específicos do IoT
- **[SDK de Dispositivos AWS IoT para Python v2](https://aws.github.io/aws-iot-device-sdk-python-v2/)** - Documentação do cliente MQTT
- **[GitHub do SDK de Dispositivos AWS IoT](https://github.com/aws/aws-iot-device-sdk-python-v2)** - Código fonte e exemplos

#### Protocolos e Padrões
- **[Especificação do Protocolo MQTT](https://mqtt.org/)** - Documentação oficial do MQTT
- **[Padrão de Certificados X.509](https://tools.ietf.org/html/rfc5280)** - Especificação do formato de certificados

## 🤝 Contribuindo

Este é um projeto educacional. Contribuições que melhorem a experiência de aprendizagem são bem-vindas:

- **Correções de bugs** para problemas de scripts
- **Melhorias de tradução** para melhor localização
- **Aprimoramentos de documentação** para clareza
- **Cenários de aprendizagem adicionais** que se adequem ao nível básico

## 📄 Licença

Este projeto está licenciado sob a Licença MIT-0 - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🏷️ Tags

`aws-iot` `iot-core` `mqtt` `device-shadow` `certificates` `python` `learning` `tutorial` `hands-on` `interactive`