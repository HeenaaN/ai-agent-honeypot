import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import xgboost as xgb
import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pickle
import warnings
warnings.filterwarnings('ignore')

DATASET = "dataset.csv"
MODEL_FILE = "classifier_model.pkl"
FEATURES = [
    "response_time_ms", "trap_followed", "paths_visited",
    "avg_delay_ms", "unique_paths", "visited_api_keys",
    "visited_backup", "visited_config", "session_duration_s"
]

def load_data():
    df = pd.read_csv(DATASET)
    df = df.drop_duplicates(subset=["session_id", "path"])
    session_df = df.groupby("session_id").agg({
        "label": "first",
        "label_name": "first",
        "response_time_ms": "mean",
        "trap_followed": "max",
        "paths_visited": "max",
        "avg_delay_ms": "mean",
        "unique_paths": "max",
        "visited_api_keys": "max",
        "visited_backup": "max",
        "visited_config": "max",
        "session_duration_s": "max"
    }).reset_index()
    print(f"Sessions loaded: {len(session_df)}")
    print(f"Class distribution:\n{session_df['label_name'].value_counts()}\n")
    return session_df

def train_random_forest(X_train, X_test, y_train, y_test, label_names):
    print("Training Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    f1 = f1_score(y_test, y_pred, average='weighted')
    print(f"Random Forest F1 Score: {f1:.4f}")
    print(classification_report(y_test, y_pred, target_names=label_names))
    return rf, f1

def train_xgboost(X_train, X_test, y_train, y_test, label_names):
    print("Training XGBoost...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric='mlogloss',
        random_state=42
    )
    xgb_model.fit(X_train, y_train)
    y_pred = xgb_model.predict(X_test)
    f1 = f1_score(y_test, y_pred, average='weighted')
    print(f"XGBoost F1 Score: {f1:.4f}")
    print(classification_report(y_test, y_pred, target_names=label_names))
    return xgb_model, f1

def generate_shap_plot(model, X_train, feature_names):
    print("\nGenerating SHAP explainability plot...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_train)
    plt.figure(figsize=(10, 6))
    if isinstance(shap_values, list):
        shap.summary_plot(shap_values[2], X_train,
                         feature_names=feature_names,
                         plot_type="bar", show=False)
    else:
        shap.summary_plot(shap_values, X_train,
                         feature_names=feature_names,
                         plot_type="bar", show=False)
    plt.title("Feature Importance — AI Agent Detection (SHAP)")
    plt.tight_layout()
    plt.savefig("shap_importance.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("SHAP plot saved to shap_importance.png")

def save_model(model, model_name):
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump(model, f)
    print(f"\nBest model ({model_name}) saved to {MODEL_FILE}")

def main():
    print("="*50)
    print("AI AGENT HONEYPOT — ML CLASSIFIER")
    print("="*50 + "\n")

    df = load_data()
    X = df[FEATURES].fillna(0)
    le = LabelEncoder()
    y = le.fit_transform(df["label_name"])
    label_names = list(le.classes_)
    print(f"Features: {FEATURES}")
    print(f"Classes: {label_names}\n")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"Train size: {len(X_train)} | Test size: {len(X_test)}\n")

    print("-"*40)
    rf_model, rf_f1 = train_random_forest(
        X_train, X_test, y_train, y_test, label_names
    )

    print("-"*40)
    xgb_model, xgb_f1 = train_xgboost(
        X_train, X_test, y_train, y_test, label_names
    )

    print("\n" + "="*50)
    print("RESULTS COMPARISON")
    print("="*50)
    print(f"Random Forest F1 : {rf_f1:.4f}")
    print(f"XGBoost F1       : {xgb_f1:.4f}")

    if xgb_f1 >= rf_f1:
        best_model = xgb_model
        best_name = "XGBoost"
        best_f1 = xgb_f1
    else:
        best_model = rf_model
        best_name = "Random Forest"
        best_f1 = rf_f1

    print(f"\nBest model: {best_name} (F1={best_f1:.4f})")

    generate_shap_plot(best_model, X_train, FEATURES)
    save_model(best_model, best_name)

    print("\n" + "="*50)
    print("CLASSIFIER READY")
    print("="*50)
    print(f"Model file  : {MODEL_FILE}")
    print(f"SHAP plot   : shap_importance.png")
    print(f"Best F1     : {best_f1:.4f}")
    print(f"Classes     : {label_names}")

if __name__ == "__main__":
    main()
