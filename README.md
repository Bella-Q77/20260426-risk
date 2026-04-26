# 风控策略/建模/算法工程师工作系统

## 项目概述

本系统是一套完整的互联网信贷风控领域策略/建模/算法工程师工作系统，包含数据准备、特征工程、模型构建与训练、模型评估与验证、模型部署与监控等完整工作流程。

## 业务场景覆盖

### 贷前风控 (Pre-loan)
- 信用评分 (Credit Scoring)
- 反欺诈 (Anti-fraud)
- 申请评分 (Application Scoring)

### 贷中监控 (Mid-loan)
- 行为评分 (Behavior Scoring)
- 贷中预警 (Early Warning)
- 额度管理 (Limit Management)

### 贷后管理 (Post-loan)
- 催收评分 (Collection Scoring)
- 损失预测 (Loss Forecast)
- 回收率预测 (Recovery Prediction)

## 系统功能

### 1. 数据管理
- 支持上传 CSV、Excel、Parquet、JSON 等格式的数据集
- 支持上传 Python 代码文件
- 自动生成模拟数据（当仅上传代码时）

### 2. 场景识别
- 自动识别业务场景（贷前/贷中/贷后）
- 自动识别子场景（信用评分、反欺诈等）
- 支持手动设置场景

### 3. 数据准备
- 探索性数据分析 (EDA)
- 数据清洗（缺失值处理、重复值处理、异常值检测）
- 数据类型转换

### 4. 特征工程
- 缺失值处理（均值/中位数/众数填充）
- 特征编码（独热编码、标签编码）
- 特征缩放（标准化、最小-最大归一化）
- 特征选择（方差阈值、相关性分析、卡方检验等）

### 5. 模型训练
支持的模型：
- 逻辑回归 (Logistic Regression)
- 随机森林 (Random Forest)
- XGBoost
- LightGBM
- 支持向量机 (SVM)

### 6. 模型评估
风控核心指标：
- AUC-ROC（曲线下面积）
- KS统计量（正负样本最大区分度）
- Gini系数
- PSI（群体稳定性指数）
- 混淆矩阵、精确率、召回率、F1分数

### 7. 模型部署
- 生成模型部署配置
- 生成模型监控方案
- 导出模型工件（模型文件、配置文件、使用说明）

### 8. 文档生成
- 每一步自动生成过程文档
- 项目完成时生成最终报告
- 支持查看原始文档和生成文档

## 快速开始

### 方式一：双击启动（推荐）
1. 双击 `启动系统.bat` 文件
2. 等待依赖检查和安装完成
3. 浏览器自动打开 http://localhost:5000

### 方式二：命令行启动
```bash
cd /path/to/risk
python app.py
```

### 方式三：打包成EXE（需要PyInstaller）
```bash
python build_exe.py
```
打包完成后，在 `dist` 目录下找到 `RiskControlWorkbench.exe`

## 使用流程

### 1. 创建项目
- 点击"新建项目"
- 输入项目名称
- 系统自动生成项目ID

### 2. 上传数据
支持三种上传方式：
- **仅上传数据集**：从数据集开始全流程工作
- **仅上传代码**：系统自动生成同名模拟数据
- **同时上传**：结合数据和代码进行开发

### 3. 场景识别
- 系统自动根据文件名、列名识别业务场景
- 可手动调整场景设置

### 4. 执行工作流
按顺序执行以下步骤：
1. 数据准备
2. 特征工程
3. 模型构建
4. 模型评估
5. 模型部署

### 5. 查看结果
- 每一步完成后可查看详细报告
- 项目完成后可查看最终报告
- 下载模型工件

## 目录结构

```
risk/
├── app.py                          # Flask应用入口
├── config.py                       # 配置文件
├── requirements.txt                # 依赖包列表
├── 启动系统.bat                    # Windows启动脚本
├── build_exe.py                    # PyInstaller打包配置
├── runtime_hook.py                 # 打包运行时钩子
│
├── backend/                        # 后端核心代码
│   ├── modules/                    # 业务模块
│   │   ├── data_manager.py         # 数据管理模块
│   │   ├── scenario_detector.py    # 场景识别模块
│   │   ├── data_preparation.py     # 数据准备模块
│   │   ├── feature_engineering.py  # 特征工程模块
│   │   ├── model_training.py       # 模型训练模块
│   │   ├── model_evaluation.py     # 模型评估模块
│   │   ├── model_deployment.py     # 模型部署模块
│   │   └── document_generator.py   # 文档生成模块
│   ├── routes/                     # API路由
│   │   ├── api.py                  # REST API路由
│   │   └── pages.py                # 页面路由
│   └── utils/                      # 工具函数
│       ├── helpers.py              # 辅助函数
│       ├── risk_metrics.py         # 风控指标计算
│       └── simulation_data.py      # 模拟数据生成
│
├── frontend/                       # 前端文件
│   └── templates/                  # HTML模板
│       ├── base.html               # 基础模板
│       ├── index.html              # 首页/工作台
│       ├── create_project.html     # 创建项目页
│       ├── project_detail.html     # 项目详情页
│       ├── projects_list.html      # 项目列表页
│       ├── documentation.html      # 使用文档页
│       └── error.html              # 错误页
│
├── data/                           # 数据存储目录（运行时生成）
│   ├── uploads/                    # 上传的文件
│   ├── projects/                   # 项目数据
│   ├── models/                     # 训练的模型
│   ├── simulations/                # 模拟数据
│   └── temp/                       # 临时文件
│
└── docs/                           # 文档存储目录（运行时生成）
    ├── templates/                  # 文档模板
    └── generated/                  # 生成的文档
```

## 依赖说明

### 核心依赖
- Flask >= 2.0
- Flask-CORS >= 4.0
- pandas >= 1.3
- numpy >= 1.19
- scikit-learn >= 1.0
- matplotlib >= 3.3
- seaborn >= 0.11

### 可选依赖
- xgboost >= 1.3
- lightgbm >= 3.2
- openpyxl >= 3.0（Excel文件支持）
- pyarrow >= 1.0（Parquet文件支持）

### 打包依赖
- PyInstaller >= 5.0

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | Flask 2.3 |
| 前端框架 | Bootstrap 5.3 + 原生JavaScript |
| 数据处理 | pandas, numpy |
| 机器学习 | scikit-learn, XGBoost, LightGBM |
| 图表可视化 | Chart.js |
| 打包工具 | PyInstaller |

## 风控指标说明

### AUC-ROC
ROC曲线下面积，衡量模型整体区分能力。
- AUC > 0.9：优秀
- AUC > 0.8：良好
- AUC > 0.7：一般
- AUC > 0.6：较弱

### KS统计量
衡量正负样本的最大区分度。
- KS > 0.4：优秀
- KS > 0.3：良好
- KS > 0.2：一般

### Gini系数
2*AUC - 1，与AUC等价的衡量指标。

### PSI (群体稳定性指数)
衡量数据分布变化，用于模型监控。
- PSI < 0.1：分布无显著变化，模型稳定
- 0.1 ≤ PSI < 0.25：分布有轻微变化，需要关注
- PSI ≥ 0.25：分布有显著变化，模型可能需要重新训练

## 注意事项

1. **Python版本**：建议使用 Python 3.9 或更高版本
2. **首次启动**：首次启动会检查并安装依赖，请确保网络连接正常
3. **数据安全**：上传的数据存储在本地 `data/uploads` 目录，不会上传到任何服务器
4. **模型存储**：训练的模型存储在 `data/models` 目录，可随时加载使用
5. **打包提示**：使用 PyInstaller 打包时，请确保所有依赖已正确安装

## 故障排除

### 问题1：启动时提示缺少依赖
解决：确保网络连接正常，重新运行 `启动系统.bat`，或手动执行：
```bash
pip install -r requirements.txt
```

### 问题2：模型训练失败
可能原因：
- 数据格式不正确
- 目标列不存在
- 样本量不足

解决：检查数据格式，确保包含目标列（如 `default`, `label`, `is_fraud` 等）

### 问题3：打包后运行报错
解决：检查是否所有依赖都正确导入，确保 `runtime_hook.py` 已配置

## 更新日志

### v1.0.0 (2024)
- 完整的风控建模工作流实现
- 支持贷前/贷中/贷后全场景
- 自动场景识别
- 过程文档自动生成
- 模型部署配置生成
