# How to Translate eudplib

## Prerequisites

- Python 3.10 or later
- [Babel](https://pypi.org/project/Babel/) (`pip install babel`)

## Quick Start

1. Clone the repository:
   ```
   git clone https://github.com/armoha/eudplib --recursive
   ```

2. Extract translatable strings to `.pot` file:
   ```
   python -m babel.messages.frontend extract --charset=UTF-8 --no-location --no-wrap --output=src/eudplib/localize/base.pot src/eudplib
   ```

3. Update existing `.po` catalog with new/modified strings:
   ```
   python -m babel.messages.frontend update -D eudplib -i src/eudplib/localize/base.pot -d src/eudplib/localize -l ko_KR --no-wrap -N
   ```
   Replace `ko_KR` with your target locale.

4. Edit translations in `.po` file using a text editor or [Poedit](https://poedit.net/).

5. Compile `.po` to `.mo`:
   ```
   python -m babel.messages.frontend compile -D eudplib -d src/eudplib/localize
   ```

6. Send a pull request for the `.po` file.

## File Structure

```
src/eudplib/localize/
  base.pot                              # Extracted translatable strings (template)
  ko_KR/LC_MESSAGES/
    eudplib.po                          # Korean translations (source)
    eudplib.mo                          # Compiled binary (auto-generated, not tracked)
```

## Guidelines

### Named Placeholders

All messages use **named placeholders** (e.g., `{name}`) instead of positional `{}`.
This allows translators to reorder arguments to match their language's grammar.

```python
# Good
_("Can't assign {src} to {dst}").format(src=other, dst=self)

# Bad (don't use positional)
_("Can't assign {} to {}").format(other, self)
```

### Rust Strings

The Rust extension (`src/rust/`) also supports translation via `crate::localize::tr()`.
Rust strings share the same `.po`/`.pot` files as Python.

When adding new user-facing strings in Rust, also add them to `base.pot` manually
(or via a custom extractor) and update the `.po` files.

### Compiling .mo Files

`.mo` files are **not tracked in Git**. They are compiled automatically during
the build process (`build_backend.py`) and when running `pybabel compile`.

For development, compile manually:
```
python -m babel.messages.frontend compile -D eudplib -d src/eudplib/localize
```

## Legacy Workflow (Deprecated)

The old workflow used `pygettext.py` from Python's Tools directory.
`pygettext.py` has been removed in recent Python distributions.
Use the Babel-based workflow described above instead.
