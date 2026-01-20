# gh-workflow-cron-trigger

automatically trigger GitHub Actions workflows with cron scheduling.

## How to (As a User)

1. Clone this Repository:

    ```bash
    git clone https://github.com/TheSpeedCubing/gh-workflow-cron-trigger.git
    cd gh-workflow-cron-trigger
    ```

2. Update `mounts/config.json` as desired

    ```conf
    {
      "repos": {
        "user/repo1": {
          "workflows": [
            {
              "name": "build.yml",
              "branch": "main",
              "cron": "0 12 * * *"
            },
            {
              "name": "deploy.yml",
              "branch": "develop",
              "cron": "30 3 * * *"
            }
          ]
        }
      }
    }
    ```

3. Add GitHub classic token in `.env`

    ```
    GITHUB_TOKEN=XXX
    ```

5. Start the container:

    ```bash
    sudo docker compose up -d
    ```
