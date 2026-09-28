# xcrong Homebrew Tap 🍺

Personal Homebrew tap for xcrong apps.

```bash
brew tap xcrong/tap
brew install brewup
```

| Formula | Upstream | Description |
| ------- | -------- | ----------- |
| `brewup` | [xcrong/brewup](https://github.com/xcrong/brewup) | One-command Homebrew update, upgrade, and cleanup |
| `pig` | [xcrong/pig](https://github.com/xcrong/pig) | Grok Build with Providers (`xcrong/tap/pig`; bare `pig` resolves to Apache Pig in homebrew-core) |

Formulae track their upstream GitHub releases automatically via a daily workflow.

## Adding a new app

1. Add `Formula/<name>.rb` for the new app.
2. Register it in `scripts/update-formula.py` (`FORMULAE`), with its upstream repo and release asset names.
3. Run `python3 scripts/update-formula.py <name>` once to verify, then commit.

> Previous location: this tap used to live at `xcrong/homebrew-brewup` as `xcrong/brewup`.
> If you tapped the old name, switch with:
>
> ```bash
> brew untap xcrong/brewup
> brew tap xcrong/tap
> ```
