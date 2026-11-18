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
