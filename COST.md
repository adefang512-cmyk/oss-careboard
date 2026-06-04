# Cost and Billing

OSS Careboard is designed to run at zero monetary cost.

- It uses only the Python standard library.
- It does not call OpenAI APIs or other paid model APIs.
- It does not require an API key, subscription, or payment method.
- Its repository workflow uses a standard GitHub-hosted runner in a public
  repository.
- It reads repository metadata and never enables paid GitHub features.

Running the CLI locally does not create a bill. GitHub currently documents that
standard GitHub-hosted runners are free for public repositories:

<https://docs.github.com/en/actions/concepts/billing-and-usage>

Users who copy the project into a private repository or change its workflow are
responsible for reviewing their own GitHub plan and billing settings.
