# GitHub Advanced — PoC learning material

Practice review gates, merge strategies, conflicts, GitHub Actions workflows, and token permissions.

Prerequisites: Complete GitHub Basics or understand repositories, commits, branches, and pull requests.

4 lessons · 16 exercises · approximately 12 minutes.

These original study notes paraphrase the linked GitHub documentation, checked 3 November 2026. The JSON pack includes questions and answer explanations; this file is the source material for reviewing or regenerating the course. No GitHub account or network connection is needed to study the bundled pack.

## 1. Review gates and protected branches

Reviews can comment, approve, or request changes. Branch protection can require approvals and passing status checks before merging. A green check does not replace a required approval. Exact enforcement depends on repository settings and bypass permissions; a review request alone is not a configured merge gate.

Sources: [GitHub Docs: Pull request reviews](https://docs.github.com/en/pull-requests/reference/pull-request-reviews), [GitHub Docs: About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

## 2. Choose a merge strategy and handle conflicts

A merge commit preserves branch commits and an explicit integration point. Squash and merge combines the pull request into one commit on the base branch. Rebase and merge places the commits onto the base without a merge commit. Conflicting edits need resolution before merging. Choosing one side blindly can discard intended changes.

Sources: [GitHub Docs: Pull request merges](https://docs.github.com/en/pull-requests/reference/pull-request-merges), [GitHub Docs: Merge conflicts](https://docs.github.com/en/pull-requests/reference/merge-conflicts)

## 3. Understand an Actions workflow

GitHub Actions can automate builds and tests. Workflow YAML files live in .github/workflows. Events such as pull_request can trigger them. A workflow contains jobs; jobs run on runners and contain steps. A step can run a command or use an action. In YAML, runs-on selects the runner for a job.

Sources: [GitHub Docs: Workflows](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows), [GitHub Docs: Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [GitHub Docs: Quickstart for GitHub Actions](https://docs.github.com/en/actions/get-started/quickstart)

## 4. Limit automation permissions

GITHUB_TOKEN lets workflows authenticate. Grant only the permissions a job needs. For example, permissions: contents: read grants read access to repository contents rather than write access. Fork pull_request workflows normally receive a read-only token and do not receive repository secrets; repository or enterprise settings can affect this behavior. Do not assume untrusted fork code can safely use privileged credentials.

Sources: [GitHub Docs: Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [GitHub Docs: Authenticate with GITHUB_TOKEN](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token), [GitHub Docs: Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)

## Practice outside the app

In a disposable repository, compare merge options and inspect a small pull-request workflow. Discuss which reviews and checks your team would require. Do not use real credentials in practice files. The app does not execute workflows or alter repository settings.
