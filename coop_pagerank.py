import networkx
import sqlite3
import pandas as pd

db = sqlite3.connect("coop.db")
db.row_factory = sqlite3.Row
cur = db.cursor()

g = networkx.DiGraph()
cur.execute("SELECT * FROM target")
for row in cur.fetchall():
	g.add_node(row["idx"], url=row["url"])

cur.execute("SELECT * FROM di")
for row in cur.fetchall():
	g.add_edge(row["src"], row["dst"])

pr = networkx.pagerank(g, alpha=0.9)

cur.execute("SELECT * FROM target ORDER BY idx")
ul=[w["url"] for w in cur.fetchall()]
u=pd.Series(ul, range(1,len(ul)+1))
w=(pd.concat([d, u], axis=1))
w2=w.sort_values(by=0, ascending=False)
#print(pr)

