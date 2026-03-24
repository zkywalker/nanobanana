# Initialization Flow

When the user runs `init`, actively diagnose and fix issues — don't just report status.

## Step 1: Run diagnostics

Run `python3 ~/.claude/skills/nanobananaskill/scripts/nanobanana.py init --skip-test` first (skip API test until basics are ready). Parse the JSON output.

## Step 2: Fix missing dependencies automatically

If `dependencies.ok` is false:
- **Directly run** `pip install google-genai pillow --break-system-packages` to install them
- Do not just tell the user to install — install for them
- If install fails, show the error and suggest the user run it manually with sudo or in a venv

## Step 3: Fix missing config file

If `config_source.ok` is false (no config found anywhere):
1. Ask the user for their Gemini API key. Provide guidance:
   - **Official Google API**: get a key from https://aistudio.google.com/apikey (free tier available)
   - **Proxy service**: if the user uses a proxy/relay (e.g., 88code), ask for their proxy key and base URL
2. Ask if they need a custom base URL (for proxy users) or will use the default Google endpoint
3. Once the user provides the key (and optionally base URL), create `~/.config/nanobanana/config.json`:
   ```json
   {"api_key": "<user's key>", "base_url": "<url if provided>"}
   ```
   (Omit `base_url` field if using default Google endpoint)

## Step 4: Fix missing API key

If config source exists but `api_key.ok` is false:
- A config file exists but `GEMINI_API_KEY` / `api_key` is empty or missing
- Ask the user for their key (same guidance as Step 3)
- Write/update the key in `~/.config/nanobanana/config.json` (preferred) or the existing config file

## Step 5: Run full diagnostics with API test

After dependencies and config are in place:
- Run `python3 ~/.claude/skills/nanobananaskill/scripts/nanobanana.py init` (without --skip-test)
- If API test passes → report success, environment is ready
- If API test fails:
  - **Auth error (401/403)**: API key is invalid — ask user to double-check and provide a new one
  - **Network error**: base URL may be wrong, or proxy is down — show the current base_url and ask user to verify
  - **Other error**: show the error message and suggest the user check their configuration

## Step 6: Report final status

Show a clear summary:
```
✅ 依赖: google-genai ✓, pillow ✓
✅ 配置: [实际命中的配置源] ✓
✅ API Key: AIzaSy...xxxx ✓
✅ 端点: https://... ✓
✅ 连通性: API 响应正常 ✓

🎉 环境已就绪，可以开始生图！试试: /nanobanana 一只猫趴在键盘上
```

Or if issues remain:
```
✅ 依赖: google-genai ✓, pillow ✓
✅ 配置: [实际命中的配置源] ✓
❌ 连通性: [error message]

请检查 API Key 和端点地址是否正确。
```
