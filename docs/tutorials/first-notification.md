# Tutorial: send your first notification

In this tutorial, you will run Moodle Mate locally and confirm a test notification at Webhook.site.

__Time required__: ~10 minutes

## Prerequisites

- `uv` installed
- A Webhook.site URL

## 1) Clone the repository

```bash
git clone https://github.com/EvickaStudio/Moodle-Mate.git
cd Moodle-Mate
```

## 2) Install dependencies

```bash
uv sync --extra dev
```

## 3) Create `.env`

```bash
cp example.env .env
```

Set at minimum:

```env
MOODLEMATE_MOODLE__URL=https://example.com
MOODLEMATE_MOODLE__USERNAME=demo_user
MOODLEMATE_MOODLE__PASSWORD=demo_password

MOODLEMATE_WEBHOOK_SITE__ENABLED=true
MOODLEMATE_WEBHOOK_SITE__WEBHOOK_URL=https://webhook.site/your-unique-id
```

## 4) Send a test notification

```bash
uv run moodlemate --test-notification
```

Expected result: log output indicating the test notification was sent.

## 5) Confirm delivery

Open your Webhook.site page and verify a new incoming request appears.

!!! success "Done"

    You have verified a working provider pipeline end-to-end.

## Next

- Configure local dashboard access: [Configure Web UI](../how-to/configure-web-ui.md)
- Add another destination: [Add custom provider](../how-to/add-custom-provider.md)
