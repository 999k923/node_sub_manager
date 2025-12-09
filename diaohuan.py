from sqlalchemy import create_engine, MetaData, Table, select, update
from sqlalchemy.orm import sessionmaker

DB_PATH = "sqlite:///nodes.db"
engine = create_engine(DB_PATH, echo=False)
metadata = MetaData()

# 反射 node 表
node_table = Table('node', metadata, autoload_with=engine)
Session = sessionmaker(bind=engine)

def swap_nodes(id1: int, id2: int):
    """
    交换两个节点的内容，ID 不变
    """
    session = Session()

    # 读取节点内容
    row1 = session.execute(select(node_table).where(node_table.c.id == id1)).first()
    row2 = session.execute(select(node_table).where(node_table.c.id == id2)).first()

    if not row1 or not row2:
        print(f"❌ 节点 {id1} 或 {id2} 不存在")
        session.close()
        return

    # 临时保存 row1 的内容
    temp = dict(row1._mapping)

    # 把 row2 的内容写入 row1
    session.execute(
        update(node_table)
        .where(node_table.c.id == id1)
        .values(name=row2.name, link=row2.link, enabled=row2.enabled)
    )

    # 把 row1（临时保存）的内容写入 row2
    session.execute(
        update(node_table)
        .where(node_table.c.id == id2)
        .values(name=temp['name'], link=temp['link'], enabled=temp['enabled'])
    )

    session.commit()
    session.close()
    print(f"✅ 节点 {id1} 和 {id2} 内容互换完成，ID 不变")

# -----------------------------
# 调用示例：把 10 和 9 互换
swap_nodes(10, 9)
