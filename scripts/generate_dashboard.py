from argparse import ArgumentParser

from aegis.dashboard.builder import (
    extract_summary,
    load_report,
    save_html,
)
from aegis.dashboard.templates import (
    build_dashboard_html,
)


def parse_args():
    parser = ArgumentParser(
        description="Generate an HTML dashboard from an AegisLLM benchmark report."
    )

    parser.add_argument(
        "report",
        help="Path to benchmark JSON report.",
    )

    parser.add_argument(
        "--output",
        default="results/dashboard.html",
        help="Output HTML file.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    report = load_report(
        args.report,
    )

    summary = extract_summary(
        report,
    )

    html = build_dashboard_html(
        summary,
    )

    save_html(
        html,
        args.output,
    )

    print(
        f"Dashboard saved to: {args.output}"
    )


if __name__ == "__main__":
    main()