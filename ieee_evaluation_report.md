# ProcessIQ IEEE Evaluation Suite Results

This document presents the quantitative benchmark results for the ProcessIQ Analytics Engine across various dataset typologies.

| Dataset Type     |   Rows |   Columns |   Execution Time (ms) |   Peak Memory (MB) |   Throughput (rows/sec) |   IDRS Delta (%) |
|:-----------------|-------:|----------:|----------------------:|-------------------:|------------------------:|-----------------:|
| clean_tabular    |  10000 |         4 |              165.235  |           3.17188  |                 60519.9 |              0   |
| missing_heavy    |  10000 |         4 |               84.5139 |           0.464844 |                118324   |              4.4 |
| high_cardinality |  10000 |         5 |               88.5236 |          -0.90625  |                112964   |              0   |
| time_series      |  10000 |         3 |              175.041  |          -0.996094 |                 57129.5 |              0   |
| skewed           |  10000 |         3 |               89.987  |           1.6875   |                111127   |              0   |
| wide             |   1000 |       201 |              244.034  |          -0.933594 |                  4097.8 |              0   |
| tall             | 500000 |         4 |             7207.29   |           2.1875   |                 69374.2 |              0   |
| mixed_industrial |  10000 |         5 |              324.344  |         -17.5039   |                 30831.5 |              1.2 |