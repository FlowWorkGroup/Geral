# Infisical authentication via GitHub Actions

This repository includes a manual workflow at `.github/workflows/infisical-auth-check.yml` to validate Infisical Universal Auth without using the remote desktop terminal.

## One-time configuration

In the GitHub repository `FlowWorkGroup/Geral`:

1. Open **Settings → Secrets and variables → Actions**.
2. Choose **New repository secret** and add:
   - Name: `INFISICAL_CLIENT_ID` — value: the Client ID from the Infisical Machine Identity's Universal Auth client.
   - Name: `INFISICAL_CLIENT_SECRET` — value: the matching Client Secret.
3. Do not put either value in source files, commits, workflow inputs, or logs.

## Run the check

1. Open **Actions → Infisical Universal Auth Check**.
2. Choose **Run workflow** on branch `main`.
3. Open the run and verify the **Validate Universal Auth** step succeeds and reports that the CLI is authenticated.

The workflow intentionally validates authentication only. It does not print credentials or retrieve project secrets. Accessing project secrets later will also require the correct Infisical project, environment, and permissions.
