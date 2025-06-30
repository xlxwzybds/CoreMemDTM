# Readme

# 1. New-CoMeT-File

## 1. 文件标注 

原CoMeT没有多级bank frequency，若要添加这一特性需要对下面的代码文件进行修改。文件的路径如下所示：

- 修改的原文件

  - ./common/performance_model/dram_perf_model_constant.h

  - ./common/performance_model/dram_perf_model_constant.cc

  - ./common/scheduler/policies

    - ./common/scheduler/policies/gdp.py

    - ./common/scheduler/policies/dramLowpower.cc

  - ./common/scheduler/scheduler_open.h

  - ./common/scheduler/scheduler_open.cc
  - ./common/scheduler/powermodel.h
  - ./common/scheduler/powermodel.cc 

  - ./common/core/memory_subsystem/pr_l1_pr_l2_dram_directory_msi/dram_cntlr.cc

  - ./common/core/memory_subsystem/pr_l1_pr_l2_dram_directory_msi/dram_trace_collect.h

  - ./common/core/memory_subsystem/pr_l1_pr_l2_dram_directory_msi/dram_cntlr.h

  - ./common/core/memory_subsystem/pr_l1_pr_l2_dram_directory_msi/dram_trace_collect.cc

  - ./scripts/memTherm_core.py
  - ./config/hotspot/3D_16core16bank
    - cores_1.flp
    - mem_bank_1.flp
    - stack.lcf
    - stack_hotspot.config
    - tim.flp

  - ./config/base.cfg
  - ./config/gainestown_3D_16core16bank.cfg
  - ./simulationcontrol/ config.py
  - ./simulationcontrol/ run.py

- benchmarks中添加矩阵GCB文件

  - CoMeT/benchmarks/gdp_thermal_matrices
    - 3D_16core16bank/
    - 4x4_3D11_A.mat
    - 4x4_3D11_A_1ms.mat

- benchmarks中矩阵GCB使用文件：

  - CoMeT/benchmarks/system_sim_state
    - gdp_map.txt
    - gdp_map.txt.bak
    -  gdp_power.txt
    - info_for_mapping.txt 
    - mapping.txt

- benchmarks中频率修改文件：

  - CoMeT/benchmarks/system_sim_state_3D
    - bank_access_counter.txt
    - frequency_bank.txt
    - frequency_core.txt

  

## 2. 安装步骤

- **git 下载** 

```shell
git clone https://github.com/xlxwzybds/New.git
```

- **docker编译**

```
cd ./CoMeT/docker
make 
make run
```

如果因为网络的问题出现故障可以更改 `Makefile`中的内容，然后直接运行 `make run`即可

```
vim Makefile
```

```shell
# DOCKER_IMAGE?=ubuntu:$(UBUNTU_VERSION)-sniper-$(USER)
DOCKER_IMAGE?=ubuntu:$(UBUNTU_VERSION)-sniper-xjy
```

```shell
make run
```

- **sniper编译**

```
cd ./CoMeT
make
```

- hotspot编译

```
cd ./CoMeT/hotspot_tool/
make
```

- benchmark编译

```
cd ./CoMeT/benchmark/
make
```

因为网络原因这一步骤也会经常性出问题，建议直接复制路径 `~/../share/xjy_demo/New/benchmark`到CoMeT根目录

```shell
cp -r ~/../share/xjy_demo/New/benchmark  Your_Directory./CoMeT/
```



## 3.运行步骤

### 3.1 选择benchmark

在config文件中选择将要运行的benchmark名称

```shell
# choose benchmark in config file
cd ./CoMeT/config
vim base.cfg
```

选择将要运行的benchmark

```shell
[benchmark]
#benchmark_name = blackscholes
#benchmark_name = swaption
benchmark_name = bodytrack
#benchmark_name = streamcluster
#benchmark_name = dedup
```

### 3.2 选择 mapping 方式

```shell
cd ./CoMeT/config
vim base.cfg

[mapping]
mapping = firstunused # FirstUnused Mapping Method
#mapping = gdp #New Mapping Method
```



### 3.3 生成自我路径下的Floorplan

生成floorplan

```shell
cd ./CoMeT/docker
make run

cd ./CoMeT
python3 floorplanlib/create.py --mode 3D --cores 4x4 --corex 1.100mm --corey 1.100mm --banks 4x4x1 --bankx 1.100mm --banky 1.100mm --out config/hotspot/3D_16core16bank
```

找到路径

```shell
cd ./CoMeT/simlationcontrol
vim config.py
```

修改config.py 文件

```shell
NUMBER_CORES_X = 4
NUMBER_CORES_Y = 4
NUMBER_CORES_Z = 1
NUMBER_MEM_BANKS_X = 4
NUMBER_MEM_BANKS_Y = 4
NUMBER_MEM_BANKS_Z = 1
SNIPER_CONFIG = 'gainestown_3D_16core16bank'
NUMBER_CORES = NUMBER_CORES_X * NUMBER_CORES_Y * NUMBER_CORES_Z

# video configuration
# use DDR ， not 3D
ARCH_TYPE = 'DDR'  # 3D, 3Dmem, 2.5D, or DDR
```

### 3.4 修改仿真文件

找到路径：

```shell
cd ./CoMeT/simlationcontrol
vim run.py ## choose benchmark
```

修改文件中的example()函数：

```python
def example():
    for freq in (4.0,):  # when adding a new frequency level, make sure that it is also added in base.cfg
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-blackscholes', parallelism=8, input_set='large'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-swaptions', parallelism=8, input_set='large'))
        runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-bodytrack', parallelism=8, input_set='small'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-streamcluster', parallelism=7, input_set='small'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-dedup', parallelism=3, input_set='small'))
```

运行

```shell
python3 run.py
```



## 4.图片

### 4.1 图片fig5-(a)

配置config

```
cd ./CoMeT/config
vim base.cfg
```

更改base.cfg

```
[mapping]
mapping = firstunused

[benchmark_name]
benchmark_name = swaption
```

仿真文件

```python
def example():
    for freq in (4.0,):  # when adding a new frequency level, make sure that it is also added in base.c
        runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-swaptions', parallelism=8, input_set='small'))
    
```



### 4.2 图片fig5-(b)

配置config

```
cd ./CoMeT/config
vim base.cfg
```

更改base.cfg

```
[mapping]
mapping = gdp

[benchmark_name]
benchmark_name = swaption
```

仿真文件

```python
def example():
    for freq in (4.0,):  # when adding a new frequency level, make sure that it is also added in base.c
        runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-swaptions', parallelism=8, input_set='small'))
    
```

### 4.3 图片fig7-(a)

配置config

```
cd ./CoMeT/config
vim base.cfg
```

更改base.cfg

```
[mapping]
mapping = gdp

[benchmark_name]
benchmark_name = bodytrack
```

仿真文件

```python
def example():
    for freq in (4.0,):  # when adding a new frequency level, make sure that it is also added in base.c
        runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-bodytrack', parallelism=8, input_set='small'))
    
```

### 

# 2. 3D-TTP

## 2.1 安装步骤

- **git 下载** 

```shell
git clone https://github.com/xlxwzybds/3DTTP.git
```

- **docker编译**

```
cd ./CoMeT/docker
make 
make run
```

如果因为网络的问题出现故障可以更改 `Makefile`中的内容，然后直接运行 `make run`即可

```
vim Makefile
```

```shell
# DOCKER_IMAGE?=ubuntu:$(UBUNTU_VERSION)-sniper-$(USER)
DOCKER_IMAGE?=ubuntu:$(UBUNTU_VERSION)-sniper-xjy
```

```shell
make run
```

- **sniper编译**

```
cd ./CoMeT
make
```

- hotspot编译

```
cd ./CoMeT/hotspot_tool/
make
```

- benchmark编译

```
cd ./CoMeT/benchmark/
make
```

因为网络原因这一步骤也会经常性出问题，建议直接复制路径 `~/../share/xjy_demo/New/benchmark`到CoMeT根目录

```shell
cp -r ~/../share/xjy_demo/New/benchmark  Your_Directory./CoMeT/
```

## 2.2 运行步骤

### 3.1 选择benchmark

在config文件中选择将要运行的benchmark名称

```shell
# choose benchmark in config file
cd ./CoMeT/config
vim base.cfg
```

选择将要运行的benchmark

```shell
[benchmark]
#benchmark_name = blackscholes
#benchmark_name = swaption
benchmark_name = bodytrack
#benchmark_name = streamcluster
#benchmark_name = dedup
```

### 3.2 选择 mapping 方式

```shell
cd ./CoMeT/config
vim base.cfg

[mapping]
mapping = firstunused # FirstUnused Mapping Method
#mapping = gdp #New Mapping Method
```



### 3.3 生成自我路径下的Floorplan

生成floorplan

```shell
cd ./CoMeT/docker
make run

cd ./CoMeT
python3 floorplanlib/create.py --mode 3D --cores 4x4 --corex 1.100mm --corey 1.100mm --banks 4x4x1 --bankx 1.100mm --banky 1.100mm --out config/hotspot/3D_16core16bank
```

找到路径

```shell
cd ./CoMeT/simlationcontrol
vim config.py
```

修改config.py 文件

```shell
NUMBER_CORES_X = 4
NUMBER_CORES_Y = 4
NUMBER_CORES_Z = 1
NUMBER_MEM_BANKS_X = 4
NUMBER_MEM_BANKS_Y = 4
NUMBER_MEM_BANKS_Z = 1
SNIPER_CONFIG = 'gainestown_3D_16core16bank'
NUMBER_CORES = NUMBER_CORES_X * NUMBER_CORES_Y * NUMBER_CORES_Z

# video configuration
# use DDR ， not 3D
ARCH_TYPE = 'DDR'  # 3D, 3Dmem, 2.5D, or DDR
```

### 3.4 修改仿真文件

找到路径：

```shell
cd ./CoMeT/simlationcontrol
vim run.py ## choose benchmark
```

修改文件中的example()函数：

```python
def example():
    for freq in (4.0,):  # when adding a new frequency level, make sure that it is also added in base.cfg
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-blackscholes', parallelism=8, input_set='large'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-swaptions', parallelism=8, input_set='large'))
        runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-bodytrack', parallelism=8, input_set='small'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-streamcluster', parallelism=7, input_set='small'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-dedup', parallelism=3, input_set='small'))
```

运行

```shell
python3 run.py
```



## 2.3 图片

### 3.1 图fig7-(b)

配置config

```shell
cd ./CoMeT/config
vim base.cfg
```

更改base.cfg

```shell
[mapping]
mapping = gdp

[benchmark_name]
benchmark_name = bodytrack
```

仿真文件

```python
def example():
    for freq in (4.0,):  # when adding a new frequency level, make sure that it is also added in base.c
        runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-bodytrack', parallelism=8, input_set='small'))
    
```





# 4. 3D-TTP

## 4.1 安装步骤

- **git 下载** 

```shell
git clone https://github.com/xlxwzybds/CoreMem.git
```

- **docker编译**

```
cd ./CoMeT/docker
make 
make run
```

如果因为网络的问题出现故障可以更改 `Makefile`中的内容，然后直接运行 `make run`即可

```
vim Makefile
```

```shell
# DOCKER_IMAGE?=ubuntu:$(UBUNTU_VERSION)-sniper-$(USER)
DOCKER_IMAGE?=ubuntu:$(UBUNTU_VERSION)-sniper-xjy
```

```shell
make run
```

- **sniper编译**

```
cd ./CoMeT
make
```

- hotspot编译

```
cd ./CoMeT/hotspot_tool/
make
```

- benchmark编译

```
cd ./CoMeT/benchmark/
make
```

因为网络原因这一步骤也会经常性出问题，建议直接复制路径 `~/../share/xjy_demo/New/benchmark`到CoMeT根目录

```shell
cp -r ~/../share/xjy_demo/CoreMemDTM/benchmarks  Your_Directory./CoMeT/
```

## 4.2 运行步骤

### 4.1 选择benchmark

在config文件中选择将要运行的benchmark名称

```shell
# choose benchmark in config file
cd ./CoMeT/config
vim base.cfg
```

选择将要运行的benchmark

```shell
[benchmark]
#benchmark_name = blackscholes
#benchmark_name = swaption
benchmark_name = bodytrack
#benchmark_name = streamcluster
#benchmark_name = dedup
```

### 3.2 暂无 mapping 方式

### 3.3 生成自我路径下的Floorplan

生成floorplan

```shell
cd ./CoMeT/docker
make run

cd ./CoMeT
python3 floorplanlib/create.py --mode 3D --cores 4x4 --corex 1.100mm --corey 1.100mm --banks 4x4x1 --bankx 1.100mm --banky 1.100mm --out config/hotspot/3D_16core16bank
```

找到路径

```shell
cd ./CoMeT/simlationcontrol
vim config.py
```

修改config.py 文件

```shell
NUMBER_CORES_X = 4
NUMBER_CORES_Y = 4
NUMBER_CORES_Z = 1
NUMBER_MEM_BANKS_X = 4
NUMBER_MEM_BANKS_Y = 4
NUMBER_MEM_BANKS_Z = 1
SNIPER_CONFIG = 'gainestown_3D_16core16bank'
NUMBER_CORES = NUMBER_CORES_X * NUMBER_CORES_Y * NUMBER_CORES_Z

# video configuration
# use DDR ， not 3D
ARCH_TYPE = 'DDR'  # 3D, 3Dmem, 2.5D, or DDR
```

### 3.4 修改仿真文件

找到路径：

```shell
cd ./CoMeT/simlationcontrol
vim run.py ## choose benchmark
```

修改文件中的example()函数：

```python
def example():
    for freq in (4.0,):  # when adding a new frequency level, make sure that it is also added in base.cfg
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-blackscholes', parallelism=8, input_set='large'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-swaptions', parallelism=8, input_set='large'))
        runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-bodytrack', parallelism=8, input_set='small'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-streamcluster', parallelism=7, input_set='small'))
        #runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-dedup', parallelism=3, input_set='small'))
```

运行

```shell
python3 run.py
```



## 2.3 图片

### 3.1 图fig7-(c)

配置config

```shell
cd ./CoMeT/config
vim base.cfg
```

更改base.cfg

```shell
[benchmark_name]
benchmark_name = bodytrack
```

仿真文件

```python
def example():
    for freq in (4.0,):  # when adding a new frequency level, make sure that it is also added in base.c
        runlib.run(['open', '{:.1f}GHz'.format(freq), 'gdp'], runlib.get_instance('parsec-bodytrack', parallelism=8, input_set='small'))

```









