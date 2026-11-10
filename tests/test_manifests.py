"""Manifest and MCP config checks. Run: python3 -m unittest discover -s tests"""

import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
CLAUDE_KEY = "${user_config.DESEARCH_API_KEY}"
ENV_KEY = "${DESEARCH_API_KEY}"

# Manifests read by hosts that cannot expand ${user_config.*}. Grok Build 1.0.77
# picks the root plugin.json over .grok-plugin/plugin.json, so each one must
# point at mcp.json or the host falls back to .mcp.json.
NON_CLAUDE_MANIFESTS = ["plugin.json", ".grok-plugin/plugin.json", ".cursor-plugin/plugin.json"]
ALL_MANIFESTS = NON_CLAUDE_MANIFESTS + [".claude-plugin/plugin.json"]


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

    def test_claude_manifest_keeps_default_mcp_json_and_user_config(self):
        manifest = load(".claude-plugin/plugin.json")
        self.assertNotIn("mcpServers", manifest)
        self.assertTrue(manifest["userConfig"]["DESEARCH_API_KEY"]["sensitive"])
        self.assertTrue(manifest["userConfig"]["DESEARCH_API_KEY"]["required"])

    def test_claude_mcp_uses_user_config_placeholder(self):
        self.assertEqual(server(".mcp.json")["env"], {"DESEARCH_API_KEY": CLAUDE_KEY})

    def test_shared_mcp_uses_env_placeholder(self):
        self.assertEqual(server("mcp.json")["env"], {"DESEARCH_API_KEY": ENV_KEY})
        self.assertNotIn("user_config", (ROOT / "mcp.json").read_text(encoding="utf-8"))

    def test_both_mcp_configs_launch_same_server(self):
        claude, shared = server(".mcp.json"), server("mcp.json")
        self.assertEqual(claude["command"], shared["command"])
        self.assertEqual(claude["args"], shared["args"])

    def test_versions_match(self):
        versions = {rel: load(rel)["version"] for rel in ALL_MANIFESTS}
        self.assertEqual(len(set(versions.values())), 1, versions)


if __name__ == "__main__":
    unittest.main()
