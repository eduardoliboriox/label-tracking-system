# 🏷️ Label Tracking System

The **Label Tracking System** is an internal platform designed to control, monitor, and record the movement of plates/parts within the production workflow. It uses **QR Codes**, batch-specific labels, and tracking points (terminals) installed in departments to ensure every item is traced from production to shipping.

This is a **real-time automated system** that replaces manual controls (spreadsheets, paper, notes), reduces human errors, and increases data reliability.
Check out the live application via the link at the end of this README.md.

---

## 📁 Project Structure

```
label-tracking-system/
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
├─ README.EN.md
├─ requirements.txt
```

---

## 🚀 Features

* Register new models (with batch, PO, line, client, etc.)
* Automatic **QR Code generation**
* Print formatted labels (label mode)
* Edit and update models
* Change history by user and date
* Responsive HTML interface with **Bootstrap**

---

## ⚙️ Technologies

* [Python 3](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/) — main web server
* [SQLite](https://www.sqlite.org/) — internal database
* [qrcode](https://pypi.org/project/qrcode/) — QR code generation
* [Pillow](https://pypi.org/project/Pillow/) — image handling
* HTML / CSS / Bootstrap — web interface and Jinja2 templates

---

## 📊 Data Flow and Control Points

* **Point-01**: PTH — Production & Receiving, department entrance control
* **Point-02**: SMT — Production & Receiving, department entrance control
* **Point-03**: SMT — Production & Receiving, quality checkpoint
* **Point-04**: IM/PA — Production & Receiving, department entrance control
* **Point-05**: IM/PA — Production & Receiving, quality checkpoint
* **Point-06**: IM/PA — Production & Receiving, quality checkpoint
* **Point-07**: Stock — registers only production, records client shipment

---

## ⚙️ How the System Works

### 1. Model Registration

Each product/model is registered with:

* Code, Name, Client
* Line and initial department
* Batch and planned production
* PO/OP, process, and CQ
* Reviewer/Operator
* Date and time

This creates a master record to be tracked.

---

### 2. Label and Batch Generation

After registering a model:

1. The system calculates the number of labels needed based on **total production** and **capacity per magazine/box**.

2. Each label receives:

   * Individual batch number (e.g., "08 / 504")
   * Unique QR Code
   * Link to the original model

3. Each label tracks:

   * Original and remaining quantity
   * Current department
   * Stage (waiting, available, shipped, etc.)
   * Movement history

---

### 3. QR Code Traceability

At terminals, employees scan the QR Code. The system identifies:

* Model, batch, department, terminal (Point-01, 02, …)
* Action (production, receiving, inspection, shipment)

Each record includes:

* Date and time
* Quantity
* Source and destination department
* User and device

This ensures a **complete and detailed audit trail**.

---

### 4. Production and Movement Rules

The system prevents errors such as:

* Duplicate production records
* Repeated department entries
* Moving more than available quantity
* Skipping workflow steps
* Mixing incorrect batches
* Confusing models with different workflows (SMT-FIRST)

---

### 5. Complete History

For each model, you can view:

* Created labels
* Movements by department
* Production deductions
* Current balance by stage
* Edit history
* Chronological log with date/time

---

### 6. Dashboard and Indicators

The dashboard shows:

* Balance by department (PTH, SMT, IM, PA, Stock)
* Stage (Waiting, Available, Shipped, etc.)
* Quantity available per batch
* Bottleneck identification
* Real-time status updates

---

## ✅ Benefits

**Productivity:**

* Reduces manual errors
* Eliminates rework
* Increases factory floor efficiency

**Security:**

* Immutable action records
* Complete audit history

---

## 📁 How to Run

```bash
pip install -r requirements.txt
python app.py
```

---

## 🔗 Access the System (Deployment)

The system is available online via Render.
Countermeasures are applied even in the free version to prevent inactivity shutdown. If it closes, wait 50 seconds and reopen.

➡️ **[https://label-tracking-system.onrender.com](https://label-tracking-system.onrender.com)**

---

## 👨‍💻 Author

* Developed by **Eduardo Libório**
* 📧 [eduardosoleno@protonmail.com](mailto:eduardosoleno@protonmail.com)

---

