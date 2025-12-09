from sqlalchemy import create_engine, MetaData, Table, select, update
from sqlalchemy.orm import sessionmaker

DB_PATH = "sqlite:///nodes.db"
engine = create_engine(DB_PATH, echo=False)
metadata = MetaData()

node_table = Table('node', metadata, autoload_with=engine)
Session = sessionmaker(bind=engine)
session = Session()

# -----------------------------
# 参数：要插入的节点ID 和 插入位置
insert_id = 10  # 原节点 ID
target_pos = 7  # 插入到目标位置 ID
# -----------------------------

# 获取所有节点按 ID 排序
nodes = session.execute(select(node_table.c.id).order_by(node_table.c.id)).scalars().all()
print("原 ID 列表:", nodes)

if insert_id not in nodes:
    print(f"❌ 节点 {insert_id} 不存在")
else:
    # 先把所有 ID 临时偏移 1000，避免冲突
    for nid in nodes:
        session.execute(update(node_table).where(node_table.c.id == nid).values(id=nid + 1000))
    session.commit()

    # 更新列表 ID 对应
    nodes = [nid + 1000 for nid in nodes]

    # 找出插入节点临时 ID
    insert_temp_id = insert_id + 1000
    nodes.remove(insert_temp_id)
    nodes.insert(target_pos - 1, insert_temp_id)

    # 重新生成连续 ID，从 1 开始
    for new_id, old_id in enumerate(nodes, start=1):
        session.execute(update(node_table).where(node_table.c.id == old_id).values(id=new_id))

    session.commit()
    print("✅ 节点已按插入顺序重新排序，ID 连续")

session.close()
