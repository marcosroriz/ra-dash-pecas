# Painel de Peças

Este repositório contém o **Painel de Combustível**, um dashboard analítico desenvolvido com objetivo de compreender a vida útil das peças, com intuito de auxiliar no planejamento das trocas, bem como auxiliar no diagnóstico mecânico

O dashboard foi desenvolvido utilizando o framework **Dash**, na linguagem de programação **Python**, e consome dados previamente integrados e processados por outros componentes do sistema (telemetria, ordens de serviço, combustível, LLM, entre outros).

---

## Dependências e Integrações

Para seu funcionamento adequado, o painel requer acesso aos seguintes recursos externos:

- **Banco de Dados PostgreSQL**, responsável por armazenar os dados consolidados e as regras de monitoramento.

---

## Estrutura de Arquivos

O projeto está organizado de forma modular e padronizada, conforme descrito a seguir.

### Diretórios e arquivos principais

| Arquivo/Diretório     | Função                                                                  |
| --------------------- | ----------------------------------------------------------------------- |
| `src/assets/`         | Arquivos estáticos (CSS, JavaScript e imagens)                          |
| `src/modules/`        | Módulos e utilitários organizados por funcionalidade                    |
| `src/pages/`          | Definição das páginas do dashboard                                      |
| `src/.env.sample`     | Exemplo das variáveis de ambiente                                       |
| `src/.env`            | Variáveis de ambiente da aplicação                                      |
| `src/app.py`          | Arquivo principal da aplicação, responsável por inicializar o dashboard |
| `src/db.py`           | Configuração e lógica de conexão com o banco de dados                   |
| `src/locale_utils.py` | Funções auxiliares para internacionalização e localização               |
| `src/tema.py`         | Definição do tema visual (cores, fontes e estilos)                      |
| `src/wsgi.sample.py`  | Exemplo de configuração do servidor WSGI                                |

### Arquivos auxiliares

| Arquivo              | Função                                              |
| -------------------- | --------------------------------------------------- |
| `Dockerfile`         | Definição da imagem Docker                          |
| `docker-compose.yml` | Orquestração e execução do contêiner                |
| `dash.wsgi.conf`     | Exemplo de configuração para deploy via Apache/WSGI |
| `Procfile`           | Comandos de inicialização para nuvens privadas      |
| `render.yaml`        | Configuração para deploy na plataforma Render       |
| `requirements.txt`   | Dependências Python do projeto                      |
| `README.md`          | Documentação do painel                              |

---

## Variáveis de Ambiente

O dashboard requer a configuração de variáveis de ambiente por meio de um arquivo `.env`, estruturado conforme o modelo disponibilizado em `.env.sample`.

### Variáveis utilizadas

| Variável                 | Função                                       | Exemplo                        |
| ------------------------ | -------------------------------------------- | ------------------------------ |
| `DEBUG`                  | Ativar mensagens de depuração                | `True` / `False`               |
| `HOST`                   | Endereço IP do dashboard                     | `0.0.0.0`                    |
| `PORT`                   | Porta de execução do dashboard               | `8000`                         |
| `PROFILE`                | Ativar modo de análise de desempenho         | `True` / `False`               |
| `PROFILE_DIR`            | Diretório dos dados de performance           | `profile`                      |
| `SECRET_KEY`             | Chave para criptografia de cookies e sessões | `********`                     |
| `DB_HOST`                | Endereço do banco PostgreSQL                 | `192.168.0.1`                  |
| `DB_PORT`                | Porta do banco PostgreSQL                    | `5432`                         |
| `DB_USER`                | Usuário do banco de dados                    | `admin`                        |
| `DB_PASS`                | Senha do banco de dados                      | `********`                     |
| `DB_NAME`                | Nome do banco de dados                       | `raufg`                        |
| `SMTP`                   | Credencial SMTP para envio de e-mails        | `**** **** **** ****`          |
| `WP_ZAPI_URL`            | URL da API WhatsApp (Z-API)                  | `********`                     |
| `WP_ZAPI_TOKEN`          | Token da API WhatsApp                        | `********`                     |
| `WP_ZAPI_LINK_IMAGE_URL` | Imagem usada nos alertas WhatsApp            | `https://ceia.ufg.br/logo.png` |

A variável `SECRET_KEY` deve ser mantida em sigilo, pois é utilizada para garantir a segurança das sessões e dos cookies da aplicação.

---

## Execução

O painel pode ser executado localmente ou por meio de contêineres e servidores de produção.

### Execução Local

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Acesse o diretório src
```bash
cd src
```

3. Configure as variáveis de ambiente:
```bash
cp .env.sample .env
```

4. Execute o dashboard:
```bash
python app.py
```

Após a execução, o dashboard estará disponível em:
http://HOST:PORT

### Execução via Docker

1. Configure as variáveis de ambiente:
```bash
cp .env.sample .env
```

2. Execute o contêiner::
```bash
docker compose --env-file src/.env up
```

Após a execução, o dashboard estará disponível em:
http://localhost:PORT
