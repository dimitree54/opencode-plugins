import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import install_plugins as installer


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class InstallPluginsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tempdir.name)
        self.plugins_root = self.workspace / "plugins"
        self.plugins_root.mkdir()
        self.target_root = self.workspace / "target"
        self.target_root.mkdir()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def make_plugin(
        self,
        name: str,
        *,
        agents: dict[str, str] | None = None,
        skills: dict[str, str] | None = None,
        rules: str | None = None,
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

        return plugin_root

    def make_target(
        self,
        *,
        agents: dict[str, str] | None = None,
        skills: dict[str, str] | None = None,
        rules: str | None = None,
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
                    self.target_root / ".opencode" / "skills" / relative_path, content
                )

        if rules is not None:
            write_file(self.target_root / "AGENTS.md", rules)

    def install(self, *plugins: str) -> int:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            return installer.install_plugins(
                self.target_root,
                list(plugins),
                repo_root=self.plugins_root,
            )

    def only_backup_session(self) -> Path:
        backup_root = self.target_root / "agents_backup"
        self.assertTrue(backup_root.exists(), "expected backup directory to exist")
        sessions = sorted(path for path in backup_root.iterdir() if path.is_dir())
        self.assertEqual(len(sessions), 1, "expected a single backup session")
        return sessions[0]

    def test_conflicting_plugin_agents_raise_error(self) -> None:
        self.make_plugin("plugin_one", agents={"shared.md": "one"})
        self.make_plugin("plugin_two", agents={"shared.md": "two"})
        self.make_target()

        with self.assertRaisesRegex(
            installer.InstallPluginsError,
            "Conflicting agent files were found",
        ):
            self.install("plugin_one", "plugin_two")

        self.assertFalse((self.target_root / ".opencode" / "agents").exists())

    def test_existing_target_agents_are_backed_up_before_replace(self) -> None:
        self.make_plugin("plugin_one", agents={"fresh.md": "fresh agent"})
        self.make_target(agents={"old.md": "old agent"})

        result = self.install("plugin_one")

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

        self.install("plugin_one")

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

        self.install("plugin_one", "plugin_two")

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

        self.install("plugin_one", "plugin_two")

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

        result = self.install("plugin_one")

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
            installer.InstallPluginsError,
            "Conflicting skill entries were found",
        ):
            self.install("plugin_one", "plugin_two")

        self.assertFalse((self.target_root / ".opencode" / "skills").exists())


if __name__ == "__main__":
    unittest.main()
