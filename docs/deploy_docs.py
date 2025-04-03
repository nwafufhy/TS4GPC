"""
文档部署工具

此脚本用于将Sphinx生成的文档部署到GitHub Pages。
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()
DOCS_DIR = ROOT_DIR / "docs"
BUILD_DIR = DOCS_DIR / "build" / "html"
DEPLOY_DIR = ROOT_DIR / "gh-pages"

def build_docs():
    """构建文档"""
    print("构建文档...")
    os.chdir(DOCS_DIR)
    result = subprocess.run("sphinx-build -b html source build/html", shell=True)
    if result.returncode != 0:
        print("文档构建失败！")
        sys.exit(1)
    
    # 创建.nojekyll文件
    with open(BUILD_DIR / ".nojekyll", "w") as f:
        pass
    
    print("文档构建成功！")

def deploy_to_gh_pages():
    """部署到GitHub Pages"""
    print("准备部署到GitHub Pages...")
    
    # 创建或清空部署目录
    if DEPLOY_DIR.exists():
        shutil.rmtree(DEPLOY_DIR)
    DEPLOY_DIR.mkdir(parents=True)
    
    # 复制构建好的文档到部署目录
    for item in BUILD_DIR.glob("*"):
        if item.is_dir():
            shutil.copytree(item, DEPLOY_DIR / item.name)
        else:
            shutil.copy2(item, DEPLOY_DIR / item.name)
    
    # 初始化git仓库
    os.chdir(DEPLOY_DIR)
    subprocess.run("git init", shell=True)
    subprocess.run("git add .", shell=True)
    subprocess.run('git commit -m "Update documentation"', shell=True)
    
    # 推送到gh-pages分支
    # 注意：需要替换为您的GitHub仓库URL
    repo_url = "https://github.com/nwafufhy/TS4GPC.git"
    subprocess.run(f"git push -f {repo_url} master:gh-pages", shell=True)
    
    print("文档已成功部署到GitHub Pages！")
    print(f"请访问 https://nwafufhy.github.io/TS4GPC/ 查看文档")

def main():
    """脚本入口点"""
    build_docs()
    deploy_to_gh_pages()

if __name__ == "__main__":
    main()