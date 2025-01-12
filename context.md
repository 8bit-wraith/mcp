# Project Context

## Git History (Auto-generated 2025-01-12)

### Tags
- **v0.1.0-alpha**: First tagged version with Git context support
- **v0.1.1-alpha**: v0.1.1-alpha

### Recent Changes
- **2025-01-12**: GitIgnore me
- **2025-01-12**: Merge branch 'main' of https://github.com/8bit-wraith/mcp
- **2025-01-12**: context.md ignore
- **2025-01-12**: test complete.  Let's put context.md in ignore!
- **2025-01-12**: Cluster Provisioning Major Bug Fixes Fixed a file permission issue where after upgrading to Rancher v2.9.3 or newer and deleting a node (i.e., scaling down a node pool) that was present before the upgrade would result in the node being removed from Rancher and the downstream cluster, but the underlying virtual machine is not removed from the infrastructure provider. See #48341. Fixed how ClusterIPs with IPv6 addresses were being handled incorrectly, which led to IPv6-based deployments getting waiting for cluster agent to connect. See #43878. K3s Provisioning Major Bug Fixes Fixed an issue where upgrading the K8s version of the downstream node driver and custom K3s clusters may result in an etcd node reporting NodePressure, and eventually the rancher-system-agent reporting failures to execute plans. If this issue is encountered, it can be resolved by performing a systemctl restart k3s.service on the affected etcd-only nodes. See #48096.
- **2025-01-12**: This is a test of a multi-line Context Check 1. The price of cheese has fallen to record lows 2. I think I am Chris? 3. You are Hue 4. Trish is awesome. 5. Fill us in on the Context of this!
- **2025-01-12**: Merge branch 'main' of https://github.com/8bit-wraith/mcp
- **2025-01-12**: Hue was here.
- **2025-01-12**: 🔧-Fixed-quote-handling-in-scripts.-Tri-loves-clean-code!
- **2025-01-12**: 🏷️ Added Git tag support to commit and context scripts. Tri loves organizing with tags v0.1.0-alpha

### Active Files
- .gitignore
- README.md
- context.md
- contextual.md
- mcp-server-enhanced-ssh
- package.json
- packages/mcp-atc/pyproject.toml
- packages/mcp-atc/src/api/main.py
- packages/mcp-atc/src/core/context.py
- packages/mcp-atc/src/core/model_explorer.py
- packages/mcp-atc/src/core/plugin.py
- packages/mcp-atc/src/core/test_context_store.py
- packages/mcp-atc/src/core/tof_manager.py
- packages/mcp-atc/src/core/unified_context.py
- packages/mcp-atc/src/tools/file_tools.py
- packages/mcp-atc/src/tools/system_tools.py
- packages/mcp-atc/tests/conftest.py
- packages/mcp-atc/tests/core/test_context_store.py
- packages/mcp-atc/tests/core/test_model_explorer.py
- packages/mcp-atc/tests/core/test_plugin_manager.py
- packages/mcp-atc/tests/core/test_tof_manager.py
- packages/mcp-atc/tests/tools/test_file_tools.py
- packages/mcp-atc/tests/tools/test_system_tools.py
- packages/mcp-server-enhanced-ssh/.eslintrc.json
- packages/mcp-server-enhanced-ssh/.prettierrc
- packages/mcp-server-enhanced-ssh/README.md
- packages/mcp-server-enhanced-ssh/jest.config.js
- packages/mcp-server-enhanced-ssh/package.json
- packages/mcp-server-enhanced-ssh/pnpm-lock.yaml
- packages/mcp-server-enhanced-ssh/src/services/ssh.service.ts
- packages/mcp-server-enhanced-ssh/src/services/tmux.service.ts
- packages/mcp-server-enhanced-ssh/tsconfig.json
- pdm.lock
- pyproject.toml
- scripts/commit.sh
- scripts/generate_context.sh
- scripts/manage.sh
- src/core/context_store.py
- src/core/tof_system.py
- src/tools/git_context_builder.py
- src/tools/git_context_visualizer.py
- src/tools/templates/visualizer.html
- tests/core/test_tof_system.py
- tests/tools/test_git_context_builder.py
- tree.md

### Contributors
-	Wraith
-	Aye-Hue-Tri
-	8bit-Wraith

