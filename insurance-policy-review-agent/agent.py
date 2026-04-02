import argparse
import json
from pathlib import Path

from agent_impl.io import load_policy_text
from agent_impl.analysis import generate_report

MODEL_DEFAULT = "./models/ggml-model-q4_0.bin"


def main() -> None:
    parser = argparse.ArgumentParser(description="Insurance Policy Review Agent")
    parser.add_argument("--policy-file", help="Path to policy text or PDF file")
    parser.add_argument("--model", default=MODEL_DEFAULT, help="Path to local Llama model")
    parser.add_argument("--out", help="Output JSON report file")
    args = parser.parse_args()

    if not args.policy_file:
        raise ValueError("--policy-file is required")

    policy_text = load_policy_text(Path(args.policy_file))

    print(">> Running policy review...")
    report = generate_report(policy_text, model_path=args.model)
    out_json = json.dumps(report, indent=2)

    if args.out:
        Path(args.out).write_text(out_json, encoding="utf-8")
        print(f"Report saved to {args.out}")

    print(out_json)


if __name__ == "__main__":
    main()
