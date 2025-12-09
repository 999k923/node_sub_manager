from flask import Flask, Response, render_template, request, redirect, url_for, flash, abort
from models import db, Node
import base64
import os
import re
from update_node_name import update_nodes  # 安全导入，无循环依赖
import string
import random
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nodes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "secret_key_for_flash"  # 防止 Flask flash 报错
db.init_app(app)

# 初始化数据库
with app.app_context():
    if not os.path.exists("nodes.db"):
        db.create_all()

# ---------------------------
# Token 生成/读取
# ---------------------------
TOKEN_FILE = "access_token.txt"

def generate_token(length=20):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    else:
        token = generate_token()
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        return token

# ---------------------------
# Web 后台用户名密码
# ---------------------------
WEB_USER = "mimayoudianfuza" # 手动填写用户名
WEB_PASS = "zhendehenfuza"  # 手动填写密码

def check_auth(username, password):
    return username == WEB_USER and password == WEB_PASS

def authenticate():
    return Response(
        '认证失败，请输入正确用户名和密码', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# ---------------------------
# Web管理后台
# ---------------------------
@app.route("/")
@requires_auth
def index():
    nodes = Node.query.all()
    token = get_token()  # 可选：在网页显示 token
    return render_template("index.html", nodes=nodes, token=token)


@app.route("/add", methods=["POST"])
@requires_auth
def add_node():
    name = request.form.get("name", "").strip()
    link = request.form.get("link", "").strip()
    link = re.sub(r"#.*$", "", link)  # 去掉 link 自带的备注

    if name and link:
        node = Node(name=name, link=link)
        try:
            db.session.add(node)
            db.session.commit()
            try:
                update_nodes()
            except Exception as e:
                print(f"update_nodes 出错: {e}")
        except Exception as e:
            db.session.rollback()
            flash(f"添加节点失败: {e}", "danger")
    else:
        flash("节点名称或链接不能为空", "warning")

    return redirect(url_for("index"))


@app.route("/delete/<int:node_id>")
@requires_auth
def delete_node(node_id):
    node = Node.query.get(node_id)
    if node:
        try:
            db.session.delete(node)
            db.session.commit()
            try:
                update_nodes()
            except Exception as e:
                print(f"update_nodes 出错: {e}")
        except Exception as e:
            db.session.rollback()
            flash(f"删除节点失败: {e}", "danger")
    else:
        flash("节点不存在", "warning")
    return redirect(url_for("index"))


@app.route("/toggle/<int:node_id>")
@requires_auth
def toggle_node(node_id):
    node = Node.query.get(node_id)
    if node:
        try:
            node.enabled = not node.enabled
            db.session.commit()
            try:
                update_nodes()
            except Exception as e:
                print(f"update_nodes 出错: {e}")
        except Exception as e:
            db.session.rollback()
            flash(f"切换节点状态失败: {e}", "danger")
    else:
        flash("节点不存在", "warning")
    return redirect(url_for("index"))


@app.route("/edit/<int:node_id>", methods=["POST"])
@requires_auth
def edit_node(node_id):
    node = Node.query.get(node_id)
    if node:
        name = request.form.get("name", "").strip()
        link = request.form.get("link", "").strip()
        if name:
            node.name = name
        if link:
            node.link = re.sub(r"#.*$", "", link)
        try:
            db.session.commit()
            try:
                update_nodes()
            except Exception as e:
                print(f"update_nodes 出错: {e}")
        except Exception as e:
            db.session.rollback()
            flash(f"编辑节点失败: {e}", "danger")
    else:
        flash("节点不存在", "warning")
    return redirect(url_for("index"))


# ---------------------------
# 动态订阅生成
# ---------------------------
@app.route("/sub")
def sub():
    token = request.args.get("token", "")
    if token != get_token():
        abort(403, description="访问订阅需要正确的 token")

    nodes = Node.query.filter_by(enabled=True).all()
    out_links = []

    for n in nodes:
        link = n.link.strip()

        # VMESS
        if link.startswith("vmess://"):
            import json
            try:
                raw = link[8:]
                decoded = base64.b64decode(raw + "==").decode()
                j = json.loads(decoded)
                j["ps"] = n.name
                new_raw = base64.b64encode(json.dumps(j).encode()).decode()
                out_links.append("vmess://" + new_raw)
            except Exception as e:
                out_links.append(link)
            continue

        # VLESS
        elif link.startswith("vless://"):
            clean = re.sub(r"#.*$", "", link)
            out_links.append(f"{clean}#{n.name}")
            continue

        # 其它协议
        else:
            clean = re.sub(r"#.*$", "", link)
            out_links.append(f"{clean}#{n.name}")

    sub_content = "\n".join(out_links)
    sub_b64 = base64.b64encode(sub_content.encode()).decode()
    return Response(sub_b64, mimetype="text/plain")


if __name__ == "__main__":
    print(f"访问订阅链接时需要使用 token: {get_token()}")
    app.run(host="0.0.0.0", port=5786, debug=True)
