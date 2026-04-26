import os
import pandas as pd
import numpy as np
from datetime import datetime
import config
from backend.modules.data_manager import DataManager

class DataPreparation:
    def __init__(self, project):
        self.project = project
        self.data_manager = DataManager(project)
        self.df = None
        self.processed_df = None
    
    def run(self):
        result = {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'steps': [],
            'errors': [],
            'summary': {},
            'eda_report': None,
            'cleaning_report': None
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
            
            eda_report = self._perform_eda()
            result['eda_report'] = eda_report
            result['steps'].append({
                'step': '2',
                'name': '探索性数据分析(EDA)',
                'description': '完成数据探索性分析',
                'details': eda_report
            })
            
            cleaning_report = self._clean_data()
            result['cleaning_report'] = cleaning_report
            result['steps'].append({
                'step': '3',
                'name': '数据清洗',
                'description': '完成数据清洗',
                'details': cleaning_report
            })
            
            data_types_report = self._convert_data_types()
            result['steps'].append({
                'step': '4',
                'name': '数据类型转换',
                'description': '完成数据类型转换',
                'details': data_types_report
            })
            
            self._save_processed_data()
            
            result['summary'] = {
                'original_rows': len(self.df),
                'original_columns': len(self.df.columns),
                'processed_rows': len(self.processed_df) if self.processed_df is not None else len(self.df),
                'processed_columns': len(self.processed_df.columns) if self.processed_df is not None else len(self.df.columns),
                'missing_values_handled': cleaning_report.get('total_missing_handled', 0),
                'duplicates_removed': cleaning_report.get('duplicates_removed', 0)
            }
            
            result['success'] = True
            
        except Exception as e:
            result['errors'].append(str(e))
            import traceback
            result['errors'].append(traceback.format_exc())
        
        return result
    
    def _perform_eda(self):
        report = {
            'basic_info': {},
            'missing_analysis': {},
            'numeric_stats': {},
            'categorical_stats': {},
            'outlier_detection': {},
            'target_analysis': {}
        }
        
        report['basic_info'] = {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'memory_usage': f"{self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            'column_types': {}
        }
        
        for dtype in ['int64', 'float64', 'object', 'bool', 'datetime64']:
            count = len(self.df.select_dtypes(include=[dtype]).columns)
            if count > 0:
                report['basic_info']['column_types'][dtype] = count
        
        missing_count = self.df.isnull().sum()
        missing_rate = (missing_count / len(self.df) * 100).round(2)
        
        report['missing_analysis'] = {
            'total_missing': int(missing_count.sum()),
            'columns_with_missing': int((missing_count > 0).sum()),
            'missing_by_column': {}
        }
        
        for col in self.df.columns:
            if missing_count[col] > 0:
                report['missing_analysis']['missing_by_column'][col] = {
                    'count': int(missing_count[col]),
                    'rate': float(missing_rate[col])
                }
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            report['numeric_stats'] = {}
            for col in numeric_cols:
                stats = self.df[col].describe()
                report['numeric_stats'][col] = {
                    'count': int(stats['count']),
                    'mean': float(stats['mean']) if not pd.isna(stats['mean']) else None,
                    'std': float(stats['std']) if not pd.isna(stats['std']) else None,
                    'min': float(stats['min']) if not pd.isna(stats['min']) else None,
                    '25%': float(stats['25%']) if not pd.isna(stats['25%']) else None,
                    '50%': float(stats['50%']) if not pd.isna(stats['50%']) else None,
                    '75%': float(stats['75%']) if not pd.isna(stats['75%']) else None,
                    'max': float(stats['max']) if not pd.isna(stats['max']) else None
                }
                
                q1 = stats['25%']
                q3 = stats['75%']
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                outliers = ((self.df[col] < lower_bound) | (self.df[col] > upper_bound)).sum()
                report['outlier_detection'][col] = {
                    'outlier_count': int(outliers),
                    'outlier_rate': float(outliers / len(self.df) * 100),
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound)
                }
        
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            report['categorical_stats'] = {}
            for col in categorical_cols:
                value_counts = self.df[col].value_counts()
                report['categorical_stats'][col] = {
                    'unique_count': int(self.df[col].nunique()),
                    'top_values': value_counts.head(10).to_dict(),
                    'missing_count': int(self.df[col].isnull().sum())
                }
        
        target_cols = ['default', 'label', 'target', 'is_fraud', 'fraud', '逾期', '违约']
        for col in target_cols:
            if col in self.df.columns:
                report['target_analysis'][col] = {
                    'dtype': str(self.df[col].dtype),
                    'value_counts': self.df[col].value_counts().to_dict(),
                    'missing_count': int(self.df[col].isnull().sum())
                }
                
                if self.df[col].dtype in ['int64', 'float64']:
                    unique_vals = self.df[col].dropna().unique()
                    if len(unique_vals) <= 10:
                        report['target_analysis'][col]['is_binary'] = len(unique_vals) == 2
                        report['target_analysis'][col]['class_balance'] = (self.df[col] == 1).sum() / len(self.df)
        
        return report
    
    def _clean_data(self):
        report = {
            'total_missing_handled': 0,
            'duplicates_removed': 0,
            'columns_dropped': [],
            'rows_dropped': 0,
            'missing_by_strategy': {}
        }
        
        original_rows = len(self.df)
        
        duplicate_count = self.df.duplicated().sum()
        if duplicate_count > 0:
            self.df = self.df.drop_duplicates()
            report['duplicates_removed'] = int(duplicate_count)
            report['rows_dropped'] += int(duplicate_count)
        
        missing_count = self.df.isnull().sum()
        total_missing = missing_count.sum()
        
        if total_missing > 0:
            for col in self.df.columns:
                if missing_count[col] > 0:
                    missing_rate = missing_count[col] / len(self.df)
                    
                    if missing_rate > 0.8:
                        self.df = self.df.drop(columns=[col])
                        report['columns_dropped'].append(col)
                        report['missing_by_strategy'][col] = 'dropped_column'
                    elif missing_rate > 0.5:
                        if col in ['default', 'label', 'target', 'is_fraud', 'fraud']:
                            self.df = self.df.dropna(subset=[col])
                            report['rows_dropped'] += int(missing_count[col])
                            report['missing_by_strategy'][col] = 'dropped_rows'
                        else:
                            if self.df[col].dtype in ['int64', 'float64']:
                                self.df[col] = self.df[col].fillna(self.df[col].median())
                            else:
                                mode_val = self.df[col].mode()
                                if len(mode_val) > 0:
                                    self.df[col] = self.df[col].fillna(mode_val.iloc[0])
                            report['missing_by_strategy'][col] = 'imputed'
                    else:
                        if self.df[col].dtype in ['int64', 'float64']:
                            self.df[col] = self.df[col].fillna(self.df[col].mean())
                        else:
                            mode_val = self.df[col].mode()
                            if len(mode_val) > 0:
                                self.df[col] = self.df[col].fillna(mode_val.iloc[0])
                        report['missing_by_strategy'][col] = 'imputed'
                    
                    report['total_missing_handled'] += int(missing_count[col])
        
        self.processed_df = self.df.copy()
        
        report['rows_remaining'] = len(self.df)
        report['columns_remaining'] = len(self.df.columns)
        
        return report
    
    def _convert_data_types(self):
        report = {
            'converted_columns': [],
            'datetime_columns': [],
            'category_columns': [],
            'numeric_columns': []
        }
        
        for col in self.processed_df.columns:
            if self.processed_df[col].dtype == 'object':
                if 'date' in col.lower() or 'time' in col.lower():
                    try:
                        self.processed_df[col] = pd.to_datetime(self.processed_df[col])
                        report['datetime_columns'].append(col)
                        report['converted_columns'].append(col)
                    except:
                        pass
                
                unique_count = self.processed_df[col].nunique()
                if unique_count <= 50 and unique_count / len(self.processed_df) < 0.1:
                    try:
                        self.processed_df[col] = self.processed_df[col].astype('category')
                        report['category_columns'].append(col)
                        report['converted_columns'].append(col)
                    except:
                        pass
            
            if self.processed_df[col].dtype in ['int64', 'float64']:
                report['numeric_columns'].append(col)
        
        return report
    
    def _save_processed_data(self):
        if self.processed_df is not None:
            project_id = self.project.get('id', 'unknown')
            output_path = os.path.join(config.TEMP_DIR, f"{project_id}_data_prepared.csv")
            self.processed_df.to_csv(output_path, index=False)
            return output_path
        return None
    
    def get_sample_data(self, n=10):
        if self.processed_df is not None:
            return self.processed_df.head(n).to_dict(orient='records')
        elif self.df is not None:
            return self.df.head(n).to_dict(orient='records')
        return None
