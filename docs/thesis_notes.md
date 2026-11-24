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

## Edge validation (60 random strong edges after reduction; 240 total)
- Labels: first pass by AI, human review pending. 12 are containment edges (Topic -> introduced term), counted as 1.
- About 62% real prerequisites overall, about 52% excluding containment. Many rejected edges are co-mentions in slides.
- Files: docs/edge_validation.csv, edge_validation_output.txt, rejected_edges.csv

## Edge validation result (60 sampled strong edges)
- 37/60 real prerequisites (62%, 95% CI 49-73%). Excluding containment: 25/47 (53%, CI 39-67%).
- By type: introduces 12/13, extends_to 13/15, reverse_introduces 11/29 (38%). Decision: demote reverse_introduces to weak; cleaned strong set = introduces + extends_to + contains.
- Limits: small sample, labels first-pass by AI (human review pending).

## Failed experiment: demoting reverse_introduces
- Removing all reverse_introduces edges (409 -> 137 strong edges) left every target with a 1-item path: those edges are the only ones pointing into Topics. Pruning must be per edge or rule-based, not per type.

## Failed experiment 2: chapter-distance rule for reverse_introduces
- Gap rule keeps only 4-5 of 29 edges and loses 8-9 of the 11 correct ones. Distance does not separate real prerequisites from co-mentions. Conclusion: needs per-edge review.

## Pruning with the 23 rejected edges
- Path items strong -> pruned: Hadoop 25 -> 25, task scheduling 28 -> 28, OpenStack 35 -> 18. Effect depends on where rejected edges sit; sample covers only part of the graph. Full review of 240 edges is next.

## OpenStack path after pruning (18 items)
云计算的定义与特征 > 云计算 > 虚拟化 > 虚拟化资源池 > 云服务 > IaaS > SaaS > PaaS > 私有云 > 并行计算 > 分布式文件系统 > MapReduce > 虚拟机 > 资源池 > 云计算的体系架构与关键技术 > 容器 > OpenStack > OpenStack体系架构与核心组件
- Sensible: keeps virtualization, VMs, private cloud, containers; drops storage/energy/security topics. Still contains MapReduce/parallel computing/DFS (unreviewed edges). Order IaaS>SaaS>PaaS follows slide order.

## Decision: use AI-labeled graph (no teacher review)
- Graph rebuilt from the 240 reduced strong edges with ai_label=1 only (reviewed.py). Labels are an AI first pass from topic names, no domain expert check: state this limit. Optional later: classmate checks 30 rows for agreement.

## Reviewed graph v1 (ai_label=1 edges only)
- 409 -> 157 edges, DAG true. Path items: Hadoop 25->6, task scheduling 28->10, OpenStack 35->10, Spark 31->6.
- Problem: 11 of 36 topics disconnected (1-item path): over-pruning. Fix: reconnect isolated topics.

## Reviewed graph v2: reconnect isolated topics
- v1 left 11 topics with 1-item paths; 云计算的定义与特征 (first topic) is legitimately empty. Rule: for other isolated topics, restore edges from basic terms (云计算, 虚拟化, 虚拟机, 数据中心, 云数据中心, 分布式计算, 云服务) that were labeled 0.

## Reviewed graph v2 results
- 165 edges; items: Hadoop 14, task scheduling 10, OpenStack 10, Spark 15 (strong: 25/28/35/31).
- 5 non-first topics still without prerequisites (storage key tech, security analysis, Amazon/Microsoft/Alibaba platforms): left as limitation or one shared prerequisite.
- Limit: AI labels, no expert review; simulator uses each graph's own arrows so it cannot judge correctness.

## Graph comparison in simulator (300 students per target, own-graph judging)
- Minutes / reached: Hadoop slide 1457/85.0, strong 696/84.3, reviewed 400/100; task scheduling 2445/93.0, 796/96.3, 219/99.7; OpenStack 3976/81.3, 970/83.7, 231/100; Spark 5311/92.7, 918/91.3, 471/100.
- Caveat: each graph judged by its own arrows, so fewer arrows means fewer failures (circular). Need a fixed strict judge to check over-pruning.

## Strict-judge test, API/website graph option, PostgreSQL log, pilot plan
- strict.py: all paths judged by the original strong graph; metric = reached target and skipped-needed items. Output: docs/strict_output.txt
- API and website now offer edge sets reviewed / strong / all. Events (quiz answers, study reports) logged to PostgreSQL table events; live session state still in memory.
- Pilot: in person, 8-10 classmates, 6-question form (order sensible, skipped items, strong vs reviewed).

## Strict-judge test (original strong graph as fixed judge, 300 students per target)
- Reached / skipped-needed: Hadoop slide 100/0, strong 99.7/0.3, reviewed 69.7/7.4; task sched 99.7/0, 100/0.3, 90.7/13.6; OpenStack 100/0, 99.3/0.8, 91.7/17.7; Spark 99.3/0, 99.7/0.2, 77.7/11.2.
- Minutes: strong saves ~55-80% vs slide order with ~no loss; reviewed saves more but over-prunes under the strict judge.
- Decision: default graph = strong; reviewed = aggressive option. Pilot Q3 (skipped items) decides.
- API and website now offer reviewed/strong/all; events logged to PostgreSQL (quiz_start, quiz_answer). Session state still in memory.
