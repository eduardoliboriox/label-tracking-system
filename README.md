
# 🏷️ Sistema de Rastreabilidade via Etiquetas

O **Sistema de Rastreabilidade via Etiquetas** é uma plataforma interna desenvolvida para controlar, monitorar e registrar toda a movimentação de placas/peças dentro do fluxo produtivo. Ele utiliza **QR Codes**, etiquetas individuais por lote e pontos de rastreio (terminais) instalados nos setores para garantir que cada item seja rastreado desde a produção até a expedição.

É um sistema **automatizado em tempo real**, que substitui controles manuais (planilhas, papéis, anotações), reduz falhas humanas e aumenta a confiabilidade da informação.

---

## 📁 Estrutura do Projeto

```
Sistema de Rastreabilidade via Etiquetas/
├─ static/
│   ├─ logo.png 
│   └─ style.css  
├─ qrcodes/
│   └─ da.png   
├─ templates/
│   ├─ base.html
│   ├─ dashboard.html    
│   ├─ etiqueta_view.html
│   ├─ form.html
│   ├─ history.html
│   ├─ index.html
│   ├─ label.html
│   └─ movimentar.html
├─ app.py
├─ models.db
├─ ping.py
├─ Profile  
├─ README.md
├─ requirements.txt
```

---

## 🚀 Funcionalidades

* Cadastro de novos modelos (com lote, PO, linha, cliente etc.)
* Geração automática de **QR Codes**
* Impressão de etiquetas formatadas (modo rótulo)
* Edição e atualização de modelos
* Histórico de alterações por usuário e data
* Interface HTML responsiva com **Bootstrap**

---

## ⚙️ Tecnologias Utilizadas

* [Python 3](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/) — servidor web principal
* [SQLite](https://www.sqlite.org/) — banco de dados interno
* [qrcode](https://pypi.org/project/qrcode/) — geração de códigos QR
* [Pillow](https://pypi.org/project/Pillow/) — manipulação de imagens
* HTML / CSS / Bootstrap — interface web e templates Jinja2

---

## 📊 Fluxo de Dados e Pontos de Controle

* **Ponto-01**: PTH — PRODUÇÃO e RECEBIMENTO, controle na porta do setor.
* **Ponto-02**: SMT — PRODUÇÃO e RECEBIMENTO, controle na porta do setor.
* **Ponto-03**: SMT — PRODUÇÃO e RECEBIMENTO, posto de qualidade.
* **Ponto-04**: IM/PA — PRODUÇÃO e RECEBIMENTO, porta do setor.
* **Ponto-05**: IM/PA — PRODUÇÃO e RECEBIMENTO, posto de qualidade.
* **Ponto-06**: IM/PA — PRODUÇÃO e RECEBIMENTO, posto de qualidade.
* **Ponto-07**: Estoque — marca apenas PRODUÇÃO, registra saída para cliente.

---

## ⚙️ Como o Sistema Funciona

### 1. Cadastro de Modelos

Cada produto/modelo recebe um cadastro contendo:

* Código, Nome, Cliente
* Linha e setor inicial
* Lote e produção prevista
* PO/OP, processo e CQ
* Revisora/Operadora
* Data e horário

Este cadastro gera o registro-mestre que será rastreado.

---

### 2. Geração de Etiquetas e Lotes

Após cadastrar o modelo:

1. O sistema calcula o número de etiquetas necessárias com base em **produção total** e **capacidade por magazine/caixa**.
2. Cada etiqueta recebe:

   * Lote individual (Ex.: "08 / 504")
   * QR Code próprio
   * Relação com o modelo original
3. Cada etiqueta possui:

   * Quantidade original e restante
   * Setor atual
   * Fase (aguardando, disponível, expedido, etc.)
   * Histórico de movimentações

---

### 3. Rastreabilidade com QR Code

Nos terminais, o colaborador escaneia o QR Code. O sistema identifica:

* Modelo, lote, setor, terminal (Ponto-01, 02, …)
* Ação (produção, recebimento, inspeção, expedição)

Cada registro contém:

* Data e hora
* Quantidade
* Setor de origem e destino
* Usuário e equipamento

Isso garante **trilha completa e detalhada** do processo.

---

### 4. Regras de Produção e Movimentação

O sistema impede erros como:

* Registro duplicado de produção
* Entrada repetida em um setor
* Movimentação acima do disponível
* Pular etapas do fluxo
* Mistura de lotes incorretos
* Confusão de modelos com fluxos diferentes (SMT-FIRST)

---

### 5. Histórico Completo

Para cada modelo, é possível visualizar:

* Etiquetas criadas
* Movimentações por setor
* Baixas de produção
* Saldo atual por fase
* Histórico de edição
* Registro cronológico completo com data/hora

---

### 6. Dashboard e Indicadores

O dashboard mostra:

* Saldo por setor (PTH, SMT, IM, PA, Estoque)
* Fase (Aguardando, Disponível, Expedido, etc.)
* Quantidade disponível por lote
* Identificação de gargalos
* Situação atualizada em tempo real

---

## ✅ Benefícios para a Empresa

**Produtividade:**

* Reduz erros manuais
* Elimina retrabalhos
* Aumenta eficiência no chão de fábrica

**Segurança:**

* Registro imutável de cada ação
* Histórico completo para auditoria

---

## 📁 Como Rodar

```bash
pip install -r requirements.txt
python app.py
```

---

## 👨‍💻 Autor

* Desenvolvido por **Eduardo Libório**
* 📧 [eduardosoleno@protonmail.com](mailto:eduardosoleno@protonmail.com)

---


