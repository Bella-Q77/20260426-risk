import os
import re
from datetime import datetime
import config

class ScenarioDetector:
    def __init__(self, project):
        self.project = project
        self.data_info = project.get('data', {}).get('data_info', {})
        self.code_filename = project.get('code', {}).get('code_filename', '')
        self.data_filename = project.get('data', {}).get('data_filename', '')
    
    def detect(self):
        result = {
            'detected': False,
            'loan_phase': None,
            'loan_phase_name': None,
            'sub_scenario': None,
            'sub_scenario_name': None,
            'confidence': 0.0,
            'method': 'auto',
            'evidence': [],
            'timestamp': datetime.now().isoformat()
        }
        
        pre_loan_keywords = [
            'credit', 'score', '申请', '评分', 'credit_score', 'application',
            'anti_fraud', 'fraud', '反欺诈', 'risk', 'risk_score',
            'default', '违约', '逾期', 'delinquency'
        ]
        
        mid_loan_keywords = [
            'behavior', '行为', 'early_warning', '预警', 'monitor',
            '监控', 'behavior_score', 'limit', '额度', '余额'
        ]
        
        post_loan_keywords = [
            'collection', '催收', 'recovery', '回收率', 'loss',
            '损失', '逾期', 'delinquency', '不良', 'NPL', 'm1', 'm2', 'm3'
        ]
        
        sub_scenario_keywords = {
            'credit_scoring': ['credit_score', '信用评分', '申请评分', 'A卡'],
            'anti_fraud': ['fraud', '反欺诈', '异常检测', 'fraud_detect'],
            'application_score': ['application', '申请', '准入'],
            'behavior_score': ['behavior', '行为评分', 'B卡'],
            'early_warning': ['early_warning', '预警', '风险预警'],
            'limit_management': ['limit', '额度', '提额', '降额'],
            'collection_score': ['collection', '催收评分', 'C卡'],
            'loss_forecast': ['loss', '损失预测', '不良预测'],
            'recovery_prediction': ['recovery', '回收率', '回款预测']
        }
        
        all_text = f"{self.data_filename} {self.code_filename}"
        
        if self.data_info and 'column_info' in self.data_info:
            column_names = [col['name'] for col in self.data_info['column_info']]
            all_text += ' ' + ' '.join(column_names)
        
        all_text_lower = all_text.lower()
        
        pre_count = sum(1 for kw in pre_loan_keywords if kw.lower() in all_text_lower)
        mid_count = sum(1 for kw in mid_loan_keywords if kw.lower() in all_text_lower)
        post_count = sum(1 for kw in post_loan_keywords if kw.lower() in all_text_lower)
        
        total_count = pre_count + mid_count + post_count
        if total_count > 0:
            max_count = max(pre_count, mid_count, post_count)
            
            if max_count == pre_count and pre_count > 0:
                result['loan_phase'] = 'pre_loan'
                result['loan_phase_name'] = '贷前'
                result['confidence'] = pre_count / total_count
                result['evidence'].append(f"贷前关键词匹配数: {pre_count}")
            elif max_count == mid_count and mid_count > 0:
                result['loan_phase'] = 'mid_loan'
                result['loan_phase_name'] = '贷中'
                result['confidence'] = mid_count / total_count
                result['evidence'].append(f"贷中关键词匹配数: {mid_count}")
            elif max_count == post_count and post_count > 0:
                result['loan_phase'] = 'post_loan'
                result['loan_phase_name'] = '贷后'
                result['confidence'] = post_count / total_count
                result['evidence'].append(f"贷后关键词匹配数: {post_count}")
        
        if result['loan_phase']:
            phase_config = config.BUSINESS_SCENARIOS.get(result['loan_phase'], {})
            sub_scenarios = phase_config.get('sub_scenarios', {})
            
            best_sub_score = 0
            best_sub = None
            
            for sub_key, sub_name in sub_scenarios.items():
                keywords = sub_scenario_keywords.get(sub_key, [])
                score = sum(1 for kw in keywords if kw.lower() in all_text_lower)
                
                if score > best_sub_score:
                    best_sub_score = score
                    best_sub = sub_key
            
            if best_sub and best_sub_score > 0:
                result['sub_scenario'] = best_sub
                result['sub_scenario_name'] = sub_scenarios[best_sub]
                result['evidence'].append(f"子场景关键词匹配: {best_sub}")
        
        if self.data_info:
            if 'sample_data' in self.data_info:
                sample = self.data_info['sample_data']
                if sample and len(sample) > 0:
                    first_row = sample[0]
                    target_cols = ['default', '逾期', '违约', 'label', 'target', 'is_fraud', 'fraud']
                    for col in first_row.keys():
                        if any(tc in col.lower() for tc in target_cols):
                            result['evidence'].append(f"发现目标变量列: {col}")
                            values = [row.get(col) for row in sample if row.get(col) is not None]
                            if values:
                                unique_vals = set(str(v) for v in values)
                                if len(unique_vals) <= 5:
                                    result['evidence'].append(f"目标变量为分类问题，可能值: {unique_vals}")
        
        if not result['loan_phase']:
            result['loan_phase'] = 'pre_loan'
            result['loan_phase_name'] = '贷前'
            result['sub_scenario'] = 'credit_scoring'
            result['sub_scenario_name'] = '信用评分'
            result['confidence'] = 0.5
            result['evidence'].append("未检测到明确场景，默认使用贷前-信用评分")
        
        result['detected'] = True
        return result
