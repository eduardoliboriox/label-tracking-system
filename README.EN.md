# 🏷️ Label Tracking System — Venttos

The **Label Tracking System** is an internal platform designed to control, monitor, and register the movement of boards/parts throughout the entire production flow.
It uses **QR Codes**, individual labels per lot, and tracking points (terminals) installed in each sector to ensure every item is traceable from production to shipment.

This is a **real-time automated system** that replaces manual processes (spreadsheets, notes, paper forms), reduces human error, and increases information reliability.

You can view the live version through the link at the end of this README.

---

## 📁 Project Structure

```
label-tracking-system-venttos
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
│   └─ ops.html
│   └─ setores.html
├─ app.py
├─ models.db
├─ ping.py
├─ Profile  
├─ README.md
├─ README.EN.md
├─ requirements.txt
```

---

## 🚀 Features

* Model registration (lot, PO, line, client, etc.)
* Automatic **QR Code generation**
* Label printing in formatted layout
* Editing and updating model information
* Complete history tracking (who changed what and when)
* Fully responsive HTML interface using **Bootstrap**
* Real-time label movement tracking across sectors

---

## ⚙️ Technologies Used

* **Python 3**
* **Flask** — main web framework
* **SQLite** — internal embedded database
* **qrcode** — QR Code generation
* **Pillow** — image processing
* **HTML / CSS / Bootstrap** — UI and Jinja2 templates

---

## 📊 Tracking Flow & Control Points

Each terminal (called **Ponto**) registers the production or receipt of labels in each sector:

| Point        | Sector | Function                |
| ------------ | ------ | ----------------------- |
| **Ponto-01** | PTH    | Production & Receiving  |
| **Ponto-02** | SMT    | Production & Receiving  |
| **Ponto-03** | SMT    | Quality Check           |
| **Ponto-04** | IM/PA  | Production & Receiving  |
| **Ponto-05** | IM/PA  | Quality Check           |
| **Ponto-06** | IM/PA  | Quality Check           |
| **Ponto-07** | Stock  | Shipment (final output) |

Every scan creates a validated movement record.

---

## ⚙️ How the System Works

### 1. Model Registration

Each product/model is registered with:

* Code, Name, Customer
* Production line and initial sector
* Lot number and production quantity
* PO/OP, quality process, operator/reviewer
* Date and time

This becomes the master record for traceability.

---

### 2. Label & Lot Generation

After a model is registered:

1. The system calculates how many labels are needed based on **production total** and **magazine/case capacity**.
2. Each label receives:

   * Individual lot (e.g., `"08 / 504"`)
   * Unique QR Code
   * Relation to the model
3. Each label tracks:

   * Original and remaining quantity
   * Current sector
   * Phase status (waiting, available, shipped, etc.)
   * Full movement history

---

### 3. QR-Code Traceability

On terminals, employees scan the label QR Code.
The system identifies:

* Model, lot, sector, and terminal (Ponto-01, Ponto-02, etc.)
* Action type (production, receiving, inspection, shipment)

Every registered movement contains:

* Timestamp
* Quantity
* Origin and destination sector
* User and workstation
* Phase (TOP/BOTTOM) when applicable

This ensures **complete, auditable traceability**.

---

### 4. Production Rules & Movement Validation

The system actively prevents:

* Duplicate production entries
* Re-entering a sector without leaving it
* Moving more units than available
* Skipping mandatory production stages
* Lot mixing or swapping
* Crossing different model flows (e.g., SMT-FIRST logic)

---

### 5. Full History Tracking

For every model, you can view:

* All generated labels
* All movements by sector
* Production counts
* Current available quantities
* Editing history
* A complete timeline of events

---

### 6. Dashboard & KPI Summary

The dashboard provides:

* Stock per sector (PTH, SMT, IM, PA, Stock)
* Production phase (Waiting, In-Process, Completed)
* Lot availability and status
* Bottleneck detection
* Real-time process monitoring

---

## ✅ Benefits for the Company

### **Productivity**

* Eliminates spreadsheet/manual controls
* Reduces human error
* Increases operational efficiency

### **Security & Reliability**

* Immutable logs for each operation
* Full traceability for audits and certifications

---

## 📁 How to Run

```bash
pip install -r requirements.txt
python app.py
```

---

## 🔗 Online Deployment

Hosted on Render.
The free plan may suspend for inactivity — if the page sleeps, wait **~50 seconds** for the server to restart.

➡️ **[https://label-tracking-system-venttos.onrender.com](https://label-tracking-system-venttos.onrender.com)**

---

## 👨‍💻 Author

Developed by **Eduardo Libório**
📧 [eduardosoleno@protonmail.com](mailto:eduardosoleno@protonmail.com)

---
