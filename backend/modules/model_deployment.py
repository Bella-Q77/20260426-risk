import os
import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import joblib
import config
from backend.utils.helpers import generate_document_id, save_json

class ModelDeployment:
    def __init__(self, project):
        self.project = project
        self.model = None
        self.model_path = None
    
    def deploy(self):
        result = {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'steps': [],
            'errors': [],
            'model_path': None,
            'deployment_config': None,
            'monitoring_plan': None,
            'summary': ''
        }
        
        try:
            model_training = self.project.get('model_training', {})
            model_evaluation = self.project.get('model_evaluation', {})
            
            if not model_training.get('success'):
                result['errors'].append("模型训练未完成，无法进行部署")
                return result
            
            self.model_path = model_training.get('model_path')
            
            if self.model_path and os.path.exists(self.model_path):
                if self.model_path.endswith('.pkl') or self.model_path.endswith('.pickle'):
                    with open(self.model_path, 'rb') as f:
                        self.model = pickle.load(f)
                elif self.model_path.endswith('.joblib'):
                    self.model = joblib.load(self.model_path)
            
            result['steps'].append({
                'step': '1',
                'name': '加载模型',
                'description': f'成功从 {self.model_path} 加载模型',
                'details': {
                    'model_path': self.model_path
                }
            })
            
            project_id = self.project.get('id', 'unknown')
            deployment_config = self._create_deployment_config(project_id)
            result['deployment_config'] = deployment_config
            
            result['steps'].append({
                'step': '2',
                'name': '生成部署配置',
                'description': '生成模型部署配置文件',
                'details': deployment_config
            })
            
            monitoring_plan = self._create_monitoring_plan()
            result['monitoring_plan'] = monitoring_plan
            
            result['steps'].append({
                'step': '3',
                'name': '生成监控方案',
                'description': '生成模型监控方案',
                'details': monitoring_plan
            })
            
            export_path = self._export_model_artifacts(project_id)
            result['model_path'] = export_path
            
            result['steps'].append({
                'step': '4',
                'name': '导出模型工件',
                'description': f'模型工件已导出到 {export_path}',
                'details': {
                    'export_path': export_path
                }
            })
            
            result['summary'] = self._generate_summary(model_evaluation)
            result['success'] = True
            
        except Exception as e:
            result['errors'].append(str(e))
            import traceback
            result['errors'].append(traceback.format_exc())
        
        return result
    
    def _create_deployment_config(self, project_id):
        project_name = self.project.get('name', '未命名项目')
        scenario = self.project.get('scenario', {})
        model_training = self.project.get('model_training', {})
        
        config_data = {
            'project_id': project_id,
            'project_name': project_name,
            'model_version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'business_scenario': {
                'loan_phase': scenario.get('loan_phase'),
                'loan_phase_name': scenario.get('loan_phase_name'),
                'sub_scenario': scenario.get('sub_scenario'),
                'sub_scenario_name': scenario.get('sub_scenario_name')
            },
            'model_info': {
                'model_type': model_training.get('model_type'),
                'target_column': model_training.get('target_column'),
                'feature_names': model_training.get('feature_names', []),
                'feature_count': model_training.get('feature_count')
            },
            'deployment_settings': {
                'environment': 'production',
                'input_format': 'json',
                'output_format': 'json',
                'batch_support': True,
                'real_time_support': True,
                'threshold': 0.5
            },
            'api_spec': {
                'predict_endpoint': '/api/v1/predict',
                'batch_endpoint': '/api/v1/predict/batch',
                'health_endpoint': '/api/v1/health',
                'request_example': {
                    'features': {}
                }
            }
        }
        
        config_path = os.path.join(config.MODELS_DIR, f"{project_id}_deployment_config.json")
        save_json(config_path, config_data)
        
        return config_data
    
    def _create_monitoring_plan(self):
        model_evaluation = self.project.get('model_evaluation', {})
        metrics = model_evaluation.get('metrics', {})
        
        monitoring_plan = {
            'created_at': datetime.now().isoformat(),
            'monitoring_frequency': {
                'performance_monitoring': 'weekly',
                'data_drift_monitoring': 'daily',
                'concept_drift_monitoring': 'weekly'
            },
            'thresholds': {
                'psi_warning': 0.1,
                'psi_critical': 0.25,
                'auc_drop_warning': 0.05,
                'ks_drop_warning': 0.1
            },
            'metrics_to_monitor': {
                'performance_metrics': [
                    'auc', 'ks', 'gini', 'accuracy', 'precision', 'recall', 'f1'
                ],
                'stability_metrics': [
                    'psi', 'csi'
                ],
                'business_metrics': [
                    'approval_rate', 'default_rate', 'loss_rate'
                ]
            },
            'alerting': {
                'channels': ['email', 'dashboard'],
                'severity_levels': ['warning', 'critical']
            },
            'baseline': {
                'baseline_auc': metrics.get('auc'),
                'baseline_ks': metrics.get('ks'),
                'baseline_gini': metrics.get('gini'),
                'baseline_date': datetime.now().isoformat()
            },
            'retraining_triggers': {
                'psi_exceeds_0_25': True,
                'auc_drop_gt_0_05': True,
                'ks_drop_gt_0_1': True,
                'time_based': '6_months'
            }
        }
        
        return monitoring_plan
    
    def _export_model_artifacts(self, project_id):
        export_dir = os.path.join(config.MODELS_DIR, f"{project_id}_export")
        os.makedirs(export_dir, exist_ok=True)
        
        if self.model and self.model_path:
            model_ext = os.path.splitext(self.model_path)[1]
            export_model_path = os.path.join(export_dir, f"model{model_ext}")
            
            if self.model_path.endswith('.pkl') or self.model_path.endswith('.pickle'):
                with open(export_model_path, 'wb') as f:
                    pickle.dump(self.model, f)
            elif self.model_path.endswith('.joblib'):
                joblib.dump(self.model, export_model_path)
        
        readme_content = self._generate_readme()
        readme_path = os.path.join(export_dir, 'README.txt')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return export_dir
    
    def _generate_readme(self):
        project_name = self.project.get('name', '未命名项目')
        scenario = self.project.get('scenario', {})
        model_training = self.project.get('model_training', {})
        model_evaluation = self.project.get('model_evaluation', {})
        metrics = model_evaluation.get('metrics', {})
        
        readme = f"""
================================================================================
                    风控模型部署工件包
                    Risk Control Model Deployment Package
================================================================================

项目信息
--------
项目名称: {project_name}
项目ID: {self.project.get('id', 'unknown')}
创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

业务场景
--------
贷款阶段: {scenario.get('loan_phase_name', '未指定')}
子场景: {scenario.get('sub_scenario_name', '未指定')}

模型信息
--------
模型类型: {model_training.get('model_type', '未指定')}
目标变量: {model_training.get('target_column', 'default')}
特征数量: {model_training.get('feature_count', 0)}
训练样本数: {model_training.get('train_samples', 0)}
测试样本数: {model_training.get('test_samples', 0)}

模型性能
--------
AUC: {metrics.get('auc', 'N/A')}
KS: {metrics.get('ks', 'N/A')}
Gini: {metrics.get('gini', 'N/A')}
准确率: {metrics.get('accuracy', 'N/A')}
精确率: {metrics.get('precision', 'N/A')}
召回率: {metrics.get('recall', 'N/A')}
F1分数: {metrics.get('f1', 'N/A')}

文件结构
--------
./
├── model.pkl          - 序列化的模型文件
├── deployment_config.json  - 部署配置文件
├── monitoring_plan.json    - 监控方案
└── README.txt         - 本文档

使用说明
--------
1. 加载模型:
   import pickle
   with open('model.pkl', 'rb') as f:
       model = pickle.load(f)

2. 预测:
   predictions = model.predict(X)
   probabilities = model.predict_proba(X)[:, 1]

3. 部署时请确保特征顺序与训练时一致

监控建议
--------
- 建议每周检查模型性能指标(AUC, KS)
- 建议每日检查数据分布稳定性(PSI)
- 当PSI > 0.25时，建议重新训练模型
- 建议每6个月进行一次模型回顾

================================================================================
                  风险控制策略/建模/算法工程师工作系统
================================================================================
"""
        return readme
    
    def _generate_summary(self, model_evaluation):
        metrics = model_evaluation.get('metrics', {}) if model_evaluation else {}
        
        summary_parts = [
            "模型部署完成",
            f"模型类型: {self.project.get('model_training', {}).get('model_type', '未指定')}",
            f"业务场景: {self.project.get('scenario', {}).get('loan_phase_name', '未指定')} - {self.project.get('scenario', {}).get('sub_scenario_name', '未指定')}"
        ]
        
        if metrics.get('auc'):
            summary_parts.append(f"基线AUC: {metrics['auc']:.4f}")
        
        if metrics.get('ks'):
            summary_parts.append(f"基线KS: {metrics['ks']:.4f}")
        
        summary_parts.append("已生成部署配置和监控方案")
        
        return "；".join(summary_parts)
