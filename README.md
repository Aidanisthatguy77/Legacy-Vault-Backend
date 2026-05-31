# Vault AI Backend 🏀

## AI Routing Backend for NBA 2K Legacy Vault

This backend handles AI chat routing:
- **URLs/Media links** → Claude (for analysis)
- **Text questions** → Gemini (for knowledge)
- **No keys** → Built-in demo responses

## Deploy to Deno Deploy (FREE!)

1. Go to [deno.com/deploy](https://deno.com/deploy)
2. Sign up with GitHub
3. Create new project → Connect this repo
4. Add environment variables:
   - `ANTHROPIC_API_KEY` = your Claude key
   - `GOOGLE_API_KEY` = your Gemini key

## API Endpoint

```
POST /
```

### Request:
```json
{
  "messages": [{ "role": "user", "content": "What is the Legacy Vault?" }],
  "session_id": "unique-id"
}
```

### Response:
```json
{
  "response": "The Legacy Vault is..."
}
```

## Free Tier: 100K requests/day, always-on!
