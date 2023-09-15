# abstract-power-supply-system-dag

[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/)

供电系统抽象有向无环图(directed acyclic graph或dag)，是供电系统分析的核心数据结构

## Sample

```python
from apssdag import AbstractPowerSupplySystemDagBuilder 

try:
    # 创建抽象模型树(abstract model tree), 从连接关系中直接创建对象， 即汇流条和负载,
    # 这些对象没必要直接存在
    dag_builder =  AbstractPowerSupplySystemDagBuilder(create_objects_from_connection=true)
    # 逐条添加记录
    dag_builder.add_connection(load="load_A", bus="bus_1", redundancy="2", ...)
    dag_builder.add_connection(load="load_B", bus="bus_1", redundancy="2", ...)
    # 如果发现某汇流条下有同名负载
    dag = dag_builder.build()
except pssmlint.errors.DuplicateLoad as e:
    print(e)
# 分别打印汇流条和负载
print(amt.buses)
print(amt.loads)

# 解除汇流条和负载的连接关系
amt.disconnect(load="load_A", bus="bus_1")
# 增加负载load_A的冗余度
amt.loads["load_A"].redundancy += 1

```
