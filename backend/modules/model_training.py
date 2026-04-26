import os
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

try:
    from lightgbm import LGBMClassifier
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

import config
from backend.modules.data_manager import DataManager

class ModelTraining:
    def __init__(self, project):
        self.project = project
        self.data_manager = DataManager(project)
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.model = None
        self.feature_names = None
        self.target_column = None
    
    def train(self, model_type='LogisticRegression', target_column='default', params=None):
        result = {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'steps': [],
            'errors': [],
            'model_type': model_type,
            'target_column': target_column,
            'train_samples': 0,
            'test_samples': 0,
            'feature_count': 0,
            'feature_names': [],
            'model_path': None,
            'processed_data_path': None,
            'params': params or {}
        }
        
        try:
            fe_processed = self.project.get('feature_engineering', {})
            data_prep = self.project.get('data_preparation', {})
            
            if fe_processed.get('success'):
                project_id = self.project.get('id', 'unknown')
                processed_path = os.path.join(config.TEMP_DIR, f"{project_id}_fe_processed.csv")
                if os.path.exists(processed_path):
                    self.df = pd.read_csv(processed_path)
                    result['processed_data_path'] = processed_path
                    
                    result['steps'].append({
                        'step': '1',
                        'name': '加载处理后数据',
                        'description': f'从特征工程结果加载数据，共{len(self.df)}行',
                        'details': {'source': 'feature_engineering'}
                    })
            
            if self.df is None and data_prep.get('success'):
                self.df = self.data_manager.load_data()
                if self.df is not None:
                    result['steps'].append({
                        'step': '1',
                        'name': '加载原始数据',
                        'description': f'从原始数据加载，共{len(self.df)}行',
                        'details': {'source': 'original'}
                    })
            
            if self.df is None:
                result['errors'].append("无法加载训练数据")
                return result
            
            target_cols = [target_column, 'default', 'label', 'target', 'is_fraud', 'fraud', '逾期', '违约']
            actual_target = None
            
            for col in target_cols:
                if col in self.df.columns:
                    actual_target = col
                    break
            
            if actual_target is None:
                result['errors'].append(f"未找到目标列，已尝试: {target_cols}")
                return result
            
            self.target_column = actual_target
            
            feature_cols = [c for c in self.df.columns if c != actual_target]
            self.feature_names = feature_cols
            
            X = self.df[feature_cols]
            y = self.df[actual_target]
            
            result['steps'].append({
                'step': '2',
                'name': '准备特征和标签',
                'description': f'目标列: {actual_target}, 特征数: {len(feature_cols)}',
                'details': {
                    'target_column': actual_target,
                    'feature_count': len(feature_cols)
                }
            })
            
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
            
            result['train_samples'] = len(self.X_train)
            result['test_samples'] = len(self.X_test)
            result['feature_count'] = len(feature_cols)
            result['feature_names'] = feature_cols
            
            result['steps'].append({
                'step': '3',
                'name': '划分数据集',
                'description': f'训练集: {len(self.X_train)}条, 测试集: {len(self.X_test)}条',
                'details': {
                    'train_size': len(self.X_train),
                    'test_size': len(self.X_test),
                    'test_ratio': 0.3
                }
            })
            
            model_params = params or {}
            self.model = self._create_model(model_type, model_params)
            
            result['steps'].append({
                'step': '4',
                'name': '初始化模型',
                'description': f'模型类型: {model_type}',
                'details': {
                    'model_type': model_type,
                    'params': model_params
                }
            })
            
            self.model.fit(self.X_train, self.y_train)
            
            result['steps'].append({
                'step': '5',
                'name': '模型训练',
                'description': '模型训练完成',
                'details': {}
            })
            
            project_id = self.project.get('id', 'unknown')
            model_path = os.path.join(config.MODELS_DIR, f"{project_id}_model.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            result['model_path'] = model_path
            
            result['steps'].append({
                'step': '6',
                'name': '保存模型',
                'description': f'模型已保存到: {model_path}',
                'details': {
                    'model_path': model_path
                }
            })
            
            if self.df is not None:
                data_path = os.path.join(config.TEMP_DIR, f"{project_id}_train_processed.csv")
                self.df.to_csv(data_path, index=False)
                result['processed_data_path'] = data_path
            
            result['success'] = True
            
        except Exception as e:
            result['errors'].append(str(e))
            import traceback
            result['errors'].append(traceback.format_exc())
        
        return result
    
    def _create_model(self, model_type, params):
        model = None
        
        if model_type == 'LogisticRegression':
            default_params = {
                'max_iter': 1000,
                'random_state': 42,
                'class_weight': 'balanced'
            }
            default_params.update(params)
            model = LogisticRegression(**default_params)
        
        elif model_type == 'RandomForest':
            default_params = {
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42,
                'class_weight': 'balanced',
                'n_jobs': -1
            }
            default_params.update(params)
            model = RandomForestClassifier(**default_params)
        
        elif model_type == 'XGBoost':
            if HAS_XGBOOST:
                default_params = {
                    'n_estimators': 100,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'random_state': 42,
                    'use_label_encoder': False,
                    'eval_metric': 'logloss'
                }
                default_params.update(params)
                model = XGBClassifier(**default_params)
            else:
                model = RandomForestClassifier(
                    n_estimators=100, random_state=42, class_weight='balanced'
                )
        
        elif model_type == 'LightGBM':
            if HAS_LIGHTGBM:
                default_params = {
                    'n_estimators': 100,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'random_state': 42,
                    'verbose': -1
                }
                default_params.update(params)
                model = LGBMClassifier(**default_params)
            else:
                model = RandomForestClassifier(
                    n_estimators=100, random_state=42, class_weight='balanced'
                )
        
        elif model_type == 'SVM':
            default_params = {
                'probability': True,
                'random_state': 42,
                'class_weight': 'balanced'
            }
            default_params.update(params)
            model = SVC(**default_params)
        
        else:
            model = LogisticRegression(
                max_iter=1000, random_state=42, class_weight='balanced'
            )
        
        return model
