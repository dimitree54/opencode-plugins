import argparse
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class InstallPluginsError(RuntimeError):
    pass


@dataclass(frozen=True)
class PluginBundle:
    name: str
    root: Path
    agent_dir: Path | None
    root_agents_file: Path | None
    agent_files: tuple[Path, ...]
    skill_entries: tuple[Path, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy agent files and skills from selected plugins into a target "
            "repository and merge AGENTS.md content."
        )
    )
    parser.add_argument(
        "plugins",
        nargs="+",
        help="Plugin directory names from this repository.",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Path to the target repository.",
    )
    return parser.parse_args()


def warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


def fail(message: str) -> InstallPluginsError:
    return InstallPluginsError(message)


def find_root_agents_file(directory: Path) -> Path | None:
    matches = [
        entry
        for entry in directory.iterdir()
        if entry.is_file() and entry.name.lower() == "agents.md"
    ]
    if len(matches) > 1:
        names = ", ".join(sorted(entry.name for entry in matches))
        raise fail(f"Multiple AGENTS.md variants found in '{directory}': {names}")
    return matches[0] if matches else None


def find_agent_dir(directory: Path) -> Path | None:
    agent_dir = directory / ".opencode" / "agents"
    return agent_dir if agent_dir.is_dir() else None


def find_skill_dir(directory: Path) -> Path | None:
    skill_dir = directory / "skills"
    return skill_dir if skill_dir.is_dir() else None


def load_plugin(repo_root: Path, plugin_name: str) -> PluginBundle:
    plugin_root = repo_root / plugin_name
    if not plugin_root.is_dir():
        raise fail(f"Plugin '{plugin_name}' does not exist at '{plugin_root}'.")

    agent_dir = find_agent_dir(plugin_root)
    skill_dir = find_skill_dir(plugin_root)
    root_agents_file = find_root_agents_file(plugin_root)
    agent_files: tuple[Path, ...] = ()
    skill_entries: tuple[Path, ...] = ()

    if agent_dir is not None:
        agent_files = tuple(
            sorted(
                (
                    entry
                    for entry in agent_dir.iterdir()
                    if entry.is_file() and entry.suffix.lower() == ".md"
                ),
                key=lambda entry: entry.name.lower(),
            )
        )

    if skill_dir is not None:
        skill_entries = tuple(
            sorted(skill_dir.iterdir(), key=lambda entry: entry.name.lower())
        )

    if not agent_files and root_agents_file is None and not skill_entries:
        raise fail(
            f"Plugin '{plugin_name}' does not contain '.opencode/agents', "
            "'skills/', or AGENTS.md."
        )

    return PluginBundle(
        name=plugin_name,
        root=plugin_root,
        agent_dir=agent_dir,
        root_agents_file=root_agents_file,
        agent_files=agent_files,
        skill_entries=skill_entries,
    )


def validate_plugin_names(plugin_names: list[str]) -> None:
    duplicates = sorted(
        name for name, count in Counter(plugin_names).items() if count > 1
    )
    if duplicates:
        raise fail("Plugin names were passed more than once: " + ", ".join(duplicates))


def validate_agent_compatibility(plugins: list[PluginBundle]) -> None:
    owners_by_name: dict[str, list[str]] = defaultdict(list)

    for plugin in plugins:
        for agent_file in plugin.agent_files:
            owners_by_name[agent_file.name.lower()].append(
                f"{plugin.name}/{agent_file.name}"
            )

    conflicts = {
        agent_name: owners
        for agent_name, owners in owners_by_name.items()
        if len(owners) > 1
    }
    if not conflicts:
        return

    lines = ["Conflicting agent files were found across selected plugins:"]
    for owners in sorted(conflicts.values(), key=lambda value: value[0].lower()):
        file_name = owners[0].split("/", 1)[1]
        lines.append(f"- {file_name}: {', '.join(owners)}")
    raise fail("\n".join(lines))


def validate_skill_compatibility(plugins: list[PluginBundle]) -> None:
    owners_by_name: dict[str, list[str]] = defaultdict(list)

    for plugin in plugins:
        for skill_entry in plugin.skill_entries:
            owners_by_name[skill_entry.name.lower()].append(
                f"{plugin.name}/{skill_entry.name}"
            )

    conflicts = {
        skill_name: owners
        for skill_name, owners in owners_by_name.items()
        if len(owners) > 1
    }
    if not conflicts:
        return

    lines = ["Conflicting skill entries were found across selected plugins:"]
    for owners in sorted(conflicts.values(), key=lambda value: value[0].lower()):
        file_name = owners[0].split("/", 1)[1]
        lines.append(f"- {file_name}: {', '.join(owners)}")
    raise fail("\n".join(lines))


def resolve_target_opencode_dir(target_root: Path) -> Path:
    if not target_root.exists():
        raise fail(f"Target path '{target_root}' does not exist.")
    if not target_root.is_dir():
        raise fail(f"Target path '{target_root}' is not a directory.")

    dot_opencode_dir = target_root / ".opencode"
    if dot_opencode_dir.exists():
        if not dot_opencode_dir.is_dir():
            raise fail(f"'{dot_opencode_dir}' exists but is not a directory.")
        return dot_opencode_dir

    dot_opencode_dir.mkdir(parents=True, exist_ok=True)
    return dot_opencode_dir


def backup_session_dir(target_root: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_dir = target_root / "agents_backup" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=False)
    return backup_dir


def copy_into_backup(source: Path, target_root: Path, backup_root: Path) -> None:
    relative_path = source.relative_to(target_root)
    destination = backup_root / relative_path
    copy_path(source, destination)


def copy_path(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination)
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def unique_backup_path(path: Path) -> Path:
    if not path.exists():
        return path

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return path.with_name(f"{path.name}.{timestamp}")


def backup_target_state(
    target_root: Path,
    target_opencode_dir: Path,
) -> tuple[Path | None, Path, Path, Path | None]:
    created_backup_dir: Path | None = None
    target_agents_dir = target_opencode_dir / "agents"
    target_skills_dir = target_opencode_dir / "skills"
    target_root_agents_file = find_root_agents_file(target_root)

    if target_agents_dir.exists() and not target_agents_dir.is_dir():
        raise fail(f"'{target_agents_dir}' exists but is not a directory.")

    if target_agents_dir.is_dir() and any(target_agents_dir.iterdir()):
        created_backup_dir = backup_session_dir(target_root)
        copy_into_backup(target_agents_dir, target_root, created_backup_dir)
        warn(
            f"'{target_agents_dir}' already contains agents. They will be replaced. "
            f"Backup: '{created_backup_dir}'."
        )

    if target_skills_dir.exists() and not target_skills_dir.is_dir():
        raise fail(f"'{target_skills_dir}' exists but is not a directory.")

    if target_skills_dir.is_dir() and any(target_skills_dir.iterdir()):
        if created_backup_dir is None:
            created_backup_dir = backup_session_dir(target_root)
        copy_into_backup(target_skills_dir, target_root, created_backup_dir)
        warn(
            f"'{target_skills_dir}' already contains skills. They will be replaced. "
            f"Backup: '{created_backup_dir}'."
        )

    if target_root_agents_file is not None:
        if created_backup_dir is None:
            created_backup_dir = backup_session_dir(target_root)
        copy_into_backup(target_root_agents_file, target_root, created_backup_dir)

        sibling_backup = unique_backup_path(
            target_root_agents_file.with_name(f"{target_root_agents_file.name}.backup")
        )
        shutil.copy2(target_root_agents_file, sibling_backup)

    return (
        created_backup_dir,
        target_agents_dir,
        target_skills_dir,
        target_root_agents_file,
    )


def replace_target_agents(
    target_agents_dir: Path, plugins: list[PluginBundle]
) -> list[Path]:
    copied_files: list[Path] = []

    if target_agents_dir.exists():
        shutil.rmtree(target_agents_dir)
    target_agents_dir.mkdir(parents=True, exist_ok=True)

    for plugin in plugins:
        for agent_file in plugin.agent_files:
            destination = target_agents_dir / agent_file.name
            copy_path(agent_file, destination)
            copied_files.append(destination)

    return copied_files


def replace_target_skills(
    target_skills_dir: Path, plugins: list[PluginBundle]
) -> list[Path]:
    copied_entries: list[Path] = []

    if target_skills_dir.exists():
        shutil.rmtree(target_skills_dir)

    skills_to_copy = [
        skill_entry for plugin in plugins for skill_entry in plugin.skill_entries
    ]
    if not skills_to_copy:
        return copied_entries

    target_skills_dir.mkdir(parents=True, exist_ok=True)

    for skill_entry in skills_to_copy:
        destination = target_skills_dir / skill_entry.name
        copy_path(skill_entry, destination)
        copied_entries.append(destination)

    return copied_entries


def merge_root_agents(
    target_root: Path,
    target_root_agents_file: Path | None,
    plugins: list[PluginBundle],
) -> Path | None:
    sections: list[str] = []

    if target_root_agents_file is not None:
        existing_content = target_root_agents_file.read_text(encoding="utf-8").strip()
        if existing_content:
            sections.append(existing_content)

    for plugin in plugins:
        if plugin.root_agents_file is None:
            continue
        content = plugin.root_agents_file.read_text(encoding="utf-8").strip()
        if content:
            sections.append(content)

    if not sections:
        return None

    destination_name = (
        target_root_agents_file.name if target_root_agents_file else "AGENTS.md"
    )
    destination = target_root / destination_name
    destination.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    return destination


def install_plugins(
    target_root: Path,
    plugin_names: list[str],
    repo_root: Path | None = None,
) -> int:
    repo_root = (
        Path(repo_root).expanduser().resolve()
        if repo_root is not None
        else Path(__file__).resolve().parent
    )

    validate_plugin_names(plugin_names)
    plugins = [load_plugin(repo_root, plugin_name) for plugin_name in plugin_names]
    validate_agent_compatibility(plugins)
    validate_skill_compatibility(plugins)

    target_opencode_dir = resolve_target_opencode_dir(target_root)
    backup_dir, target_agents_dir, target_skills_dir, target_root_agents_file = (
        backup_target_state(target_root, target_opencode_dir)
    )

    copied_agents = replace_target_agents(target_agents_dir, plugins)
    copied_skills = replace_target_skills(target_skills_dir, plugins)
    merged_agents_file = merge_root_agents(
        target_root, target_root_agents_file, plugins
    )

    print(f"Installed {len(copied_agents)} agent file(s) into '{target_agents_dir}'.")
    print(f"Installed {len(copied_skills)} skill item(s) into '{target_skills_dir}'.")
    if merged_agents_file is not None:
        print(f"Merged AGENTS.md content into '{merged_agents_file}'.")
    else:
        print("No AGENTS.md content was found to merge.")

    if backup_dir is not None:
        print(f"Backups were written to '{backup_dir}'.")

    return 0


def main() -> int:
    args = parse_args()
    try:
        return install_plugins(Path(args.target).expanduser().resolve(), args.plugins)
    except InstallPluginsError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
