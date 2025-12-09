from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)  # 备注
    link = db.Column(db.String(1024), nullable=False) # 完整节点链接
    enabled = db.Column(db.Boolean, default=True)
