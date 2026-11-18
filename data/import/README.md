# 云计算技术课程知识图谱数据包

## 文件清单
- `triples_normalized_all_refined.json`：知识图谱三元组（subject-predicate-object）（741.2 KB）
- `prerequisite_graph.json`：知识点前置关系图（nodes/edges 有向无环图）（204.1 KB）

## 数据格式
- 三元组：[{"subject":..., "predicate":..., "object":...}, ...]
- 前置关系图：{"nodes":[...], "edges":[...]}，边表示前置依赖。