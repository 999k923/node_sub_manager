# db_init.py
import os
from models import db
from app import app

DB_FILE = "instance/nodes.db"

def init_database():
    db_path = os.path.join(app.root_path, DB_FILE)

    # 如果数据库已经存在，不再初始化
    if os.path.exists(db_path):
        print("数据库已存在，跳过初始化。")
        return

    # 确保 instance 目录存在
    instance_dir = os.path.join(app.root_path, "instance")
    os.makedirs(instance_dir, exist_ok=True)

    print("数据库不存在，开始创建...")

    with app.app_context():
        db.create_all()
        print("数据库初始化完成！")


if __name__ == "__main__":
    init_database()
