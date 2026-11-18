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

    def test_claude_uses_default_config_without_key_prompt(self):
        manifest = load(".claude-plugin/plugin.json")
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("userConfig", manifest)

    def test_claude_remote_config_has_no_local_or_secret_fallback(self):
        self.assertEqual(load(".mcp.json"), {"mcpServers": {"desearch": {
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

    def test_versions_match(self):
        versions = {rel: load(rel)["version"] for rel in ALL_MANIFESTS}
        versions["marketplace"] = load(".claude-plugin/marketplace.json")["plugins"][0]["version"]
        self.assertEqual(versions[".claude-plugin/plugin.json"], "0.5.1")
        self.assertEqual(len(set(versions.values())), 1, versions)


if __name__ == "__main__":
    unittest.main()
