# Copyright 2024 EvickaStudio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest.mock import Mock, patch

import pytest
import requests

from notification.discord import Discord

# Constants for tests
WEBHOOK_URL = "https://discord.com/api/webhooks/test-webhook-id"
SUBJECT = "Test Subject"
TEXT = "Test message"
SUMMARY = "Test summary"
FULLNAME = "Test User"
PICTURE_URL = "https://example.com/test.png"

# Test cases for parametrization
test_cases = [
    # ID: Description
    (
        "happy-path-embed",
        SUBJECT,
        TEXT,
        SUMMARY,
        FULLNAME,
        PICTURE_URL,
        True,
        200,
        True,
    ),
    ("happy-path-simple", SUBJECT, TEXT, "", "", "", False, 200, True),
    ("edge-case-long-subject", "A" * 256, TEXT, "", "", "", True, 200, True),
    ("error-case-bad-request", SUBJECT, TEXT, "", "", "", True, 400, False),
    ("error-case-server-error", SUBJECT, TEXT, "", "", "", True, 500, False),
]


# @pytest.mark.parametrize(
#     "test_id, subject, text, summary, fullname, picture_url, embed, status_code, expected_result",
#     test_cases,
#     ids=[case[0] for case in test_cases],
# )
# def test_discord_notification(
#     test_id,
#     subject,
#     text,
#     summary,
#     fullname,
#     picture_url,
#     embed,
#     status_code,
#     expected_result,
# ):
#     # Arrange
#     discord = Discord(WEBHOOK_URL)
#     response_mock = Mock()
#     response_mock.status_code = status_code
#     response_mock.raise_for_status.side_effect = (
#         requests.exceptions.HTTPError if status_code != 200 else None
#     )

#     with patch("requests.post") as mock_post:
#         mock_post.return_value = response_mock

#         # Act
#         result = discord(
#             subject,
#             text,
#             summary=summary,
#             fullname=fullname,
#             picture_url=picture_url,
#             embed=embed,
#         )

#         # Assert
#         mock_post.assert_called_once()
#         assert result == expected_result
#         if embed:
#             assert (
#                 mock_post.call_args[1]["json"]["embeds"][0]["title"] == subject
#             )
#         else:
#             assert mock_post.call_args[1]["json"]["content"].startswith(
#                 f"<strong>{subject}</strong>"
#             )


# @pytest.mark.parametrize(
#     "color_code",
#     [
#         ("#000000"),
#         ("#FFFFFF"),
#         ("#123456"),
#     ],
#     ids=["black", "white", "random"],
# )
# def test_random_color(color_code):
#     # Arrange
#     discord = Discord(WEBHOOK_URL)

#     with patch("random.randint", return_value=int(color_code[1:], 16)):
#         # Act
#         color = discord.random_color()

#         # Assert
#         assert color == color_code
