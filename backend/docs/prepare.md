# 环境部署

##  尝试使用Areal的镜像
```
docker pull ghcr.io/inclusionai/areal-runtime:v0.3.0.post2
docker create --runtime=nvidia --gpus all --net=host --shm-size="10g" --cap-add=SYS_ADMIN -v .:/workspace/verl -v /etc/localtime:/etc/localtime:ro -v /etc/timezone:/etc/timezone:ro --name areal ghcr.io/inclusionai/areal-runtime:v0.3.0.post2 sleep infinity
docker start areal
docker exec -it areal bash
```

## ~/.bashrc中配置使用的GPU和实用的hugging face镜像
CUDA_VISIBLE_DEVICES=1
HF_ENDPOINT=https://hf-mirror.com

## 设置pip镜像源
```
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```
# 克隆强化学习训练框架
```
git clone https://github.com/OpenPipe/ART.git
cd ART
pip install .
pip install ".[backend]"
```

## 设置代理，安装git上的项目
```
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890
export all_proxy=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPs_PROXY=http://127.0.0.1:7890
pip install 'torchtune @ git+https://github.com/pytorch/torchtune.git'
pip install 'unsloth-zoo @ git+https://github.com/bradhilton/unsloth-zoo'
```

## WanDB docker 训练记录
```
docker pull wandb/local
docker run -d --restart always -v wandb:/vol -p 3005:8080 --name wandb-local wandb/local
#会提示您配置打开浏览器http://localhost:3005/authorize，新建一个本地普通用户, 粘贴key
输入邮箱和用户名创建一个本地的用户，得到类似这样的KEY， local-f2ca8cd44276ac92ca0a2c12641a6902beb6847d
粘贴到.env的环境变量配置文件中
```