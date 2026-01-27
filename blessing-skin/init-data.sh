#!/bin/bash
set -e

BS_VERSION=6.0.2

if [ -d "temp" ]; then
    echo "删除已存在的 temp 目录..."
    rm -rf temp
fi

if [ -d "data" ]; then
    echo "错误：data 目录已存在！" >&2
    echo "请删除现有 data 目录后再运行此脚本，或手动备份数据。" >&2
    exit 1
fi

mkdir temp

wget --directory-prefix=./temp "https://github.com/bs-community/blessing-skin-server/releases/download/${BS_VERSION}/blessing-skin-server-${BS_VERSION}.zip"

unzip -qq "./temp/blessing-skin-server-${BS_VERSION}.zip" -d ./temp

# 创建数据目录结构
mkdir data
mkdir ./data/skin
mkdir ./data/plugins

# 复制 Blessing Skin 的 Storage 目录，该目录含有持久化信息
cp -r ./temp/storage ./data/

# 复制 .env 文件
cp ./src/app.env ./data/.env

# 创建数据库文件
touch ./data/data.db

# 清理临时文件
rm -rf temp

echo "数据初始化完成"