import os
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import joblib
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve
)
import config
from backend.utils.risk_metrics import (
    calculate_ks, calculate_gini, calculate_psi,
    calculate_classification_metrics, calculate_feature_importance
)

class ModelEvaluation:
    def __init__(self, project):
        self.project = project
        self.model = None
        self.X_test = None
        self.y_test = None
        self.y_pred = None
        self.y_pred_proba = None
        self.feature_names = None
        self.model_path = None
    
    def evaluate(self):
        result = {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'steps': [],
            'errors': [],
            'metrics': {},
            'plots': {},
            'feature_importance': None,
            'calibration': None,
            'stability': None
        }
        
        try:
            model_training = self.project.get('model_training', {})
            if not model_training.get('success'):
                result['errors'].append("模型训练未完成，无法进行评估")
                return result
            
            self.model_path = model_training.get('model_path')
            self.feature_names = model_training.get('feature_names', [])
            
            if self.model_path and os.path.exists(self.model_path):
                if self.model_path.endswith('.pkl') or self.model_path.endswith('.pickle'):
                    with open(self.model_path, 'rb') as f:
                        self.model = pickle.load(f)
                elif self.model_path.endswith('.joblib'):
                    self.model = joblib.load(self.model_path)
            
            if self.model is None:
                result['errors'].append("无法加载已训练的模型")
                return result
            
            result['steps'].append({
                'step': '1',
                'name': '模型加载',
                'description': '成功加载训练好的模型',
                'details': {
                    'model_type': model_training.get('model_type'),
                    'model_path': self.model_path
                }
            })
            
            processed_data_path = model_training.get('processed_data_path')
            if processed_data_path and os.path.exists(processed_data_path):
                df = pd.read_csv(processed_data_path)
                target_col = model_training.get('target_column', 'default')
                
                if target_col in df.columns:
                    X = df.drop(columns=[target_col])
                    y = df[target_col]
                    
                    _, self.X_test, _, self.y_test = train_test_split(
                        X, y, test_size=0.3, random_state=42, stratify=y
                    )
                    
                    result['steps'].append({
                        'step': '2',
                        'name': '测试数据准备',
                        'description': f'准备测试数据，共{len(self.X_test)}条样本',
                        'details': {
                            'test_samples': len(self.X_test),
                            'features': len(self.X_test.columns)
                        }
                    })
                else:
                    result['errors'].append(f"目标列 {target_col} 不存在于数据中")
                    return result
            else:
                result['errors'].append("无法加载处理后的数据")
                return result
            
            if hasattr(self.model, 'predict_proba'):
                self.y_pred_proba = self.model.predict_proba(self.X_test)[:, 1]
            else:
                self.y_pred_proba = self.model.decision_function(self.X_test)
                if np.ndim(self.y_pred_proba) > 1:
                    self.y_pred_proba = self.y_pred_proba[:, 1]
            
            self.y_pred = self.model.predict(self.X_test)
            
            result['steps'].append({
                'step': '3',
                'name': '模型预测',
                'description': '完成模型预测',
                'details': {}
            })
            
            metrics = self._calculate_metrics()
            result['metrics'] = metrics
            
            result['steps'].append({
                'step': '4',
                'name': '指标计算',
                'description': '完成评估指标计算',
                'details': {
                    'auc': metrics.get('auc'),
                    'ks': metrics.get('ks'),
                    'gini': metrics.get('gini'),
                    'accuracy': metrics.get('accuracy')
                }
            })
            
            feature_imp = calculate_feature_importance(self.model, self.feature_names)
            if feature_imp:
                result['feature_importance'] = feature_imp[:20]
                
                result['steps'].append({
                    'step': '5',
                    'name': '特征重要性分析',
                    'description': f'分析完成，Top 5特征: {[f["feature"] for f in feature_imp[:5]]}',
                    'details': {
                        'top_features': [f['feature'] for f in feature_imp[:10]]
                    }
                })
            
            cv_results = self._cross_validation()
            if cv_results:
                result['cross_validation'] = cv_results
                
                result['steps'].append({
                    'step': '6',
                    'name': '交叉验证',
                    'description': f'5折交叉验证完成，平均AUC: {cv_results.get("mean_auc", 0):.4f}',
                    'details': cv_results
                })
            
            if len(self.X_test) > 0:
                mid_idx = len(self.X_test) // 2
                expected = self.y_pred_proba[:mid_idx]
                actual = self.y_pred_proba[mid_idx:]
                
                try:
                    psi = calculate_psi(expected, actual)
                    result['stability'] = {
                        'psi': psi,
                        'interpretation': self._interpret_psi(psi)
                    }
                except:
                    pass
            
            result['summary'] = self._generate_summary(result)
            result['success'] = True
            
        except Exception as e:
            result['errors'].append(str(e))
            import traceback
            result['errors'].append(traceback.format_exc())
        
        return result
    
    def _calculate_metrics(self):
        metrics = {}
        
        metrics['accuracy'] = float(accuracy_score(self.y_test, self.y_pred))
        metrics['precision'] = float(precision_score(self.y_test, self.y_pred, zero_division=0))
        metrics['recall'] = float(recall_score(self.y_test, self.y_pred, zero_division=0))
        metrics['f1'] = float(f1_score(self.y_test, self.y_pred, zero_division=0))
        
        try:
            metrics['auc'] = float(roc_auc_score(self.y_test, self.y_pred_proba))
            metrics['ks'] = float(calculate_ks(self.y_test, self.y_pred_proba))
            metrics['gini'] = float(calculate_gini(self.y_test, self.y_pred_proba))
        except:
            pass
        
        cm = confusion_matrix(self.y_test, self.y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            metrics['tn'] = int(tn)
            metrics['fp'] = int(fp)
            metrics['fn'] = int(fn)
            metrics['tp'] = int(tp)
            
            metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
            metrics['fallout'] = fp / (tn + fp) if (tn + fp) > 0 else 0
            metrics['miss_rate'] = fn / (fn + tp) if (fn + tp) > 0 else 0
        
        try:
            fpr, tpr, thresholds = roc_curve(self.y_test, self.y_pred_proba)
            metrics['roc_curve'] = {
                'fpr': fpr.tolist()[:100] if len(fpr) > 100 else fpr.tolist(),
                'tpr': tpr.tolist()[:100] if len(tpr) > 100 else tpr.tolist()
            }
            
            precision_curve, recall_curve, _ = precision_recall_curve(self.y_test, self.y_pred_proba)
            metrics['pr_curve'] = {
                'precision': precision_curve.tolist()[:100] if len(precision_curve) > 100 else precision_curve.tolist(),
                'recall': recall_curve.tolist()[:100] if len(recall_curve) > 100 else recall_curve.tolist()
            }
        except:
            pass
        
        return metrics
    
    def _cross_validation(self):
        try:
            model_training = self.project.get('model_training', {})
            processed_data_path = model_training.get('processed_data_path')
            
            if processed_data_path and os.path.exists(processed_data_path):
                df = pd.read_csv(processed_data_path)
                target_col = model_training.get('target_column', 'default')
                
                if target_col in df.columns:
                    X = df.drop(columns=[target_col])
                    y = df[target_col]
                    
                    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
                    
                    auc_scores = cross_val_score(
                        self.model, X, y, cv=cv, scoring='roc_auc'
                    )
                    
                    accuracy_scores = cross_val_score(
                        self.model, X, y, cv=cv, scoring='accuracy'
                    )
                    
                    return {
                        'n_splits': 5,
                        'auc_scores': auc_scores.tolist(),
                        'mean_auc': float(np.mean(auc_scores)),
                        'std_auc': float(np.std(auc_scores)),
                        'accuracy_scores': accuracy_scores.tolist(),
                        'mean_accuracy': float(np.mean(accuracy_scores)),
                        'std_accuracy': float(np.std(accuracy_scores))
                    }
        except:
            pass
        
        return None
    
    def _interpret_psi(self, psi):
        if psi < 0.1:
            return 'PSI < 0.1: 分布无显著变化，模型稳定'
        elif psi < 0.25:
            return '0.1 ≤ PSI < 0.25: 分布有轻微变化，需要关注'
        else:
            return 'PSI ≥ 0.25: 分布有显著变化，模型可能需要重新训练'
    
    def _generate_summary(self, result):
        metrics = result.get('metrics', {})
        
        summary_parts = []
        
        if metrics.get('auc'):
            if metrics['auc'] >= 0.85:
                summary_parts.append(f"AUC={metrics['auc']:.4f}，模型区分能力优秀")
            elif metrics['auc'] >= 0.75:
                summary_parts.append(f"AUC={metrics['auc']:.4f}，模型区分能力良好")
            else:
                summary_parts.append(f"AUC={metrics['auc']:.4f}，模型区分能力一般，建议优化")
        
        if metrics.get('ks'):
            if metrics['ks'] >= 0.4:
                summary_parts.append(f"KS={metrics['ks']:.4f}，模型区分能力优秀")
            elif metrics['ks'] >= 0.3:
                summary_parts.append(f"KS={metrics['ks']:.4f}，模型区分能力良好")
            else:
                summary_parts.append(f"KS={metrics['ks']:.4f}，模型区分能力一般")
        
        if metrics.get('gini'):
            if metrics['gini'] >= 0.7:
                summary_parts.append(f"Gini={metrics['gini']:.4f}，模型表现优秀")
            elif metrics['gini'] >= 0.5:
                summary_parts.append(f"Gini={metrics['gini']:.4f}，模型表现良好")
        
        if result.get('feature_importance'):
            top_features = [f['feature'] for f in result['feature_importance'][:3]]
            summary_parts.append(f"Top 3重要特征: {', '.join(top_features)}")
        
        return '；'.join(summary_parts) if summary_parts else '模型评估完成'
