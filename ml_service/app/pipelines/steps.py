from zenml import step
from app.core.train_config import create_ml_config,MLConfig,PipelineMode
from typing import List, Dict, Tuple
import pandas as pd
from app.ml.data import Document, build_pair_dataset
from app.ml.spark_jobs import spark_generate_pairs
from app.ml.features import make_vectorizer
from app.ml.prep import create_missing_value_handler, MissingValueHandler, TextPairBuilder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, average_precision_score
import mlflow
import os
import hashlib
from pathlib import Path

@step
def get_config_hash(config_path: str) -> str:
    return hashlib.sha256(Path(config_path).read_bytes()).hexdigest()

@step
def load_ml_config(config_path:str,config_hash: str)->MLConfig:
    ml_config = create_ml_config(config_path=config_path)
    return ml_config

@step
def load_docs(docs_json: List[Dict]) -> List[Dict]:
    return docs_json

@step
def generate_training_pairs(docs: List[Dict],ml_config:MLConfig)->pd.DataFrame:
    if ml_config.pipeline.mode == PipelineMode.pandas:
        docs_typed = [
            Document(id=d["id"], title=d["title"], text=d["text"], tags=d.get("tags", []))
            for d in docs
        ]
        return build_pair_dataset(
            docs=docs_typed,
            negative_sampling_ratio= ml_config.data.negative_sampling_ratio,
            seed= ml_config.data.random_seed
        )
    elif ml_config.pipeline.mode == PipelineMode.spark:
        sdf = spark_generate_pairs(
            docs=docs,
            negative_sampling_ratio= ml_config.data.negative_sampling_ratio,
            seed= ml_config.data.random_seed
        )
        return sdf.toPandas()
    else:
        raise ValueError(f"unkonw pipeline mode:{ml_config.pipeline.mode}")
@step
def handle_missing_values(df: pd.DataFrame,ml_config: MLConfig) -> pd.DataFrame:
    handler: MissingValueHandler = create_missing_value_handler(method=ml_config.data.mising_value_method)
    df = handler.transform(df)
    return df
@step
def split_dataset(df: pd.DataFrame, ml_config:MLConfig) -> Tuple[pd.DataFrame, pd.DataFrame]:
    train_df, test_df = train_test_split(
        df,
        test_size= ml_config.data.test_size,
        random_state= ml_config.data.random_seed,
        stratify=df["label"],
    )
    return train_df, test_df

@step
def build_feature_text(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    builder = TextPairBuilder(sep=" [SEP] ")
    X_train, y_train = builder.transform(train_df)
    X_test, y_test = builder.transform(test_df)
    return X_train, y_train, X_test, y_test

@step
def build_model(ml_config:MLConfig) -> Pipeline:
    vectorizer = make_vectorizer(
        max_features= ml_config.features.max_features,
        ngram_min= ml_config.features.ngram_min,
        ngram_max= ml_config.features.ngram_max
    )
    clf = LogisticRegression(
        max_iter= ml_config.model.max_iter,
        solver="liblinear",
    )
    return Pipeline([("tfidf", vectorizer), ("clf", clf)])

@step
def tune_train_log_register(
    model: Pipeline,
    X_train:pd.Series,
    y_train:pd.Series,
    X_test:pd.Series,
    y_test:pd.Series,
    ml_config:MLConfig,
) -> Dict:
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    mlflow.set_experiment(ml_config.project.experiment_name)

    param_grid = {"clf__C": ml_config.model.grid_C}
    gs = GridSearchCV(model, param_grid=param_grid, cv=3, scoring="roc_auc", n_jobs=-1)

    with mlflow.start_run() as run:
        mlflow.log_params({
            "mode": ml_config.pipeline.mode,
            "max_features": ml_config.features.max_features,
            "ngram_min": ml_config.features.ngram_min,
            "ngram_max": ml_config.features.ngram_max,
            "neg_ratio": ml_config.data.negative_sampling_ratio,
        })

        gs.fit(X_train, y_train)
        best = gs.best_estimator_

        probs = best.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, probs)
        ap = average_precision_score(y_test, probs)

        mlflow.log_metric("roc_auc", float(auc))
        mlflow.log_metric("avg_precision", float(ap))
        mlflow.log_params(gs.best_params_)

        model_info = mlflow.sklearn.log_model(
            sk_model=best,
            artifact_path="model",
            registered_model_name= ml_config.project.registered_model_name,
        )

        return {
            "run_id": run.info.run_id,
            "model_uri": model_info.model_uri,
            "roc_auc": float(auc),
            "avg_precision": float(ap),
        }
@step
def set_champion_alias(train_result: Dict, ml_config: MLConfig) -> str:
    # ensure same tracking backend as training
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))

    client = mlflow.MlflowClient()
    name = ml_config.project.registered_model_name
    alias = ml_config.project.alias_for_best

    versions = client.search_model_versions(f"name='{name}'")
    if not versions:
        raise RuntimeError(f"No model versions found for {name}")

    best_v, best_auc = None, -1.0
    for v in versions:
        run = client.get_run(v.run_id)
        auc = run.data.metrics.get("roc_auc", -1.0)
        if auc > best_auc:
            best_auc, best_v = auc, v

    client.set_registered_model_alias(name, alias, best_v.version)
    return f"{name}@{alias}"
