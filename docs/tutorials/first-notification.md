# Tutorial: send your first notification

In this tutorial, we will run Moodle Mate locally and send a test
notification to a Webhook.site endpoint.

## Before we start

You need a Webhook.site URL. Open Webhook.site in your browser and copy the
unique URL it gives you.

## 1) Get the code

```bash
git clone https://github.com/EvickaStudio/Moodle-Mate.git
cd Moodle-Mate
```

You should now be in the project root directory.

## 2) Install dependencies

```bash
uv sync --extra dev
```

The command should finish without errors.

## 3) Create `.env`

```bash
cp example.env .env
```

Open `.env` and set the following values:

```env
MOODLEMATE_MOODLE__URL=https://example.com
MOODLEMATE_MOODLE__USERNAME=demo_user
MOODLEMATE_MOODLE__PASSWORD=demo_password

MOODLEMATE_WEBHOOK_SITE__ENABLED=1
MOODLEMATE_WEBHOOK_SITE__WEBHOOK_URL=https://webhook.site/your-unique-id
```

## 4) Run a test notification

```bash
uv run moodlemate --test-notification
```

You should see a log line about sending a test notification.

## 5) Confirm delivery

Open your Webhook.site page. You should see a new request appear. If you do,
we have successfully sent your first notification.
