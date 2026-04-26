import os
import pandas as pd
import numpy as np
from datetime import datetime
import config

class DataManager:
    def __init__(self, project):
        self.project = project
        self.data_path = project.get('data', {}).get('data_path')
        self.df = None
        
    def load_data(self):
        if not self.data_path or not os.path.exists(self.data_path):
            return None
        
        ext = os.path.splitext(self.data_path)[1].lower()
        
        try:
            if ext == '.csv':
                self.df = pd.read_csv(self.data_path)
            elif ext in ['.xlsx', '.xls']:
                self.df = pd.read_excel(self.data_path)
            elif ext == '.parquet':
                self.df = pd.read_parquet(self.data_path)
            elif ext == '.json':
                self.df = pd.read_json(self.data_path)
            else:
                return None
            return self.df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def get_basic_info(self):
        if self.df is None:
            if not self.load_data():
                return None
        
        info = {
            'rows': len(self.df),
            'columns': len(self.df.columns),
            'memory_usage': f"{self.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            'column_info': []
        }
        
        for col in self.df.columns:
            col_info = {
                'name': col,
                'dtype': str(self.df[col].dtype),
                'non_null_count': int(self.df[col].count()),
                'missing_count': int(self.df[col].isnull().sum()),
                'missing_rate': float(self.df[col].isnull().sum() / len(self.df) * 100),
                'unique_count': int(self.df[col].nunique()),
                'unique_values': None
            }
            
            if self.df[col].nunique() <= 20:
                col_info['unique_values'] = self.df[col].value_counts().to_dict()
            
            info['column_info'].append(col_info)
        
        return info
    
    def get_sample_data(self, n=5):
        if self.df is None:
            if not self.load_data():
                return None
        return self.df.head(n).to_dict(orient='records')
    
    def get_numeric_stats(self):
        if self.df is None:
            if not self.load_data():
                return None
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        stats = {}
        
        for col in numeric_cols:
            stats[col] = {
                'count': int(self.df[col].count()),
                'mean': float(self.df[col].mean()),
                'std': float(self.df[col].std()),
                'min': float(self.df[col].min()),
                '25%': float(self.df[col].quantile(0.25)),
                '50%': float(self.df[col].median()),
                '75%': float(self.df[col].quantile(0.75)),
                'max': float(self.df[col].max())
            }
        
        return stats
    
    def save_processed_data(self, df, filename_suffix='_processed'):
        base_name = os.path.splitext(os.path.basename(self.data_path))[0]
        new_filename = f"{base_name}{filename_suffix}.csv"
        new_path = os.path.join(config.TEMP_DIR, new_filename)
        df.to_csv(new_path, index=False)
        return new_path
