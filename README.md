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

- benchmark编译

```
cd ./CoMeT/benchmark/
make
```

因为网络原因这一步骤也会经常性出问题，建议直接复制路径 `~/../share/xjy_demo/New/benchmark`到CoMeT根目录

```shell
cp -r ~/../share/xjy_demo/New/benchmarks  Your_Directory./CoMeT/
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

改命令可以在下面路径中找到相应的floorplan

```
cd ./CoMeT/config/hotspot/3D_16core16bank
```

然后需要在路径下创建一个 `gainstown_3D_16core16bank.cfg`文件使用相应的floorplan配置

```
cd ./CoMeT/config
vim gainstown_3D_16core16bank.cfg
```

更改 `gainstown_3D_16core16bank.cfg` 中的下面的变量保持和 `3D_16core16bank` 中想等

```shell
[memory]
banks_in_x = 4                      # total banks in x-dimension
banks_in_y = 4                      # total banks in y-dimension
banks_in_z = 1                      # total banks in z-dimension (layers)
cores_in_x = 4                      # total cores in x-dimension
cores_in_y = 4                      # total cores in y-dimension
cores_in_z = 1                      # total cores in z-dimension (layers)
type_of_stack = 3D                  #DDR, 3Dmem, 2.5D, 3D

#depending upon the arch. either one (core+memory) or two (separate for core and memory) instances of hotspot are invoked.
[hotspot]
tool_path = hotspot_tool/           #tool path, relative to the SNIPER ROOT
floorplan_folder  = config/hotspot/3D_16core16bank     # the folder in which various floorplans are stored. This folder is required to be present in the run directory as hotspot uses relative path in lcf
sampling_interval = 1000000     # in ns. Time epoch for invoking hotspot (same interval for both core and memory)

#for memory/combined cases
#init_file_external_mem = config/hotspot/3D_16core/stack.init  #The external init for to initialize temperature of different blocks. If init file not needed, say None
init_file_external_mem = None  #The external init for to initialize temperature of different blocks. If init file not needed, say None
hotspot_config_file_mem  =  config/hotspot/3D_16core16bank/stack_hotspot.config      #hotspot configuration file for memory. relative to sniper_root
layer_file_mem  =   config/hotspot/3D_16core16bank/stack.lcf    #hotspot lcf file for the memory. relative to sniper_root
```

找到路径

```shell
cd ./CoMeT/simlationcontrol
vim config.py
```

修改config.py 文件 和 gainstown_3D_16core16bank.cfg 中的下列文数据保持一致。

```shell
NUMBER_CORES_X = 4
NUMBER_CORES_Y = 4
NUMBER_CORES_Z = 1
NUMBER_MEM_BANKS_X = 4
NUMBER_MEM_BANKS_Y = 4
NUMBER_MEM_BANKS_Z = 1
SNIPER_CONFIG = 'gainestown_3D_16core16bank'
NUMBER_CORES = NUMBER_CORES_X * NUMBER_CORES_Y * NUMBER_CORES_Z
```

为了方便生成的图片为 `2D` 平面结构，需要保持在该文件中 `video configuration = DDR`。如果需要3-D芯片图则将 `ARCH_TYPE`改为 `3D`。

```
# video configuration
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
```

运行

```shell
python3 run.py
```

 

# 2. 3D-TTP

## 2.1 安装步骤

- **git 下载** 

```shell
git clone https://github.com/xlxwzybds/3DTTP.git
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



# 4. 3D-TTP

## 4.1 安装步骤

- **git 下载** 

```shell
git clone https://github.com/xlxwzybds/CoreMem.git
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





## 4.3 频率与温度梯度选择

**频率梯度选择**

```shell
cd CoMeT/config/
vim base.cfg
```

然后修改相应的benchmark

```shell
[benchmark]
#benchmark_name = blackscholes
#benchmark_name = swaption
benchmark_name = bodytrack
#benchmark_name = streamcluster
#benchmark_name = dedup
```

**温度梯度选择**

```shell
cd /home/xjy/TEST/3D_GDP/CoMeT/common/scheduler/policies
vim CoreMemDTM.py
```

根据将运行的benchmark改变下面的温度梯度

```python
       for x in range(NOF_CORE):
            Heated_Core[x] = 1
            #######################################
            ### for swaptions and blacksholes , for core-3,core-7 , radiosity
            #######################################
            #if (max_k_core_temperature[x] >= thermal_limit_core):
            #    Freq_Downgrade[x] = 4
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 0.5)): ## 79.5
            #    Freq_Downgrade[x] = 3
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 1.0)): ## 79
            #    Freq_Downgrade[x] = 2 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 2)): ## 78
            #    Freq_Downgrade[x] = 1
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 2.5)): ## 77.7
            #    Freq_Downgrade[x] = 1 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 3)): ## 77
            #    Freq_Downgrade[x] = 1 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 3.5)): # 73.5
            #    Freq_Downgrade[x] = 1 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 4)): 
            #    Freq_Downgrade[x] = 1 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 6)): ##
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 8)): ##
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 10)): #
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 12)): #
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 15)): #
            #    Freq_Downgrade[x] = 0
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 20)): #
            #    Freq_Downgrade[x] = 0
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 25)):
            #    Freq_Downgrade[x] = 0
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 30)):
            #    Freq_Downgrade[x] = 0
            #else:
            #    #if not(benchmark_type[x] == 2):
            #    #   Freq_Downgrade[x] = 0
            #    #   Heated_Core[x] = 0
            #    Freq_Downgrade[x] = 2
            #    Heated_Core[x] = 0
            #######################################
            ### for swaptions and blacksholes , for core-12
            #######################################
            #if (max_k_core_temperature[x] >= thermal_limit_core):
            #    Freq_Downgrade[x] = 4
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 0.5)): ## 79.5
            #    Freq_Downgrade[x] = 3
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 1.0)): ## 79
            #    Freq_Downgrade[x] = 3 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 2)): ## 78
            #    Freq_Downgrade[x] = 3
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 2.5)): ## 77.7
            #    Freq_Downgrade[x] = 2 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 3)): ## 77
            #    Freq_Downgrade[x] = 2 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 3.5)): # 73.5
            #    Freq_Downgrade[x] = 1 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 4)): 
            #    Freq_Downgrade[x] = 1 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 6)): ##
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 8)): ##
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 10)): #
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 12)): #
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 15)): #
            #    Freq_Downgrade[x] = 0
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 20)): #
            #    Freq_Downgrade[x] = 0
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 25)):
            #    Freq_Downgrade[x] = 0
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 30)):
            #    Freq_Downgrade[x] = 0
            #else:
            #    #if not(benchmark_type[x] == 2):
            #    #   Freq_Downgrade[x] = 0
            #    #   Heated_Core[x] = 0
            #    Freq_Downgrade[x] = 2
            #    Heated_Core[x] = 0
            ########################################
            ### for bodytrack & streamcluster
            #######################################
            if (max_k_core_temperature[x] >= thermal_limit_core):
                Freq_Downgrade[x] = 4
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 0.5)): ## 76.5
                Freq_Downgrade[x] = 3
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 1.0)): ## 76
                Freq_Downgrade[x] = 3
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 1.5)): ## 75
                Freq_Downgrade[x] = 3
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 2.0)): ## 75
                Freq_Downgrade[x] = 3
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 2.5)): ## 74.5
                Freq_Downgrade[x] = 2
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 3)): ## 74
                Freq_Downgrade[x] = 2
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 3.5)): # 73.5
                Freq_Downgrade[x] = 1
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 4)): 
                Freq_Downgrade[x] = 1
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 6)): ##
                Freq_Downgrade[x] = 0
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 8)): ##
                Freq_Downgrade[x] = 0
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 10)): #
                Freq_Downgrade[x] = 0
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 12)): #
                Freq_Downgrade[x] = 0 
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 15)): #
                Freq_Downgrade[x] = 0
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 20)): #
                Freq_Downgrade[x] = 0
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 25)):
                Freq_Downgrade[x] = 0
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 30)):
                Freq_Downgrade[x] = 0
            else:
                #if not(benchmark_type[x] == 2):
                #   Freq_Downgrade[x] = 0
                #   Heated_Core[x] = 0
                Freq_Downgrade[x] = 2
                Heated_Core[x] = 0


```







