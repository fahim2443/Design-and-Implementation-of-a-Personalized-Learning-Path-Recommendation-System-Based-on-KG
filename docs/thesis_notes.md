# Thesis notes (running log)

## Decisions
- 2026-11-18: Teacher provided the cloud computing KG (prerequisite_graph.json, triples). I focus on the recommendation design. Title: Personalized Learning Path Recommendation System Based on Knowledge Graphs.
- Stack: Neo4j + PostgreSQL (Docker), Python path engine, FastAPI + React later.

## Data facts (for chapter 3)
- KG: 165 nodes (41 Topic, 71 Concept, 53 ExtendedConcept), 703 edges, DAG = True.
- Transitive reduction: 703 -> 213 edges.
- Edges were auto-generated from slide order, not expert-checked (limitation).
- Strong edges = introduces / extends / contains family; weak = related / course_order.

## Assumptions (must state in thesis)
- Difficulty and minutes are estimated from node type + chapter (no real data).
- Vendor/company nodes (category: 商用平台, 企业, 标准组织) are not study items.

## Results so far
| Target | Slide order | Graph (all) | Graph (strong) |
|---|---|---|---|
| Hadoop architecture | 65 | 46 | 25 |
| Task scheduling | 91 | 54 | 28 |
| OpenStack architecture | 115 | 56 | 35 |

## Problems found and fixes (good for the "implementation" chapter)
- Sorting put detail terms before topics -> sort by chapter, section, type, difficulty.
- Company nodes appeared as prerequisites -> filtered by category.

- Figures saved in docs/figures: path comparison bar chart, Spark raw prerequisites table, Neo4j graph, environment screenshots.
- Finding: the raw teacher graph gives 61 ancestors for Spark architecture, so filtering is required.

- Raw ancestors with all arrows: Hadoop 51, task scheduling 59, OpenStack 61, Spark 61.
- Simulator v1 (500 students, 1 try per item): strong-edge graph path saves 55-76% time, 60-75% fewer fails vs slide order. Reached-target ~equal (~46-53%) but too low for both: no retries in v1.
- Ablation: strong edges beat all edges (e.g. 763 vs 1232 min for task scheduling).
- Simulator assumptions: p_ok=0.9, p_missing=0.35, re-study penalty 50%. Need sensitivity test later.

- Simulator v2 (3 attempts per item): reached target 81-95% for both methods, no meaningful difference. Graph path (strong edges) saves 52-75% time and 40-70% fails.
- Ablation: strong edges better than all edges.
- Limits: model assumes prerequisites matter; minutes estimated; random students.
- TODO: sensitivity test (vary p_ok, p_missing, retries), real classmate pilot.

## Still to do
- Simulator + experiment, student quiz, API, frontend, hand-verify Topic edges.
## Simulator v2 results (500 fake students, 3 attempts per item, strong edges)
| Target | Slide order min | Graph path min | Time saved | Fails (slide -> graph) | Reached target (slide -> graph) |
|---|---|---|---|---|---|
| Hadoop architecture | 1418 | 674 | 52% | 11.6 -> 6.0 | 85.2% -> 84.6% |
| Task scheduling | 2403 | 792 | 67% | 16.7 -> 6.9 | 95.0% -> 94.2% |
| OpenStack architecture | 4013 | 992 | 75% | 28.0 -> 8.4 | 81.4% -> 84.8% |

- Same final outcome, far less effort. Ablation: strong edges beat all edges (e.g. 792 vs 1343 min for task scheduling).
- Limits: model assumes missing prerequisites hurt learning; minutes estimated; random students (no real learners yet).
- Raw output file: docs/simulation_output.txt
- TODO: sensitivity test, classmate pilot.

## Sensitivity test (27 settings: p_ok 0.8/0.9/0.95, p_missing 0.2/0.35/0.5, tries 2/3/4; 300 students x 3 targets, strong edges)
- Time saved: min 64.2%, mean 65.3%, max 66.2%.
- Success-rate gap (graph - slide): min -2.3, mean +0.2, max +2.6 points (no real difference).
- Conclusion: time saving is robust to learning assumptions. Limit: this does not validate the graph edges themselves.
- Files: docs/sensitivity_results.csv, docs/figures/fig_sensitivity.png

## Student model (adaptive quiz, quiz.py)
- Idea: correct answer => prerequisites assumed known; wrong => dependents assumed unknown. Question = item that splits the unknown set most evenly.
- Assumptions: slip 10%, guess 20%, tested on simulated students only (200 per target). Compared against random question choice and budget 0.
- Output file: docs/quiz_output.txt
- Limit: inference only holds if the graph edges are true prerequisites (needs the hand-verified edges).

## Student model (adaptive quiz, quiz.py)
- Idea: correct answer => prerequisites assumed known; wrong => dependents assumed unknown. Question = item that splits the unknown set most evenly.
- Assumptions: slip 10%, guess 20%, tested on simulated students only (200 per target). Compared against random question choice and budget 0.
- Output file: docs/quiz_output.txt
- Limit: inference only holds if the graph edges are true prerequisites (needs the hand-verified edges).

## Quiz results (200 simulated students x 3 targets, slip 10%, guess 20%)
| Questions | Accuracy graph/random | Path vs ideal graph/random |
|---|---|---|
| 0 | 67.8% | 1.76x |
| 4 | 74.8 / 71.0 | 1.27 / 1.41 |
| 8 | 78.6 / 74.9 | 1.16 / 1.20 |
| 12 | 81.9 / 78.1 | 1.07 / 1.06 |
- Graph-chosen questions help most with few questions. Wrongly skipped stays ~3 items (caused by lucky guesses): limitation, possible fix = require 2 correct answers.

## API (api.py, FastAPI, port 8000)
- Endpoints: GET /topics, GET /graph, POST /path, POST /quiz/start, POST /quiz/answer. Test page: /docs.
- Quiz sessions kept in memory (demo-level, no login). Student history not yet saved in PostgreSQL (TODO).
- Screenshot to take: the /docs page and one /path response.

## Frontend status
- Website runs at localhost:5173 and calls the API at localhost:8000. Dropdown, quiz, path card and force graph work.
- Issue: Topic-only graph had almost no edges; switched to Topic+Concept.

## Algorithm variants (pathv.py, compare_variants.py, replan.py)
- v1 = course order tie-break; v2 = global PageRank on reversed graph (hubs first); v3 = personalized PageRank toward the target.
- Any valid order has equal total time in the simulator, so variants are compared on progress at 50% of the time budget.
- Dynamic re-planning: after a failed item, distrust quiz-guessed prerequisites and re-run plan(). Assumption: reviewing a known item costs 20% of its time.
- Outputs: docs/variants_output.txt, docs/replan_output.txt

## Results: PageRank variants and re-planning
- 50% time budget, items/importance mastered: v1 50.2/67.0, v2 46.2/66.5, v3 48.3/64.1. PageRank ordering did not beat course order (negative result, keep v1).
- Re-planning, reached target: quiz 4 Q static 92.7% vs dynamic 100.0% (+36 min); quiz 8 Q 93.3% vs 99.8% (+44 min). Dynamic fixes quiz mistakes at about 5% extra time.
- Assumptions: review costs 20%, 3 attempts, simulated students.

## Re-planning demo (API /study/start, /study/report)
- Student claims 7 known items: 17 remaining. After failing Hadoop简介, distrusted 云计算 and MapReduce: 19 remaining. A second failure (HBase) added nothing.
- Only guessed items that are direct prerequisites of the failed item are distrusted (simplification).
- Sessions are held in memory and lost on API restart (future work: PostgreSQL).
