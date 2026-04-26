import os
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler,
    OneHotEncoder, LabelEncoder, OrdinalEncoder
)
from sklearn.feature_selection import (
    VarianceThreshold, SelectKBest, chi2, f_classif,
    mutual_info_classif, RFE, SelectFromModel
)
from sklearn.linear_model import LogisticRegression
import config
from backend.modules.data_manager import DataManager

class FeatureEngineering:
    def __init__(self, project, config_params=None):
        self.project = project
        self.config_params = config_params or {}
        self.data_manager = DataManager(project)
        self.df = None
        self.processed_df = None
        self.feature_names = None
        self.target_column = None
    
    def run(self):
        result = {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'steps': [],
            'errors': [],
            'summary': {},
            'feature_importance': None
        }
        
        try:
            self.df = self.data_manager.load_data()
            if self.df is None:
                result['errors'].append("无法加载数据")
                return result
            
            result['steps'].append({
                'step': '1',
                'name': '数据加载',
                'description': f'成功加载数据，共{len(self.df)}行{len(self.df.columns)}列',
                'details': {
                    'rows': len(self.df),
                    'columns': len(self.df.columns)
                }
            })
            
            missing_report = self._analyze_missing_values()
            result['steps'].append({
                'step': '2',
                'name': '缺失值分析',
                'description': f'分析完成，共发现{missing_report["total_missing"]}个缺失值',
                'details': missing_report
            })
            
            self._handle_missing_values()
            result['steps'].append({
                'step': '3',
                'name': '缺失值处理',
                'description': '缺失值处理完成',
                'details': {
                    'method': self.config_params.get('missing_method', 'auto')
                }
            })
            
            encoding_report = self._perform_encoding()
            result['steps'].append({
                'step': '4',
                'name': '特征编码',
                'description': f'完成{encoding_report["encoded_columns"]}个分类特征编码',
                'details': encoding_report
            })
            
            scaling_report = self._perform_scaling()
            result['steps'].append({
                'step': '5',
                'name': '特征缩放',
                'description': f'完成{scaling_report["scaled_columns"]}个数值特征缩放',
                'details': scaling_report
            })
            
            selection_report = self._perform_feature_selection()
            result['steps'].append({
                'step': '6',
                'name': '特征选择',
                'description': f'特征选择完成，保留{selection_report["selected_count"]}个特征',
                'details': selection_report
            })
            
            self._save_processed_data()
            
            result['summary'] = {
                'original_features': len(self.df.columns),
                'processed_features': len(self.processed_df.columns) if self.processed_df is not None else 0,
                'rows': len(self.processed_df) if self.processed_df is not None else 0
            }
            result['success'] = True
            
        except Exception as e:
            result['errors'].append(str(e))
            import traceback
            result['errors'].append(traceback.format_exc())
        
        return result
    
    def _analyze_missing_values(self):
        missing_count = self.df.isnull().sum()
        missing_rate = (missing_count / len(self.df) * 100).round(2)
        
        missing_report = {
            'total_missing': int(missing_count.sum()),
            'columns_with_missing': int((missing_count > 0).sum()),
            'by_column': {}
        }
        
        for col in self.df.columns:
            if missing_count[col] > 0:
                missing_report['by_column'][col] = {
                    'count': int(missing_count[col]),
                    'rate': float(missing_rate[col])
                }
        
        return missing_report
    
    def _handle_missing_values(self):
        method = self.config_params.get('missing_method', 'auto')
        
        for col in self.df.columns:
            if self.df[col].isnull().sum() > 0:
                if method == 'mean' or (method == 'auto' and self.df[col].dtype in ['float64', 'int64']):
                    self.df[col] = self.df[col].fillna(self.df[col].mean())
                elif method == 'median' or (method == 'auto' and self.df[col].dtype in ['float64', 'int64'] and (self.df[col].skew() > 1 or self.df[col].skew() < -1)):
                    self.df[col] = self.df[col].fillna(self.df[col].median())
                elif method == 'mode' or method == 'auto':
                    mode_val = self.df[col].mode()
                    if len(mode_val) > 0:
                        self.df[col] = self.df[col].fillna(mode_val.iloc[0])
                elif method == 'drop':
                    self.df = self.df.dropna(subset=[col])
    
    def _perform_encoding(self):
        encoded_count = 0
        encoded_cols = []
        
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        method = self.config_params.get('encoding_method', 'onehot')
        
        for col in categorical_cols:
            if self.df[col].nunique() <= 10 and method == 'onehot':
                encoder = OneHotEncoder(sparse_output=False, drop='first')
                encoded = encoder.fit_transform(self.df[[col]])
                encoded_df = pd.DataFrame(
                    encoded,
                    columns=[f'{col}_{cat}' for cat in encoder.categories_[0][1:]],
                    index=self.df.index
                )
                self.df = pd.concat([self.df.drop(columns=[col]), encoded_df], axis=1)
                encoded_count += 1
                encoded_cols.append(col)
            elif method == 'label' or self.df[col].nunique() > 10:
                encoder = LabelEncoder()
                self.df[col] = encoder.fit_transform(self.df[col].astype(str))
                encoded_count += 1
                encoded_cols.append(col)
        
        return {
            'encoded_columns': encoded_count,
            'method': method,
            'columns': encoded_cols
        }
    
    def _perform_scaling(self):
        scaled_count = 0
        scaled_cols = []
        
        numeric_cols = self.df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        method = self.config_params.get('scaling_method', 'standard')
        
        target_cols = ['default', 'label', 'target', 'is_fraud', 'fraud']
        scale_cols = [c for c in numeric_cols if c.lower() not in [t.lower() for t in target_cols]]
        
        if len(scale_cols) > 0:
            if method == 'standard':
                scaler = StandardScaler()
            elif method == 'minmax':
                scaler = MinMaxScaler()
            elif method == 'robust':
                scaler = RobustScaler()
            else:
                scaler = StandardScaler()
            
            self.df[scale_cols] = scaler.fit_transform(self.df[scale_cols])
            scaled_count = len(scale_cols)
            scaled_cols = scale_cols
        
        return {
            'scaled_columns': scaled_count,
            'method': method,
            'columns': scaled_cols
        }
    
    def _perform_feature_selection(self):
        selected_count = len(self.df.columns)
        selected_features = list(self.df.columns)
        
        method = self.config_params.get('selection_method', 'auto')
        k = self.config_params.get('k', min(20, len(self.df.columns) - 1))
        
        target_cols = ['default', 'label', 'target', 'is_fraud', 'fraud', '逾期', '违约']
        X_cols = []
        y_col = None
        
        for col in self.df.columns:
            if any(t in col.lower() for t in [tc.lower() for tc in target_cols]):
                y_col = col
            else:
                X_cols.append(col)
        
        if y_col and len(X_cols) > 0:
            X = self.df[X_cols]
            y = self.df[y_col]
            self.target_column = y_col
            
            if method == 'variance' or method == 'auto':
                selector = VarianceThreshold(threshold=0.01)
                X_selected = selector.fit_transform(X)
                selected_mask = selector.get_support()
                selected_features = [X_cols[i] for i, mask in enumerate(selected_mask) if mask]
                selected_count = len(selected_features)
            elif method == 'correlation':
                correlations = X.corrwith(y).abs().sort_values(ascending=False)
                selected_features = correlations.head(k).index.tolist()
                selected_count = k
            elif method == 'chi2':
                selector = SelectKBest(chi2, k=min(k, len(X_cols)))
                selector.fit(X.abs(), y)
                selected_mask = selector.get_support()
                selected_features = [X_cols[i] for i, mask in enumerate(selected_mask) if mask]
                selected_count = len(selected_features)
            elif method == 'rfe':
                estimator = LogisticRegression(max_iter=1000)
                selector = RFE(estimator, n_features_to_select=min(k, len(X_cols)))
                selector.fit(X, y)
                selected_mask = selector.get_support()
                selected_features = [X_cols[i] for i, mask in enumerate(selected_mask) if mask]
                selected_count = len(selected_features)
            
            if selected_count < len(X_cols):
                keep_cols = selected_features + ([y_col] if y_col else [])
                self.processed_df = self.df[keep_cols]
            else:
                self.processed_df = self.df
        else:
            self.processed_df = self.df
        
        self.feature_names = [c for c in self.processed_df.columns if c != self.target_column]
        
        return {
            'selected_count': selected_count,
            'method': method,
            'features': self.feature_names,
            'target_column': self.target_column
        }
    
    def _save_processed_data(self):
        if self.processed_df is not None:
            project_id = self.project.get('id', 'unknown')
            output_path = os.path.join(config.TEMP_DIR, f"{project_id}_fe_processed.csv")
            self.processed_df.to_csv(output_path, index=False)
            return output_path
        return None
