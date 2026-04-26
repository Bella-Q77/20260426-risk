import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = 'risk-control-workbench-2024-secret-key'

DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOADS_DIR = os.path.join(DATA_DIR, 'uploads')
PROJECTS_DIR = os.path.join(DATA_DIR, 'projects')
MODELS_DIR = os.path.join(DATA_DIR, 'models')
SIMULATIONS_DIR = os.path.join(DATA_DIR, 'simulations')
TEMP_DIR = os.path.join(DATA_DIR, 'temp')

DOCS_DIR = os.path.join(BASE_DIR, 'docs')
DOC_TEMPLATES_DIR = os.path.join(DOCS_DIR, 'templates')
DOC_GENERATED_DIR = os.path.join(DOCS_DIR, 'generated')

STATIC_DIR = os.path.join(BASE_DIR, 'frontend', 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'frontend', 'templates')

ALLOWED_EXTENSIONS = {
    'data': {'csv', 'xlsx', 'xls', 'parquet', 'json'},
    'code': {'py', 'ipynb', 'r'},
    'model': {'pkl', 'pickle', 'joblib', 'onnx'}
}

MAX_CONTENT_LENGTH = 500 * 1024 * 1024

BUSINESS_SCENARIOS = {
    'pre_loan': {
        'name': '贷前',
        'sub_scenarios': {
            'credit_scoring': '信用评分',
            'anti_fraud': '反欺诈',
            'application_score': '申请评分'
        }
    },
    'mid_loan': {
        'name': '贷中',
        'sub_scenarios': {
            'behavior_score': '行为评分',
            'early_warning': '贷中预警',
            'limit_management': '额度管理'
        }
    },
    'post_loan': {
        'name': '贷后',
        'sub_scenarios': {
            'collection_score': '催收评分',
            'loss_forecast': '损失预测',
            'recovery_prediction': '回收率预测'
        }
    }
}

RISK_MODELS = {
    'classification': {
        'LogisticRegression': '逻辑回归',
        'RandomForest': '随机森林',
        'XGBoost': 'XGBoost',
        'LightGBM': 'LightGBM',
        'CatBoost': 'CatBoost',
        'SVM': '支持向量机'
    },
    'regression': {
        'LinearRegression': '线性回归',
        'Ridge': '岭回归',
        'Lasso': 'Lasso回归',
        'XGBoostRegressor': 'XGBoost回归'
    }
}

FEATURE_ENGINEERING_METHODS = {
    'missing_value': {
        'mean': '均值填充',
        'median': '中位数填充',
        'mode': '众数填充',
        'constant': '常数填充',
        'interpolate': '插值填充',
        'drop': '删除含缺失值的行'
    },
    'encoding': {
        'onehot': '独热编码',
        'label': '标签编码',
        'target': '目标编码',
        'frequency': '频率编码',
        'woe': 'WOE编码'
    },
    'scaling': {
        'standard': '标准化',
        'minmax': '最小-最大归一化',
        'robust': '鲁棒缩放',
        'log': '对数变换'
    },
    'feature_selection': {
        'variance': '方差阈值法',
        'correlation': '相关性分析',
        'chi2': '卡方检验',
        'f_classif': 'F检验',
        'mutual_info': '互信息',
        'rfe': '递归特征消除',
        'select_from_model': '模型选择'
    },
    'feature_construction': {
        'cross': '交叉特征',
        'ratio': '比率特征',
        'aggregation': '聚合特征',
        'binning': '分箱特征',
        'polynomial': '多项式特征'
    }
}

EVALUATION_METRICS = {
    'classification': {
        'accuracy': '准确率',
        'precision': '精确率',
        'recall': '召回率',
        'f1': 'F1分数',
        'auc': 'AUC-ROC',
        'ks': 'KS统计量',
        'gini': '基尼系数',
        'psi': '群体稳定性指数',
        'confusion_matrix': '混淆矩阵',
        'classification_report': '分类报告'
    },
    'regression': {
        'mse': '均方误差',
        'rmse': '根均方误差',
        'mae': '平均绝对误差',
        'r2': 'R²决定系数',
        'mape': '平均绝对百分比误差'
    }
}

for dir_path in [DATA_DIR, UPLOADS_DIR, PROJECTS_DIR, MODELS_DIR, 
                 SIMULATIONS_DIR, TEMP_DIR, DOCS_DIR, DOC_TEMPLATES_DIR, 
                 DOC_GENERATED_DIR, STATIC_DIR, TEMPLATES_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
