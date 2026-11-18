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

## Still to do
- Simulator + experiment, student quiz, API, frontend, hand-verify Topic edges.
