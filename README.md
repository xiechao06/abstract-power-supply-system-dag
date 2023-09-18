# abstract-power-supply-system-dag

[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/)

供电系统抽象有向无环图(directed acyclic graph 或 dag)，是供电系统分析的核心数据结构

## Sample

[sample](./sample.py)

## Limitations

- 电源一定接开关
- 开关接汇流条, DC/DC 或者负载
- 汇流条下有 DC/DC 或者其他开关

## Development & Test

Install [rye](https://rye-up.com/guide/installation/), then:

```bash
rye sync
pytest
```
