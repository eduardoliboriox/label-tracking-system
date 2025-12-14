#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort, jsonify
from datetime import datetime
import sqlite3, os, qrcode
from io import BytesIO
import socket
import re

app = Flask(__name__)
app.secret_key = "chave_super_secreta_trocar"
DB_PATH = "models.db"

# ---------------- Banco de Dados ----------------
def init_db():
    if os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            model_name TEXT,
            cliente TEXT,
            linha TEXT,
            turno TEXT,
            data TEXT,
            lote TEXT,
            quantidade TEXT,
            revisora TEXT,
            horario TEXT,
            po TEXT,
            op TEXT,
            status_cq TEXT,
            processo TEXT,
            obs TEXT,
            setor TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER,
            changed_at TEXT,
            changed_by TEXT,
            change_text TEXT,
            FOREIGN KEY(model_id) REFERENCES models(id)
        )
    ''')
    c.execute('''
        CREATE TABLE labels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER,
            lote TEXT,
            producao_total INTEGER,
            capacidade_magazine INTEGER,
            created_at TEXT,
            linked_label_id INTEGER,
            setor_atual TEXT,
            FOREIGN KEY(model_id) REFERENCES models(id),
            FOREIGN KEY(linked_label_id) REFERENCES labels(id)
        )
    ''')
    c.execute('''
        CREATE TABLE movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER,
            label_id INTEGER,
            ponto TEXT,
            acao TEXT,
            quantidade INTEGER,
            from_setor TEXT,
            to_setor TEXT,
            created_at TEXT,
            created_by TEXT,
            FOREIGN KEY(model_id) REFERENCES models(id),
            FOREIGN KEY(label_id) REFERENCES labels(id)
        )
    ''')
    conn.commit()
    conn.close()

def add_missing_column():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("PRAGMA table_info(models);")
    columns = [col[1] for col in c.fetchall()]

    # Colunas existentes
    if "op" not in columns:
        c.execute("ALTER TABLE models ADD COLUMN op TEXT;")
    if "setor" not in columns:
        c.execute("ALTER TABLE models ADD COLUMN setor TEXT;")

    if "fase" not in columns:
        c.execute("ALTER TABLE models ADD COLUMN fase TEXT;")

    if "phase_type" not in columns:
        c.execute("ALTER TABLE models ADD COLUMN phase_type TEXT DEFAULT 'TOP_ONLY';")

    if "operadora" not in columns:
        c.execute("ALTER TABLE models ADD COLUMN operadora TEXT;")
    
    if "lote_padrao" not in columns:
        c.execute("ALTER TABLE models ADD COLUMN lote_padrao TEXT;")

    conn.commit()   
    conn.close()

def add_missing_table_labels():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='labels';")
    if not c.fetchone():
        c.execute("""
            CREATE TABLE labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                lote TEXT,
                producao_total INTEGER,
                capacidade_magazine INTEGER,
                remaining INTEGER,
                created_at TEXT,
                linked_label_id INTEGER,
                setor_atual TEXT,
                fase TEXT,
                top_done INTEGER DEFAULT 0,
                bottom_done INTEGER DEFAULT 0,
                status TEXT DEFAULT 'ATIVO',
                FOREIGN KEY(model_id) REFERENCES models(id),
                FOREIGN KEY(linked_label_id) REFERENCES labels(id)
            )
        """)
        conn.commit()
    else:
        c.execute("PRAGMA table_info(labels);")
        columns = [col[1] for col in c.fetchall()]
        if "linked_label_id" not in columns:
            c.execute("ALTER TABLE labels ADD COLUMN linked_label_id INTEGER REFERENCES labels(id);")
        if "setor_atual" not in columns:
            c.execute("ALTER TABLE labels ADD COLUMN setor_atual TEXT;")
        if "fase" not in columns:
            c.execute("ALTER TABLE labels ADD COLUMN fase TEXT;")
        if "remaining" not in columns:
            c.execute("ALTER TABLE labels ADD COLUMN remaining INTEGER;")
            # Inicializa remaining com capacidade_magazine para registros antigos
            c.execute("UPDATE labels SET remaining = capacidade_magazine WHERE remaining IS NULL;")
        if "top_done" not in columns:
            c.execute("ALTER TABLE labels ADD COLUMN top_done INTEGER DEFAULT 0;")
        if "bottom_done" not in columns:
            c.execute("ALTER TABLE labels ADD COLUMN bottom_done INTEGER DEFAULT 0;")
        if "status" not in columns:
            c.execute("ALTER TABLE labels ADD COLUMN status TEXT DEFAULT 'ATIVO';")
        if "updated_at" not in columns:
            c.execute("ALTER TABLE labels ADD COLUMN updated_at TEXT;")
        conn.commit()
    conn.close()

def add_missing_table_movements():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movements';")
    if not c.fetchone():
        c.execute('''
            CREATE TABLE movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                label_id INTEGER,
                ponto TEXT,
                acao TEXT,
                quantidade INTEGER,
                from_setor TEXT,
                to_setor TEXT,
                fase TEXT, 
                created_at TEXT,
                created_by TEXT
            )
        ''')
        conn.commit()
    conn.close()

def add_missing_columns_movements():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("PRAGMA table_info(movements);")
    columns = [col[1] for col in c.fetchall()]
    if "fase" not in columns:
        c.execute("ALTER TABLE movements ADD COLUMN fase TEXT;")
    conn.commit()
    conn.close()

def add_new_label_id_column_movements():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("PRAGMA table_info(movements);")
    columns = [col[1] for col in c.fetchall()]

    if "new_label_id" not in columns:
        c.execute("ALTER TABLE movements ADD COLUMN new_label_id INTEGER;")

    conn.commit()
    conn.close()

def add_missing_table_ops():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ops';")
    if not c.fetchone():
        c.execute('''
            CREATE TABLE ops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filial TEXT,
                numero_op TEXT,
                produto TEXT,
                descricao TEXT,
                armazem TEXT,
                quantidade INTEGER,
                produzido INTEGER,
                setores TEXT,
                created_at TEXT
            )
        ''')
        conn.commit()

    conn.close()

def add_missing_table_ops_saldos():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Se a tabela não existe, cria corretamente já com fase
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ops_saldos';")
    if not c.fetchone():
        c.execute("""
            CREATE TABLE ops_saldos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_op INTEGER,
                setor TEXT,
                fase TEXT,                        
                quantidade INTEGER DEFAULT 0,
                updated_at TEXT,
                FOREIGN KEY (id_op) REFERENCES ops(id)
            );
        """)
        conn.commit()
        conn.close()
        return

    # Se já existe, garantir que todas as colunas necessárias existem
    c.execute("PRAGMA table_info(ops_saldos);")
    columns = [col[1] for col in c.fetchall()]

    if "setor" not in columns:
        c.execute("ALTER TABLE ops_saldos ADD COLUMN setor TEXT;")

    if "fase" not in columns:
        c.execute("ALTER TABLE ops_saldos ADD COLUMN fase TEXT;")   

    if "quantidade" not in columns:
        c.execute("ALTER TABLE ops_saldos ADD COLUMN quantidade INTEGER DEFAULT 0;")

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

with app.app_context():
    init_db()
    add_missing_column()           # para models
    add_missing_table_labels()     # para labels
    add_missing_table_movements() 
    add_missing_columns_movements()
    add_new_label_id_column_movements() 
    add_missing_table_ops()  
    add_missing_table_ops_saldos() 

# ---------------- Regras de Ponto / Roteiro ----------------
# Definir um mapeamento básico dos pontos para setores.
POINT_RULES = {
    "Ponto-01": {"setor": "PTH", "type": "porta"},
    "Ponto-02": {"setor": "SMT", "type": "porta"},
    "Ponto-03": {"setor": "SMT", "type": "qualidade"},
    "Ponto-04": {"setor": "IM/PA", "type": "porta"},
    "Ponto-05": {"setor": "IM/PA", "type": "qualidade"},
    "Ponto-06": {"setor": "IM/PA", "type": "qualidade"},
    "Ponto-07": {"setor": "ESTOQUE", "type": "expedicao"},
}

def normalize_lote_from_qr(lote_sufixo):
    """Converte o sufixo vindo do QR (ex: '08-504' ou '08-504-xyz') para o formato salvo '08 / 504' (aprox)."""
    if not lote_sufixo:
        return None
    parts = lote_sufixo.split("-")
    if len(parts) == 1:
        return parts[0].replace('-', ' / ').strip()
    first = parts[0].strip()
    second = parts[1].strip() if len(parts) > 1 else ""
    return f"{first} / {second}"

def find_label(conn, model_id, lote_formatado):
    """Procura uma label do model_id com lote exatamente igual (tente correspondência direta)."""
    if not lote_formatado:
        return None
    cur = conn.execute("SELECT * FROM labels WHERE model_id=? AND lote=?", (model_id, lote_formatado)).fetchone()
    if cur:
        return dict(cur)
    # tentativa de correspondência mais permissiva (removendo espaços)
    simple = lote_formatado.replace(" ", "")
    cur2 = conn.execute("SELECT * FROM labels WHERE model_id=? AND REPLACE(lote,' ','') LIKE ?", (model_id, f"%{simple}%")).fetchone()
    if cur2:
        return dict(cur2)
    return None

def register_movement(conn, model_id, label_id, new_label_id, ponto, acao, quantidade, from_setor, to_setor, fase, created_by="terminal_movimentacao"):
    now = datetime.now().isoformat()

    conn.execute("""
        INSERT INTO movements 
            (model_id, label_id, new_label_id, ponto, acao, quantidade, from_setor, to_setor, fase, created_at, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        model_id,
        label_id,
        new_label_id,
        ponto,
        acao,
        quantidade,
        from_setor,
       to_setor,
        fase,
        now,
        created_by
    ))

# ---------------- Rotas ----------------

@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    conn = get_db()
    if search:
        query = """
            SELECT * FROM models 
            WHERE code LIKE ? OR model_name LIKE ? OR cliente LIKE ?
            ORDER BY id DESC
        """
        models = conn.execute(query, (f"%{search}%", f"%{search}%", f"%{search}%")).fetchall()
    else:
        models = conn.execute("SELECT * FROM models ORDER BY id DESC").fetchall()
    conn.close()

    def format_updated_at(value):
        if not value:
            return ""
        try:
            s = str(value).replace("T", " ")
            s_short = s.split(".")[0].split("+")[0].split("Z")[0].strip()
            dt = datetime.strptime(s_short, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d/%m/%Y às %H:%M:%S")
        except:
            try:
                dt2 = datetime.fromisoformat(str(value))
                return dt2.strftime("%d/%m/%Y às %H:%M:%S")
            except:
                return str(value)

    models = [dict(m) for m in models]
    for m in models:
        m["updated_at_formatted"] = format_updated_at(m.get("updated_at"))

    return render_template("index.html", models=models, search=search)

@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        f = request.form
        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO models 
                    (code, model_name, cliente, linha, setor, fase, phase_type, turno, data, lote, quantidade, revisora, operadora, horario, po, op, status_cq, processo, obs, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                (
                    f.get("code", ""),
                    f.get("model_name", ""),
                    f.get("cliente", ""),
                    f.get("linha", ""),
                    f.get("setor", ""),
                    f.get("fase", ""),  
                    f.get("phase_type", "TOP_ONLY"), 
                    f.get("turno", ""),
                    f.get("data") or datetime.now().strftime("%d/%m/%Y"),
                    f"{f.get('lote_num', '').strip()} / {f.get('lote_padrao', '').strip()}",
                    f.get("quantidade", ""),
                    f.get("revisora", ""),
                    f.get("operadora", ""),
                    f.get("horario", ""),
                    f.get("po", ""),
                    f.get("op", ""),
                    ",".join(request.form.getlist("status_cq")),
                    ",".join(request.form.getlist("processo")),
                    f.get("obs", ""),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                )
            )
            conn.commit()

            flash("Modelo cadastrado com sucesso!", "success")
        except sqlite3.Error as e:
            flash(f"Erro ao salvar: {e}", "danger")

        finally:
            conn.close()
        return redirect(url_for("index"))
    return render_template("form.html", model=None)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    try:
        model = conn.execute("SELECT * FROM models WHERE id=?", (id,)).fetchone()
        if not model:
            conn.close()
            abort(404)

        # -----------------------------------------------
        # SE FOR POST: atualizar registro
        # -----------------------------------------------
        if request.method == "POST":
            f = request.form

            lote_num = f.get("lote_num", "").strip()
            lote_padrao = f.get("lote_padrao", "").strip()
            lote_final = f"{lote_num} / {lote_padrao}"

            try:
                conn.execute("""
                    UPDATE models 
                    SET code=?, model_name=?, cliente=?, linha=?, setor=?, fase=?, phase_type=?, turno=?, data=?, 
                        lote=?, quantidade=?, revisora=?, operadora=?, horario=?, po=?, op=?, status_cq=?, processo=?, obs=?, updated_at=?
                    WHERE id=?
                """, (
                    f["code"],
                    f["model_name"],
                    f["cliente"],
                    f["linha"],
                    f.get("setor", ""),
                    f.get("fase", ""),
                    f.get("phase_type", "TOP_ONLY"),
                    f["turno"],
                    f["data"],
                    lote_final,
                    f["quantidade"],
                    f["revisora"],
                    f["operadora"],
                    f["horario"],
                    f["po"],
                    f.get("op", ""),
                    ",".join(request.form.getlist("status_cq")),
                    ",".join(request.form.getlist("processo")),
                    f["obs"],
                    datetime.now().isoformat(),
                    id
                ))
            except sqlite3.IntegrityError:
                flash("❌ Já existe um modelo com este CODE. Escolha outro.", "danger")
                return redirect(url_for("edit", id=id))

            # REGISTRAR HISTÓRICO
            conn.execute(
                "INSERT INTO history (model_id, changed_at, changed_by, change_text) VALUES (?, ?, ?, ?)",
                (id, datetime.now().isoformat(), "web_user", "Edição de modelo")
            )

            conn.commit()
            flash("Modelo atualizado com sucesso!", "success")

  
            return redirect(url_for("index"))

        # -----------------------------------------------
        # SE FOR GET: carregar form.html com modelo
        # -----------------------------------------------
        lote_num, lote_padrao = "", ""
        if model["lote"]:
            partes = [p.strip() for p in model["lote"].split("/")]
            if len(partes) >= 1:
                lote_num = partes[0]
            if len(partes) >= 2:
                lote_padrao = partes[1]

        return render_template("form.html", model=model, lote_num=lote_num, lote_padrao=lote_padrao)

    except Exception as e:
        print("Erro no edit():", e)
        raise e
    finally:
        conn.close()

@app.route("/view/<int:id>", methods=["GET", "POST"])
def view_label(id):
    with get_db() as conn:
        model = conn.execute("SELECT * FROM models WHERE id=?", (id,)).fetchone()
    existing_labels = conn.execute("SELECT * FROM labels WHERE model_id=? ORDER BY created_at DESC", (id,)).fetchall()
    conn.close()
    if not model:
        abort(404)

    etiquetas_por_folha = 3
    producao_total = None
    capacidade_magazine = None
    lotes = []

    if request.method == "POST":
        try:
            producao_total = int(request.form.get("producao_total", 0))
            capacidade_magazine = request.form.get("capacidade_magazine")
            capacidade_magazine = int(capacidade_magazine) if capacidade_magazine and capacidade_magazine.isdigit() else 50
            if capacidade_magazine <= 0:
                capacidade_magazine = 1

            total_etiquetas = (producao_total + capacidade_magazine - 1) // capacidade_magazine
            total_folhas = (total_etiquetas + etiquetas_por_folha - 1) // etiquetas_por_folha

            try:
                parte_num, parte_padrao = [x.strip() for x in model['lote'].split('/')[:2]]
                lote_inicial = int(parte_num)
                padrao = parte_padrao
            except:
                lote_inicial = 1
                padrao = "900"

            lotes = [f"{lote_inicial + i:02d} / {padrao}" for i in range(total_etiquetas)]

            linked_label_id = request.form.get("linked_label_id") or None

            conn = get_db()

            remaining_total = producao_total

            for lote in lotes:
                amount = min(capacidade_magazine, remaining_total)

                if amount <= 0:
                    break

            conn = get_db()

            remaining_total = producao_total

            for lote in lotes:
                amount = min(capacidade_magazine, remaining_total)

                if amount <= 0:
                    break

                conn.execute("""
                    INSERT INTO labels 
                        (model_id, lote, producao_total, capacidade_magazine, remaining, created_at, linked_label_id, setor_atual, fase)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id,
                    lote,
                    amount,                    # ✅ Grava apenas o valor REAL desta etiqueta
                    capacidade_magazine,
                    amount,                    # remaining começa igual ao amount
                    datetime.now().isoformat(),
                    linked_label_id,
                    model["setor"] if model["setor"] else "PTH",
                    "AGUARDANDO"
                ))

                remaining_total -= amount

            conn.commit()
            conn.close()

            flash(f"Produção: {producao_total} placas → {total_etiquetas} etiquetas → {total_folhas} folhas. Etiquetas salvas no histórico.", "info")

        except ValueError:
            flash("⚠️ Digite valores válidos para produção e capacidade.", "danger")

    return render_template("label.html", m=model, lotes=lotes, existing_labels=existing_labels)

@app.route("/setores/<int:id>")
def setores(id):
    # Buscar OP original
    conn = get_db()
    model = conn.execute("SELECT * FROM models WHERE id = ?", (id,)).fetchone()

    if not model:
        return "OP não encontrada", 404

    setores = ["PTH", "SMT", "IM", "PA", "ESTOQUE"]

    return render_template("setores.html", model=model, setores=setores)

@app.route("/setores/<int:id>/<setor>", methods=["GET", "POST"])
def setor_form(id, setor):
    conn = get_db()
    model = conn.execute("SELECT * FROM models WHERE id = ?", (id,)).fetchone()

    if not model:
        return "OP não encontrada", 404

    # Copia o model original para usar nos forms e no POST
    model_dict = dict(model)
    model_dict["setor"] = setor  

    if request.method == "POST":
        data = dict(request.form)
        data["setor"] = setor  

        data["code"] = f"{data['code']}_{setor}"
        data["updated_at"] = datetime.now().isoformat()

        conn.execute("""
            INSERT INTO models 
            (code, model_name, cliente, linha, setor, fase, phase_type, turno, data, horario, 
             lote, lote_padrao, po, quantidade, op, revisora, operadora, obs, updated_at)
            VALUES 
            (:code, :model_name, :cliente, :linha, :setor, :fase, :phase_type, :turno, :data, :horario,
             :lote, :lote_padrao, :po, :quantidade, :op, :revisora, :operadora, :obs, :updated_at)
        """, data)

        conn.commit()

        novo_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.close()
        return redirect(url_for("view_label", id=novo_id))

    conn.close()
    return render_template("form.html", model=model_dict)

@app.route("/qr/<string:code>")
def qr(code):
    import socket
    from io import BytesIO
    import qrcode

    # 🔹 Detecta o IP local da máquina automaticamente
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"

    # 🔹 Gera a URL completa 
    qr_url = f"http://{local_ip}:5000/movimentar/{code.strip()}"

    img = qrcode.make(qr_url)
    buf = BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

def salvar_op(dados):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # salva OP
    c.execute("""
        INSERT INTO ops (filial, numero_op, produto, descricao, armazem, quantidade, produzido, setores, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dados["filial"],
        dados["numero_op"],
        dados["produto"],
        dados["descricao"],
        dados["armazem"],
        dados["quantidade"],
        dados.get("produzido", 0),
        ",".join(dados["setores"]),
        datetime.now().isoformat()
    ))

    id_op = c.lastrowid

    # criar entradas por setor × fase — quantidade inicial = 0 (saldo planejado separado da produção)
    for setor in dados["setores"]:
        for fase in dados["fases"]:
            c.execute("""
                INSERT INTO ops_saldos (id_op, setor, fase, quantidade)
                VALUES (?, ?, ?, 0)
            """, (id_op, setor, fase))

    conn.commit()
    conn.close()

def buscar_ops():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT 
            o.id AS id,
            s.id AS saldo_id,
            o.filial,
            o.numero_op,
            o.produto,
            o.descricao,
            o.armazem,
            o.quantidade,

            -- total produzido da OP (somando movements marcados como PRODUCAO para este model/op)
            COALESCE((
                SELECT SUM(m.quantidade)
                FROM movements m
                WHERE m.acao = 'PRODUCAO'
                  AND m.model_id = (
                      SELECT id FROM models WHERE op = o.numero_op AND code = o.produto LIMIT 1
                  )
            ), 0) AS produzido_total,

            -- setor + fase (linha)
            s.setor,
            s.fase,

            -- produzido real por setor + fase (somando movements.to_setor + fase)
            COALESCE((
                SELECT SUM(m.quantidade)
                FROM movements m
                WHERE m.acao = 'PRODUCAO'
                  AND m.to_setor = s.setor
                  AND UPPER(TRIM(m.fase)) = UPPER(TRIM(s.fase))
                  AND m.model_id = (
                      SELECT id FROM models WHERE op = o.numero_op AND code = o.produto LIMIT 1
                  )
            ), 0) AS produzido_setor,

            -- saldo planejado (ops_saldos) — valor inicial que você cadastrou (aqui mantido separadamente)
            s.quantidade AS saldo_planejado

        FROM ops o
        LEFT JOIN ops_saldos s ON o.id = s.id_op
        ORDER BY 
            o.id DESC,
            s.setor,
            s.fase
    """)

    res = c.fetchall()
    conn.close()
    return res


@app.route("/ops/delete_saldo/<int:saldo_id>", methods=["GET"])
def delete_saldo(saldo_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id_op FROM ops_saldos WHERE id = ?", (saldo_id,))
    row = c.fetchone()

    if not row:
        flash("Registro não encontrado!", "danger")
        return redirect(url_for("ops"))

    id_op = row[0]

    c.execute("DELETE FROM ops_saldos WHERE id = ?", (saldo_id,))

    # verificar se ainda sobrou algum setor/fase para essa OP
    c.execute("SELECT COUNT(*) FROM ops_saldos WHERE id_op = ?", (id_op,))
    restantes = c.fetchone()[0]

    # se não sobrou nenhum -> apagar OP inteira
    if restantes == 0:
        c.execute("DELETE FROM ops WHERE id = ?", (id_op,))

    conn.commit()
    conn.close()

    flash("Linha removida com sucesso!", "success")
    return redirect(url_for("ops"))

@app.route("/ops")
def ops():
    lista_ops = buscar_ops()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT MAX(id) FROM movements")
    max_ops_id = c.fetchone()[0] or 0
    conn.close()

    return render_template("ops.html", ops=lista_ops, max_ops_id=max_ops_id)

@app.route("/ops/add", methods=["POST"])
def add_op():
    dados = {
        "filial": request.form.get("filial"),
        "numero_op": request.form.get("numero_op"),
        "produto": request.form.get("produto"),
        "descricao": request.form.get("descricao"),
        "armazem": request.form.get("armazem"),
        "quantidade": int(request.form.get("quantidade")),
        "produzido": int(request.form.get("produzido")),
        "setores": request.form.getlist("setores"),
        "fases": request.form.getlist("fase")   
    }
    salvar_op(dados)
    flash("OP cadastrada com sucesso!", "success")
    return redirect(url_for("ops"))


@app.route("/ops/update/<int:id>", methods=["POST"])
def update_op(id):
    dados = {
        "filial": request.form.get("filial"),
        "numero_op": request.form.get("numero_op"),
        "produto": request.form.get("produto"),
        "descricao": request.form.get("descricao"),
        "armazem": request.form.get("armazem"),
        "quantidade": int(request.form.get("quantidade")),
        "produzido": int(request.form.get("produzido")),
        "setores": ",".join(request.form.getlist("setores"))
    }

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE ops SET 
            filial = ?,
            numero_op = ?,
            produto = ?,
            descricao = ?,
            armazem = ?,
            quantidade = ?,
            produzido = ?,
            setores = ?
        WHERE id = ?
    """, (
        dados["filial"], dados["numero_op"], dados["produto"], dados["descricao"],
        dados["armazem"], dados["quantidade"], dados["produzido"], dados["setores"],
        id
    ))
    conn.commit()
    conn.close()

    flash("OP atualizada com sucesso!", "success")
    return redirect(url_for("ops"))

def atualizar_producao_op(conn, produto, numero_op, setor, fase, quantidade):
    """
    Usa a conexão passada (mesma transação). NÃO altera ops_saldos.
    Atualiza somente o campo ops.produzido (somatório total) — opcional.
    """
    c = conn.cursor()

    # Busca OP pelo produto + OP
    c.execute("""
        SELECT id FROM ops 
        WHERE produto=? AND numero_op=?
    """, (produto, numero_op))

    op = c.fetchone()
    if not op:
        return False

    id_op = op[0]

    # Atualiza total produzido da OP (mantém total OP)
    c.execute("""
        UPDATE ops 
        SET produzido = COALESCE(produzido,0) + ?
        WHERE id = ?
    """, (quantidade, id_op))

    return True

@app.route("/movimentar", methods=["GET", "POST"])
def movimentar():
    ponto_url = request.form.get("ponto_url") or request.args.get("p") or request.args.get("ponto")
    model = None
    label = None
    full_code = request.form.get("qr_code") or request.args.get("qr_code")
    clean_display_code = clean_display_qr(full_code)

    if full_code:
        full_code = extract_real_code(full_code)
        if not full_code:
            flash("QR inválido", "danger")
            return redirect(url_for("movimentar", p=ponto_url))

        parts = full_code.split("-")
        base_code = parts[0].upper()
        lote_sufixo = "-".join(parts[1:]) if len(parts) > 1 else None
        lote_formatado = normalize_lote_from_qr(lote_sufixo) if lote_sufixo else None

        conn = get_db()
        model_row = conn.execute("SELECT * FROM models WHERE UPPER(code)=?", (base_code,)).fetchone()
        if not model_row:
            conn.close()
            flash(f"Código '{full_code}' não encontrado.", "danger")
            return redirect(url_for("movimentar", p=ponto_url))
        model = dict(model_row)

        if lote_formatado:
            label_row = conn.execute(
                "SELECT * FROM labels WHERE model_id=? AND lote=? ORDER BY id DESC LIMIT 1",
                (model["id"], lote_formatado)
            ).fetchone()
            if label_row:
                label = dict(label_row)

        if not label:
            conn.close()
            flash("Etiqueta não encontrada para o lote informado.", "danger")
            return redirect(url_for("movimentar", p=ponto_url))
        conn.close()

    def get_fase(ponto, acao):
        p = (ponto or "").strip()
        a = (acao or "").strip().upper()

        if p == "Ponto-03":
            if a == "RECEBIMENTO":
                return "PENDENTE CQ"
            if a == "CQ":
                return "CQ APROVOU"
            return "DISPONIVEL"


        # Ponto-02 (SMT) segue fluxo SMT normal:
        # RECEBIMENTO -> AGUARDANDO, caso contrário -> DISPONIVEL
        if p == "Ponto-02":
            if a == "RECEBIMENTO":
                return "AGUARDANDO"
            return "DISPONIVEL"

        # default para outros pontos
        return "DISPONIVEL"

    # --- START POST handling ---
    if request.method == "POST" and model and label:
        acao = (request.form.get("acao") or "").strip().upper()
        ponto = request.form.get("ponto") or ponto_url
        conn = get_db()
        try:
            setor_origem = label.get("setor_atual")
            capacidade = int(label.get("capacidade_magazine") or 0)
            remaining = int(label.get("remaining") or capacidade)
            quantidade = int(request.form.get("quantidade") or remaining)

            top_mark = int(request.form.get("top_mark") or 0)
            bottom_mark = int(request.form.get("bottom_mark") or 0)

            # --- validação de fase existente ---
            if top_mark == 1 and bottom_mark == 1:
                bottom_mark = 0

            if top_mark == 0 and bottom_mark == 0:
                flash("Escolha uma fase: TOP ou BOTTOM!", "danger")
                return redirect(url_for("movimentar", p=ponto_url))

            # --- validação: tipo de fase ---
            possible_keys = ["tipo_de_fase", "tipo_fase", "phase_type", "fase_tipo", "type_phase", "tipo"]
            tipo_de_fase = None
            for k in possible_keys:
                if k in model and model.get(k) is not None:
                    tipo_de_fase = str(model.get(k)).strip().upper()
                    break

            if tipo_de_fase:
                if "TOP ONLY" in tipo_de_fase or tipo_de_fase == "TOPONLY" or tipo_de_fase == "TOP":
                    if bottom_mark == 1 and top_mark == 0:
                        flash("Modelo é TOP ONLY — não é permitido registrar BOTTOM.", "danger")
                        return redirect(url_for("movimentar", p=ponto_url))
                if "BOTTOM ONLY" in tipo_de_fase or tipo_de_fase == "BOTTOMONLY" or tipo_de_fase == "BOTTOM":
                    if top_mark == 1 and bottom_mark == 0:
                        flash("Modelo é BOTTOM ONLY — não é permitido registrar TOP.", "danger")
                        return redirect(url_for("movimentar", p=ponto_url))

            old_top = int(label.get("top_done") or 0)
            old_bottom = int(label.get("bottom_done") or 0)

            top_done_new = old_top + quantidade if top_mark == 1 else old_top
            bottom_done_new = old_bottom + quantidade if bottom_mark == 1 else old_bottom

            # --- Lógica do RECEBIMENTO (SMT) ---
            # Se for RECEBIMENTO em SMT (Ponto-02 ou Ponto-03) -> zera contadores para a nova etiqueta
            if acao == "RECEBIMENTO" and ponto in ("Ponto-02", "Ponto-03"):
                top_done_new = 0
                bottom_done_new = 0

            fase_nova = get_fase(ponto, acao)

            # --- BLOQUEIO DUPLICADO por fase (igual já existente) ---
            label_id = label["id"]
            if top_mark == 1:
                already_top = conn.execute("""
                    SELECT 1
                    FROM movements
                    WHERE (
                        label_id = ? OR
                        new_label_id = ? OR
                        label_id IN (SELECT id FROM labels WHERE linked_label_id = ?) OR
                        new_label_id IN (SELECT id FROM labels WHERE linked_label_id = ?)
                    )
                    AND ponto = ?
                    AND acao = ?
                    AND UPPER(TRIM(fase)) = 'TOP'
                    LIMIT 1
                """, (label_id, label_id, label_id, label_id, ponto, acao)).fetchone()
                if already_top:
                    conn.close()
                    flash("TOP já foi registrado para esta etiqueta (ou filha) neste ponto.", "danger")
                    return redirect(url_for("movimentar", p=ponto_url))

            if bottom_mark == 1:
                already_bottom = conn.execute("""
                    SELECT 1
                    FROM movements
                    WHERE (
                        label_id = ? OR
                        new_label_id = ? OR
                        label_id IN (SELECT id FROM labels WHERE linked_label_id = ?) OR
                        new_label_id IN (SELECT id FROM labels WHERE linked_label_id = ?)
                    )
                    AND ponto = ?
                    AND acao = ?
                    AND UPPER(TRIM(fase)) = 'BOTTOM'
                    LIMIT 1
                """, (label_id, label_id, label_id, label_id, ponto, acao)).fetchone()
                if already_bottom:
                    conn.close()
                    flash("BOTTOM já foi registrado para esta etiqueta (ou filha) neste ponto.", "danger")
                    return redirect(url_for("movimentar", p=ponto_url))

            # --- FLUXO NORMAL (DISPONIVEL) ---
            transfer = quantidade if quantidade > 0 else remaining
            if transfer <= 0 or transfer > remaining:
                conn.close()
                flash("Quantidade inválida.", "danger")
                return redirect(url_for("movimentar", p=ponto_url))

            # Atualiza remaining da etiqueta original
            novo_remaining = remaining - transfer
            conn.execute("UPDATE labels SET remaining=?, updated_at=? WHERE id=?",
                         (novo_remaining, datetime.now().isoformat(), label["id"]))

            destino_map = {
                "Ponto-01": "PTH",
                "Ponto-02": "SMT",
                "Ponto-03": "SMT",
                "Ponto-04": "IM",
                "Ponto-05": "PA",
                "Ponto-06": "IM",
                "Ponto-07": "ESTOQUE"
            }
            setor_destino = destino_map.get(ponto, setor_origem)

            conn.execute("""
                INSERT INTO labels
                (model_id, lote, producao_total, capacidade_magazine, remaining,
                 created_at, linked_label_id, setor_atual, fase,
                 top_done, bottom_done)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                model["id"], label["lote"], transfer, transfer, transfer,
                datetime.now().isoformat(), label["id"],
                setor_destino, fase_nova,
                top_done_new, bottom_done_new
            ))
            new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            if top_mark == 1:
                register_movement(
                    conn,
                    model["id"],
                    label["id"],
                    new_id,
                    ponto,
                    acao,
                    transfer,
                    setor_origem,
                    setor_destino,
                    "TOP"
                )

            if bottom_mark == 1:
                register_movement(
                    conn,
                    model["id"],
                    label["id"],
                    new_id,
                    ponto,
                    acao,
                    transfer,
                    setor_origem,
                    setor_destino,
                    "BOTTOM"
                )

            # Identifica setor do ponto de marcação
            setor_map = {
                "Ponto-01": "PTH",
                "Ponto-02": "SMT",
                "Ponto-03": "SMT",
                "Ponto-04": "IM",
                "Ponto-05": "IM",
                "Ponto-06": "IM",
                "Ponto-07": "ESTOQUE"
            }

            setor = setor_map.get(ponto, None)

            if acao == "PRODUCAO" and setor:
                atualizar_producao_op(
                conn,
                produto=model["code"],
                numero_op=model["op"],
                setor=setor,
                fase=("TOP" if top_mark == 1 else "BOTTOM"),
                quantidade=transfer
            )

            conn.commit()
            flash(f"{acao} registrada ({transfer} un.)", "success")
            return redirect(url_for("movimentar", p=ponto_url))

        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
            flash(f"Erro ao registrar movimentação: {e}", "danger")
            return redirect(url_for("movimentar", p=ponto_url))
        finally:
            try:
                conn.close()
            except:
                pass

    # GET or fallback render
    return render_template(
        "movimentar.html",
        model=model,
        label=label,
        ponto=ponto_url,
        hide_top_menu=True,
        clean_display_code=clean_display_code
    )

def extract_real_code(raw):
    if not raw:
        return ""

    # Trocar caracteres errados
    cleaned = raw.replace("ç", ";").replace(";;", ";")
    cleaned = cleaned.replace("http", "").replace("https", "")
    cleaned = cleaned.replace("://", "").replace("/", "").replace(":", "")

    # Divide por ';'
    partes = cleaned.split(";")

    for p in reversed(partes):
        p = p.strip()
        if p:
            return p

    return cleaned.strip()

def clean_display_qr(raw):
    if not raw:
        return ""

    real = extract_real_code(raw)
    if real:
        return real

    txt = raw.upper()
    txt = (txt.replace("HTTP", "")
               .replace("Ç", "")
               .replace("ç", "")
               .replace(";", "")
               .replace(":", "")
               .strip())
    return txt

@app.route("/dashboard")
def dashboard():
    conn = get_db()
    
    # Lista todos os modelos
    models = conn.execute("SELECT * FROM models ORDER BY model_name").fetchall()
    models = [dict(m) for m in models]

    dashboard_data = []

    for m in models:

        labels = conn.execute("""
            SELECT *
            FROM labels
            WHERE model_id=? AND remaining > 0
        """, (m["id"],)).fetchall()

        labels = [dict(l) for l in labels]

        saldo_setores = []

        for lab in labels:

            setor = lab["setor_atual"] or "SEM SETOR"
            fase = (lab["fase"] or "").strip().upper()
            saldo = int(lab["remaining"] or 0)
            total = int(lab["producao_total"] or 0)
            top_done = int(lab["top_done"] or 0)
            bottom_done = int(lab["bottom_done"] or 0)

            # STATUS REAL
            if fase == "DISPONIVEL":
                status = "DISPONIVEL"
            elif fase.startswith("AGUARDANDO"):
                status = "AGUARDANDO"
            elif fase == "PENDENTE CQ":
                status = "PENDENTE CQ"
            elif fase == "CQ APROVOU":
                status = "CQ APROVOU"
            elif fase in ("EXPEDIDO", "EXPEDICAO"):
                status = "QUALIDADE"
            else:
                status = "AGUARDANDO"

            # EXIBIÇÃO AMIGÁVEL
            display_fase = fase

            # STATUS TOP/BOTTOM REAL
            fase_type = (m.get("phase_type") or "").strip().upper()

            if fase_type == "TOP ONLY":
                status_top = f"⬜ ({top_done}/{total})"
                status_bottom = "N/A"
            else:
                status_top = f" ({top_done}/{total})"
                status_bottom = f" ({bottom_done}/{total})"

            saldo_setores.append({
                "setor": setor,
                "fase": display_fase,
                "saldo": saldo,
                "status": status,
                "status_top": status_top,
                "status_bottom": status_bottom,
                "saldo_blank": total
            })

        dashboard_data.append({
            "model": m,
            "saldo_setores": saldo_setores
        })

    conn.close()
    return render_template("dashboard.html", data=dashboard_data)

@app.route("/history/<int:id>")
def history(id):
    with get_db() as conn:
        model = conn.execute("SELECT * FROM models WHERE id=?", (id,)).fetchone()
    hist = conn.execute(
        "SELECT * FROM history WHERE model_id=? ORDER BY changed_at DESC LIMIT 10",
        (id,)
    ).fetchall()

    etiquetas = conn.execute("SELECT * FROM labels WHERE model_id=? ORDER BY created_at DESC", (id,)).fetchall()
    movements = conn.execute("SELECT * FROM movements WHERE model_id=? ORDER BY created_at DESC LIMIT 50", (id,)).fetchall()
    conn.close()

    if not model:
        abort(404)

    # 🔹 Função para formatar data no padrão brasileiro
    def format_datetime(value):
        if not value:
            return ""
        try:
            s = str(value).replace("T", " ").split(".")[0]
            dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d/%m/%Y às %H:%M:%S")
        except Exception:
            return str(value)

    hist = [dict(h) for h in hist]
    for h in hist:
        h["changed_at_formatted"] = format_datetime(h["changed_at"])

    etiquetas = [dict(e) for e in etiquetas]
    for e in etiquetas:
        e["created_at_formatted"] = format_datetime(e["created_at"])

    movements = [dict(mv) for mv in movements]
    for mv in movements:
        mv["created_at_formatted"] = format_datetime(mv["created_at"])

    return render_template("history.html", model=model, history=hist, etiquetas=etiquetas, movements=movements)

@app.route("/etiqueta/<string:code>")
def etiqueta(code):
    conn = get_db()

    if "-" in code:
        base_code = code.split("-")[0]
        lote_sufixo = "-".join(code.split("-")[1:])
        # formato original (ex: "08-504" → "08 / 504")
        lote_sufixo = lote_sufixo.replace("-", " / ")
    else:
        base_code = code
        lote_sufixo = None

    model_row = conn.execute("SELECT * FROM models WHERE code=?", (base_code,)).fetchone()
    conn.close()

    if not model_row:
        return f"<h3>❌ Etiqueta não encontrada para código '{base_code}'.</h3>", 404

    model = dict(model_row)

    if lote_sufixo:
        model["lote"] = lote_sufixo

    def format_updated_at(value):
        if not value:
            return ""
        try:
            s = str(value).replace("T", " ")
            s_short = s.split(".")[0].split("+")[0].split("Z")[0].strip()
            dt = datetime.strptime(s_short, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d/%m/%Y às %H:%M:%S")
        except Exception:
            try:
                dt2 = datetime.fromisoformat(str(value))
                return dt2.strftime("%d/%m/%Y às %H:%M:%S")
            except Exception:
                return str(value)

    model["updated_at_formatted"] = format_updated_at(model.get("updated_at"))

    return render_template("etiqueta_view.html", m=model)

@app.route("/labels/<int:model_id>")
def label_history(model_id):
    conn = get_db()
    model = conn.execute("SELECT * FROM models WHERE id=?", (model_id,)).fetchone()
    etiquetas = conn.execute(
        "SELECT * FROM labels WHERE model_id=? ORDER BY created_at DESC", (model_id,)
    ).fetchall()
    conn.close()
    if not model:
        abort(404)
    return render_template("labels_history.html", model=model, etiquetas=etiquetas)

@app.route("/delete_label/<int:id>", methods=["DELETE"])
def delete_label(id):
    conn = get_db()
    conn.execute("DELETE FROM labels WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return "", 204

@app.route("/print_label/<int:model_id>/<lote>")
def print_label(model_id, lote):
    conn = get_db()
    model = conn.execute("SELECT * FROM models WHERE id=?", (model_id,)).fetchone()
    conn.close()
    if not model:
        abort(404)

    # Limpa o formato do lote, caso venha com "-"
    lote = lote.replace('-', ' / ')
    
    return render_template("label.html", model=model, lotes=[lote])

@app.route("/etiqueta_visualizar/<string:code>/<string:lote>")
def etiqueta_visualizar(code, lote):
    conn = get_db()
    model_row = conn.execute("SELECT * FROM models WHERE code=?", (code,)).fetchone()
    conn.close()

    if not model_row:
        return "<h3>Etiqueta não encontrada.</h3>", 404

    model = dict(model_row)
    lote_formatado = lote.replace("-", " / ")

    return render_template("label.html", m=model, lotes=[lote_formatado])

@app.get("/api/atualizado")
def api_atualizado():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT MAX(id) FROM movements")
    mov = cur.fetchone()[0] or 0

    cur.execute("SELECT MAX(id) FROM history")
    his = cur.fetchone()[0] or 0

    conn.close()
    return {"ultimo": max(mov, his)}

@app.route("/api/ops_atualizado")
def ops_atualizado():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT MAX(id) FROM movements")
    ultimo = c.fetchone()[0] or 0

    conn.close()
    return jsonify({"ultimo": ultimo})

@app.get("/api/tabela_models")
def tabela_models():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, linha, setor, code, model_name, cliente, updated_at
        FROM models
        ORDER BY id DESC
    """)
    rows = cur.fetchall()

    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "linha": r["linha"],
            "setor": r["setor"],
            "code": r["code"],
            "model_name": r["model_name"],
            "cliente": r["cliente"],
            "updated_at_formatted": (
                datetime.fromisoformat(r["updated_at"]).strftime("%d/%m/%Y %H:%M:%S")
                if r["updated_at"] else "-"
            )
        })

    conn.close()
    return jsonify({"models": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
