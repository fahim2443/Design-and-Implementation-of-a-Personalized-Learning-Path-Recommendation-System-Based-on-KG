import psycopg
DSN = "postgresql://thesis:thesis12345@localhost:5432/learning"

def init():
    try:
        with psycopg.connect(DSN) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY, ts TIMESTAMPTZ DEFAULT now(),
                session TEXT, kind TEXT, target TEXT, edge_set TEXT, item TEXT, value TEXT)""")
    except Exception as e:
        print("db init failed:", e)

def log(session, kind, target="", edge_set="", item="", value=""):
    try:
        with psycopg.connect(DSN) as c:
            c.execute("INSERT INTO events (session,kind,target,edge_set,item,value) "
                      "VALUES (%s,%s,%s,%s,%s,%s)",
                      (session, kind, target, edge_set, item, str(value)))
    except Exception as e:
        print("db log failed:", e)
