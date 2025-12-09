from sqlalchemy import create_engine, MetaData, Table, select, update
from sqlalchemy.orm import sessionmaker

DB_PATH = "sqlite:///nodes.db"  # SQLite URL 形式

# 创建数据库引擎
engine = create_engine(DB_PATH, echo=False)
metadata = MetaData()

# 反射表结构
node_table = Table('node', metadata, autoload_with=engine)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

# 获取所有节点，按 id 排序
nodes = session.execute(select(node_table.c.id)).scalars().all()
print("原 ID 列表:", nodes)

# 重新生成连续 ID
for new_id, old_id in enumerate(nodes, start=1):
    stmt = update(node_table).where(node_table.c.id == old_id).values(id=new_id)
    session.execute(stmt)

session.commit()
session.close()
print("✅ ID 已重新顺延完成！")
