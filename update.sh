#!/bin/bash

# 动态获取Windows系统文档路径
documents_dir=$(powershell -Command "[Environment]::GetFolderPath('MyDocuments')")
documents_dir_unix=$(cygpath -u "$documents_dir")
target_dir="$documents_dir_unix/Github/simonwangsub"

# 进入目标目录
cd "$target_dir" || {
    echo -e "\033[31m错误：无法进入目录 $target_dir\033[0m"
    exit 1
}

# 下载文件
echo -e "\033[34m正在下载 pg.zip...\033[0m"
if ! wget -q --show-progress http://simonwang.cn:7090/pg/pg.zip; then
    echo -e "\033[31m错误：文件下载失败\033[0m"
    exit 1
fi

# 解压文件
echo -e "\033[34m正在解压文件...\033[0m"
if ! unzip -o -q pg.zip -d pg/; then
    echo -e "\033[31m错误：解压失败\033[0m"
    rm -f pg.zip
    exit 1
fi

# 清理压缩包
rm -f pg.zip

# Git操作
echo -e "\033[34m正在更新Git仓库...\033[0m"
git add . && \
git commit -m "Files Update" && \
git push -u origin main || {
    echo -e "\033[31m错误：Git操作失败\033[0m"
    exit 1
}

echo -e "\033[32m操作成功完成！\033[0m"