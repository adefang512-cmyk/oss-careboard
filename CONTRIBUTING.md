# Contributing

Thank you for helping make open-source maintenance calmer and more sustainable.

## Before opening a change

- Search existing issues first.
- Keep proposals focused on a concrete maintainer workflow.
- Do not include private repository data, tokens, or copied issue content.
- Open an issue before large behavior or output-format changes.

## Local development

```bash
python -m pip install .
python -m unittest discover -s tests -v
```

The project intentionally uses the Python standard library only. A new
dependency should remove substantial complexity and be discussed first.

## Pull requests

Pull requests should include:

- A concise explanation of the maintainer problem being solved.
- Tests for changed behavior.
- Documentation updates for user-facing changes.
- Backward-compatible report output when practical.

## Roadmap

Good first contributions include:

- More report languages.
- Better release and activity health signals.
- Configurable label-based queues.
- GitHub Enterprise compatibility tests.
- Accessibility improvements to generated Markdown.

Look for issues labeled `good first issue` or `help wanted`. A focused change
with tests and documentation is easier to review than a large mixed proposal.
