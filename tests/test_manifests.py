"""Manifest and MCP config checks. Run: python3 -m unittest discover -s tests"""

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENV_KEY = "${DESEARCH_API_KEY}"

# Manifests read by hosts that cannot expand ${user_config.*}. Grok Build 1.0.77
# picks the root plugin.json over .grok-plugin/plugin.json, so each one must
# point at mcp.json or the host falls back to .mcp.json.
NON_CLAUDE_MANIFESTS = ["plugin.json", ".grok-plugin/plugin.json", ".cursor-plugin/plugin.json"]
CLAUDE_ROOT = "plugins/desearch"
CLAUDE_MANIFEST = CLAUDE_ROOT + "/.claude-plugin/plugin.json"


def load(rel):
    with open(ROOT / rel, encoding="utf-8") as f:
        return json.load(f)


def server(rel):
    return load(rel)["mcpServers"]["desearch"]


class ManifestTests(unittest.TestCase):
    def test_non_claude_manifests_select_mcp_json(self):
        for rel in NON_CLAUDE_MANIFESTS:
            with self.subTest(manifest=rel):
                self.assertEqual(load(rel).get("mcpServers"), "./mcp.json")

    def test_claude_uses_default_config_without_key_prompt(self):
        manifest = load(CLAUDE_MANIFEST)
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("userConfig", manifest)

    def test_claude_remote_config_has_no_local_or_secret_fallback(self):
        self.assertEqual(load(CLAUDE_ROOT + "/.mcp.json"), {"mcpServers": {"desearch": {
            "type": "http", "url": "https://mcp.desearch.ai/mcp"
        }}})

    def test_shared_mcp_uses_env_placeholder(self):
        self.assertEqual(server("mcp.json")["env"], {"DESEARCH_API_KEY": ENV_KEY})
        self.assertNotIn("user_config", (ROOT / "mcp.json").read_text(encoding="utf-8"))

    def test_legacy_hosts_keep_their_pinned_launcher(self):
        shared = server("mcp.json")
        self.assertEqual(shared["type"], "stdio")
        self.assertEqual(shared["command"], "npx")
        self.assertEqual(shared["args"], ["-y", "desearch-mcp-server@0.9.0"])

    def test_versions_are_scoped_to_each_host(self):
        self.assertEqual(load(CLAUDE_MANIFEST)["version"], "0.5.1")
        self.assertEqual(load(".claude-plugin/marketplace.json")["plugins"][0]["version"], "0.5.1")
        for rel in NON_CLAUDE_MANIFESTS:
            with self.subTest(manifest=rel):
                self.assertEqual(load(rel)["version"], "0.5.0")

    def test_marketplace_resolves_only_the_contained_claude_package(self):
        marketplace = load(".claude-plugin/marketplace.json")
        self.assertEqual(marketplace["name"], "desearch")
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        self.assertEqual(entry["name"], "desearch")
        self.assertEqual(entry["source"], "./" + CLAUDE_ROOT)
        self.assertEqual(load(CLAUDE_MANIFEST)["name"], entry["name"])
        self.assertFalse((ROOT / ".claude-plugin/plugin.json").exists())
        self.assertFalse((ROOT / ".mcp.json").exists())
        package = ROOT / entry["source"]
        expected = {".claude-plugin/plugin.json", ".mcp.json", "README.md", "LICENSE", "assets/logo.png"}
        expected.update("skills/" + name + "/SKILL.md" for name in (
            "desearch", "desearch-social", "desearch-people-search", "desearch-company-search"))
        self.assertEqual({str(p.relative_to(package)) for p in package.rglob("*") if p.is_file()}, expected)
        for path in package.rglob("*"):
            self.assertTrue(path.resolve().is_relative_to(package.resolve()))
            self.assertFalse(path.is_symlink())

    def test_claude_skills_keep_tool_guidance_with_remote_auth(self):
        old_transport = "The plugin launches `npx -y desearch-mcp-server@0.9.0`, which registers"
        for legacy in (ROOT / "skills").glob("*/SKILL.md"):
            with self.subTest(skill=legacy.parent.name):
                expected = legacy.read_text(encoding="utf-8")
                expected = expected.replace(
                    "The host passes `DESEARCH_API_KEY` into the server. " + old_transport + " 39 tools.",
                    "The plugin connects to `https://mcp.desearch.ai/mcp` over HTTPS using host-managed OAuth. Authenticate through the host before calling the tools; the hosted service registers 39 tools.")
                expected = expected.replace(old_transport,
                    "The plugin connects to `https://mcp.desearch.ai/mcp` using host-managed OAuth. The hosted service registers")
                self.assertEqual((ROOT / CLAUDE_ROOT / legacy.relative_to(ROOT)).read_text(encoding="utf-8"), expected)


if __name__ == "__main__":
    unittest.main()
