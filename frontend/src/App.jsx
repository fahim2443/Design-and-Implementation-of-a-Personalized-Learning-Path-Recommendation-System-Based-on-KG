import { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";
import "./App.css";

const API = "http://localhost:8000";
const post = (url, body) =>
  fetch(API + url, { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body) }).then((r) => r.json());

export default function App() {
  const [topics, setTopics] = useState([]);
  const [target, setTarget] = useState("");
  const [budget, setBudget] = useState(8);
  const [quiz, setQuiz] = useState(null);
  const [result, setResult] = useState(null);
  const [graph, setGraph] = useState(null);

  useEffect(() => {
    fetch(API + "/topics").then((r) => r.json()).then((t) => {
      setTopics(t); if (t.length) setTarget(t[t.length - 1].name);
    });
    fetch(API + "/graph?edge_set=strong&types=Topic,Concept").then((r) => r.json()).then(setGraph);
  }, []);

  const handle = (q) => { if (q.done) { setQuiz(null); setResult(q); } else setQuiz(q); };
  const start = async () => {
    setResult(null);
    handle(await post("/quiz/start", { target, budget: Number(budget) }));
  };
  const answer = async (correct) =>
    handle(await post("/quiz/answer", { session: quiz.session, correct }));
  const skipQuiz = async () => {
    setQuiz(null);
    setResult({ mastered: [], path: await post("/path", { target, mastered: [], edge_set: "strong" }) });
  };

  const pathNames = new Set(result ? result.path.path.map((p) => p.name) : []);
  const option = graph && {
    tooltip: {},
    series: [{
      type: "graph", layout: "force", roam: true, draggable: true,
      force: { repulsion: 60, edgeLength: 40 },
      label: { show: true, fontSize: 9 },
      edgeSymbol: ["none", "arrow"], edgeSymbolSize: 6,
      lineStyle: { opacity: 0.4, curveness: 0.1 },
      data: graph.nodes.map((n) => ({
        name: n.name, symbolSize: n.name === target ? 22 : 12,
        itemStyle: { color: n.name === target ? "#d62728" : pathNames.has(n.name) ? "#2ca02c" : "#9aa5b1" },
      })),
      links: graph.edges,
    }],
  };

  return (
    <div className="page">
      <h1>Personalized Learning Path: Cloud Computing</h1>
      <div className="row">
        <label>Target topic:&nbsp;
          <select value={target} onChange={(e) => setTarget(e.target.value)}>
            {topics.map((t) => <option key={t.name}>{t.name}</option>)}
          </select>
        </label>
        <label>Quiz questions:&nbsp;
          <input type="number" min="0" max="20" value={budget} style={{ width: 60 }}
            onChange={(e) => setBudget(e.target.value)} />
        </label>
        <button onClick={start}>Start quiz</button>
        <button onClick={skipQuiz}>Skip quiz (I know nothing)</button>
      </div>

      {quiz && (
        <div className="card">
          <b>Do you know this?</b>
          <h2>{quiz.question.name}</h2>
          <small>{quiz.question.type} · {quiz.questions_left} questions left after this</small>
          <div className="row">
            <button onClick={() => answer(true)}>I know it</button>
            <button onClick={() => answer(false)}>I don't know it</button>
          </div>
        </div>
      )}

      {result && (
        <div className="card">
          <h2>Your path</h2>
          <p>
            <b>{result.path.path.length}</b> items, about <b>{result.path.minutes}</b> min
            &nbsp;vs slide order: <b>{result.path.slide_order_items}</b> items,
            about <b>{result.path.slide_order_minutes}</b> min
          </p>
          <ol>{result.path.path.map((p) => (
            <li key={p.name}>{p.name} <small>({p.type}, difficulty {p.difficulty}, {p.minutes} min)</small></li>
          ))}</ol>
          {result.mastered.length > 0 && <p><small>Marked as known: {result.mastered.join(", ")}</small></p>}
        </div>
      )}

      <h2>Course topic map</h2>
      <p><small>Red = target, green = your path, grey = other topics. Drag and zoom.</small></p>
      {option && <ReactECharts option={option} style={{ height: 700 }} />}
    </div>
  );
}
