import json
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


class InstallPluginsError(RuntimeError):
    pass


@dataclass(frozen=True)
class PluginBundle:
    name: str
    root: Path
    agent_dir: Path | None
    root_agents_file: Path | None
    config_file: Path | None
    agent_files: tuple[Path, ...]
    skill_entries: tuple[Path, ...]


@dataclass(frozen=True)
class ProjectInstallResult:
    copied_agents: list[Path]
    copied_skills: list[Path]
    merged_agents_file: Path | None
    merged_config_file: Path | None
    backup_dir: Path | None
    target_agents_dir: Path
    target_skills_dir: Path


@dataclass(frozen=True)
class SystemInstallResult:
    copied_agents: list[Path]
    copied_skills: list[Path]
    merged_agents_file: Path | None
    merged_config_file: Path | None
    target_agents_dir: Path
    target_skills_dir: Path


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
    skill_dir = directory / ".opencode" / "skills"
    return skill_dir if skill_dir.is_dir() else None


def find_config_file(directory: Path) -> Path | None:
    config_file = directory / "opencode.json"
    return config_file if config_file.is_file() else None


def load_plugin(repo_root: Path, plugin_name: str) -> PluginBundle:
    plugin_root = repo_root / plugin_name
    if not plugin_root.is_dir():
        raise fail(f"Plugin '{plugin_name}' does not exist at '{plugin_root}'.")

    agent_dir = find_agent_dir(plugin_root)
    skill_dir = find_skill_dir(plugin_root)
    root_agents_file = find_root_agents_file(plugin_root)
    config_file = find_config_file(plugin_root)
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

    if (
        not agent_files
        and root_agents_file is None
        and not skill_entries
        and config_file is None
    ):
        raise fail(
            f"Plugin '{plugin_name}' does not contain '.opencode/agents', "
            "'.opencode/skills', AGENTS.md, or opencode.json."
        )

    return PluginBundle(
        name=plugin_name,
        root=plugin_root,
        agent_dir=agent_dir,
        root_agents_file=root_agents_file,
        config_file=config_file,
        agent_files=agent_files,
        skill_entries=skill_entries,
    )


def load_plugins(repo_root: Path, plugin_names: list[str]) -> list[PluginBundle]:
    validate_plugin_names(plugin_names)
    plugins = [load_plugin(repo_root, plugin_name) for plugin_name in plugin_names]
    validate_agent_compatibility(plugins)
    validate_skill_compatibility(plugins)
    # Load configs during validation so invalid or conflicting configs fail before writes.
    aggregate_plugin_configs(plugins)
    return plugins


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


def resolve_repo_root(repo_root: Path | None, default_file: str) -> Path:
    if repo_root is not None:
        return Path(repo_root).expanduser().resolve()
    return Path(default_file).resolve().parent


def resolve_project_opencode_dir(target_root: Path) -> Path:
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


def remove_existing_path(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
        return

    path.unlink()


def unique_backup_path(path: Path) -> Path:
    if not path.exists():
        return path

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return path.with_name(f"{path.name}.{timestamp}")


def ensure_backup_dir(
    created_backup_dir: Path | None,
    target_root: Path,
) -> Path:
    return (
        created_backup_dir
        if created_backup_dir is not None
        else backup_session_dir(target_root)
    )


def prepare_directory_root(path: Path, overwrite_existing: bool) -> None:
    if path.exists():
        if path.is_dir():
            return
        if not overwrite_existing:
            raise fail(f"'{path}' exists but is not a directory.")
        remove_existing_path(path)

    path.mkdir(parents=True, exist_ok=True)


def prepare_file_destination(path: Path, overwrite_existing: bool) -> None:
    if path.exists() and path.is_dir() and not path.is_symlink():
        if not overwrite_existing:
            raise fail(f"'{path}' exists but is not a file.")
        remove_existing_path(path)

    path.parent.mkdir(parents=True, exist_ok=True)


def prepare_tree_destination(path: Path, overwrite_existing: bool) -> None:
    if path.exists():
        if not overwrite_existing:
            raise fail(f"'{path}' already exists.")
        remove_existing_path(path)

    path.parent.mkdir(parents=True, exist_ok=True)


def backup_project_target_state(
    target_root: Path,
    target_opencode_dir: Path,
) -> tuple[Path | None, Path, Path, Path | None, Path | None]:
    created_backup_dir: Path | None = None
    target_agents_dir = target_opencode_dir / "agents"
    target_skills_dir = target_opencode_dir / "skills"
    target_root_agents_file = find_root_agents_file(target_root)
    target_config_file = target_root / "opencode.json"

    if target_agents_dir.exists() and not target_agents_dir.is_dir():
        raise fail(f"'{target_agents_dir}' exists but is not a directory.")

    if target_agents_dir.is_dir() and any(target_agents_dir.iterdir()):
        created_backup_dir = ensure_backup_dir(created_backup_dir, target_root)
        copy_into_backup(target_agents_dir, target_root, created_backup_dir)
        warn(
            f"'{target_agents_dir}' already contains agents. They will be replaced. "
            f"Backup: '{created_backup_dir}'."
        )

    if target_skills_dir.exists() and not target_skills_dir.is_dir():
        raise fail(f"'{target_skills_dir}' exists but is not a directory.")

    if target_skills_dir.is_dir() and any(target_skills_dir.iterdir()):
        created_backup_dir = ensure_backup_dir(created_backup_dir, target_root)
        copy_into_backup(target_skills_dir, target_root, created_backup_dir)
        warn(
            f"'{target_skills_dir}' already contains skills. They will be replaced. "
            f"Backup: '{created_backup_dir}'."
        )

    if target_root_agents_file is not None:
        created_backup_dir = ensure_backup_dir(created_backup_dir, target_root)
        copy_into_backup(target_root_agents_file, target_root, created_backup_dir)

        sibling_backup = unique_backup_path(
            target_root_agents_file.with_name(f"{target_root_agents_file.name}.backup")
        )
        shutil.copy2(target_root_agents_file, sibling_backup)

    if target_config_file.exists():
        if not target_config_file.is_file():
            raise fail(f"'{target_config_file}' exists but is not a file.")
        created_backup_dir = ensure_backup_dir(created_backup_dir, target_root)
        copy_into_backup(target_config_file, target_root, created_backup_dir)

        sibling_backup = unique_backup_path(
            target_config_file.with_name(f"{target_config_file.name}.backup")
        )
        shutil.copy2(target_config_file, sibling_backup)

    return (
        created_backup_dir,
        target_agents_dir,
        target_skills_dir,
        target_root_agents_file,
        target_config_file if target_config_file.exists() else None,
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


def read_plugin_config(plugin: PluginBundle) -> Any:
    if plugin.config_file is None:
        return None

    raw_content = plugin.config_file.read_text(encoding="utf-8")
    if not raw_content.strip():
        raise fail(f"Plugin '{plugin.name}' has an empty opencode.json.")

    try:
        config = json.loads(raw_content)
    except json.JSONDecodeError as error:
        raise fail(
            f"Plugin '{plugin.name}' has invalid opencode.json: {error.msg} "
            f"at line {error.lineno}, column {error.colno}."
        ) from error

    if not isinstance(config, dict):
        raise fail(f"Plugin '{plugin.name}' opencode.json must contain a JSON object.")

    return config


def format_config_path(path: tuple[str, ...]) -> str:
    return ".".join(path) if path else "<root>"


def strict_merge_config_values(
    existing: Any,
    incoming: Any,
    path: tuple[str, ...],
    existing_owner: str,
    incoming_owner: str,
) -> Any:
    if isinstance(existing, dict) and isinstance(incoming, dict):
        merged = dict(existing)
        for key, incoming_value in incoming.items():
            if key in merged:
                merged[key] = strict_merge_config_values(
                    merged[key],
                    incoming_value,
                    (*path, key),
                    existing_owner,
                    incoming_owner,
                )
            else:
                merged[key] = incoming_value
        return merged

    if existing == incoming:
        return existing

    raise fail(
        "Conflicting opencode.json values at "
        f"'{format_config_path(path)}' between {existing_owner} and {incoming_owner}."
    )


def aggregate_plugin_configs(plugins: list[PluginBundle]) -> dict[str, Any] | None:
    merged: dict[str, Any] | None = None
    owner = ""

    for plugin in plugins:
        config = read_plugin_config(plugin)
        if config is None:
            continue

        if merged is None:
            merged = config
            owner = plugin.name
            continue

        merged = strict_merge_config_values(
            merged,
            config,
            (),
            owner,
            plugin.name,
        )
        owner = f"{owner}, {plugin.name}"

    return merged


def write_aggregated_config(
    destination: Path,
    plugins: list[PluginBundle],
    overwrite_existing: bool = False,
) -> Path | None:
    merged_config = aggregate_plugin_configs(plugins)
    if merged_config is None:
        return None

    prepare_file_destination(destination, overwrite_existing)
    destination.write_text(
        json.dumps(merged_config, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    return destination


def install_plugins_project(
    target_root: Path,
    plugin_names: list[str],
    repo_root: Path,
) -> ProjectInstallResult:
    validate_plugin_names(plugin_names)
    plugins = [load_plugin(repo_root, plugin_name) for plugin_name in plugin_names]
    validate_agent_compatibility(plugins)
    validate_skill_compatibility(plugins)
    aggregate_plugin_configs(plugins)

    target_opencode_dir = resolve_project_opencode_dir(target_root)
    (
        backup_dir,
        target_agents_dir,
        target_skills_dir,
        target_root_agents_file,
        _target_config_file,
    ) = backup_project_target_state(target_root, target_opencode_dir)

    copied_agents = replace_target_agents(target_agents_dir, plugins)
    copied_skills = replace_target_skills(target_skills_dir, plugins)
    merged_agents_file = merge_root_agents(
        target_root, target_root_agents_file, plugins
    )
    merged_config_file = write_aggregated_config(target_root / "opencode.json", plugins)

    return ProjectInstallResult(
        copied_agents=copied_agents,
        copied_skills=copied_skills,
        merged_agents_file=merged_agents_file,
        merged_config_file=merged_config_file,
        backup_dir=backup_dir,
        target_agents_dir=target_agents_dir,
        target_skills_dir=target_skills_dir,
    )


def preflight_system_targets(
    config_dir: Path,
    plugins: list[PluginBundle],
    overwrite_existing: bool,
) -> None:
    if config_dir.exists() and not config_dir.is_dir():
        if not overwrite_existing:
            raise fail(f"'{config_dir}' exists but is not a directory.")
        return

    if overwrite_existing:
        return

    conflicts: list[Path] = []
    target_agents_dir = config_dir / "agents"
    target_skills_dir = config_dir / "skills"

    if target_agents_dir.exists() and not target_agents_dir.is_dir():
        conflicts.append(target_agents_dir)

    if target_skills_dir.exists() and not target_skills_dir.is_dir():
        conflicts.append(target_skills_dir)

    if any(plugin.root_agents_file is not None for plugin in plugins):
        agents_file = config_dir / "AGENTS.md"
        if agents_file.exists():
            conflicts.append(agents_file)

    if any(plugin.config_file is not None for plugin in plugins):
        config_file = config_dir / "opencode.json"
        if config_file.exists():
            conflicts.append(config_file)

    for plugin in plugins:
        for agent_file in plugin.agent_files:
            destination = target_agents_dir / agent_file.name
            if destination.exists():
                conflicts.append(destination)

    for plugin in plugins:
        for skill_entry in plugin.skill_entries:
            destination = target_skills_dir / skill_entry.name
            if destination.exists():
                conflicts.append(destination)

    if conflicts:
        lines = ["System install target already exists; refusing to overwrite:"]
        lines.extend(f"- {path}" for path in sorted(conflicts, key=lambda p: str(p)))
        raise fail("\n".join(lines))


def copy_system_agents(
    config_dir: Path,
    plugins: list[PluginBundle],
    overwrite_existing: bool,
) -> list[Path]:
    copied_files: list[Path] = []
    target_agents_dir = config_dir / "agents"
    prepare_directory_root(target_agents_dir, overwrite_existing)

    for plugin in plugins:
        for agent_file in plugin.agent_files:
            destination = target_agents_dir / agent_file.name
            prepare_file_destination(destination, overwrite_existing)
            copy_path(agent_file, destination)
            copied_files.append(destination)

    return copied_files


def copy_system_skills(
    config_dir: Path,
    plugins: list[PluginBundle],
    overwrite_existing: bool,
) -> list[Path]:
    copied_entries: list[Path] = []
    target_skills_dir = config_dir / "skills"
    prepare_directory_root(target_skills_dir, overwrite_existing)

    for plugin in plugins:
        for skill_entry in plugin.skill_entries:
            destination = target_skills_dir / skill_entry.name
            prepare_tree_destination(destination, overwrite_existing)
            copy_path(skill_entry, destination)
            copied_entries.append(destination)

    return copied_entries


def write_system_agents(
    config_dir: Path,
    plugins: list[PluginBundle],
    overwrite_existing: bool,
) -> Path | None:
    sections: list[str] = []
    for plugin in plugins:
        if plugin.root_agents_file is None:
            continue
        content = plugin.root_agents_file.read_text(encoding="utf-8").strip()
        if content:
            sections.append(content)

    if not sections:
        return None

    destination = config_dir / "AGENTS.md"
    prepare_file_destination(destination, overwrite_existing)
    destination.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    return destination


def install_plugins_system(
    config_dir: Path,
    plugin_names: list[str],
    repo_root: Path,
    overwrite_existing: bool = False,
) -> SystemInstallResult:
    plugins = load_plugins(repo_root, plugin_names)
    preflight_system_targets(config_dir, plugins, overwrite_existing)
    prepare_directory_root(config_dir, overwrite_existing)

    copied_agents = copy_system_agents(config_dir, plugins, overwrite_existing)
    copied_skills = copy_system_skills(config_dir, plugins, overwrite_existing)
    merged_agents_file = write_system_agents(
        config_dir,
        plugins,
        overwrite_existing,
    )
    merged_config_file = write_aggregated_config(
        config_dir / "opencode.json",
        plugins,
        overwrite_existing=overwrite_existing,
    )

    return SystemInstallResult(
        copied_agents=copied_agents,
        copied_skills=copied_skills,
        merged_agents_file=merged_agents_file,
        merged_config_file=merged_config_file,
        target_agents_dir=config_dir / "agents",
        target_skills_dir=config_dir / "skills",
    )
