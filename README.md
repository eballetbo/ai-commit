# AI-Powered Git Commit Assistant

Small, local tool that generates commit messages from staged changes using an AI model.

## Quick summary

- Install the script as a Git custom command and run it as `git ai-commit`.
- The tool analyzes your staged diff and (optionally) a cached project-style profile to generate a concise commit message.

## Requirements

- Python 3
- `google-generativeai` (install with `pip install -r requirements.txt`)
- A Gemini API key in `GOOGLE_API_KEY` or enter it when prompted

## Install & usage (quick)

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Install as a git command

```bash
# make it executable
chmod +x ai-commit.py

# rename to the git-subcommand form and copy to a bin directory on your PATH
mv ai-commit.py git-ai-commit
cp git-ai-commit ~/.local/bin/  # or /usr/local/bin (use sudo if needed)

# OR create a symlink from the repository into ~/.local/bin
ln -s "$(pwd)/ai-commit.py" ~/.local/bin/git-ai-commit
```

Notes:

- The file must be named `git-ai-commit` and be executable so Git will expose it as `git ai-commit`.
- Ensure the target directory (`~/.local/bin` or `/usr/local/bin`) is in your `PATH`.

## Project-style analysis & cache

You can create a small, per-repo style profile to improve prompts and avoid repeated scanning.

```bash
git ai-commit --analyze            # scans recent commits and writes .git/ai-commit-style.json
git ai-commit --analyze --history-depth 2000
```

To force recompute at commit time:

```bash
git ai-commit --force-analyze
```

Default cache file: `.git/ai-commit-style.json` (can be overridden with `--cache-file`).

## Editor behavior

- By default, the script silently generates the commit message and opens your configured git editor (similar to `git commit`).
- Use `--verbose` to see progress messages and a confirmation prompt before committing.

## Passing additional context

You can provide additional context to the AI using the `--context` flag. This is useful when you want to help the AI understand the scope of the changes more deeply. For example:

```bash
git ai-commit --context "fixes the following build error: undefined reference to foo"
git ai-commit --context "part of ticket PROJ-123"
```

The context is included in the AI prompt and can help generate a more accurate commit message.

## Project commit guidelines

Some projects maintain strict commit message guidelines (kernel-style, project-specific
templates, or ticket metadata). Pass those guidelines to the AI so the generated message
follows them closely. The tool accepts a single `--guidelines` argument which can be one of:

- Inline text (quoted on the command line)
- A local file path (e.g. `./COMMIT_GUIDELINES.md`)
- An `http://` or `https://` URL (the tool will download the page and use its text)

When you provide `--guidelines`, the tool will automatically cache the guidelines into the
repository style cache (default: `.git/ai-commit-style.json`), overwriting any previously
cached guidelines for that repo. On subsequent runs, if you don't pass `--guidelines`, the
cached guidelines will be used automatically.

Examples:

```bash
# Pass guidelines inline
git ai-commit --guidelines "Subjects must start with a subsystem in brackets, e.g. [net]: and include a bug tracker ID when applicable"

# Pass a local file containing longer guidelines
git ai-commit --guidelines ./COMMIT_GUIDELINES.md

# Pass a URL to fetch guidelines (downloaded and cached)
git ai-commit --guidelines https://example.com/COMMIT_POLICY.md
```

## Verbose and quiet modes

By default, `git ai-commit` runs in **quiet mode**: it silently generates the message and opens your configured git editor (similar to `git commit`). This is the recommended workflow for everyday use.

For a more interactive experience with progress messages and confirmation prompts, use the `--verbose` flag:

```bash
git ai-commit --verbose
```

In verbose mode, you'll see:
- Progress messages as the tool analyzes your changes
- The AI-generated commit message displayed in full
- A prompt to confirm before committing, with options to edit (`e`) or abort

## Forwarding git flags

- Any unknown flags passed to `git ai-commit` are forwarded directly to the underlying `git commit` command. For example:

```bash
git ai-commit --no-verify --signoff
```

If you pass a commit-message flag (`-m`, `-F`, `--file`), the tool will respect it and will not overwrite it with the AI suggestion.

## Recommended workflow

1. Stage your changes: `git add <files>`
2. Use `git ai-commit` for the quiet, editor-based workflow (similar to `git commit`)
3. Or use `git ai-commit --verbose` for an interactive confirmation flow
4. Or use `git ai-commit --dry-run` to preview the generated message without committing

## Contributing

- PRs and issues welcome.

## License

- See `LICENSE` in this repository.
