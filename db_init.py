from app import app
from models import db

with app.app_context():
    db.create_all()
    print("数据库初始化完成")
