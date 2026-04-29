import argparse
import sys
from pathlib import Path

from _opencode_plugin_installer import InstallPluginsError, install_plugins_system


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy agent files and skills from selected plugins into the global "
            "opencode config directory."
        )
    )
    parser.add_argument(
        "plugins",
        nargs="+",
        help="Plugin directory names from this repository.",
    )
    parser.add_argument(
        "--config-dir",
        default="~/.config/opencode",
        help="Global opencode config directory. Defaults to ~/.config/opencode.",
    )
    parser.add_argument(
        "--overwrite-existing",
        action="store_true",
        help=(
            "Overwrite conflicting existing global artifacts instead of failing."
        ),
    )
    return parser.parse_args()


def install_system_plugins(
    config_dir: Path,
    plugin_names: list[str],
    repo_root: Path | None = None,
    overwrite_existing: bool = False,
) -> int:
    resolved_repo_root = (
        Path(repo_root).expanduser().resolve()
        if repo_root is not None
        else Path(__file__).resolve().parent
    )
    result = install_plugins_system(
        config_dir,
        plugin_names,
        resolved_repo_root,
        overwrite_existing=overwrite_existing,
    )

    print(
        f"Installed {len(result.copied_agents)} agent file(s) into "
        f"'{result.target_agents_dir}'."
    )
    print(
        f"Installed {len(result.copied_skills)} skill item(s) into "
        f"'{result.target_skills_dir}'."
    )
    if result.merged_agents_file is not None:
        print(f"Wrote AGENTS.md content into '{result.merged_agents_file}'.")
    else:
        print("No AGENTS.md content was found to write.")

    if result.merged_config_file is not None:
        print(f"Wrote opencode.json content into '{result.merged_config_file}'.")
    else:
        print("No opencode.json content was found to write.")

    return 0


def main() -> int:
    args = parse_args()
    try:
        return install_system_plugins(
            Path(args.config_dir).expanduser().resolve(),
            args.plugins,
            overwrite_existing=args.overwrite_existing,
        )
    except InstallPluginsError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
