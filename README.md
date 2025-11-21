# 🏷️ Sistema de Rastreabilidade via Etiquetas

O Sistema de Rastreabilidade via Etiquetas é uma plataforma interna desenvolvida para controlar, monitorar e registrar toda a movimentação de placas/peças dentro do fluxo produtivo.
Ele utiliza QR Codes, etiquetas individuais por lote e pontos de rastreio (terminais) instalados nos setores para garantir que cada item seja rastreado desde a produção até a expedição.
É um sistema totalmente automatizado, em tempo real, que substitui controles manuais (planilhas, papéis, anotações), reduz falhas humanas e aumenta a confiabilidade da informação.

---

## 📁 Estrutura do Projeto
Sistema de Rastreabilidade via Etiquetas/
├─ static/
    └─ logo.png 
    └─ style.css  
  ├─ qrcodes/
       └─ da.png   
├─ templates/
    ├─ base.html
    ├─ dashboard.html    
    ├─ etiqueta_view.html
    ├─ form.html
    └─ history.html
    ├─ index.html
    ├─ label.html
    └─ movimentar.html
├─ app.py
├─ estrutura.txt
├─ models.db  
├─ README.md
├─ requirements.txt

---

## 🚀 Funcionalidades

✅ Cadastro de novos modelos (com lote, PO, linha, cliente etc.)  
✅ Geração automática de **QR Codes**  
✅ Impressão de etiquetas formatadas (modo rótulo)  
✅ Edição e atualização de modelos  
✅ Histórico de alterações por usuário e data  
✅ Interface HTML responsiva com Bootstrap

---

## ⚙️ Tecnologias Utilizadas

- [Python 3](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/) •	Flask (Python) — servidor web principal
- [SQLite](https://www.sqlite.org/) •	SQLite — banco de dados interno
- [qrcode](https://pypi.org/project/qrcode/) •	QRCODE — geração de códigos para movimentação
- [Pillow](https://pypi.org/project/Pillow/)
- HTML / CSS / Bootstrap •	HTML/CSS/Jinja2 — interface

---

## ⚙️ Descrição Fluxo de Dados

- Ponto-01 Objetivo: Ponto do PTH. Marcar ponto de PRODUÇÃO E RECEBIMENTO, para controle de produção. Fica na porta do setor.
- Ponto-02 Objetivo: Ponto do SMT. Marcar ponto de PRODUÇÃO E RECEBIMENTO, para controle de produção. Fica na porta do setor.
- Ponto-03 Objetivo: Ponto do SMT. Marcar ponto de PRODUÇÃO E RECEBIMENTO no posto da qualidade, para saber que o produto está pronto caso outro setor vá produzir. Fica no posto da qualidade.
- Ponto-04 Objetivo: Ponto do IM e ou PA. Marcar ponto de PRODUÇÃO E RECEBIMENTO, para controle de produção. Fica na porta do setor.
- Ponto-05 Objetivo: Ponto do IM e ou PA. Marcar ponto de PRODUÇÃO E RECEBIMENTO no posto da qualidade, para saber que o produto está pronto caso outro setor vá produzir. Fica no posto da qualidade.
- Ponto-06 Objetivo: Ponto do IM e ou PA. Marcar ponto de PRODUÇÃO E RECEBIMENTO no posto da qualidade, para saber que o produto está pronto caso outro setor vá produzir. Fica no posto da qualidade. 
- Ponto-07 Objetivo: Estoque. Marcar ponto de PRODUÇÃO, tem os dois botões, mas eles marcam somente produção, para sabermos que o material acabou de sair da empresa para ser entregue de caminhão até a fábrica do cliente.

- 3. Como o Sistema Funciona
3.1 Cadastro de Modelos
Cada produto/modelo recebe um cadastro contendo:
•	Código
•	Nome
•	Cliente
•	Linha e setor inicial
•	Lote
•	Produção prevista
•	PO/OP
•	Processo e CQ
•	Revisora/Operadora
•	Data e horário
Esse cadastro gera o registro-mestre que será rastreado.
________________________________________
3.2 Geração de Etiquetas e Lotes
Após cadastrar o modelo:
1.	O sistema calcula o número de etiquetas necessárias com base:
o	Produção total
o	Capacidade por magazine/caixa
2.	Para cada etiqueta, é gerado:
o	Lote individual (Ex.: "08 / 504")
o	QR Code próprio
o	Relação com o modelo original
3.	Cada etiqueta passa a ter:
o	Quantidade original
o	Quantidade restante
o	Setor atual
o	Fase (aguardando, disponível, expedido, etc.)
o	Histórico de movimentações
________________________________________
3.3 Rastreabilidade com QR Code
Nos terminais de chão de fábrica, o colaborador escaneia o QR Code.
O sistema identifica automaticamente:
•	O modelo
•	O lote
•	O setor
•	O terminal (Ponto-01, 02, 03...)
•	A ação (produção / recebimento / inspeção / expedição)
Cada bip é registrado com:
•	Data e hora
•	Quantidade
•	Setor de origem
•	Setor de destino
•	Usuário
•	Equipamento
Isso permite uma trilha detalhada de tudo que aconteceu no processo.
________________________________________
3.4 Regras de Produção e Movimentação
O sistema possui lógica inteligente que impede erros como:
✔ Registrar produção repetida
✔ Dar entrada duplicada no setor
✔ Movimentar quantidade superior à disponível
✔ Pular etapas do fluxo
✔ Misturar lotes incorretos
✔ Confundir modelos com fluxos diferentes (inclui casos SMT-FIRST)
Modelos especiais como SMT-FIRST já têm fluxo próprio automatizado.
________________________________________
3.5 Histórico Completo
Para cada modelo é possível visualizar:
•	Etiquetas criadas
•	Movimentações por setor
•	Baixas de produção
•	Saldo atual por fase
•	Histórico de edição do cadastro
•	Registro cronológico completo
Tudo isso com data/hora no padrão brasileiro.
________________________________________
4. Dashboard e Indicadores
O dashboard exibe:
•	Saldo por setor (PTH, SMT, IM, PA, Estoque)
•	Fase (Aguardando, Disponível, Expedido, etc.)
•	Quantidade disponível por lote
•	Identificação rápida de gargalos
•	Situação atualizada em tempo real
Isso permite ao gestor enxergar onde está cada lote, quanto ainda falta e quem movimentou.
________________________________________
5. Benefícios diretos para a empresa
📈 Produtividade
•	Reduz erros manuais
•	Elimina retrabalhos
•	Aumenta a eficiência do chão de fábrica
🛡 Segurança
•	Cada ação fica registrada de forma imutável
•	Histórico completo para auditoria

## 📁 Rode no seu terminal
pip install -r requirements.txt

👨‍💻 Autor
Desenvolvido por Eduardo Libório    
📧 eduardosoleno@protonmail.com

GUARDAR

  {% if request.args.get('auto_print') %}
  <script>
    window.onload = () => window.print();
  </script>
  {% endif %}

  <div class="mb-3">
    <label>Vincular a etiqueta existente (opcional)</label>
    <select name="linked_label_id" class="form-control">
      <option value="">Nenhuma</option>
      {% for l in existing_labels %}
        <option value="{{ l['id'] }}">{{ l['lote'] }} - {{ l['model_name'] }}</option>
      {% endfor %}
    </select>
  </div>

        <div class="cliente">CLIENTE: {{ m['cliente'] or '---' }}</div>

        NO LABEL
