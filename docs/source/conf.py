# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# 添加项目路径到Python路径
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'TS4GPC'
copyright = '2025, fhy'
author = 'fhy'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # 自动从docstrings生成文档
    'sphinx.ext.viewcode',  # 添加查看源代码的链接
    'sphinx.ext.napoleon',  # 支持Google风格的docstrings
    'sphinx.ext.intersphinx',  # 链接到其他项目的文档
    'sphinx_autodoc_typehints',  # 支持类型提示
]

templates_path = ['_templates']
exclude_patterns = []

# 语言设置
language = 'zh_CN'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'  # 使用ReadTheDocs主题
html_static_path = ['_static']
html_baseurl = 'https://nwafufhy.github.io/TS4GPC/'
# 创建.nojekyll文件，防止GitHub Pages忽略下划线开头的文件夹
html_extra_path = ['.nojekyll']

# autodoc设置
autodoc_member_order = 'bysource'  # 按源代码顺序排列成员
autodoc_typehints = 'description'  # 在描述中显示类型提示
napoleon_google_docstring = True  # 使用Google风格的docstrings
napoleon_numpy_docstring = False  # 不使用NumPy风格的docstrings

