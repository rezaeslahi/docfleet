import json
from pathlib import Path

from app.pipelines.train_pipeline import training_pipeline

CONFIG_PATH = "config/train.yaml"


def main() -> None:
    docs_path = Path("artifacts/docs_snapshot.json")
    if not docs_path.exists():
        raise RuntimeError("Missing artifacts/docs_snapshot.json")

    docs_json = json.loads(docs_path.read_text(encoding="utf-8"))

    res = training_pipeline(config_path=CONFIG_PATH, docs_json=docs_json)
    

    # print("PIPELINE_RESULT=", res["train_result"])
    # print("BEST_MODEL_REF=", res["best_ref"])
    # print(type(res))
    # print(f"res:{res}")


if __name__ == "__main__":
    main()