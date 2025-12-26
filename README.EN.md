

# 🏷️ Venttos Electronics. Venttos Trace

**Venttos Trace** is an internal platform developed to control, monitor, and record the entire movement of boards/parts within the production flow. It uses **QR Codes**, individual labels per batch, and tracking points (terminals) installed across departments to ensure that each item is tracked from production to final shipment.

It is a **real-time automated system** that replaces manual controls (spreadsheets, paper logs, handwritten notes), reduces human error, and increases data reliability.

You can view the live application through the link at the end of this README.md.

---

## 📁 Project Structure

```
label-tracking-system-venttos/venttos-trace
├─ static/
│     ├─ icons/ 
│     ├─ logos/
│     ├─ qrcodes/
│     ├─ users/ 
│     └─ style.css      
│   
├─ templates/
│     ├─ base.html
│     ├─ dashboard.html    
│     ├─ etiqueta_view.html
│     ├─ form.html
│     ├─ history.html
│     ├─ home.html
│     ├─ index.html
│     ├─ label.html
│     ├─ live.html
│     ├─ live_consultar.html
│     ├─ menu.html
│     ├─ movimentar.html
│     ├─ ops.html
│     └─ setores.html
│
├─ app.py
├─ models.db
├─ ping.py
├─ Profile
├─ README.EN.md
├─ README.md
└─ requirements.txt

├─ icons/config.jpeg, dashboard.jpeg, home-hero.png, home.jpeg, live.jpeg, logo-page-dashboard.png,
logo-page-live.png, logo-page-ops.png, logo-page-ordens.png, menu.jpeg, movimentar.jpeg, ops.jpeg,
ordens.jpeg
├─ logos/logo-name.jpeg, logo.jpeg, logo.png
├─ qrcodes/da.png
├─ users/eduardo.jpeg
```

---

## 🚀 Features

* Product/model registration (customer, line, batch, OP, process, QC, etc.)
* Automatic **QR Code** generation
* Individual label printing per batch
* Produced quantity and available balance control
* Complete movement history by department
* Real-time Production Order (OP) control
* Detailed production inquiry per OP
* Indicators by department, shift, phase, and time
* Dynamic production dashboard
* Responsive HTML interface with **Bootstrap**
* Optimized experience for desktop and mobile

---

## ⚙️ Technologies Used

* [Python 3](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/) — main web server
* [SQLite](https://www.sqlite.org/) — internal database
* [qrcode](https://pypi.org/project/qrcode/) — QR code generation
* [Pillow](https://pypi.org/project/Pillow/) — image manipulation
* HTML / CSS / Bootstrap — web interface and Jinja2 templates

---

## 🧾 Production Order (OP) Control

In addition to label traceability, Venttos Trace includes a complete OP control module, allowing real-time production monitoring directly from the shop floor or the office.

---

## 📌 OP Overview (Real-Time Production)

The live production screen displays:

* Consolidated list of active OPs
* Model and customer
* Quantity already produced
* Current production department

Filters available:

* Start and end date
* Department (PTH, SMT, IM, PA, Stock)
* Search by model, customer, or OP

All data is dynamically updated as records are entered into the system.

---

## 🔍 Detailed OP Inquiry

### When accessing a specific OP, the system provides a detailed production view:

* Total produced
* Production filtered by phase
* Automatic data consolidation
* Hour-by-hour production
* Quantity produced by time range
* Shift separation
* Clear visualization of production pace

### Detailed Records

Each production entry contains:

* Date and time
* Shift
* Phase (TOP / BOTTOM)
* Department
* Produced quantity
* Responsible operator

Additionally, dynamic filters can be applied by:

* Shift (1st, 2nd, or all)
* Phase (TOP, BOTTOM, or all)

---

## 📱 Desktop and Mobile Experience (Enhanced UX)

Venttos Trace was developed as a complete web system for computer use, with special attention to the mobile experience.

💻 **Desktop**

When accessed on a computer:

* Traditional corporate system layout
* Full data tables
* Large dashboards
* Ideal for supervision, management, and analysis

---

## 📲 Mobile (App-Like Experience)

### When accessed on a mobile device, the system:

* Detects screen size
* Activates mobile-specific layouts
* Uses simplified navigation
* Large, touch-friendly buttons
* Menus optimized for touch
* Reorganized filters for quick access

Even without being a native app, the mobile experience behaves like an industrial application, making it ideal for direct use on the shop floor, terminals, or mobile devices.

---

## 📊 Data Flow and Control Points

| Point        | Department | Function                |
| ------------ | ---------- | ----------------------- |
| **Point-01** | PTH        | Production & Receiving  |
| **Point-02** | SMT        | Production & Receiving  |
| **Point-03** | SMT        | Quality Inspection      |
| **Point-04** | IM/PA      | Production & Receiving  |
| **Point-05** | IM/PA      | Quality Inspection      |
| **Point-06** | IM/PA      | Quality Inspection      |
| **Point-07** | Stock      | Shipping (Final Output) |

---

## ⚙️ How the System Works

### 1. Model Registration

Each product/model is registered with:

* Code, name, customer
* Line and initial department
* Batch and planned production
* PO/OP, process, and QC
* Inspector/operator
* Date and time

This registration generates the master record that will be tracked.

---

### 2. Label and Batch Generation

After registering the model:

1. The system calculates the number of labels required based on **total production** and **capacity per magazine/box**.
2. Each label receives:

   * Individual batch (e.g., "08 / 504")
   * Its own QR Code
   * Link to the original model
3. Each label contains:

   * Original and remaining quantity
   * Current department
   * Phase (waiting, available, shipped, etc.)
   * Movement history

---

### 3. QR Code Traceability

At each terminal, the operator scans the QR Code. The system identifies:

* Model, batch, department, terminal (Point-01, 02, …)
* Action (production, receiving, inspection, shipping)

Each record includes:

* Date and time
* Quantity
* Origin and destination department
* User and equipment

This ensures a **complete and detailed traceability trail**.

---

### 4. Production and Movement Rules

The system prevents errors such as:

* Duplicate production records
* Repeated entry into the same department
* Movements exceeding available quantity
* Skipping production steps
* Incorrect batch mixing
* Confusion between models with different flows (SMT-FIRST)

---

### 5. Complete History

For each model, it is possible to view:

* Created labels
* Movements by department
* Production deductions
* Current balance by phase
* Edit history
* Full chronological log with date/time

---

### 6. Dashboard and Indicators

The dashboard displays:

* Balance by department (PTH, SMT, IM, PA, Stock)
* Phase (Waiting, Available, Shipped, etc.)
* Available quantity per batch
* Bottleneck identification
* Real-time updated status

---

## ✅ Benefits for the Company

**Productivity:**

* Reduces manual errors
* Eliminates rework
* Increases shop floor efficiency

**Security:**

* Immutable record of every action
* Complete audit-ready history

---

## 📁 How to Run

```bash
pip install -r requirements.txt
python app.py
```

---

## 🔗 System Access (Deploy)

The system is available online via Render:
Countermeasures are used even on the free tier to prevent the page from sleeping due to inactivity. If it does go down, please wait about 50 seconds.

➡️ **[https://label-tracking-system-venttos.onrender.com](https://label-tracking-system-venttos.onrender.com)**

---

## 👨‍💻 Author

* Developed by **Eduardo Libório**
* 📧 [eduardosoleno@protonmail.com](mailto:eduardosoleno@protonmail.com)

---
