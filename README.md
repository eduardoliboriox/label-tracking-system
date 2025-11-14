# 🏷️ Sistema de Etiquetas com QR Code

Um sistema web simples desenvolvido em **Python (Flask)** para **geração, visualização e histórico de etiquetas com QR Codes**.  
Ideal para ambientes industriais, controle de produção ou rastreabilidade de produtos.

---

## 📁 Estrutura do Projeto
Sistema-Etiquetas-QrCode/
├─ app.py
├─ models.db
├─ requirements.txt
├─ static/
│ ├─ logo.png
│ ├─ style.css
│ └─ qrcodes/
│ └─ da.png
├─ templates/
│ ├─ base.html
│ ├─ index.html
│ ├─ form.html
│ ├─ etiqueta_view.html
│ ├─ label.html
│ ├─ history.html
│ └─ logo.png

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
- [Flask](https://flask.palletsprojects.com/)
- [SQLite](https://www.sqlite.org/)
- [qrcode](https://pypi.org/project/qrcode/)
- [Pillow](https://pypi.org/project/Pillow/)
- HTML / CSS / Bootstrap

---

## ⚙️ Descrição Fluxo de Dados

- Ponto-01 Objetivo: Ponto do PTH. Marcar ponto de PRODUÇÃO E RECEBIMENTO, para controle de produção. Fica na porta do setor.
- Ponto-02 Objetivo: Ponto do SMT. Marcar ponto de PRODUÇÃO E RECEBIMENTO, para controle de produção. Fica na porta do setor.
- Ponto-03 Objetivo: Ponto do SMT. Marcar ponto de PRODUÇÃO E RECEBIMENTO no posto da qualidade, para saber que o produto está pronto caso outro setor vá produzir. Fica no posto da qualidade.
- Ponto-04 Objetivo: Ponto do IM e ou PA. Marcar ponto de PRODUÇÃO E RECEBIMENTO, para controle de produção. Fica na porta do setor.
- Ponto-05 Objetivo: Ponto do IM e ou PA. Marcar ponto de PRODUÇÃO E RECEBIMENTO no posto da qualidade, para saber que o produto está pronto caso outro setor vá produzir. Fica no posto da qualidade.
- Ponto-06 Objetivo: Ponto do IM e ou PA. Marcar ponto de PRODUÇÃO E RECEBIMENTO no posto da qualidade, para saber que o produto está pronto caso outro setor vá produzir. Fica no posto da qualidade. 
- Ponto-07 Objetivo: Estoque. Marcar ponto de PRODUÇÃO, tem os dois botões, mas eles marcam somente produção, para sabermos que o material acabou de sair da empresa para ser entregue de caminhão até a fábrica do cliente.

## 📁 Rode no seu terminal
pip install -r requirements.txt

👨‍💻 Autor

Desenvolvido por Eduardo Libório    
📧 eduardosoleno@protonmail.com



AGUARDAR

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