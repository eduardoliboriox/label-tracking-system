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

- 1. Etiqueta gerada no PTH [Abre Contagem de Placas Disponiveis] > 

## 📁 Rode no seu terminal
pip install -r requirements.txt

👨‍💻 Autor

Desenvolvido por Eduardo Libório    
📧 eduardosoleno@protonmail.com




Na empresa existem 5 setores: IM, PA, PTH, SMT, Estoque (logistica). Um computador com a interface de marcação de PRODUÇÃO ou RECEBIMENTO está espalhado em pontos estratégicos da fábrica e alguns deles são pontos interligados da qualidade. Por organização, temos que nomeá-los:
- Ponto-01 Objetivo: Ponto do PTH. Marcar ponto de PRODUÇÃO E RECEBIMENTO, para controle de produção. Fica na porta do setor.
- Ponto-02 Objetivo: Ponto do SMT. Marcar ponto de PRODUÇÃO E RECEBIMENTO, para controle de produção. Fica na porta do setor.
- Ponto-03 Objetivo: Ponto do SMT. Marcar ponto de PRODUÇÃO E RECEBIMENTO no posto da qualidade, para saber que o produto está pronto caso outro setor vá produzir. Fica no posto da qualidade.
- Ponto-04 Objetivo: Ponto do IM e ou PA. Marcar ponto de PRODUÇÃO E RECEBIMENTO, para controle de produção. Fica na porta do setor.
- Ponto-05 Objetivo: Ponto do IM e ou PA. Marcar ponto de PRODUÇÃO E RECEBIMENTO no posto da qualidade, para saber que o produto está pronto caso outro setor vá produzir. Fica no posto da qualidade.
- Ponto-06 Objetivo: Ponto do IM e ou PA. Marcar ponto de PRODUÇÃO E RECEBIMENTO no posto da qualidade, para saber que o produto está pronto caso outro setor vá produzir. Fica no posto da qualidade. 
- Ponto-07 Objetivo: Estoque. Marcar ponto de PRODUÇÃO, tem os dois botões, mas eles marcam somente produção, para sabermos que o material acabou de sair da empresa para ser entregue de caminhão até a fábrica do cliente.

Eu preciso conseguir identificar as passagens de material por esses pontos expalhados pelo empresa. Vamos a um cenário e explicações: O PTH normalmente começa a produção, fez um etiqueta de capacidade de 50 placas, e levou o magazine com e etiqueta pra perto da porta para bipar o qr code, e marcar PRODUÇÃO, nesse momento temos 50 placas no PTH, vão levar esse magazine pro SMT, ao chegar vão bipar RECEBIMENTOS, agora o saldo do PTH perde a mesma qdt e ela vem pro setor que recebeu. SMT com 50 placas esperando ir pra produção em alguma linha. quando produzir, vai pro Ponto-03 da qualidade, quando bipar lá sei que as 50 placas não estão aguardando produção, elas estão prontas.

o próximo é IM, vão pegar o magazine no SMT E levar pra IM ou PA, por ultimo, Vai ser o ponto do estoque quando vou saber que vai sair pra entregue. Eu explicar e ajustar que existe ROTEIRO.




