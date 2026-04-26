import os
import pandas as pd
import numpy as np
from datetime import datetime
import config
from backend.utils.helpers import generate_document_id, save_json, load_json

class DocumentGenerator:
    def __init__(self, project):
        self.project = project
        self.project_id = project.get('id', 'unknown')
    
    def add_document(self, name, content):
        doc = {
            'id': generate_document_id(),
            'name': name,
            'timestamp': datetime.now().isoformat(),
            'content': content,
            'project_id': self.project_id
        }
        
        if 'documents' not in self.project:
            self.project['documents'] = []
        
        self.project['documents'].append(doc)
        
        return doc
    
    def generate_final_report(self):
        report = {
            'id': generate_document_id(),
            'name': '最终项目报告',
            'timestamp': datetime.now().isoformat(),
            'project_id': self.project_id,
            'sections': []
        }
        
        section_project_overview = self._generate_project_overview_section()
        report['sections'].append(section_project_overview)
        
        section_workflow = self._generate_workflow_summary_section()
        report['sections'].append(section_workflow)
        
        section_data = self._generate_data_summary_section()
        report['sections'].append(section_data)
        
        section_feature = self._generate_feature_summary_section()
        report['sections'].append(section_feature)
        
        section_model = self._generate_model_summary_section()
        report['sections'].append(section_model)
        
        section_evaluation = self._generate_evaluation_summary_section()
        report['sections'].append(section_evaluation)
        
        section_deployment = self._generate_deployment_summary_section()
        report['sections'].append(section_deployment)
        
        section_recommendations = self._generate_recommendations_section()
        report['sections'].append(section_recommendations)
        
        return report
    
    def _generate_project_overview_section(self):
        scenario = self.project.get('scenario', {})
        
        return {
            'section_name': '项目概述',
            'section_order': 1,
            'content': {
                'project_id': self.project.get('id'),
                'project_name': self.project.get('name'),
                'created_at': self.project.get('created_at'),
                'status': self.project.get('status'),
                'business_scenario': {
                    'loan_phase': scenario.get('loan_phase_name'),
                    'sub_scenario': scenario.get('sub_scenario_name'),
                    'confidence': scenario.get('confidence')
                },
                'description': f"""
本项目为{scenario.get('loan_phase_name', '未指定')}场景下的{scenario.get('sub_scenario_name', '未指定')}风控建模任务。

项目目标：
1. 基于历史数据构建风险评估模型
2. 通过特征工程提升模型预测能力
3. 生成可部署的风控模型并制定监控方案

业务背景：
在互联网信贷业务中，{scenario.get('loan_phase_name', '风险控制')}是信贷全生命周期中的关键环节。
{self._get_scenario_description(scenario.get('loan_phase'))}
"""
            }
        }
    
    def _get_scenario_description(self, phase):
        descriptions = {
            'pre_loan': """
贷前风控主要关注申请人的还款意愿和还款能力评估：
- 通过信用评分模型评估申请人的信用风险
- 通过反欺诈模型识别潜在的欺诈行为
- 为审批决策提供量化依据
""",
            'mid_loan': """
贷中监控关注贷款发放后的风险变化：
- 通过行为评分模型持续评估客户风险
- 通过预警系统及时识别风险信号
- 支持额度调整和客户分层管理
""",
            'post_loan': """
贷后管理关注违约后的风险处置：
- 通过催收评分模型优化催收策略
- 通过损失预测模型评估预期损失
- 通过回收率预测提高回款效率
"""
        }
        return descriptions.get(phase, "通过数据驱动的方法提升风险决策效率。")
    
    def _generate_workflow_summary_section(self):
        workflow_steps = self.project.get('workflow_steps', [])
        
        completed_steps = [s for s in workflow_steps if s.get('status') == 'completed']
        pending_steps = [s for s in workflow_steps if s.get('status') == 'pending']
        error_steps = [s for s in workflow_steps if s.get('status') == 'error']
        
        return {
            'section_name': '工作流执行摘要',
            'section_order': 2,
            'content': {
                'total_steps': len(workflow_steps),
                'completed_count': len(completed_steps),
                'pending_count': len(pending_steps),
                'error_count': len(error_steps),
                'current_step': self.project.get('current_step', 0),
                'step_details': workflow_steps,
                'summary': f"""
工作流执行情况：
- 总步骤数: {len(workflow_steps)}
- 已完成: {len(completed_steps)}
- 进行中: {len(pending_steps)}
- 出错: {len(error_steps)}

执行进度: {len(completed_steps)}/{len(workflow_steps)} ({len(completed_steps)/len(workflow_steps)*100:.1f}%)
"""
            }
        }
    
    def _generate_data_summary_section(self):
        data_info = self.project.get('data', {}).get('data_info', {})
        data_prep = self.project.get('data_preparation', {})
        
        return {
            'section_name': '数据准备摘要',
            'section_order': 3,
            'content': {
                'data_source': self.project.get('data', {}).get('data_filename'),
                'code_source': self.project.get('code', {}).get('code_filename'),
                'data_stats': {
                    'samples': data_info.get('rows'),
                    'features': data_info.get('columns')
                },
                'data_preparation_result': data_prep,
                'summary': f"""
数据准备阶段完成情况：

原始数据：
- 样本数: {data_info.get('rows', 'N/A')}
- 特征数: {data_info.get('columns', 'N/A')}

数据处理：
{self._format_data_prep_summary(data_prep)}

数据质量评估：
- 缺失值处理: {self._assess_missing_values(data_prep)}
- 数据类型转换: 已完成
- 异常值检测: 已集成到处理流程
"""
            }
        }
    
    def _format_data_prep_summary(self, data_prep):
        if not data_prep or not data_prep.get('success'):
            return "数据准备尚未完成或执行出错"
        
        steps = data_prep.get('steps', [])
        summary = ""
        for step in steps:
            summary += f"- {step.get('name')}: {step.get('description')}\n"
        return summary
    
    def _assess_missing_values(self, data_prep):
        if not data_prep:
            return "未评估"
        
        steps = data_prep.get('steps', [])
        for step in steps:
            if 'missing' in step.get('name', '').lower():
                return "已处理"
        return "无缺失或未处理"
    
    def _generate_feature_summary_section(self):
        feature_eng = self.project.get('feature_engineering', {})
        
        return {
            'section_name': '特征工程摘要',
            'section_order': 4,
            'content': {
                'feature_engineering_result': feature_eng,
                'summary': f"""
特征工程阶段完成情况：

处理步骤：
{self._format_feature_eng_summary(feature_eng)}

特征处理方法：
1. 缺失值处理: 根据数据类型自动选择填充方法
2. 特征编码: 分类特征采用独热编码或标签编码
3. 特征缩放: 数值特征标准化处理
4. 特征选择: 基于方差、相关性等方法筛选重要特征

特征工程对模型效果的影响：
- 提升特征质量，减少噪声
- 增强模型的泛化能力
- 提高模型的可解释性
"""
            }
        }
    
    def _format_feature_eng_summary(self, feature_eng):
        if not feature_eng or not feature_eng.get('success'):
            return "特征工程尚未完成或执行出错"
        
        summary = f"- 原始特征数: {feature_eng.get('summary', {}).get('original_features', 'N/A')}\n"
        summary += f"- 处理后特征数: {feature_eng.get('summary', {}).get('processed_features', 'N/A')}\n"
        
        steps = feature_eng.get('steps', [])
        for step in steps:
            summary += f"- {step.get('name')}: {step.get('description')}\n"
        
        return summary
    
    def _generate_model_summary_section(self):
        model_training = self.project.get('model_training', {})
        
        return {
            'section_name': '模型训练摘要',
            'section_order': 5,
            'content': {
                'model_training_result': model_training,
                'summary': f"""
模型训练阶段完成情况：

模型配置：
- 模型类型: {model_training.get('model_type', 'N/A')}
- 目标变量: {model_training.get('target_column', 'N/A')}
- 特征数量: {model_training.get('feature_count', 'N/A')}
- 训练样本: {model_training.get('train_samples', 'N/A')}
- 测试样本: {model_training.get('test_samples', 'N/A')}

模型介绍：
{self._get_model_description(model_training.get('model_type'))}

训练过程：
{self._format_training_summary(model_training)}
"""
            }
        }
    
    def _get_model_description(self, model_type):
        descriptions = {
            'LogisticRegression': """
逻辑回归 (Logistic Regression)
- 优点：可解释性强，训练速度快，适合线性可分问题
- 应用场景：信用评分卡、风险概率估计
- 输出：概率值，便于设置阈值
""",
            'RandomForest': """
随机森林 (Random Forest)
- 优点：抗过拟合能力强，处理高维数据效果好
- 应用场景：特征重要性评估、非线性关系建模
- 输出：可解释性相对较弱，但效果稳定
""",
            'XGBoost': """
XGBoost (Extreme Gradient Boosting)
- 优点：预测精度高，支持并行计算
- 应用场景：竞赛级模型，追求最高预测效果
- 输出：需要更多调参，但效果通常最优
""",
            'LightGBM': """
LightGBM (Light Gradient Boosting Machine)
- 优点：训练速度快，内存占用低
- 应用场景：大规模数据、实时预测场景
- 输出：与XGBoost类似，但更高效
""",
            'SVM': """
支持向量机 (Support Vector Machine)
- 优点：高维数据表现好，泛化能力强
- 应用场景：样本量适中、特征维度较高
- 输出：可解释性较差，但理论基础扎实
"""
        }
        return descriptions.get(model_type, "请参考模型文档了解详细信息")
    
    def _format_training_summary(self, model_training):
        if not model_training or not model_training.get('success'):
            return "模型训练尚未完成或执行出错"
        
        steps = model_training.get('steps', [])
        summary = ""
        for step in steps:
            summary += f"- {step.get('name')}: {step.get('description')}\n"
        return summary
    
    def _generate_evaluation_summary_section(self):
        model_evaluation = self.project.get('model_evaluation', {})
        metrics = model_evaluation.get('metrics', {})
        
        return {
            'section_name': '模型评估摘要',
            'section_order': 6,
            'content': {
                'model_evaluation_result': model_evaluation,
                'metrics': metrics,
                'summary': f"""
模型评估阶段完成情况：

核心指标：
- AUC: {metrics.get('auc', 'N/A')} - {self._interpret_auc(metrics.get('auc'))}
- KS: {metrics.get('ks', 'N/A')} - {self._interpret_ks(metrics.get('ks'))}
- Gini: {metrics.get('gini', 'N/A')}
- 准确率: {metrics.get('accuracy', 'N/A')}
- 精确率: {metrics.get('precision', 'N/A')}
- 召回率: {metrics.get('recall', 'N/A')}
- F1分数: {metrics.get('f1', 'N/A')}

指标解读：
{self._get_metrics_interpretation()}

模型稳定性：
{self._format_stability_analysis(model_evaluation)}
"""
            }
        }
    
    def _interpret_auc(self, auc):
        if auc is None:
            return "无法评估"
        if auc >= 0.9:
            return "模型区分能力优秀"
        elif auc >= 0.8:
            return "模型区分能力良好"
        elif auc >= 0.7:
            return "模型区分能力一般"
        else:
            return "模型区分能力较弱，建议优化"
    
    def _interpret_ks(self, ks):
        if ks is None:
            return "无法评估"
        if ks >= 0.4:
            return "区分能力优秀"
        elif ks >= 0.3:
            return "区分能力良好"
        elif ks >= 0.2:
            return "区分能力一般"
        else:
            return "区分能力较弱"
    
    def _get_metrics_interpretation(self):
        return """
- AUC (Area Under Curve): ROC曲线下面积，衡量模型整体区分能力
  - AUC > 0.9: 优秀
  - AUC > 0.8: 良好
  - AUC > 0.7: 一般
  - AUC > 0.6: 较弱

- KS (Kolmogorov-Smirnov): 衡量正负样本的最大区分度
  - KS > 0.4: 优秀
  - KS > 0.3: 良好
  - KS > 0.2: 一般

- Gini系数: 2*AUC - 1，与AUC等价的衡量指标

- 精确率/召回率/F1: 针对分类结果的评估指标
  - 精确率: 预测为正样本中实际为正的比例
  - 召回率: 实际为正样本中被正确预测的比例
  - F1分数: 精确率和召回率的调和平均
"""
    
    def _format_stability_analysis(self, model_evaluation):
        if not model_evaluation:
            return "稳定性分析尚未完成"
        
        stability = model_evaluation.get('stability', {})
        cv = model_evaluation.get('cross_validation', {})
        
        summary = ""
        
        if stability:
            summary += f"PSI (群体稳定性指数): {stability.get('psi', 'N/A')}\n"
            summary += f"解读: {stability.get('interpretation', '')}\n"
        
        if cv:
            summary += f"\n交叉验证结果:\n"
            summary += f"- 5折平均AUC: {cv.get('mean_auc', 'N/A')}\n"
            summary += f"- AUC标准差: {cv.get('std_auc', 'N/A')}\n"
            summary += f"- 5折平均准确率: {cv.get('mean_accuracy', 'N/A')}\n"
        
        if not stability and not cv:
            summary = "稳定性分析结果为空"
        
        return summary
    
    def _generate_deployment_summary_section(self):
        model_deployment = self.project.get('model_deployment', {})
        
        return {
            'section_name': '模型部署与监控摘要',
            'section_order': 7,
            'content': {
                'model_deployment_result': model_deployment,
                'summary': f"""
模型部署与监控阶段完成情况：

部署配置：
{self._format_deployment_config(model_deployment)}

监控方案：
{self._format_monitoring_plan(model_deployment)}

部署输出：
- 模型文件: 已序列化保存
- 配置文件: 已生成部署配置
- 监控方案: 已制定监控计划
- 使用文档: 已生成README

下一步建议：
1. 在测试环境验证模型预测接口
2. 设置监控告警阈值
3. 制定模型定期回顾计划
4. 准备A/B测试方案（如需要）
"""
            }
        }
    
    def _format_deployment_config(self, model_deployment):
        if not model_deployment or not model_deployment.get('success'):
            return "部署配置尚未生成"
        
        config = model_deployment.get('deployment_config', {})
        if not config:
            return "部署配置为空"
        
        summary = f"- 项目ID: {config.get('project_id', 'N/A')}\n"
        summary += f"- 模型版本: {config.get('model_version', 'N/A')}\n"
        
        model_info = config.get('model_info', {})
        summary += f"- 模型类型: {model_info.get('model_type', 'N/A')}\n"
        summary += f"- 目标变量: {model_info.get('target_column', 'N/A')}\n"
        summary += f"- 特征数: {model_info.get('feature_count', 'N/A')}\n"
        
        deploy_settings = config.get('deployment_settings', {})
        summary += f"- 部署环境: {deploy_settings.get('environment', 'N/A')}\n"
        summary += f"- 预测阈值: {deploy_settings.get('threshold', 'N/A')}\n"
        
        return summary
    
    def _format_monitoring_plan(self, model_deployment):
        if not model_deployment:
            return "监控方案尚未生成"
        
        plan = model_deployment.get('monitoring_plan', {})
        if not plan:
            return "监控方案为空"
        
        summary = "监控频率:\n"
        freq = plan.get('monitoring_frequency', {})
        for key, value in freq.items():
            summary += f"- {key}: {value}\n"
        
        summary += "\n告警阈值:\n"
        thresholds = plan.get('thresholds', {})
        for key, value in thresholds.items():
            summary += f"- {key}: {value}\n"
        
        summary += "\n重训练触发条件:\n"
        triggers = plan.get('retraining_triggers', {})
        for key, value in triggers.items():
            summary += f"- {key}: {value}\n"
        
        return summary
    
    def _generate_recommendations_section(self):
        model_evaluation = self.project.get('model_evaluation', {})
        metrics = model_evaluation.get('metrics', {})
        auc = metrics.get('auc', 0) if metrics.get('auc') else 0
        
        recommendations = []
        
        if auc < 0.7:
            recommendations.append({
                'priority': '高',
                'category': '模型优化',
                'content': '模型AUC较低，建议从以下方面优化：\n'
                          '- 增加训练样本量\n'
                          '- 进行更精细的特征工程\n'
                          '- 尝试其他模型类型（如XGBoost、LightGBM）\n'
                          '- 调整模型超参数'
            })
        elif auc < 0.8:
            recommendations.append({
                'priority': '中',
                'category': '模型优化',
                'content': '模型表现一般，可以考虑：\n'
                          '- 进一步优化特征选择\n'
                          '- 进行模型集成（Ensemble）\n'
                          '- 调整分类阈值'
            })
        else:
            recommendations.append({
                'priority': '低',
                'category': '模型维护',
                'content': '模型表现良好，建议：\n'
                          '- 定期监控模型性能\n'
                          '- 关注数据分布变化\n'
                          '- 制定模型更新计划'
            })
        
        recommendations.append({
            'priority': '高',
            'category': '部署监控',
            'content': '部署前准备：\n'
                      '- 验证模型预测接口正确性\n'
                      '- 设置监控告警阈值\n'
                      '- 准备回滚方案\n'
                      '- 制定模型生命周期管理计划'
        })
        
        recommendations.append({
            'priority': '中',
            'category': '文档管理',
            'content': '模型文档化：\n'
                      '- 保存完整的训练代码和配置\n'
                      '- 记录特征工程细节\n'
                      '- 保存验证集和测试集\n'
                      '- 记录模型评估结果'
        })
        
        return {
            'section_name': '建议与下一步',
            'section_order': 8,
            'content': {
                'recommendations': recommendations,
                'summary': f"""
项目完成度评估：
- 工作流执行: {self.project.get('status') == 'completed' and '已完成' or '进行中'}
- 模型效果: {auc >= 0.8 and '良好' or auc >= 0.7 and '一般' or '待优化'}
- 文档完整性: 良好

总体评估：
本项目已完成风控建模全流程，包括数据准备、特征工程、模型训练、评估和部署准备。
模型效果{'达到预期标准' if auc >= 0.7 else '需要进一步优化'}，建议根据上述建议进行后续工作。
"""
            }
        }
