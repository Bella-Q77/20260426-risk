import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_simulation_data(scenario='pre_loan', sub_scenario='credit_scoring', dataset_name=None, n_samples=10000):
    """
    根据业务场景生成模拟风控数据
    
    参数:
    - scenario: 贷款阶段 ('pre_loan', 'mid_loan', 'post_loan')
    - sub_scenario: 子场景 ('credit_scoring', 'anti_fraud', 等)
    - dataset_name: 数据集名称（用于根据名称推断场景）
    - n_samples: 样本数量
    
    返回:
    - DataFrame: 模拟的风控数据集
    """
    np.random.seed(42)
    
    if dataset_name:
        dataset_name_lower = dataset_name.lower()
        if any(kw in dataset_name_lower for kw in ['pre_loan', 'preloan', 'application', 'credit_score', '申请', '信用评分']):
            scenario = 'pre_loan'
            sub_scenario = 'credit_scoring'
        elif any(kw in dataset_name_lower for kw in ['fraud', 'anti_fraud', '欺诈', '反欺诈']):
            scenario = 'pre_loan'
            sub_scenario = 'anti_fraud'
        elif any(kw in dataset_name_lower for kw in ['mid_loan', 'midloan', 'behavior', '行为评分', 'monitor', '预警']):
            scenario = 'mid_loan'
            sub_scenario = 'behavior_score'
        elif any(kw in dataset_name_lower for kw in ['post_loan', 'postloan', 'collection', '催收', 'loss', '损失', 'recovery', '回收']):
            scenario = 'post_loan'
            sub_scenario = 'collection_score'
    
    if scenario == 'pre_loan':
        if sub_scenario == 'anti_fraud':
            return _generate_anti_fraud_data(n_samples)
        else:
            return _generate_credit_scoring_data(n_samples)
    elif scenario == 'mid_loan':
        if sub_scenario == 'early_warning':
            return _generate_early_warning_data(n_samples)
        else:
            return _generate_behavior_scoring_data(n_samples)
    elif scenario == 'post_loan':
        if sub_scenario == 'loss_forecast':
            return _generate_loss_forecast_data(n_samples)
        elif sub_scenario == 'recovery_prediction':
            return _generate_recovery_prediction_data(n_samples)
        else:
            return _generate_collection_scoring_data(n_samples)
    else:
        return _generate_credit_scoring_data(n_samples)

def _generate_credit_scoring_data(n_samples=10000):
    """生成信用评分模拟数据 - 贷前场景"""
    
    df = pd.DataFrame()
    
    df['user_id'] = [f'USER_{i:08d}' for i in range(n_samples)]
    
    df['age'] = np.random.randint(22, 65, n_samples)
    df['gender'] = np.random.choice([0, 1], n_samples, p=[0.45, 0.55])
    df['education'] = np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.3, 0.35, 0.2, 0.05])
    
    df['income'] = np.random.lognormal(10, 0.8, n_samples).astype(int)
    df['income_verified'] = np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
    
    df['credit_score'] = np.clip(np.random.normal(650, 80, n_samples), 300, 900).astype(int)
    df['credit_utilization'] = np.random.beta(2, 5, n_samples)
    df['num_credit_lines'] = np.random.poisson(5, n_samples)
    df['delinquency_6m'] = np.random.poisson(0.3, n_samples)
    df['delinquency_hist'] = np.random.poisson(1, n_samples)
    
    df['loan_amount'] = np.random.lognormal(9, 0.7, n_samples).astype(int)
    df['loan_term'] = np.random.choice([3, 6, 12, 24, 36], n_samples, p=[0.1, 0.2, 0.35, 0.25, 0.1])
    df['interest_rate'] = np.random.uniform(0.06, 0.24, n_samples)
    
    df['dti_ratio'] = np.clip(np.random.normal(0.3, 0.15, n_samples), 0, 1)
    df['employment_length'] = np.random.randint(0, 30, n_samples)
    df['residence_length'] = np.random.randint(0, 20, n_samples)
    
    df['phone_verified'] = np.random.choice([0, 1], n_samples, p=[0.1, 0.9])
    df['identity_verified'] = np.random.choice([0, 1], n_samples, p=[0.15, 0.85])
    df['workplace_verified'] = np.random.choice([0, 1], n_samples, p=[0.25, 0.75])
    
    df['inquiries_6m'] = np.random.poisson(2, n_samples)
    df['rejected_applications_12m'] = np.random.poisson(0.5, n_samples)
    
    default_prob = (
        0.05 + 
        0.02 * (df['credit_score'] < 550).astype(int) +
        0.03 * (df['credit_utilization'] > 0.7).astype(int) +
        0.02 * (df['dti_ratio'] > 0.5).astype(int) +
        0.04 * (df['delinquency_6m'] > 0).astype(int) +
        0.03 * (df['inquiries_6m'] > 5).astype(int) +
        0.02 * (df['income_verified'] == 0).astype(int)
    )
    
    df['default'] = (np.random.random(n_samples) < default_prob).astype(int)
    
    fraud_prob = (
        0.02 +
        0.03 * (df['identity_verified'] == 0).astype(int) +
        0.02 * (df['phone_verified'] == 0).astype(int) +
        0.02 * (df['income_verified'] == 0).astype(int)
    )
    
    df['is_fraud'] = (np.random.random(n_samples) < fraud_prob).astype(int)
    df.loc[df['is_fraud'] == 1, 'default'] = 1
    
    df['application_date'] = [
        (datetime.now() - timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d')
        for _ in range(n_samples)
    ]
    
    cols = ['user_id', 'application_date', 'age', 'gender', 'education', 
            'income', 'income_verified', 'employment_length', 'residence_length',
            'credit_score', 'credit_utilization', 'num_credit_lines', 
            'delinquency_6m', 'delinquency_hist', 'inquiries_6m', 'rejected_applications_12m',
            'loan_amount', 'loan_term', 'interest_rate', 'dti_ratio',
            'phone_verified', 'identity_verified', 'workplace_verified',
            'is_fraud', 'default']
    
    return df[cols]

def _generate_anti_fraud_data(n_samples=10000):
    """生成反欺诈模拟数据 - 贷前场景"""
    
    df = pd.DataFrame()
    
    df['user_id'] = [f'USER_{i:08d}' for i in range(n_samples)]
    df['application_id'] = [f'APP_{i:010d}' for i in range(n_samples)]
    
    df['age'] = np.random.randint(18, 70, n_samples)
    df['gender'] = np.random.choice([0, 1], n_samples, p=[0.45, 0.55])
    
    df['registration_days'] = np.random.randint(0, 1825, n_samples)
    df['login_count_7d'] = np.random.poisson(3, n_samples)
    df['login_count_30d'] = np.random.poisson(10, n_samples)
    
    df['device_count'] = np.random.randint(1, 5, n_samples)
    df['ip_count_7d'] = np.random.randint(1, 10, n_samples)
    df['location_change_7d'] = np.random.randint(0, 5, n_samples)
    
    df['phone_registration_days'] = np.random.randint(0, 3650, n_samples)
    df['phone_match_name'] = np.random.choice([0, 1], n_samples, p=[0.15, 0.85])
    df['phone_match_idcard'] = np.random.choice([0, 1], n_samples, p=[0.1, 0.9])
    
    df['idcard_age_match'] = np.random.choice([0, 1], n_samples, p=[0.05, 0.95])
    df['idcard_gender_match'] = np.random.choice([0, 1], n_samples, p=[0.03, 0.97])
    df['idcard_province_match'] = np.random.choice([0, 1], n_samples, p=[0.2, 0.8])
    
    df['loan_amount'] = np.random.lognormal(8, 0.8, n_samples).astype(int)
    df['loan_purpose'] = np.random.choice(['消费', '经营', '装修', '教育', '医疗', '其他'], n_samples)
    
    df['bankcard_count'] = np.random.randint(0, 8, n_samples)
    df['bankcard_verified'] = np.random.choice([0, 1], n_samples, p=[0.2, 0.8])
    
    df['contact_count'] = np.random.randint(0, 50, n_samples)
    df['blacklist_contact_count'] = np.random.randint(0, 5, n_samples)
    
    df['ocr_success'] = np.random.choice([0, 1], n_samples, p=[0.05, 0.95])
    df['face_verify_success'] = np.random.choice([0, 1], n_samples, p=[0.03, 0.97])
    df['face_similarity'] = np.random.uniform(0.5, 1.0, n_samples)
    
    df['risk_score'] = np.clip(np.random.normal(50, 20, n_samples), 0, 100).astype(int)
    
    fraud_prob = (
        0.03 +
        0.05 * (df['registration_days'] < 7).astype(int) +
        0.04 * (df['ip_count_7d'] > 3).astype(int) +
        0.03 * (df['device_count'] > 2).astype(int) +
        0.05 * (df['phone_match_name'] == 0).astype(int) +
        0.04 * (df['idcard_age_match'] == 0).astype(int) +
        0.05 * (df['face_verify_success'] == 0).astype(int) +
        0.03 * (df['face_similarity'] < 0.7).astype(int) +
        0.04 * (df['blacklist_contact_count'] > 0).astype(int) +
        0.02 * (df['risk_score'] > 70).astype(int)
    )
    
    df['is_fraud'] = (np.random.random(n_samples) < fraud_prob).astype(int)
    
    df['fraud_type'] = df['is_fraud'].apply(
        lambda x: np.random.choice(['身份冒用', '团伙欺诈', '虚假信息', '异常行为', '其他']) 
        if x == 1 else '正常'
    )
    
    df['application_time'] = [
        datetime.now().replace(hour=np.random.randint(0, 24), 
                                minute=np.random.randint(0, 60)).strftime('%Y-%m-%d %H:%M:%S')
        for _ in range(n_samples)
    ]
    
    cols = ['application_id', 'user_id', 'application_time', 'age', 'gender',
            'registration_days', 'login_count_7d', 'login_count_30d',
            'device_count', 'ip_count_7d', 'location_change_7d',
            'phone_registration_days', 'phone_match_name', 'phone_match_idcard',
            'idcard_age_match', 'idcard_gender_match', 'idcard_province_match',
            'bankcard_count', 'bankcard_verified',
            'contact_count', 'blacklist_contact_count',
            'ocr_success', 'face_verify_success', 'face_similarity',
            'loan_amount', 'loan_purpose',
            'risk_score', 'is_fraud', 'fraud_type']
    
    return df[cols]

def _generate_behavior_scoring_data(n_samples=10000):
    """生成行为评分模拟数据 - 贷中场景"""
    
    df = pd.DataFrame()
    
    df['user_id'] = [f'USER_{i:08d}' for i in range(n_samples)]
    df['loan_id'] = [f'LOAN_{i:010d}' for i in range(n_samples)]
    
    df['orig_credit_score'] = np.clip(np.random.normal(680, 70, n_samples), 300, 900).astype(int)
    df['current_credit_score'] = df['orig_credit_score'] + np.random.randint(-100, 50, n_samples)
    df['current_credit_score'] = np.clip(df['current_credit_score'], 300, 900)
    
    df['loan_amount'] = np.random.lognormal(9, 0.7, n_samples).astype(int)
    df['loan_term'] = np.random.choice([12, 24, 36, 48, 60], n_samples)
    df['remaining_term'] = np.random.randint(0, df['loan_term'] + 1)
    df['interest_rate'] = np.random.uniform(0.06, 0.24, n_samples)
    
    df['outstanding_principal'] = (df['loan_amount'] * df['remaining_term'] / df['loan_term']).astype(int)
    df['total_paid'] = df['loan_amount'] - df['outstanding_principal']
    
    df['payment_days_since'] = np.random.randint(0, 60, n_samples)
    df['days_past_due'] = np.random.choice([0, 1, 3, 7, 15, 30, 60], n_samples, 
                                            p=[0.85, 0.05, 0.03, 0.025, 0.02, 0.015, 0.01])
    
    df['max_dpd_3m'] = np.maximum(df['days_past_due'], np.random.choice([0, 1, 3, 7, 15, 30], n_samples, 
                                                                           p=[0.8, 0.06, 0.04, 0.03, 0.04, 0.03]))
    df['max_dpd_6m'] = np.maximum(df['max_dpd_3m'], np.random.choice([0, 1, 3, 7, 15, 30, 60], n_samples,
                                                                         p=[0.75, 0.07, 0.05, 0.04, 0.04, 0.03, 0.02]))
    
    df['on_time_payments'] = np.random.poisson(df['loan_term'] - df['remaining_term'] - df['max_dpd_6m'] / 30, n_samples)
    df['on_time_payments'] = np.minimum(df['on_time_payments'], df['loan_term'] - df['remaining_term'])
    
    df['utilization_ratio'] = np.random.beta(2, 5, n_samples)
    df['balance_change_3m'] = np.random.uniform(-0.3, 0.5, n_samples)
    
    df['monthly_income_est'] = np.random.lognormal(10, 0.8, n_samples).astype(int)
    df['monthly_payment'] = (df['loan_amount'] * df['interest_rate'] / 12 * 
                              (1 + df['interest_rate'] / 12) ** df['loan_term'] / 
                              ((1 + df['interest_rate'] / 12) ** df['loan_term'] - 1)).astype(int)
    df['current_dti'] = df['monthly_payment'] / df['monthly_income_est']
    
    df['transaction_count_30d'] = np.random.poisson(20, n_samples)
    df['transaction_amount_30d'] = np.random.lognormal(8, 1, n_samples).astype(int)
    df['large_transaction_count'] = np.random.poisson(2, n_samples)
    
    df['login_count_7d'] = np.random.poisson(5, n_samples)
    df['login_count_30d'] = np.random.poisson(15, n_samples)
    df['app_opens_7d'] = np.random.poisson(10, n_samples)
    
    df['inquiry_count_3m'] = np.random.poisson(1, n_samples)
    df['new_credit_lines_6m'] = np.random.poisson(0.5, n_samples)
    
    df['contact_attempts_30d'] = np.random.poisson(0.3, n_samples)
    df['promise_to_pay'] = np.random.choice([0, 1], n_samples, p=[0.9, 0.1])
    
    default_prob = (
        0.03 +
        0.1 * (df['days_past_due'] >= 30).astype(int) +
        0.05 * (df['days_past_due'] >= 15).astype(int) +
        0.03 * (df['days_past_due'] >= 7).astype(int) +
        0.04 * (df['max_dpd_6m'] >= 30).astype(int) +
        0.03 * (df['current_credit_score'] < 580).astype(int) +
        0.02 * (df['current_dti'] > 0.5).astype(int) +
        0.03 * (df['utilization_ratio'] > 0.8).astype(int) +
        0.02 * (df['inquiry_count_3m'] > 3).astype(int) +
        0.02 * (df['login_count_7d'] == 0).astype(int)
    )
    
    df['default_risk'] = (np.random.random(n_samples) < default_prob).astype(int)
    
    df['behavior_score'] = np.clip(
        600 - 50 * df['default_risk'] + 
        np.random.normal(0, 30, n_samples) -
        df['days_past_due'] * 2 -
        (df['current_credit_score'] - 650) * 0.1,
        300, 900
    ).astype(int)
    
    df['risk_level'] = pd.cut(df['behavior_score'], 
                               bins=[0, 550, 620, 680, 750, 1000],
                               labels=['高风险', '中高风险', '中风险', '中低风险', '低风险'])
    
    df['report_date'] = datetime.now().strftime('%Y-%m-%d')
    
    cols = ['loan_id', 'user_id', 'report_date',
            'orig_credit_score', 'current_credit_score',
            'loan_amount', 'loan_term', 'remaining_term', 'interest_rate',
            'outstanding_principal', 'total_paid', 'monthly_payment',
            'payment_days_since', 'days_past_due', 'max_dpd_3m', 'max_dpd_6m',
            'on_time_payments', 'utilization_ratio', 'balance_change_3m',
            'monthly_income_est', 'current_dti',
            'transaction_count_30d', 'transaction_amount_30d', 'large_transaction_count',
            'login_count_7d', 'login_count_30d', 'app_opens_7d',
            'inquiry_count_3m', 'new_credit_lines_6m',
            'contact_attempts_30d', 'promise_to_pay',
            'behavior_score', 'risk_level', 'default_risk']
    
    return df[cols]

def _generate_early_warning_data(n_samples=10000):
    """生成贷中预警模拟数据"""
    
    df = _generate_behavior_scoring_data(n_samples)
    
    df['warning_level'] = df['default_risk'].apply(
        lambda x: np.random.choice(['红色预警', '黄色预警', '蓝色预警']) if x == 1 else '正常'
    )
    
    df['warning_reason'] = df.apply(
        lambda row: 
            '逾期超过30天' if row['days_past_due'] >= 30 else
            '逾期超过15天' if row['days_past_due'] >= 15 else
            '征信评分大幅下降' if row['current_credit_score'] - row['orig_credit_score'] < -50 else
            '负债比率过高' if row['current_dti'] > 0.6 else
            '账户活跃度异常' if row['login_count_7d'] == 0 else
            '无预警',
        axis=1
    )
    
    df['action_required'] = df['warning_level'].apply(
        lambda x: 
            '立即催收、冻结额度' if x == '红色预警' else
            '电话提醒、降低额度' if x == '黄色预警' else
            '短信提醒、关注' if x == '蓝色预警' else
            '无需操作'
    )
    
    return df

def _generate_collection_scoring_data(n_samples=10000):
    """生成催收评分模拟数据 - 贷后场景"""
    
    df = pd.DataFrame()
    
    df['user_id'] = [f'USER_{i:08d}' for i in range(n_samples)]
    df['loan_id'] = [f'LOAN_{i:010d}' for i in range(n_samples)]
    
    df['default_date'] = [
        (datetime.now() - timedelta(days=np.random.randint(30, 365))).strftime('%Y-%m-%d')
        for _ in range(n_samples)
    ]
    
    df['days_in_collection'] = [(datetime.now() - datetime.strptime(d, '%Y-%m-%d')).days 
                                for d in df['default_date']]
    
    df['bucket'] = pd.cut(df['days_in_collection'],
                           bins=[0, 30, 60, 90, 180, 365, 1000],
                           labels=['M1', 'M2', 'M3', 'M4', 'M5', 'M6+'])
    
    df['outstanding_principal'] = np.random.lognormal(8, 0.8, n_samples).astype(int)
    df['outstanding_interest'] = (df['outstanding_principal'] * np.random.uniform(0.05, 0.25, n_samples)).astype(int)
    df['outstanding_penalty'] = (df['outstanding_principal'] * np.random.uniform(0.01, 0.1, n_samples)).astype(int)
    df['total_outstanding'] = df['outstanding_principal'] + df['outstanding_interest'] + df['outstanding_penalty']
    
    df['collection_attempts'] = np.random.poisson(df['days_in_collection'] / 15, n_samples)
    df['contact_success_rate'] = np.random.uniform(0, 1, n_samples)
    df['last_contact_days'] = np.random.randint(0, 60, n_samples)
    
    df['promise_count'] = np.random.poisson(2, n_samples)
    df['kept_promise_count'] = np.random.binomial(df['promise_count'], 0.3, n_samples)
    df['broken_promise_count'] = df['promise_count'] - df['kept_promise_count']
    
    df['partial_payment_count'] = np.random.poisson(1, n_samples)
    df['total_partial_paid'] = (df['total_outstanding'] * np.random.uniform(0, 0.3, n_samples)).astype(int)
    
    df['phone_numbers'] = np.random.randint(1, 5, n_samples)
    df['valid_phone_numbers'] = np.random.randint(0, df['phone_numbers'] + 1)
    df['address_count'] = np.random.randint(1, 4, n_samples)
    df['workplace_known'] = np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
    
    df['contact_alternatives'] = np.random.randint(0, 10, n_samples)
    df['emergency_contact_reachable'] = np.random.choice([0, 1], n_samples, p=[0.4, 0.6])
    
    df['historical_delinquency'] = np.random.poisson(3, n_samples)
    df['max_historical_dpd'] = np.random.choice([30, 60, 90, 180], n_samples, p=[0.4, 0.3, 0.2, 0.1])
    
    df['last_credit_score'] = np.clip(np.random.normal(550, 80, n_samples), 300, 900).astype(int)
    
    df['repayment_probability'] = np.clip(
        0.5 +
        0.2 * (df['kept_promise_count'] > 0).astype(int) +
        0.1 * (df['valid_phone_numbers'] > 1).astype(int) +
        0.1 * (df['workplace_known'] == 1).astype(int) +
        0.15 * (df['contact_success_rate'] > 0.5).astype(int) +
        -0.15 * (df['days_in_collection'] > 90).astype(int) +
        -0.1 * (df['broken_promise_count'] > 2).astype(int) +
        np.random.normal(0, 0.1, n_samples),
        0, 1
    )
    
    df['collection_score'] = (df['repayment_probability'] * 600 + 100).astype(int)
    df['collection_score'] = np.clip(df['collection_score'], 100, 700)
    
    df['collection_priority'] = pd.cut(df['collection_score'],
                                        bins=[0, 250, 400, 550, 700],
                                        labels=['低优先级', '中低优先级', '中高优先级', '高优先级'])
    
    df['recommended_action'] = df['collection_priority'].apply(
        lambda x: 
            '司法催收、委外催收' if x == '低优先级' else
            '上门催收、联系亲友' if x == '中低优先级' else
            '电话催收、短信提醒' if x == '中高优先级' else
            '温柔提醒、优惠协商'
    )
    
    df['expected_recovery_rate'] = df['repayment_probability'] * np.random.uniform(0.3, 0.9, n_samples)
    df['expected_recovery_amount'] = (df['total_outstanding'] * df['expected_recovery_rate']).astype(int)
    
    cols = ['loan_id', 'user_id', 'default_date', 'days_in_collection', 'bucket',
            'outstanding_principal', 'outstanding_interest', 'outstanding_penalty', 'total_outstanding',
            'collection_attempts', 'contact_success_rate', 'last_contact_days',
            'promise_count', 'kept_promise_count', 'broken_promise_count',
            'partial_payment_count', 'total_partial_paid',
            'phone_numbers', 'valid_phone_numbers', 'address_count', 'workplace_known',
            'contact_alternatives', 'emergency_contact_reachable',
            'historical_delinquency', 'max_historical_dpd', 'last_credit_score',
            'repayment_probability', 'collection_score', 'collection_priority',
            'recommended_action', 'expected_recovery_rate', 'expected_recovery_amount']
    
    return df[cols]

def _generate_loss_forecast_data(n_samples=10000):
    """生成损失预测模拟数据"""
    
    df = _generate_collection_scoring_data(n_samples)
    
    df['lgd_probability'] = np.clip(
        0.3 +
        0.2 * (df['days_in_collection'] > 180).astype(int) +
        0.15 * (df['days_in_collection'] > 90).astype(int) +
        0.1 * (df['valid_phone_numbers'] == 0).astype(int) +
        0.1 * (df['workplace_known'] == 0).astype(int) +
        0.15 * (df['broken_promise_count'] > 3).astype(int) +
        -0.1 * (df['last_credit_score'] > 600).astype(int) +
        np.random.normal(0, 0.1, n_samples),
        0, 1
    )
    
    df['loss_given_default'] = df['lgd_probability'] * np.random.uniform(0.4, 1.0, n_samples)
    
    df['expected_loss'] = (df['total_outstanding'] * df['loss_given_default']).astype(int)
    df['loss_category'] = pd.cut(df['loss_given_default'],
                                  bins=[0, 0.3, 0.6, 0.8, 1.0],
                                  labels=['低损失', '中低损失', '中高损失', '高损失'])
    
    df['write_off_probability'] = np.clip(df['lgd_probability'] * 1.2, 0, 1)
    df['recommended_write_off'] = df['write_off_probability'] > 0.7
    
    return df

def _generate_recovery_prediction_data(n_samples=10000):
    """生成回收率预测模拟数据"""
    
    df = _generate_collection_scoring_data(n_samples)
    
    actual_recovery = df['repayment_probability'] * np.random.uniform(0.2, 0.95, n_samples)
    df['actual_recovery_rate'] = actual_recovery
    df['actual_recovery_amount'] = (df['total_outstanding'] * actual_recovery).astype(int)
    
    df['recovery_timeline_days'] = np.clip(
        np.random.poisson(df['days_in_collection'] / 2, n_samples) + 30,
        30, 365
    )
    
    df['recovery_method'] = np.random.choice(
        ['电话催收', '短信催收', '上门催收', '司法催收', '委外催收', '协商还款'],
        n_samples,
        p=[0.3, 0.2, 0.15, 0.1, 0.1, 0.15]
    )
    
    df['settlement_discount'] = np.where(
        df['recovery_method'] == '协商还款',
        np.random.uniform(0.2, 0.5, n_samples),
        0
    )
    
    return df
