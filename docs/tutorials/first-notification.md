---
icon: material/send-check
description: Run Moodle Mate locally and confirm a test notification appears at Webhook.site.
---

# Tutorial: send your first notification

In this tutorial you will run Moodle Mate locally and confirm a test notification at
[Webhook.site](https://webhook.site), a free tool that gives you a unique HTTPS URL
you can use to catch incoming HTTP requests.

__Time required:__ ~10 minutes

## Prerequisites

- [`uv`](https://astral.sh/uv) installed (the package manager used by Moodle Mate)
- A free [Webhook.site](https://webhook.site) URL — open the site and copy your unique URL

## 1 — Clone the repository

```bash
git clone https://github.com/EvickaStudio/Moodle-Mate.git
cd Moodle-Mate
```

## 2 — Install dependencies

```bash
uv sync --extra dev
```

## 3 — Create your `.env` file

```bash
cp example.env .env
```

Open `.env` and set at minimum:

```env title=".env"
MOODLEMATE_MOODLE__URL=https://moodle.example.com   # (1)!
MOODLEMATE_MOODLE__USERNAME=your_username             # (2)!
MOODLEMATE_MOODLE__PASSWORD=your_password             # (3)!

MOODLEMATE_WEBHOOK_SITE__ENABLED=true
MOODLEMATE_WEBHOOK_SITE__WEBHOOK_URL=https://webhook.site/your-unique-id  # (4)!
```

1.  The base URL of your Moodle instance — no trailing slash.
2.  Your Moodle login username.
3.  Your Moodle login password. Keep this secret; never commit `.env` to version control.
4.  Paste the unique URL from [webhook.site](https://webhook.site) here.

!!! info "No Moodle account?"
    You can still test the pipeline: leave the Moodle credentials as dummy values and only the
    provider delivery part of the test runs. The `--test-notification` flag bypasses the live polling
    loop and sends a hardcoded test payload directly to enabled providers.

## 4 — Send a test notification

```bash
uv run moodlemate --test-notification
```

You should see log output ending with confirmation that the test notification was sent.

## 5 — Confirm delivery

Open your [Webhook.site](https://webhook.site) page — a new incoming request should appear
within a second or two.

!!! success "Done!"
    You have verified a working provider pipeline end-to-end. Moodle Mate is correctly
    installed and able to deliver notifications.

## What's next?

- Set up the local dashboard: [Configure Web UI](../how-to/configure-web-ui.md)
- Add another delivery destination: [Add a custom provider](../how-to/add-custom-provider.md)
