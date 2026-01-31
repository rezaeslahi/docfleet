from typing import List, Dict
from zenml import pipeline

from .steps import (
    get_config_hash,
    load_ml_config,
    load_docs,
    generate_training_pairs,
    handle_missing_values,
    split_dataset,
    build_feature_text,
    build_model,
    tune_train_log_register,
    set_champion_alias,
)


@pipeline
def training_pipeline(config_path: str, docs_json: List[Dict])-> Dict:
    cfg_hash = get_config_hash(config_path)
    cfg = load_ml_config(config_path,cfg_hash)
    docs = load_docs(docs_json)

    df = generate_training_pairs(docs, cfg)
    df = handle_missing_values(df,cfg)

    train_df, test_df = split_dataset(df, cfg)
    X_train, y_train, X_test, y_test = build_feature_text(train_df, test_df)

    model = build_model(cfg)
    result = tune_train_log_register(model, X_train, y_train, X_test, y_test, cfg)

    best_ref = set_champion_alias(result,cfg)
    return {"train_result": result, "best_ref": best_ref}