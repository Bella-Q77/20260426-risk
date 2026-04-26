import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_simulation_data(scenario=None, sub_scenario=None, dataset_name=None, n_samples=10000):
    np.random.seed(42)
    random.seed(42)
    
    data = {}
    default_rate = 0.05
    
    if scenario == 'pre_loan':
        default_rate = 0.03
        data = generate_pre_loan_data(n_samples, sub_scenario)
    elif scenario == 'mid_loan':
        default_rate = 0.05
        data = generate_mid_loan_data(n_samples, sub_scenario)
    elif scenario == 'post_loan':
        default_rate = 0.15
        data = generate_post_loan_data(n_samples, sub_scenario)
    else:
        data = generate_generic_credit_data(n_samples, default_rate)
    
    return data

def generate_generic_credit_data(n_samples, default_rate=0.05):
    n_default = int(n_samples * default_rate)
    n_good = n_samples - n_default
    
    data = pd.DataFrame()
    
    data['user_id'] = [f'U{i:06d}' for i in range(n_samples)]
    
    data['age'] = np.concatenate([
        np.random.normal(40, 12, n_good),
        np.random.normal(35, 10, n_default)
    ]).clip(18, 70).astype(int)
    
    data['income'] = np.concatenate([
        np.random.lognormal(10.5, 0.8, n_good),
        np.random.lognormal(9.8, 0.9, n_default)
    ]).astype(int)
    
    data['loan_amount'] = np.concatenate([
        np.random.lognormal(10, 0.7, n_good),
        np.random.lognormal(10.2, 0.8, n_default)
    ]).astype(int)
    
    data['loan_term'] = np.random.choice([6, 12, 24, 36, 48, 60], n_samples, 
                                           p=[0.1, 0.2, 0.25, 0.25, 0.1, 0.1])
    
    data['interest_rate'] = np.concatenate([
        np.random.normal(0.12, 0.03, n_good),
        np.random.normal(0.18, 0.04, n_default)
    ]).clip(0.06, 0.36)
    
    data['dti'] = np.concatenate([
        np.random.normal(0.3, 0.15, n_good),
        np.random.normal(0.55, 0.2, n_default)
    ]).clip(0, 1)
    
    data['revolving_utilization'] = np.concatenate([
        np.random.normal(0.4, 0.25, n_good),
        np.random.normal(0.7, 0.2, n_default)
    ]).clip(0, 1)
    
    data['num_open_accounts'] = np.concatenate([
        np.random.poisson(8, n_good),
        np.random.poisson(5, n_default)
    ]).clip(0, 30)
    
    data['credit_history_length'] = np.concatenate([
        np.random.poisson(12, n_good),
        np.random.poisson(5, n_default)
    ]).clip(0, 30)
    
    data['num_delinquencies_2yrs'] = np.concatenate([
        np.random.poisson(0.3, n_good),
        np.random.poisson(2, n_default)
    ]).clip(0, 10)
    
    data['num_inquiries_6m'] = np.concatenate([
        np.random.poisson(1, n_good),
        np.random.poisson(3, n_default)
    ]).clip(0, 10)
    
    data['employment_length'] = np.concatenate([
        np.random.poisson(8, n_good),
        np.random.poisson(3, n_default)
    ]).clip(0, 30)
    
    data['home_ownership'] = np.random.choice(['RENT', 'OWN', 'MORTGAGE', 'OTHER'], n_samples,
                                                p=[0.4, 0.15, 0.4, 0.05])
    
    data['verification_status'] = np.random.choice(['Verified', 'Source Verified', 'Not Verified'], n_samples,
                                                     p=[0.4, 0.35, 0.25])
    
    data['purpose'] = np.random.choice([
        'debt_consolidation', 'credit_card', 'home_improvement',
        'major_purchase', 'small_business', 'other'
    ], n_samples, p=[0.45, 0.2, 0.12, 0.08, 0.05, 0.1])
    
    data['default'] = np.concatenate([np.zeros(n_good), np.ones(n_default)]).astype(int)
    
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return data

def generate_pre_loan_data(n_samples, sub_scenario=None):
    if sub_scenario == 'anti_fraud':
        return generate_anti_fraud_data(n_samples)
    elif sub_scenario == 'credit_scoring':
        return generate_credit_scoring_data(n_samples)
    else:
        return generate_generic_credit_data(n_samples, 0.03)

def generate_anti_fraud_data(n_samples):
    n_fraud = int(n_samples * 0.02)
    n_legit = n_samples - n_fraud
    
    data = pd.DataFrame()
    
    data['transaction_id'] = [f'T{i:08d}' for i in range(n_samples)]
    data['user_id'] = [f'U{np.random.randint(0, 1000):06d}' for _ in range(n_samples)]
    
    data['transaction_amount'] = np.concatenate([
        np.random.lognormal(5, 1.5, n_legit),
        np.random.lognormal(8, 1, n_fraud)
    ]).astype(int)
    
    data['is_new_user'] = np.concatenate([
        np.random.binomial(1, 0.05, n_legit),
        np.random.binomial(1, 0.4, n_fraud)
    ])
    
    data['is_new_device'] = np.concatenate([
        np.random.binomial(1, 0.03, n_legit),
        np.random.binomial(1, 0.5, n_fraud)
    ])
    
    data['is_new_location'] = np.concatenate([
        np.random.binomial(1, 0.02, n_legit),
        np.random.binomial(1, 0.6, n_fraud)
    ])
    
    data['velocity_1h'] = np.concatenate([
        np.random.poisson(1, n_legit),
        np.random.poisson(5, n_fraud)
    ])
    
    data['velocity_24h'] = np.concatenate([
        np.random.poisson(3, n_legit),
        np.random.poisson(10, n_fraud)
    ])
    
    data['num_failures_7d'] = np.concatenate([
        np.random.poisson(0.1, n_legit),
        np.random.poisson(3, n_fraud)
    ])
    
    data['anomaly_score'] = np.concatenate([
        np.random.normal(0, 1, n_legit),
        np.random.normal(3, 1, n_fraud)
    ])
    
    data['is_fraud'] = np.concatenate([np.zeros(n_legit), np.ones(n_fraud)]).astype(int)
    
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return data

def generate_credit_scoring_data(n_samples):
    return generate_generic_credit_data(n_samples, 0.03)

def generate_mid_loan_data(n_samples, sub_scenario=None):
    if sub_scenario == 'early_warning':
        return generate_early_warning_data(n_samples)
    else:
        return generate_behavior_score_data(n_samples)

def generate_behavior_score_data(n_samples):
    n_risk = int(n_samples * 0.05)
    n_normal = n_samples - n_risk
    
    data = pd.DataFrame()
    
    data['account_id'] = [f'A{i:08d}' for i in range(n_samples)]
    data['loan_id'] = [f'L{i:09d}' for i in range(n_samples)]
    
    data['original_amount'] = np.random.lognormal(10, 0.7, n_samples).astype(int)
    data['current_balance'] = data['original_amount'] * np.random.uniform(0.1, 0.9, n_samples)
    
    data['months_since_origination'] = np.random.randint(1, 37, n_samples)
    
    data['num_days_past_due'] = np.concatenate([
        np.random.poisson(0.5, n_normal),
        np.random.poisson(15, n_risk)
    ])
    
    data['num_delinquent_cycles'] = np.concatenate([
        np.random.poisson(0.2, n_normal),
        np.random.poisson(3, n_risk)
    ])
    
    data['payment_ratio'] = np.concatenate([
        np.random.normal(1.2, 0.3, n_normal),
        np.random.normal(0.3, 0.2, n_risk)
    ]).clip(0, 2)
    
    data['utilization_change'] = np.concatenate([
        np.random.normal(0, 0.1, n_normal),
        np.random.normal(0.15, 0.1, n_risk)
    ])
    
    data['inquiry_count_3m'] = np.concatenate([
        np.random.poisson(1, n_normal),
        np.random.poisson(4, n_risk)
    ])
    
    data['new_accounts_6m'] = np.concatenate([
        np.random.poisson(0.5, n_normal),
        np.random.poisson(2, n_risk)
    ])
    
    data['balance_to_limit'] = np.concatenate([
        np.random.normal(0.4, 0.2, n_normal),
        np.random.normal(0.8, 0.15, n_risk)
    ]).clip(0, 1)
    
    data['behavior_risk'] = np.concatenate([np.zeros(n_normal), np.ones(n_risk)]).astype(int)
    
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return data

def generate_early_warning_data(n_samples):
    n_warning = int(n_samples * 0.08)
    n_normal = n_samples - n_warning
    
    data = pd.DataFrame()
    
    data['account_id'] = [f'A{i:08d}' for i in range(n_samples)]
    data['monitoring_date'] = [datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 365)) 
                                for _ in range(n_samples)]
    
    data['original_loan_amount'] = np.random.lognormal(10, 0.7, n_samples).astype(int)
    data['remaining_balance'] = data['original_loan_amount'] * np.random.uniform(0.2, 0.95, n_samples)
    
    data['payment_status'] = np.concatenate([
        np.random.choice(['Current', '1-30 DPD'], n_normal, p=[0.95, 0.05]),
        np.random.choice(['31-60 DPD', '61-90 DPD', '90+ DPD'], n_warning, p=[0.4, 0.35, 0.25])
    ])
    
    data['days_past_due'] = np.concatenate([
        np.random.poisson(2, n_normal),
        np.random.poisson(45, n_warning)
    ])
    
    data['missed_payments_6m'] = np.concatenate([
        np.random.poisson(0.3, n_normal),
        np.random.poisson(4, n_warning)
    ])
    
    data['employment_status_change'] = np.concatenate([
        np.random.binomial(1, 0.02, n_normal),
        np.random.binomial(1, 0.3, n_warning)
    ])
    
    data['income_change_pct'] = np.concatenate([
        np.random.normal(0, 0.05, n_normal),
        np.random.normal(-0.3, 0.1, n_warning)
    ])
    
    data['credit_utilization_increase'] = np.concatenate([
        np.random.binomial(1, 0.05, n_normal),
        np.random.binomial(1, 0.4, n_warning)
    ])
    
    data['new_credit_inquiries'] = np.concatenate([
        np.random.poisson(1, n_normal),
        np.random.poisson(5, n_warning)
    ])
    
    data['early_warning_flag'] = np.concatenate([np.zeros(n_normal), np.ones(n_warning)]).astype(int)
    
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return data

def generate_post_loan_data(n_samples, sub_scenario=None):
    if sub_scenario == 'collection_score':
        return generate_collection_score_data(n_samples)
    elif sub_scenario == 'loss_forecast':
        return generate_loss_forecast_data(n_samples)
    else:
        return generate_collection_score_data(n_samples)

def generate_collection_score_data(n_samples):
    n_high_priority = int(n_samples * 0.2)
    n_medium = int(n_samples * 0.3)
    n_low = n_samples - n_high_priority - n_medium
    
    data = pd.DataFrame()
    
    data['account_id'] = [f'A{i:08d}' for i in range(n_samples)]
    data['default_date'] = [datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365)) 
                            for _ in range(n_samples)]
    
    data['days_in_collection'] = np.concatenate([
        np.random.randint(1, 30, n_low),
        np.random.randint(31, 90, n_medium),
        np.random.randint(91, 365, n_high_priority)
    ])
    
    data['outstanding_balance'] = np.concatenate([
        np.random.lognormal(8, 0.6, n_low),
        np.random.lognormal(9, 0.7, n_medium),
        np.random.lognormal(10, 0.8, n_high_priority)
    ]).astype(int)
    
    data['original_amount'] = data['outstanding_balance'] * np.random.uniform(1.2, 2, n_samples)
    
    data['number_of_calls'] = np.concatenate([
        np.random.poisson(2, n_low),
        np.random.poisson(8, n_medium),
        np.random.poisson(15, n_high_priority)
    ])
    
    data['number_of_letters'] = np.concatenate([
        np.random.poisson(1, n_low),
        np.random.poisson(3, n_medium),
        np.random.poisson(6, n_high_priority)
    ])
    
    data['contact_success_rate'] = np.concatenate([
        np.random.normal(0.8, 0.15, n_low),
        np.random.normal(0.4, 0.2, n_medium),
        np.random.normal(0.1, 0.1, n_high_priority)
    ]).clip(0, 1)
    
    data['promise_to_pay_count'] = np.concatenate([
        np.random.poisson(3, n_low),
        np.random.poisson(1, n_medium),
        np.random.poisson(0, n_high_priority)
    ])
    
    data['broken_promise_count'] = np.concatenate([
        np.random.poisson(0, n_low),
        np.random.poisson(2, n_medium),
        np.random.poisson(5, n_high_priority)
    ])
    
    data['phone_status'] = np.concatenate([
        np.random.choice(['Active', 'Disconnected'], n_low, p=[0.95, 0.05]),
        np.random.choice(['Active', 'Disconnected'], n_medium, p=[0.7, 0.3]),
        np.random.choice(['Active', 'Disconnected', 'Wrong Number'], n_high_priority, p=[0.4, 0.4, 0.2])
    ])
    
    data['employment_status'] = np.concatenate([
        np.random.choice(['Employed', 'Self-employed'], n_low, p=[0.8, 0.2]),
        np.random.choice(['Employed', 'Unemployed', 'Unknown'], n_medium, p=[0.5, 0.3, 0.2]),
        np.random.choice(['Unemployed', 'Unknown', 'Employed'], n_high_priority, p=[0.5, 0.35, 0.15])
    ])
    
    data['collection_score'] = np.concatenate([
        np.random.normal(750, 50, n_low),
        np.random.normal(550, 80, n_medium),
        np.random.normal(350, 100, n_high_priority)
    ]).clip(300, 850)
    
    priority_labels = np.concatenate([
        np.full(n_low, 'Low'),
        np.full(n_medium, 'Medium'),
        np.full(n_high_priority, 'High')
    ])
    data['collection_priority'] = priority_labels
    
    priority_encoded = np.concatenate([
        np.zeros(n_low),
        np.ones(n_medium),
        np.full(n_high_priority, 2)
    ]).astype(int)
    data['priority_encoded'] = priority_encoded
    
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return data

def generate_loss_forecast_data(n_samples):
    n_high_loss = int(n_samples * 0.15)
    n_medium_loss = int(n_samples * 0.25)
    n_low_loss = n_samples - n_high_loss - n_medium_loss
    
    data = pd.DataFrame()
    
    data['account_id'] = [f'A{i:08d}' for i in range(n_samples)]
    data['default_date'] = [datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 730)) 
                            for _ in range(n_samples)]
    
    data['original_loan_amount'] = np.random.lognormal(10, 0.8, n_samples).astype(int)
    
    data['days_past_due'] = np.concatenate([
        np.random.randint(30, 90, n_low_loss),
        np.random.randint(91, 180, n_medium_loss),
        np.random.randint(181, 730, n_high_loss)
    ])
    
    data['collateral_value'] = data['original_loan_amount'] * np.concatenate([
        np.random.uniform(0.8, 1.2, n_low_loss),
        np.random.uniform(0.4, 0.8, n_medium_loss),
        np.random.uniform(0, 0.4, n_high_loss)
    ])
    
    data['lgd'] = np.concatenate([
        np.random.beta(2, 5, n_low_loss),
        np.random.beta(3, 3, n_medium_loss),
        np.random.beta(5, 2, n_high_loss)
    ]).clip(0, 1)
    
    data['recovery_rate'] = 1 - data['lgd']
    
    data['expected_loss'] = data['original_loan_amount'] * data['lgd']
    
    data['collateral_type'] = np.random.choice(['Real Estate', 'Vehicle', 'Equipment', 'None', 'Securities'], 
                                                  n_samples, p=[0.3, 0.25, 0.15, 0.2, 0.1])
    
    data['loan_type'] = np.random.choice(['Mortgage', 'Auto', 'Personal', 'Business', 'Credit Card'],
                                           n_samples, p=[0.25, 0.2, 0.25, 0.15, 0.15])
    
    data['number_of_collaterals'] = np.concatenate([
        np.random.poisson(2, n_low_loss),
        np.random.poisson(1, n_medium_loss),
        np.random.poisson(0, n_high_loss)
    ])
    
    data['legal_status'] = np.concatenate([
        np.random.choice(['Active', 'Settled'], n_low_loss, p=[0.6, 0.4]),
        np.random.choice(['Active', 'Legal Proceedings'], n_medium_loss, p=[0.7, 0.3]),
        np.random.choice(['Legal Proceedings', 'Write-off', 'Active'], n_high_loss, p=[0.5, 0.3, 0.2])
    ])
    
    data = data.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return data
