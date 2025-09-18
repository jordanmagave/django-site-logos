# Site Institucional - Centro Educacional Logos

Este é o repositório do site institucional do Centro Educacional Logos, uma aplicação web construída com Django e hospedada na nuvem do Google Cloud.

## Descrição do Projeto

O objetivo principal do site é servir como um portal informativo para pais e alunos, apresentando a instituição, seus serviços e valores. A principal funcionalidade de conversão é um formulário de contato para agendamento de visitas, cujos dados são armazenados de forma segura e integrados com ferramentas de análise.

## Principais Funcionalidades

* **Páginas Institucionais:** Home, Sobre, Serviços (Educação Infantil, Fundamental, etc.).
* **Formulário de Contato:** Captura de leads com validação e armazenamento em banco de dados.
* **Rastreamento de Marketing (Client-Side):** Captura automática de parâmetros de URL (`utm_*`, `gclid`, `fbclid`) para análise de campanhas.
* **Gestão de Consentimento (LGPD):** Integração com a plataforma Ketch para gerenciar o consentimento de cookies e rastreamento.
* **Painel de Administração:** Interface do Django Admin para visualização dos contatos recebidos.
* **Testes Automatizados:** Suíte de testes para garantir a qualidade e estabilidade do código.

## Tecnologias Utilizadas

* **Backend:** Django
* **Frontend:** HTML, CSS, JavaScript
* **Banco de Dados:** PostgreSQL (gerenciado pelo Google Cloud SQL)
* **Infraestrutura:**
    * **Hospedagem:** Google Cloud Run
    * **CI/CD:** Google Cloud Build com gatilhos do GitHub
    * **Armazenamento de Imagens Docker:** Google Artifact Registry
    * **Gerenciamento de Segredos:** Google Secret Manager
* **Serviços Adicionais:**
    * **Servidor de Arquivos Estáticos:** Whitenoise
    * **Análise (Client-Side):** RudderStack
    * **Privacidade (LGPD):** Ketch

## Configuração do Ambiente Local

Siga os passos abaixo para rodar o projeto em um ambiente de desenvolvimento local.

**1. Clone o Repositório:**
```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio
