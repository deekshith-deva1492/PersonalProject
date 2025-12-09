# GitHub Push Instructions - Quick Reference

## Initial Setup (One Time Only)

### 1. Create GitHub Repository
- Go to: https://github.com/new
- Name: TradingBot
- Description: Advanced NIFTY 50 Trading Bot with 8-layer filtering
- Choose: Public or Private
- **DO NOT** initialize with README
- Click: "Create repository"

### 2. Connect Local Repo to GitHub

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/TradingBot.git
git branch -M main
git push -u origin main
```

You'll be prompted for GitHub credentials:
- Username: your GitHub username
- Password: use Personal Access Token (not your password!)

### Get Personal Access Token:
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select scopes: `repo` (all)
4. Copy the token and use as password

---

## Daily Workflow (For Future Updates)

### Making Changes

```bash
# 1. Check what changed
git status

# 2. Add all changes
git add .

# 3. Commit with message
git commit -m "Your descriptive message here"

# 4. Push to GitHub
git push
```

### Example Commits

```bash
# Adding a new feature
git commit -m "Added ADX indicator for trend strength"

# Fixing a bug
git commit -m "Fixed volume calculation in realtime_stream.py"

# Updating strategy
git commit -m "Adjusted RSI thresholds from 30/70 to 25/75"

# Documentation
git commit -m "Updated README with new strategy filters"
```

---

## Useful Git Commands

### Check Status
```bash
git status                    # See what's changed
git status --ignored          # Verify ignored files
git log --oneline            # See commit history
git diff                     # See exact changes
```

### Branch Management
```bash
git branch                   # List branches
git branch feature-name      # Create new branch
git checkout feature-name    # Switch to branch
git checkout -b feature-name # Create and switch
```

### Undo Changes
```bash
git restore filename         # Discard changes to file
git restore .               # Discard all changes
git reset HEAD~1            # Undo last commit (keep changes)
```

### Pull Latest Changes
```bash
git pull                    # Get updates from GitHub
```

---

## Security Checklist

### ✅ Files That ARE Pushed to GitHub:
- ✓ All Python source code (`src/`)
- ✓ Configuration templates (`config.yaml`)
- ✓ Documentation (`*.md` files)
- ✓ Requirements file (`requirements.txt`)
- ✓ Dashboard files (`dashboard/`)

### ❌ Files That ARE NOT Pushed (Protected):
- ✗ `.env` - Your API credentials
- ✗ `access_token.txt` - Zerodha tokens
- ✗ `*.log` - Log files
- ✗ `__pycache__/` - Python cache
- ✗ `zerodha_*.txt` - Login data

### Verify Before Pushing:
```bash
git status
# Make sure .env is NOT listed!
```

---

## Troubleshooting

### Problem: ".env appears in git status"
```bash
# Solution 1: Remove from tracking
git rm --cached .env
git commit -m "Remove .env from tracking"

# Solution 2: Verify .gitignore
cat .gitignore | Select-String ".env"
```

### Problem: "Permission denied (publickey)"
- Use HTTPS URL instead of SSH
- Or set up SSH keys: https://docs.github.com/en/authentication

### Problem: "Failed to push some refs"
```bash
# Pull changes first, then push
git pull --rebase
git push
```

### Problem: "Merge conflict"
```bash
# Open conflicted files, resolve conflicts
git add .
git commit -m "Resolved merge conflict"
git push
```

---

## Best Practices

1. **Commit Often**: Small, focused commits are better
2. **Descriptive Messages**: Explain WHAT and WHY
3. **Test Before Commit**: Make sure code works
4. **Pull Before Push**: Stay synced with remote
5. **Never Commit Secrets**: Double-check .env is ignored

---

## Project Stats

- **Total Files**: 61
- **Total Lines**: 11,522+
- **Strategy Filters**: 8 layers
- **Supported Stocks**: 49 NIFTY 50
- **Latency**: <2 seconds (WebSocket)

---

## Quick Reference Card

```
Common Commands:
├─ git status          → Check changes
├─ git add .           → Stage all changes
├─ git commit -m "msg" → Commit with message
├─ git push            → Upload to GitHub
├─ git pull            → Download from GitHub
└─ git log             → View history

Emergency:
├─ git restore .       → Discard all changes
├─ git reset --hard    → Reset to last commit
└─ git stash           → Save changes temporarily
```

---

**Remember**: Your `.env` file with API credentials is PROTECTED and will never be pushed to GitHub!

---

Generated: December 9, 2025
