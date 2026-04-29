import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import install_plugins as project_installer
import install_plugins_system as system_installer
from _opencode_plugin_installer import InstallPluginsError


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


class InstallerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tempdir.name)
        self.plugins_root = self.workspace / "plugins"
        self.plugins_root.mkdir()
        self.target_root = self.workspace / "target"
        self.target_root.mkdir()
        self.config_dir = self.workspace / "global-opencode"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def make_plugin(
        self,
        name: str,
        *,
        agents: dict[str, str] | None = None,
        skills: dict[str, str] | None = None,
        rules: str | None = None,
        config: str | dict[str, object] | None = None,
    ) -> Path:
        plugin_root = self.plugins_root / name
        plugin_root.mkdir()

        if agents:
            for agent_name, content in agents.items():
                write_file(plugin_root / ".opencode" / "agents" / agent_name, content)

        if skills:
            for relative_path, content in skills.items():
                write_file(
                    plugin_root / ".opencode" / "skills" / relative_path, content
                )

        if rules is not None:
            write_file(plugin_root / "AGENTS.md", rules)

        if config is not None:
            content = config if isinstance(config, str) else json.dumps(config)
            write_file(plugin_root / "opencode.json", content)

        return plugin_root

    def make_target(
        self,
        *,
        agents: dict[str, str] | None = None,
        skills: dict[str, str] | None = None,
        rules: str | None = None,
        config: str | dict[str, object] | None = None,
    ) -> None:
        write_file(self.target_root / ".opencode" / ".keep", "")
        (self.target_root / ".opencode" / ".keep").unlink()

        if agents:
            for agent_name, content in agents.items():
                write_file(
                    self.target_root / ".opencode" / "agents" / agent_name,
                    content,
                )

        if skills:
            for relative_path, content in skills.items():
                write_file(
                    self.target_root / ".opencode" / "skills" / relative_path,
                    content,
                )

        if rules is not None:
            write_file(self.target_root / "AGENTS.md", rules)

        if config is not None:
            content = config if isinstance(config, str) else json.dumps(config)
            write_file(self.target_root / "opencode.json", content)

    def install_project(self, *plugins: str) -> int:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            return project_installer.install_plugins(
                self.target_root,
                list(plugins),
                repo_root=self.plugins_root,
            )

    def install_system(
        self,
        *plugins: str,
        overwrite_existing: bool = False,
    ) -> int:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            return system_installer.install_system_plugins(
                self.config_dir,
                list(plugins),
                repo_root=self.plugins_root,
                overwrite_existing=overwrite_existing,
            )

    def only_backup_session(self) -> Path:
        backup_root = self.target_root / "agents_backup"
        self.assertTrue(backup_root.exists(), "expected backup directory to exist")
        sessions = sorted(path for path in backup_root.iterdir() if path.is_dir())
        self.assertEqual(len(sessions), 1, "expected a single backup session")
        return sessions[0]


class ProjectInstallPluginsTests(InstallerTestCase):
    def test_conflicting_plugin_agents_raise_error(self) -> None:
        self.make_plugin("plugin_one", agents={"shared.md": "one"})
        self.make_plugin("plugin_two", agents={"shared.md": "two"})
        self.make_target()

        with self.assertRaisesRegex(
            InstallPluginsError,
            "Conflicting agent files were found",
        ):
            self.install_project("plugin_one", "plugin_two")

        self.assertFalse((self.target_root / ".opencode" / "agents").exists())

    def test_existing_target_agents_are_backed_up_before_replace(self) -> None:
        self.make_plugin("plugin_one", agents={"fresh.md": "fresh agent"})
        self.make_target(agents={"old.md": "old agent"})

        result = self.install_project("plugin_one")

        self.assertEqual(result, 0)
        self.assertFalse(
            (self.target_root / ".opencode" / "agents" / "old.md").exists()
        )
        self.assertEqual(
            (self.target_root / ".opencode" / "agents" / "fresh.md").read_text(
                encoding="utf-8"
            ),
            "fresh agent",
        )

        backup_session = self.only_backup_session()
        self.assertEqual(
            (backup_session / ".opencode" / "agents" / "old.md").read_text(
                encoding="utf-8"
            ),
            "old agent",
        )

    def test_existing_agents_md_is_backed_up_in_both_locations(self) -> None:
        self.make_plugin(
            "plugin_one",
            agents={"fresh.md": "fresh agent"},
            rules="# Plugin rules",
        )
        self.make_target(rules="# Existing rules")

        self.install_project("plugin_one")

        backup_session = self.only_backup_session()
        self.assertEqual(
            (backup_session / "AGENTS.md").read_text(encoding="utf-8"),
            "# Existing rules",
        )

        sibling_backups = sorted(self.target_root.glob("AGENTS.md.backup*"))
        self.assertEqual(len(sibling_backups), 1)
        self.assertEqual(
            sibling_backups[0].read_text(encoding="utf-8"),
            "# Existing rules",
        )

    def test_agents_md_merge_keeps_target_and_all_plugin_content(self) -> None:
        self.make_plugin("plugin_one", rules="# Plugin one")
        self.make_plugin("plugin_two", rules="# Plugin two")
        self.make_target(rules="# Target rules")

        self.install_project("plugin_one", "plugin_two")

        self.assertEqual(
            (self.target_root / "AGENTS.md").read_text(encoding="utf-8"),
            "# Target rules\n\n# Plugin one\n\n# Plugin two\n",
        )

    def test_plugins_with_skills_are_installed_into_opencode_skills(self) -> None:
        self.make_plugin(
            "plugin_one",
            skills={
                "env-skill/SKILL.md": "# Env skill",
                "env-skill/references/guide.md": "use envs carefully",
            },
        )
        self.make_plugin(
            "plugin_two",
            skills={"ops-skill/SKILL.md": "# Ops skill"},
        )
        self.make_target()

        self.install_project("plugin_one", "plugin_two")

        self.assertEqual(
            (
                self.target_root / ".opencode" / "skills" / "env-skill" / "SKILL.md"
            ).read_text(encoding="utf-8"),
            "# Env skill",
        )
        self.assertEqual(
            (
                self.target_root
                / ".opencode"
                / "skills"
                / "env-skill"
                / "references"
                / "guide.md"
            ).read_text(encoding="utf-8"),
            "use envs carefully",
        )
        self.assertEqual(
            (
                self.target_root / ".opencode" / "skills" / "ops-skill" / "SKILL.md"
            ).read_text(encoding="utf-8"),
            "# Ops skill",
        )

    def test_existing_target_skills_are_backed_up_before_replace(self) -> None:
        self.make_plugin(
            "plugin_one",
            skills={"fresh-skill/SKILL.md": "fresh skill"},
        )
        self.make_target(skills={"old-skill/SKILL.md": "old skill"})

        result = self.install_project("plugin_one")

        self.assertEqual(result, 0)
        self.assertFalse(
            (
                self.target_root / ".opencode" / "skills" / "old-skill" / "SKILL.md"
            ).exists()
        )
        self.assertEqual(
            (
                self.target_root / ".opencode" / "skills" / "fresh-skill" / "SKILL.md"
            ).read_text(encoding="utf-8"),
            "fresh skill",
        )

        backup_session = self.only_backup_session()
        self.assertEqual(
            (
                backup_session / ".opencode" / "skills" / "old-skill" / "SKILL.md"
            ).read_text(encoding="utf-8"),
            "old skill",
        )

    def test_conflicting_plugin_skills_raise_error(self) -> None:
        self.make_plugin("plugin_one", skills={"shared-skill/SKILL.md": "one"})
        self.make_plugin("plugin_two", skills={"shared-skill/SKILL.md": "two"})
        self.make_target()

        with self.assertRaisesRegex(
            InstallPluginsError,
            "Conflicting skill entries were found",
        ):
            self.install_project("plugin_one", "plugin_two")

        self.assertFalse((self.target_root / ".opencode" / "skills").exists())

    def test_single_plugin_config_writes_project_opencode_json(self) -> None:
        config = {"permission": {"read": "allow"}}
        self.make_plugin("plugin_one", config=config)
        self.make_target()

        self.install_project("plugin_one")

        self.assertEqual(read_json(self.target_root / "opencode.json"), config)
        self.assertTrue(
            (self.target_root / "opencode.json").read_text(encoding="utf-8").endswith(
                "\n"
            )
        )

    def test_multiple_plugin_configs_are_strictly_aggregated(self) -> None:
        self.make_plugin(
            "plugin_one",
            config={
                "$schema": "https://opencode.ai/config.json",
                "permission": {"read": {"*": "allow"}},
            },
        )
        self.make_plugin(
            "plugin_two",
            config={
                "$schema": "https://opencode.ai/config.json",
                "permission": {"edit": {"*": "ask"}},
            },
        )
        self.make_target()

        self.install_project("plugin_one", "plugin_two")

        self.assertEqual(
            read_json(self.target_root / "opencode.json"),
            {
                "$schema": "https://opencode.ai/config.json",
                "permission": {
                    "read": {"*": "allow"},
                    "edit": {"*": "ask"},
                },
            },
        )

    def test_conflicting_plugin_configs_raise_before_writing(self) -> None:
        self.make_plugin("plugin_one", config={"permission": {"read": "allow"}})
        self.make_plugin("plugin_two", config={"permission": {"read": "deny"}})
        self.make_target()

        with self.assertRaisesRegex(InstallPluginsError, "Conflicting opencode.json"):
            self.install_project("plugin_one", "plugin_two")

        self.assertFalse((self.target_root / "opencode.json").exists())
        self.assertFalse((self.target_root / ".opencode" / "agents").exists())

    def test_invalid_or_empty_plugin_config_fails(self) -> None:
        self.make_plugin("plugin_one", config="")
        self.make_target()

        with self.assertRaisesRegex(InstallPluginsError, "empty opencode.json"):
            self.install_project("plugin_one")

    def test_existing_project_config_is_backed_up_before_replacement(self) -> None:
        self.make_plugin("plugin_one", config={"permission": {"read": "allow"}})
        self.make_target(config={"permission": {"read": "ask"}})

        self.install_project("plugin_one")

        self.assertEqual(
            read_json(self.target_root / "opencode.json"),
            {"permission": {"read": "allow"}},
        )
        backup_session = self.only_backup_session()
        self.assertEqual(
            read_json(backup_session / "opencode.json"),
            {"permission": {"read": "ask"}},
        )
        sibling_backups = sorted(self.target_root.glob("opencode.json.backup*"))
        self.assertEqual(len(sibling_backups), 1)
        self.assertEqual(
            read_json(sibling_backups[0]),
            {"permission": {"read": "ask"}},
        )


class SystemInstallPluginsTests(InstallerTestCase):
    def test_installs_rules_agents_skills_and_config_into_config_dir(self) -> None:
        self.make_plugin(
            "plugin_one",
            agents={"agent.md": "agent content"},
            skills={"skill-one/SKILL.md": "skill content"},
            rules="# Global rules",
            config={"permission": {"read": "allow"}},
        )

        self.install_system("plugin_one")

        self.assertEqual(
            (self.config_dir / "agents" / "agent.md").read_text(encoding="utf-8"),
            "agent content",
        )
        self.assertEqual(
            (
                self.config_dir / "skills" / "skill-one" / "SKILL.md"
            ).read_text(encoding="utf-8"),
            "skill content",
        )
        self.assertEqual(
            (self.config_dir / "AGENTS.md").read_text(encoding="utf-8"),
            "# Global rules\n",
        )
        self.assertEqual(
            read_json(self.config_dir / "opencode.json"),
            {"permission": {"read": "allow"}},
        )

    def test_system_install_fails_if_any_target_file_already_exists(self) -> None:
        self.make_plugin(
            "plugin_one",
            agents={"agent.md": "agent content"},
            skills={"skill-one/SKILL.md": "skill content"},
            rules="# Global rules",
            config={"permission": {"read": "allow"}},
        )
        write_file(self.config_dir / "agents" / "agent.md", "existing")

        with self.assertRaisesRegex(InstallPluginsError, "refusing to overwrite"):
            self.install_system("plugin_one")

        self.assertEqual(
            (self.config_dir / "agents" / "agent.md").read_text(encoding="utf-8"),
            "existing",
        )
        self.assertFalse((self.config_dir / "AGENTS.md").exists())
        self.assertFalse((self.config_dir / "opencode.json").exists())
        self.assertFalse((self.config_dir / "skills" / "skill-one").exists())

    def test_system_install_fails_if_skill_directory_already_exists(self) -> None:
        self.make_plugin(
            "plugin_one",
            skills={"skill-one/SKILL.md": "skill content"},
        )
        (self.config_dir / "skills" / "skill-one").mkdir(parents=True)

        with self.assertRaisesRegex(InstallPluginsError, "refusing to overwrite"):
            self.install_system("plugin_one")

        self.assertFalse(
            (self.config_dir / "skills" / "skill-one" / "SKILL.md").exists()
        )

    def test_system_install_fails_if_agents_or_config_already_exist(self) -> None:
        self.make_plugin(
            "plugin_one",
            rules="# Global rules",
            config={"permission": {"read": "allow"}},
        )
        write_file(self.config_dir / "AGENTS.md", "existing rules")
        write_file(self.config_dir / "opencode.json", "{}")

        with self.assertRaisesRegex(InstallPluginsError, "refusing to overwrite"):
            self.install_system("plugin_one")

        self.assertEqual(
            (self.config_dir / "AGENTS.md").read_text(encoding="utf-8"),
            "existing rules",
        )
        self.assertEqual(
            (self.config_dir / "opencode.json").read_text(encoding="utf-8"),
            "{}",
        )

    def test_conflicting_plugin_configs_fail_before_system_writes(self) -> None:
        self.make_plugin("plugin_one", config={"permission": {"read": "allow"}})
        self.make_plugin("plugin_two", config={"permission": {"read": "deny"}})

        with self.assertRaisesRegex(InstallPluginsError, "Conflicting opencode.json"):
            self.install_system("plugin_one", "plugin_two")

        self.assertFalse(self.config_dir.exists())

    def test_system_cli_accepts_config_dir_for_tests(self) -> None:
        self.make_plugin("plugin_one", rules="# Global rules")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = system_installer.install_system_plugins(
                self.config_dir,
                ["plugin_one"],
                repo_root=self.plugins_root,
            )

        self.assertEqual(result, 0)
        self.assertIn("Wrote AGENTS.md", stdout.getvalue())
        self.assertEqual(
            (self.config_dir / "AGENTS.md").read_text(encoding="utf-8"),
            "# Global rules\n",
        )

    def test_system_install_overwrites_conflicting_artifacts_when_enabled(
        self,
    ) -> None:
        self.make_plugin(
            "plugin_one",
            agents={"agent.md": "agent content"},
            skills={"skill-one/SKILL.md": "skill content"},
            rules="# Global rules",
            config={"permission": {"read": "allow"}},
        )
        write_file(self.config_dir / "agents", "old agents artifact")
        write_file(self.config_dir / "skills", "old skills artifact")
        write_file(self.config_dir / "AGENTS.md", "old rules")
        write_file(self.config_dir / "opencode.json", '{"permission": {"read": "deny"}}')
        write_file(self.config_dir / "unrelated.txt", "keep me")

        result = self.install_system("plugin_one", overwrite_existing=True)

        self.assertEqual(result, 0)
        self.assertEqual(
            (self.config_dir / "agents" / "agent.md").read_text(encoding="utf-8"),
            "agent content",
        )
        self.assertEqual(
            (
                self.config_dir / "skills" / "skill-one" / "SKILL.md"
            ).read_text(encoding="utf-8"),
            "skill content",
        )
        self.assertEqual(
            (self.config_dir / "AGENTS.md").read_text(encoding="utf-8"),
            "# Global rules\n",
        )
        self.assertEqual(
            read_json(self.config_dir / "opencode.json"),
            {"permission": {"read": "allow"}},
        )
        self.assertEqual(
            (self.config_dir / "unrelated.txt").read_text(encoding="utf-8"),
            "keep me",
        )


if __name__ == "__main__":
    unittest.main()
