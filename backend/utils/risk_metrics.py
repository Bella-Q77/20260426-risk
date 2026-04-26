import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    mean_squared_error, mean_absolute_error, r2_score
)
from scipy import stats
import math

def calculate_ks(y_true, y_pred_proba):
    df = pd.DataFrame({'y_true': y_true, 'y_pred': y_pred_proba})
    df = df.sort_values('y_pred', ascending=False)
    df['cumulative_ones'] = (df['y_true'] == 1).cumsum()
    df['cumulative_zeros'] = (df['y_true'] == 0).cumsum()
    total_ones = df['y_true'].sum()
    total_zeros = len(df) - total_ones
    
    df['tpr'] = df['cumulative_ones'] / total_ones
    df['fpr'] = df['cumulative_zeros'] / total_zeros
    df['ks'] = df['tpr'] - df['fpr']
    
    return df['ks'].max()

def calculate_gini(y_true, y_pred_proba):
    auc = roc_auc_score(y_true, y_pred_proba)
    gini = 2 * auc - 1
    return gini

def calculate_psi(expected, actual, bins=10):
    def calculate_bin_psi(expected_perc, actual_perc):
        if expected_perc == 0:
            expected_perc = 1e-10
        if actual_perc == 0:
            actual_perc = 1e-10
        return (actual_perc - expected_perc) * np.log(actual_perc / expected_perc)
    
    expected = np.array(expected)
    actual = np.array(actual)
    
    quantiles = np.percentile(expected, np.linspace(0, 100, bins + 1))
    quantiles = np.unique(quantiles)
    
    expected_counts = np.zeros(len(quantiles) - 1)
    actual_counts = np.zeros(len(quantiles) - 1)
    
    for i in range(len(quantiles) - 1):
        lower = quantiles[i]
        upper = quantiles[i + 1]
        if i == len(quantiles) - 2:
            expected_counts[i] = np.sum((expected >= lower) & (expected <= upper))
            actual_counts[i] = np.sum((actual >= lower) & (actual <= upper))
        else:
            expected_counts[i] = np.sum((expected >= lower) & (expected < upper))
            actual_counts[i] = np.sum((actual >= lower) & (actual < upper))
    
    expected_percs = expected_counts / len(expected)
    actual_percs = actual_counts / len(actual)
    
    psi = 0.0
    for ep, ap in zip(expected_percs, actual_percs):
        psi += calculate_bin_psi(ep, ap)
    
    return psi

def calculate_woe_iv(df, feature, target):
    df_temp = df.copy()
    grouped = df_temp.groupby(feature)[target].agg(['count', 'sum'])
    grouped.columns = ['total', 'bad']
    grouped['good'] = grouped['total'] - grouped['bad']
    
    total_bad = grouped['bad'].sum()
    total_good = grouped['good'].sum()
    
    grouped['bad_rate'] = grouped['bad'] / grouped['total']
    grouped['bad_dist'] = grouped['bad'] / total_bad
    grouped['good_dist'] = grouped['good'] / total_good
    grouped['woe'] = np.log(grouped['good_dist'] / grouped['bad_dist'].replace(0, 0.0001))
    grouped['iv'] = (grouped['good_dist'] - grouped['bad_dist']) * grouped['woe']
    
    total_iv = grouped['iv'].sum()
    
    return grouped, total_iv

def calculate_classification_metrics(y_true, y_pred, y_pred_proba=None):
    metrics = {}
    
    metrics['accuracy'] = accuracy_score(y_true, y_pred)
    metrics['precision'] = precision_score(y_true, y_pred, zero_division=0)
    metrics['recall'] = recall_score(y_true, y_pred, zero_division=0)
    metrics['f1'] = f1_score(y_true, y_pred, zero_division=0)
    
    if y_pred_proba is not None:
        try:
            metrics['auc'] = roc_auc_score(y_true, y_pred_proba)
            metrics['gini'] = calculate_gini(y_true, y_pred_proba)
            metrics['ks'] = calculate_ks(y_true, y_pred_proba)
        except:
            pass
    
    metrics['confusion_matrix'] = confusion_matrix(y_true, y_pred).tolist()
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    metrics['tn'] = int(tn)
    metrics['fp'] = int(fp)
    metrics['fn'] = int(fn)
    metrics['tp'] = int(tp)
    
    metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
    metrics['fallout'] = fp / (tn + fp) if (tn + fp) > 0 else 0
    
    return metrics

def calculate_regression_metrics(y_true, y_pred):
    metrics = {}
    
    metrics['mse'] = mean_squared_error(y_true, y_pred)
    metrics['rmse'] = np.sqrt(metrics['mse'])
    metrics['mae'] = mean_absolute_error(y_true, y_pred)
    metrics['r2'] = r2_score(y_true, y_pred)
    
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-10))) * 100
    metrics['mape'] = mape
    
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    metrics['explained_variance'] = 1 - (ss_res / (ss_tot + 1e-10))
    
    return metrics

def calculate_all_metrics(y_true, y_pred, y_pred_proba=None, task_type='classification'):
    if task_type == 'classification':
        return calculate_classification_metrics(y_true, y_pred, y_pred_proba)
    else:
        return calculate_regression_metrics(y_true, y_pred)

def calculate_feature_importance(model, feature_names):
    importance = None
    
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importance = np.abs(model.coef_[0]) if len(model.coef_.shape) > 1 else np.abs(model.coef_)
    
    if importance is not None:
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        })
        importance_df = importance_df.sort_values('importance', ascending=False)
        return importance_df.to_dict(orient='records')
    
    return None

def calculate_correlation(df, method='pearson'):
    corr_matrix = df.corr(method=method)
    return corr_matrix.to_dict()

def calculate_descriptive_stats(df):
    stats = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        stats[col] = {
            'count': int(df[col].count()),
            'missing': int(df[col].isnull().sum()),
            'missing_rate': float(df[col].isnull().sum() / len(df)),
            'mean': float(df[col].mean()) if not df[col].isnull().all() else None,
            'std': float(df[col].std()) if not df[col].isnull().all() else None,
            'min': float(df[col].min()) if not df[col].isnull().all() else None,
            '25%': float(df[col].quantile(0.25)) if not df[col].isnull().all() else None,
            '50%': float(df[col].median()) if not df[col].isnull().all() else None,
            '75%': float(df[col].quantile(0.75)) if not df[col].isnull().all() else None,
            'max': float(df[col].max()) if not df[col].isnull().all() else None,
            'skewness': float(df[col].skew()) if not df[col].isnull().all() else None,
            'kurtosis': float(df[col].kurtosis()) if not df[col].isnull().all() else None
        }
    
    return stats
