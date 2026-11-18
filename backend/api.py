import uuid
import networkx as nx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from path_engine import load_graph, plan, linear_baseline
from quiz import caches, pick_question, update

app = FastAPI(title="Learning Path API")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

G_STRONG = load_graph("strong")
G_ALL = load_graph("all")
SESSIONS = {}   # quiz sessions kept in memory (fine for a thesis demo)

def info(G, n):
    d = G.nodes[n]
    return {"name": n, "type": d["type"], "difficulty": d["diff"], "minutes": d["minutes"]}

def pick_graph(edge_set):
    return G_ALL if edge_set == "all" else G_STRONG

@app.get("/topics")
def topics():
    ts = [n for n in G_STRONG if G_STRONG.nodes[n]["type"] == "Topic"
          and G_STRONG.nodes[n]["order"][0] != 99]
    ts.sort(key=lambda n: G_STRONG.nodes[n]["order"])
    return [info(G_STRONG, n) for n in ts]

@app.get("/graph")
def graph(edge_set: str = "strong", types: str = "Topic,Concept"):
    G = pick_graph(edge_set); keep = set(types.split(","))
    nodes = [info(G, n) for n in G if G.nodes[n]["type"] in keep]
    names = {x["name"] for x in nodes}
    H = nx.transitive_reduction(G.subgraph(names))      # clean drawing, same reachability
    return {"nodes": nodes, "edges": [{"source": a, "target": b} for a, b in H.edges]}

class PathReq(BaseModel):
    target: str
    mastered: list[str] = []
    edge_set: str = "strong"

@app.post("/path")
def path(req: PathReq):
    G = pick_graph(req.edge_set)
    if req.target not in G:
        raise HTTPException(404, "unknown target")
    m = set(req.mastered)
    p = plan(G, req.target, m)
    base = linear_baseline(G, req.target, m)
    return {"path": [info(G, n) for n in p],
            "minutes": sum(G.nodes[n]["minutes"] for n in p),
            "slide_order_items": len(base),
            "slide_order_minutes": sum(G.nodes[n]["minutes"] for n in base)}

class QuizStart(BaseModel):
    target: str
    budget: int = 8

@app.post("/quiz/start")
def quiz_start(req: QuizStart):
    if req.target not in G_STRONG:
        raise HTTPException(404, "unknown target")
    scope = nx.ancestors(G_STRONG, req.target) | {req.target}
    anc, desc = caches(G_STRONG, scope)
    sid = str(uuid.uuid4())
    SESSIONS[sid] = dict(target=req.target, scope=scope, anc=anc, desc=desc,
                         known=set(), unknown=set(), left=req.budget, last=None)
    return quiz_next(sid)

class QuizAnswer(BaseModel):
    session: str
    correct: bool

@app.post("/quiz/answer")
def quiz_answer(req: QuizAnswer):
    s = SESSIONS.get(req.session)
    if not s:
        raise HTTPException(404, "unknown session")
    if s["last"] is not None:
        update(s["last"], req.correct, s["scope"], s["known"], s["unknown"], s["anc"], s["desc"])
    return quiz_next(req.session)

def quiz_next(sid):
    import random
    s = SESSIONS[sid]
    q = None
    if s["left"] > 0:
        q = pick_question(s["scope"], s["known"], s["unknown"], s["anc"], s["desc"],
                          "graph", random.Random())
    s["last"] = q
    if q is None:
        mastered = sorted(s["known"] - {s["target"]})
        return {"session": sid, "done": True, "mastered": mastered,
                "path": path(PathReq(target=s["target"], mastered=mastered))}
    s["left"] -= 1
    return {"session": sid, "done": False, "question": info(G_STRONG, q),
            "questions_left": s["left"]}
