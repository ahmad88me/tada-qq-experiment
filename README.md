
# tada-qq-experiment

[![Build Status](https://ahmad88me.semaphoreci.com/badges/tada-qq-experiment/branches/main.svg)](https://ahmad88me.semaphoreci.com/projects/tada-qq-experiment)
[![codecov](https://codecov.io/gh/ahmad88me/tada-qq-experiment/branch/main/graph/badge.svg?token=EEMOL78RCW)](https://codecov.io/gh/ahmad88me/tada-qq-experiment)

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)




Semantic labelling and experiments using [tada-qq](https://github.com/oeg-upm/tada-qq)




## Datasets
### Olympic Games Dataset

The data is available here: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1408562.svg)](https://doi.org/10.5281/zenodo.1408562)

We have a script to download the data automatically here `scripts/olympic-download.sh` 
You can run it as follows:```sh scripts/olympic-download.sh```

<!--
## Data
1. Download the csv files from here: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1408562.svg)](https://doi.org/10.5281/zenodo.1408562)
1. Create a folder `local_data/olympic_games/data`
1. Put the csv files of the Olympic games inside it.
1. Put the `meta.csv` in `local_data/olympic_games`
-->

#### To cite the Olympic Games dataset
```
@dataset{alobaid_ahmad_2018_1408562,
  author       = {Alobaid, Ahmad and
                  Corcho, Oscar},
  title        = {Olympic Games 2020},
  month        = sep,
  year         = 2018,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.1408562},
  url          = {https://doi.org/10.5281/zenodo.1408562}
}
```

### T2Dv2
#### Automatic
1. `pip install requests chardet`
2. To download and transform the data automatically, you can use [this](scripts/prep_t2dv2.py)
script.
3. Make sure to use the Updated typology CSV file [T2Dv2_typology.csv](https://zenodo.org/record/6334120).


#### Manual
* [T2Dv2_typology.csv](https://zenodo.org/record/6334120)
* [T2Dv2](http://webdatacommons.org/webtables/extended_instance_goldstandard.tar.gz)

#### Extra preprocessing
The application expects to have a folder named `csv` inside the T2Dv2 which includes the files in csv format. You can use the script `scripts/json_to_csv.py` to do that.


## Clustering Experiments

Matching similar columns. The main differences between the clustering and the semantic labelling are:
1. Clustering does not add an annotation to the cluster.
2. The clustering does not use the knowledge graph.
3. The clustering does not take into account the subject class/type.

The command used: 
```
python -m clus.t2dv2 -c 0.02 0.04 0.06 0.08 0.1 0.12 0.14 0.16 0.18 0.2
```

### Clustering Results - T2Dv2

#### Class Agnostic

![](results/clustering/t2dv2.svg)

#### Same Class

![](results/clustering/t2dv2_sameclass.svg)


## Semantic labelling
### Olympic Games
Command used:
```
python -m slabelexp.olympic
```

#### Results

|  remove outlier |  estimate |    error method | Precision |    Recall |    F1 |
|:---------------:|:---------:|:---------------:|:---------:|:---------:|:-----:|
|            True |  estimate |        mean_err |      0.88 |      1.00 |  0.93 |
|            True |  estimate |     mean_sq_err |      0.88 |      1.00 |  0.93 |
|            True |  estimate | mean_sqroot_err |      0.88 |      1.00 |  0.93 |
|            True |     exact |        mean_err |      0.88 |      1.00 |  0.93 |
|            True |     exact |     mean_sq_err |      0.88 |      1.00 |  0.93 |
|            True |     exact | mean_sqroot_err |      0.88 |      1.00 |  0.93 |
|           False |  estimate |        mean_err |      0.83 |      1.00 |  0.91 |
|           False |  estimate |     mean_sq_err |      0.83 |      1.00 |  0.91 |
|           False |  estimate | mean_sqroot_err |      0.88 |      1.00 |  0.93 |
|           False |     exact |        mean_err |      0.83 |      1.00 |  0.91 |
|           False |     exact |     mean_sq_err |      0.88 |      1.00 |  0.93 |
|           False |     exact | mean_sqroot_err |      0.79 |      1.00 |  0.88 |



### T2Dv2

Arguments
```
optional arguments:
  -h, --help            show this help message and exit
  -e {mean_err,mean_sq_err}, --err-meth {mean_err,mean_sq_err}
                        Functions to computer errors.
  -o {true,false}, --outlier-removal {true,false}
```

Used:
1. with outlier removal
```
python -m slabelexp.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o true --estimate True False --draw
```
2. with outliers kept
```
python -m slabelexp.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o false --estimate True False --draw
```

#### Results

##### Performance for the different parameters

|  remove outlier |  estimate |    error method | Precision |    Recall |    F1 |
|:---------------:|:---------:|:---------------:|:---------:|:---------:|:-----:|
|            True |  estimate |        mean_err |      0.49 |      0.84 |  0.62 |
|            True |  estimate |     mean_sq_err |      0.50 |      0.84 |  0.63 |
|            True |  estimate | mean_sqroot_err |      0.51 |      0.85 |  0.64 |
|            True |     exact |        mean_err |      0.45 |      0.83 |  0.58 |
|            True |     exact |     mean_sq_err |      0.49 |      0.84 |  0.62 |
|            True |     exact | mean_sqroot_err |      0.39 |      0.81 |  0.53 |
|           False |  estimate |        mean_err |      0.53 |      0.85 |  0.65 |
|           False |  estimate |     mean_sq_err |      0.53 |      0.85 |  0.65 |
|           False |  estimate | mean_sqroot_err |      0.53 |      0.85 |  0.65 |
|           False |     exact |        mean_err |      0.53 |      0.85 |  0.65 |
|           False |     exact |     mean_sq_err |      0.53 |      0.85 |  0.65 |
|           False |     exact | mean_sqroot_err |      0.50 |      0.84 |  0.63 |



### Number of data points vs performance score per evaluation method

#### Outlier Removal
![datapoints.svg](results/slabelling/t2dv2-err-methods.svg)

#### Raw
![datapoints.svg](results/slabelling/t2dv2-err-methods-raw.svg)

### Number of data points and performance of different metrics

#### mean error
mean error + estimate + raw

![](results/slabelling/datapoints-t2dv2-mean-err-estimate-raw.svg)

mean error + estimate + outlier removed

![](results/slabelling/datapoints-t2dv2-mean-err-estimate.svg)

mean error + exact + raw

![](results/slabelling/datapoints-t2dv2-mean-err-exact-raw.svg)

mean error + exact + outlier removed

![](results/slabelling/datapoints-t2dv2-mean-err-exact.svg)

#### mean square error

mean square error + estimate + raw

![](results/slabelling/datapoints-t2dv2-mean-sq-err-estimate-raw.svg)

mean square error + estimate + outlier removed

![](results/slabelling/datapoints-t2dv2-mean-sq-err-estimate.svg)

mean square error + exact + raw

![](results/slabelling/datapoints-t2dv2-mean-sq-err-exact-raw.svg)

mean square error + exact + outlier removed

![](results/slabelling/datapoints-t2dv2-mean-sq-err-exact.svg)

#### mean square root 

mean square root + estimate + raw

![](results/slabelling/datapoints-t2dv2-mean-sqroot-err-estimate-raw.svg)

mean square root + estimate + outlier removed

![](results/slabelling/datapoints-t2dv2-mean-sqroot-err-estimate.svg)

mean square root + exact + raw

![](results/slabelling/datapoints-t2dv2-mean-sqroot-err-exact-raw.svg)

mean square root + exact + outlier removed

![](results/slabelling/datapoints-t2dv2-mean-sqroot-err-exact.svg)













## Merged Experiment (Slab Preference)
Clustering as a way to improve Semantic Labelling


*Note: be default the diagrams and readmes are not updated. You can pass`--draw` to generate/update the diagrams and `-a` to append the results to the readme in the results folder*




### Cluster without class consideration
1. with outlier removal and candidate fail back
```
python -m merged.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o true --estimate True False --pref slab --failback --draw -c 0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.24 0.26 0.28 0.30 0.32 0.34 0.36 0.38 0.40 0.42 0.44 0.46 0.48 0.50 0.52 0.54 0.56 0.58 0.60 0.62 0.64 0.66 0.68 0.70 0.72 0.74 0.76 0.78 0.80 0.82 0.84 0.86 0.88 0.90 0.92 0.94 0.96 0.98
```

Estimate
![](results/merged-slab/t2dv2_mer_estimate_reo_ca_cf.svg)

Exact
![](results/merged-slab/t2dv2_mer_exact_reo_ca_cf.svg)


2. with outlier removal and without candidate fail back
```
python -m merged.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o true --estimate True False --pref slab --draw -c 0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.24 0.26 0.28 0.30 0.32 0.34 0.36 0.38 0.40 0.42 0.44 0.46 0.48 0.50 0.52 0.54 0.56 0.58 0.60 0.62 0.64 0.66 0.68 0.70 0.72 0.74 0.76 0.78 0.80 0.82 0.84 0.86 0.88 0.90 0.92 0.94 0.96 0.98
```

Estimate
![](results/merged-slab/t2dv2_mer_estimate_reo_ca_nc.svg)

Exact
![](results/merged-slab/t2dv2_mer_exact_reo_ca_nc.svg)

3. with outliers kept and candidate fail back
```
python -m merged.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o false --estimate True False --pref slab --failback --draw -c 0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.24 0.26 0.28 0.30 0.32 0.34 0.36 0.38 0.40 0.42 0.44 0.46 0.48 0.50 0.52 0.54 0.56 0.58 0.60 0.62 0.64 0.66 0.68 0.70 0.72 0.74 0.76 0.78 0.80 0.82 0.84 0.86 0.88 0.90 0.92 0.94 0.96 0.98
```

Estimate
![](results/merged-slab/t2dv2_mer_estimate_raw_ca_cf.svg)

Exact
![](results/merged-slab/t2dv2_mer_exact_raw_ca_cf.svg)


4. with outliers kept and without candidate fail back
```
python -m merged.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o false --estimate True False --pref slab --draw -c 0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.24 0.26 0.28 0.30 0.32 0.34 0.36 0.38 0.40 0.42 0.44 0.46 0.48 0.50 0.52 0.54 0.56 0.58 0.60 0.62 0.64 0.66 0.68 0.70 0.72 0.74 0.76 0.78 0.80 0.82 0.84 0.86 0.88 0.90 0.92 0.94 0.96 0.98
```

Estimate
![](results/merged-slab/t2dv2_mer_estimate_raw_ca_nc.svg)

Exact
![](results/merged-slab/t2dv2_mer_exact_raw_ca_nc.svg)


### Force same class clustering
5. with outlier removal and candidate fail back
```
python -m merged.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o true --estimate True False  --pref slab --failback --sameclass --draw -c 0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.24 0.26 0.28 0.30 0.32 0.34 0.36 0.38 0.40 0.42 0.44 0.46 0.48 0.50 0.52 0.54 0.56 0.58 0.60 0.62 0.64 0.66 0.68 0.70 0.72 0.74 0.76 0.78 0.80 0.82 0.84 0.86 0.88 0.90 0.92 0.94 0.96 0.98
```


Estimate
![](results/merged-slab/t2dv2_mer_estimate_reo_sc_cf.svg)

Exact
![](results/merged-slab/t2dv2_mer_exact_reo_sc_cf.svg)

6. with outlier removal and without candidate fail back
```
python -m merged.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o true --estimate True False --pref slab --sameclass --draw -c 0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.24 0.26 0.28 0.30 0.32 0.34 0.36 0.38 0.40 0.42 0.44 0.46 0.48 0.50 0.52 0.54 0.56 0.58 0.60 0.62 0.64 0.66 0.68 0.70 0.72 0.74 0.76 0.78 0.80 0.82 0.84 0.86 0.88 0.90 0.92 0.94 0.96 0.98
```


Estimate
![](results/merged-slab/t2dv2_mer_estimate_reo_sc_nc.svg)

Exact
![](results/merged-slab/t2dv2_mer_exact_reo_sc_nc.svg)

7. with outliers kept and candidate fail back
```
python -m merged.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o false --estimate True False --pref slab --failback --sameclass --draw -c 0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.24 0.26 0.28 0.30 0.32 0.34 0.36 0.38 0.40 0.42 0.44 0.46 0.48 0.50 0.52 0.54 0.56 0.58 0.60 0.62 0.64 0.66 0.68 0.70 0.72 0.74 0.76 0.78 0.80 0.82 0.84 0.86 0.88 0.90 0.92 0.94 0.96 0.98
```


Estimate
![](results/merged-slab/t2dv2_mer_estimate_raw_sc_cf.svg)

Exact
![](results/merged-slab/t2dv2_mer_exact_raw_sc_cf.svg)

8. with outliers kept and without candidate fail back
```
python -m merged.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o false --estimate True False --pref slab --sameclass --draw -c 0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.24 0.26 0.28 0.30 0.32 0.34 0.36 0.38 0.40 0.42 0.44 0.46 0.48 0.50 0.52 0.54 0.56 0.58 0.60 0.62 0.64 0.66 0.68 0.70 0.72 0.74 0.76 0.78 0.80 0.82 0.84 0.86 0.88 0.90 0.92 0.94 0.96 0.98
```

Estimate
![](results/merged-slab/t2dv2_mer_estimate_raw_sc_nc.svg)

Exact
![](results/merged-slab/t2dv2_mer_exact_raw_sc_nc.svg)

### Results

[merged results](results/merged/README.md)












## Merged Experiment (Clus Preference)
Clustering as a way to improve Semantic Labelling

*Note that candidate failback has no effects with clus preference*

1. with outlier removal
```
python -m merged.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o true --estimate True False -p clus --draw -c 0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.24 0.26 0.28 0.30 0.32 0.34 0.36 0.38 0.40 0.42 0.44 0.46 0.48 0.50 0.52 0.54 0.56 0.58 0.60 0.62 0.64 0.66 0.68 0.70 0.72 0.74 0.76 0.78 0.80 0.82 0.84 0.86 0.88 0.90 0.92 0.94 0.96 0.98
```

Estimate
![](results/merged-clus/t2dv2_mer_estimate_reo_ca_nc.svg)

Exact
![](results/merged-clus/t2dv2_mer_exact_reo_ca_nc.svg)


2. with outliers kept
```
python -m merged.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o false --estimate True False -p clus --draw -c 0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.24 0.26 0.28 0.30 0.32 0.34 0.36 0.38 0.40 0.42 0.44 0.46 0.48 0.50 0.52 0.54 0.56 0.58 0.60 0.62 0.64 0.66 0.68 0.70 0.72 0.74 0.76 0.78 0.80 0.82 0.84 0.86 0.88 0.90 0.92 0.94 0.96 0.98
```

Estimate
![](results/merged-clus/t2dv2_mer_estimate_raw_ca_nc.svg)

Exact
![](results/merged-clus/t2dv2_mer_exact_raw_ca_nc.svg)


### Force same class clustering

3. with outlier removal 
```
python -m merged.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o true --estimate True False -p clus --sameclass --draw -c 0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.24 0.26 0.28 0.30 0.32 0.34 0.36 0.38 0.40 0.42 0.44 0.46 0.48 0.50 0.52 0.54 0.56 0.58 0.60 0.62 0.64 0.66 0.68 0.70 0.72 0.74 0.76 0.78 0.80 0.82 0.84 0.86 0.88 0.90 0.92 0.94 0.96 0.98
```


Estimate
![](results/merged-clus/t2dv2_mer_estimate_reo_sc_nc.svg)

Exact
![](results/merged-clus/t2dv2_mer_exact_reo_sc_nc.svg)

4. with outliers kept
```
python -m merged.t2dv2 -e mean_err mean_sq_err mean_sqroot_err -o false --estimate True False -p clus --sameclass --draw -c 0.02 0.04 0.06 0.08 0.10 0.12 0.14 0.16 0.18 0.20 0.22 0.24 0.26 0.28 0.30 0.32 0.34 0.36 0.38 0.40 0.42 0.44 0.46 0.48 0.50 0.52 0.54 0.56 0.58 0.60 0.62 0.64 0.66 0.68 0.70 0.72 0.74 0.76 0.78 0.80 0.82 0.84 0.86 0.88 0.90 0.92 0.94 0.96 0.98
```

Estimate
![](results/merged-clus/t2dv2_mer_estimate_raw_sc_nc.svg)

Exact
![](results/merged-clus/t2dv2_mer_exact_raw_sc_nc.svg)

### Results

[merged results](results/merged/README.md)



# Installation

## Known issues
* Error installing Pillow on ubuntu: `sudo apt-get install libjpeg-dev`