# ci-llm-code-review

This custom GitHub action provides AI-generated code reviews based on several freely available APIs, specifically, GitHub Models (which has various models including Microsoft Phi models, GPT4, Llama), Google Gemini, and Mistral AI. It uploads the reviews as HTML files, one per modified file, to a GitHub Actions artifact (ZIP file) associated with the calling workflow.

Author: Alex Richert ([@AlexanderRichert-NOAA](https://github.com/AlexanderRichert-NOAA))

## Installation

### Set up access keys for external services (optional; alternative is GitHub Models)

1. Create the API key for Gemini, Mistral, etc.

2. Copy and paste the key into a repository-level secret called GEMINI_API_KEY or MISTRAL_API_KEY as appropriate if you plan to run workflows in your fork (if you are putting a token in a repo owned by NOAA-EMC, see the Usage instructions below).

### Configure permissions for using GitHub Models (optional; alternative in external models Google Gemini, Mistral AI)

1. Create a fine-grained ("beta version") Personal Access Token for your user.

2. Copy and paste the Personal Access Token (`github_pat_XXXX...`) into a repository-level secret called GH_API_KEY if you plan to run workflows in your fork (if you are putting a token in a repo owned by NOAA-EMC, see the Usage instructions below). Do not enable any permissions for the PAT.

### Create a new workflow

Create a new workflow in your repository called, say, code-review.yml with the below code. Note that in order to use the pull_request_target trigger (see [Usage](#usage) below), this workflow must be in the base repository's default branch ("develop" for all NOAA-EMC repos). See [Inputs](#inputs) below for a list of configurable options.

```yaml
name: ai-code-review
on:
  workflow_dispatch:
    branches: '*'
  pull_request:
    branches: [develop]
  pull_request_target:
    branches: '*'

jobs:
  ai-code-review:
    runs-on: ubuntu-latest
    env:
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      MISTRAL_API_KEY: ${{ secrets.MISTRAL_API_KEY }}
      GH_API_KEY: ${{ secrets.GH_API_KEY }}
    permissions:
      pull-requests: write

    steps:

    - name: "Check if we want pull_request or pull_request_target"
      shell: bash
      run: |
        if [ ${{ github.event_name }} == 'pull_request' ]; then
          if [ ${{ github.event.pull_request.head.repo.owner.login }} == ${{ github.repository_owner }} ]; then
            echo CONTINUE=true >> $GITHUB_ENV
          fi
        elif [ ${{ github.event_name }} == 'pull_request_target' ]; then
          if [ ${{ github.event.pull_request.head.repo.owner.login }} != ${{ github.repository_owner }} ]; then
            echo CONTINUE=true >> $GITHUB_ENV
          fi
        elif [ ${{ github.event_name }} == 'workflow_dispatch' ]; then
          echo CONTINUE=true >> $GITHUB_ENV
        fi

    - name: "Code review"
      uses: AlexanderRichert-NOAA/ci-llm-code-review@develop
      if: ${{ env.CONTINUE == 'true' }}
      with:
        # Modify these inputs to select a model/API
        backend: gh-phi-4
        api-key-variable: GH_API_KEY
        github-token: ${{ github.token }}
```

## Usage:

There are three ways to use this action to generate AI-based code reviews. Be sure that you have created repo-level secrets as needed.

### Option 1: Manual trigger

1. Add the above workflow (code-review.yml) to some branch of your repository, which may be a fork.

2. In your repository, go to Actions, click the 'ai-code-review' workflow on the left, and click the 'Run workflow' menu on the right, selecting the branch you wish to obtain a code review for.

3. You may need to reload the page to see the new workflow instance. Click on it, and when it is complete, find the URL proceeding "Artifact download URL:" at the bottom to download the code reviews.

### Option 2: `pull_request` trigger: same repo
1. Add the above workflow (code-review.yml) to some branch of your repository. Typically this will be a repo owned by NOAA-EMC (this does not work from a fork branch).

2. Create a uniquely named secret (ALEX_GH_API_KEY) in your repository.  

3. As long as code-review.yml is present in the target branch of a GitHub pull request (i.e., the branch containing the modified code to be merged), it should automatically run and post a comment to the PR containing a link to the workflow artifact.

> [!NOTE]  
> In a repository with multiple contributors who each have their own API keys/secrets, you will need to assign the appropriate secret to the appropriate environment variable, for example, `GH_API_KEY: ${{ secrets.ALEX_GH_API_KEY }}`. Those modifications can either be reverted prior to merging the pull request, or can be left in place for the next user to modify as needed.

### Option 3: `pull_request_target` trigger: fork to upstream
1. Add the above workflow (code-review.yml) to the *default* branch ("develop" "main" etc.) of your upstream repository (i.e., owned by NOAA-EMC). It must be merged into that branch before it can be used.

2. Create a pull request targeting the default branch ("develop" "main" etc.) and this action should automatically run and post a comment to the PR containing a link to the workflow artifact.

> [!WARNING]  
>  When using a `pull_request_target` workflow event, the workflow will have access to the target repo's secrets. Be sure that when you open a pull request whose base repository has one or more workflows containing the `pull_request_target` trigger, it is a repository that you trust to not steal or abuse your secrets.

### Inputs

| Name | Description | Default | Required |
| ---- | ----------- | ------- | -------- |
| `backend` | Language model to query: gemini-2.0, mistral, or gh-<GitHub Models model name> (e.g., gh-phi-4, gh-gpt-4o) | `gemini-2.0` | No |
| `code-dir` | Directory containing modified code | `coderoot` | No |
| `api-key-variable` | Name of variable in which API key is stored; must be set in calling workflow | `LLM_API_KEY` | No |
| `api-key` | API key | `empty` | No |
| `reference-owner` | Owner of reference branch to diff against | `NOAA-EMC` | No |
| `reference-branch` | Name of reference branch to diff against | `${{ github.event.pull_request.base.ref \|\| 'develop' }}` | No |
| `context-lines` | Number of context lines for each file diff | `100` | No |
| `prompt-text` | Input prompt provided before each file diff | (see action.yml) | No |
| `github-token` | GitHub token for posting PR comments | n/a (must be set to `github.token` in calling workflow) | No |
