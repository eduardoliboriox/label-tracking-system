#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
from datetime import datetime
import sqlite3, os, qrcode
from io import BytesIO
import socket

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

    # ➕ Nova coluna fase
    if "fase" not in columns:
        c.execute("ALTER TABLE models ADD COLUMN fase TEXT;")

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
                created_at TEXT,
                created_by TEXT
            )
        ''')
        conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

with app.app_context():
    init_db()
    add_missing_column()
    add_missing_table_labels()
    add_missing_table_movements()

# ---------------- Regras de Ponto / Roteiro ----------------
# Definimos um mapeamento básico dos pontos para setores.
# Observação: a lógica pode ser expandida conforme regras do seu roteiro.
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
    # substitui hífens por ' / ' em duas primeiras partes, se tiver apenas uma parte retorna como está
    parts = lote_sufixo.split("-")
    if len(parts) == 1:
        return parts[0].replace('-', ' / ').strip()
    # junta primeira e segunda como 'NN / PPP' e ignora extras (ou junta com ' - ')
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

def register_movement(conn, model_id, label_id, ponto, acao, quantidade, from_setor, to_setor, created_by="terminal_movimentacao"):
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO movements (model_id, label_id, ponto, acao, quantidade, from_setor, to_setor, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (model_id, label_id, ponto, acao, quantidade, from_setor, to_setor, now, created_by)
    )

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
                (code, model_name, cliente, linha, setor, fase, turno, data, lote, quantidade, revisora, horario, po, op, status_cq, processo, obs, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    f.get("code", ""),
                    f.get("model_name", ""),
                    f.get("cliente", ""),
                    f.get("linha", ""),
                    f.get("setor", ""),
                    f.get("fase", ""),  # 👈 agora na posição correta
                    f.get("turno", ""),
                    f.get("data") or datetime.now().strftime("%d/%m/%Y"),
                    f"{f.get('lote_num', '').strip()} / {f.get('lote_padrao', '').strip()}",
                    f.get("quantidade", ""),
                    f.get("revisora", ""),
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
        except sqlite3.IntegrityError:
            flash("Erro: código já existe.", "danger")
        finally:
            conn.close()
        return redirect(url_for("index"))
    return render_template("form.html", model=None)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()
    model = conn.execute("SELECT * FROM models WHERE id=?", (id,)).fetchone()
    if not model:
        abort(404)

    if request.method == "POST":
        f = request.form
        conn.execute("""
            UPDATE models 
            SET code=?, model_name=?, cliente=?, linha=?, setor=?, fase=?, turno=?, data=?, lote=?, quantidade=?, 
                revisora=?, horario=?, po=?, op=?, status_cq=?, processo=?, obs=?, updated_at=? 
            WHERE id=?
        """, (
            f["code"], f["model_name"], f["cliente"], f["linha"],
            f.get("setor", ""), f.get("fase", ""),  # 👈 agora correto
            f["turno"], f["data"],
            f"{f.get('lote_num', '').strip()} / {f.get('lote_padrao', '').strip()}",
            f["quantidade"], f["revisora"], f["horario"],
            f["po"], f.get("op", ""),
            ",".join(request.form.getlist("status_cq")),
            ",".join(request.form.getlist("processo")),
            f["obs"], datetime.now().isoformat(), id
        ))

        conn.execute(
            "INSERT INTO history (model_id, changed_at, changed_by, change_text) VALUES (?, ?, ?, ?)",
            (id, datetime.now().isoformat(), "web_user", "Edição de modelo")
        )
        conn.commit()
        conn.close()
        flash("Modelo atualizado!", "success")
        return redirect(url_for("index"))

    conn.close()
    return render_template("form.html", model=model)


@app.route("/view/<int:id>", methods=["GET", "POST"])
def view_label(id):
    conn = get_db()
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
            capacidade_magazine = int(request.form.get("capacidade_magazine", 1))
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
            for lote in lotes:
                conn.execute("""
                    INSERT INTO labels 
                        (model_id, lote, producao_total, capacidade_magazine, remaining, created_at, linked_label_id, setor_atual, fase)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id,
                    lote,
                    producao_total,
                    capacidade_magazine,
                    capacidade_magazine,
                    datetime.now().isoformat(),
                    linked_label_id,
                    model["setor"] if model["setor"] else "PTH",
                    "AGUARDANDO"
                ))
            conn.commit()
            conn.close()

            flash(f"Produção: {producao_total} placas → {total_etiquetas} etiquetas → {total_folhas} folhas. Etiquetas salvas no histórico.", "info")

        except ValueError:
            flash("⚠️ Digite valores válidos para produção e capacidade.", "danger")

    return render_template("label.html", m=model, lotes=lotes, existing_labels=existing_labels)

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

    # 🔹 Gera a URL completa (agora compatível com códigos únicos)
    # OBS: os terminais/físicos onde o QR será lido podem adicionar o parâmetro ?p=Ponto-01
    qr_url = f"http://{local_ip}:5000/movimentar/{code.strip()}"

    # 🔹 Gera e retorna o QR Code
    img = qrcode.make(qr_url)
    buf = BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/movimentar", methods=["GET", "POST"])
@app.route("/movimentar/<string:full_code>", methods=["GET", "POST"])
def movimentar(full_code=None):
    ponto_query = request.args.get("ponto") or request.args.get("p") or None
    model = label = None
    lote_sufixo = None

    # --- Se veio full_code pela URL ou foi digitado no POST ---
    if request.method == "POST":
        full_code = full_code or request.form.get("qr_code")

    if full_code:
        parts = full_code.split("-")
        base_code = parts[0].strip().upper()
        lote_sufixo = "-".join(parts[1:]) if len(parts) > 1 else None
        lote_formatado = normalize_lote_from_qr(lote_sufixo) if lote_sufixo else None

        conn = get_db()
        model_row = conn.execute("SELECT * FROM models WHERE UPPER(code)=?", (base_code,)).fetchone()
        if not model_row:
            conn.close()
            flash(f"Código '{full_code}' não encontrado.", "danger")
            return redirect(url_for("index"))
        model = dict(model_row)

        label = find_label(conn, model["id"], lote_formatado) if lote_formatado else None
        if not label:
            cur = conn.execute(
                "SELECT * FROM labels WHERE model_id=? ORDER BY created_at DESC LIMIT 1",
                (model["id"],),
            ).fetchone()
            if cur:
                label = dict(cur)
        conn.close()

    # --- Se for envio do formulário ---
    if request.method == "POST" and model:
        acao = request.form.get("acao")  # PRODUCAO ou RECEBIMENTO
        ponto = request.form.get("ponto") or ponto_query or "Ponto-?"
        quantidade = int(request.form.get("quantidade") or (label["capacidade_magazine"] if label else 0))

        ponto_rule = POINT_RULES.get(ponto)
        setor_origem = (label.get("setor_atual") if label else model.get("setor")) or None
        setor_destino = setor_origem  # padrão

        # --- Lógica de destino baseada em regras ---
        if acao == "PRODUCAO":
            if ponto == "Ponto-07":
                setor_destino = "EXPEDICAO"
            elif ponto_rule and ponto_rule["type"] == "qualidade":
                setor_destino = setor_origem  # marca como pronto, mas não muda setor
            elif ponto_rule:
                setor_destino = ponto_rule["setor"]
        elif acao == "RECEBIMENTO":
            if ponto_rule:
                setor_destino = ponto_rule["setor"]

        # --- Normaliza IM/PA ---
        if setor_destino == "IM/PA":
            if model.get("setor") in ["IM", "PA"]:
                setor_destino = model.get("setor")
            else:
                setor_destino = "IM"

        try:
            conn = get_db()

            # Se tivermos uma label (origem), usamos ela como fonte de peças.
            # Caso contrário (nenhuma label encontrada), tratamos como movimentação sobre o modelo inteiro.
            if label:
                # garante que a coluna remaining exista e seja int
                remaining = int(label.get("remaining") if label.get("remaining") is not None else (label.get("capacidade_magazine") or 0))
                transfer = int(quantidade)

                if transfer <= 0:
                    flash("Quantidade inválida.", "danger")
                    conn.close()
                    return redirect(url_for("index"))

                if transfer > remaining:
                    flash(f"Quantidade solicitada ({transfer}) maior que o disponível na etiqueta ({remaining}).", "danger")
                    conn.close()
                    return redirect(url_for("index"))

                # decrementa remaining da etiqueta origem
                new_remaining = remaining - transfer
                conn.execute(
                    "UPDATE labels SET remaining=?, updated_at=? WHERE id=?",
                    (new_remaining, datetime.now().isoformat(), label["id"])
                )

                # se precisar, marca etiqueta origem como vazia quando remaining == 0 (opcional)
                if new_remaining == 0:
                    # opcional: mantém setor_atual como estava, ou marca como 'CONSUMIDO'
                    # aqui vamos deixar setor_atual inalterado, mas pode-se adicionar um flag se desejar
                    pass

                # cria nova etiqueta no setor destino representando a quantidade transferida
                conn.execute("""
                    INSERT INTO labels (model_id, lote, producao_total, capacidade_magazine, remaining, created_at, linked_label_id, setor_atual, fase)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    model["id"],
                    label["lote"],
                    transfer,            # producao_total desta "sub-etiqueta"
                    transfer,            # capacidade_magazine = transfer (agora este lote tem tamanho transfer)
                    transfer,            # remaining = transfer
                    datetime.now().isoformat(),
                    label["id"],         # linked_label_id referencia origem
                    setor_destino,
                    "DISPONIVEL" if acao == "PRODUCAO" else (label.get("fase") or "AGUARDANDO")
                ))

                # pega o id da nova etiqueta inserida para histórico/moviment
                new_label_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            else:
                # Não havia label encontrada: cria uma nova etiqueta diretamente no setor destino
                transfer = int(quantidade)
                if transfer <= 0:
                    flash("Quantidade inválida.", "danger")
                    conn.close()
                    return redirect(url_for("index"))

                conn.execute("""
                    INSERT INTO labels (model_id, lote, producao_total, capacidade_magazine, remaining, created_at, linked_label_id, setor_atual, fase)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    model["id"],
                    model.get("lote"),
                    transfer,
                    transfer,
                    transfer,
                    datetime.now().isoformat(),
                    None,
                    setor_destino,
                    "DISPONIVEL" if acao == "PRODUCAO" else "AGUARDANDO"
                ))

                new_label_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                label_id = new_label_id  # para histórico

            # histórico
            conn.execute(
                "INSERT INTO history (model_id, changed_at, changed_by, change_text) VALUES (?, ?, ?, ?)",
                (
                    model["id"],
                    datetime.now().isoformat(),
                    "terminal_movimentacao",
                    f"{acao} em {ponto} (origem: {setor_origem} → destino: {setor_destino}) - qtd: {transfer}"
                ),
            )

            # movimentação (registra a quantidade transferida)
            register_movement(
                conn,
                model["id"],
                new_label_id if 'new_label_id' in locals() else label_id,
                ponto,
                acao,
                transfer,
                setor_origem,
                setor_destino,
                created_by="terminal_movimentacao",
            )

            conn.commit()
            flash(f"✅ {acao} registrada no {ponto} ({setor_origem} → {setor_destino}) - {transfer} un.", "success")


        except Exception as e:
            conn.rollback()
            flash(f"Erro ao registrar movimentação: {e}", "danger")
        finally:
            conn.close()

        return redirect(url_for("index"))

    # --- Renderiza a tela ---
    return render_template(
        "movimentar.html",
        model=model,
        lote_sufixo=lote_sufixo,
        label=label,
        ponto=ponto_query,
        full_code=full_code,
        header_title=ponto_query
    )

@app.route("/dashboard")
def dashboard():
    conn = get_db()
    # Lista de todos os modelos
    models = conn.execute("SELECT * FROM models ORDER BY model_name").fetchall()
    models = [dict(m) for m in models]

    # Para cada modelo, consulta saldo por setor + fase
    dashboard_data = []
    for m in models:
        labels = conn.execute("""
            SELECT setor_atual, fase, SUM(remaining) AS saldo
            FROM labels
            WHERE model_id=?
            GROUP BY setor_atual, fase
        """, (m["id"],)).fetchall()

        saldo_setores = []
        for l in labels:
            setor = l["setor_atual"] or "SEM SETOR"
            fase = (l["fase"] or "").strip().upper()
            saldo = int(l["saldo"] or 0)

            # Regra simples de status:
            # - Se fase == 'AGUARDANDO' -> AGUARDANDO
            # - Else se saldo > 0 -> DISPONIVEL
            # - Else -> AGUARDANDO
            if fase == "AGUARDANDO" or fase == "":
                status = "AGUARDANDO"
            else:
                status = "DISPONIVEL" if saldo > 0 else "AGUARDANDO"

            saldo_setores.append({
                "setor": setor,
                "fase": fase if fase else "",
                "saldo": saldo,
                "status": status
            })

        dashboard_data.append({
            "model": m,
            "saldo_setores": saldo_setores
        })
    conn.close()
    return render_template("dashboard.html", data=dashboard_data)


@app.route("/history/<int:id>")
def history(id):
    conn = get_db()
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

    # 🔹 Aplica a formatação
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

    # 🔹 Se o código tiver parte de lote, separamos
    if "-" in code:
        base_code = code.split("-")[0]
        lote_sufixo = "-".join(code.split("-")[1:])
        # Reconstrói o formato original (ex: "08-504" → "08 / 504")
        lote_sufixo = lote_sufixo.replace("-", " / ")
    else:
        base_code = code
        lote_sufixo = None

    model_row = conn.execute("SELECT * FROM models WHERE code=?", (base_code,)).fetchone()
    conn.close()

    if not model_row:
        return f"<h3>❌ Etiqueta não encontrada para código '{base_code}'.</h3>", 404

    # Converte row para dict mutável
    model = dict(model_row)

    # 🔹 Substitui o lote apenas visualmente, sem alterar o banco
    if lote_sufixo:
        model["lote"] = lote_sufixo

    # 🔹 Formata o campo de atualização
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
    
    # Renderiza o mesmo template usado para etiquetas
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
