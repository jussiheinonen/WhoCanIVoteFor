import datetime
import pytest

from referendums.models import Referendum


class TestReferendum:
    def test_str(self):
        question = "How should Sheffield council be run?"
        referendum = Referendum(question=question)
        assert str(referendum) == question

    @pytest.mark.parametrize(
        "campaign_urls",
        [
            {
                "answer_one_campaign_url": "https://nocampaign.com",
                "answer_two_campaign_url": "https://yescampaign.com",
            },
            {
                "answer_one_campaign_url": "https://nocampaign.com",
                "answer_two_campaign_url": "",
            },
            {
                "answer_one_campaign_url": "",
                "answer_two_campaign_url": "https://yescampaign.com",
            },
            {"answer_one_campaign_url": "", "answer_two_campaign_url": ""},
        ],
    )
    def test_campaign_urls(self, campaign_urls):
        expected = [url for _, url in campaign_urls.items() if url]
        referendum = Referendum(**campaign_urls)
        assert list(referendum.campaign_urls) == expected

    @pytest.mark.freeze_time("2021-09-15")
    @pytest.mark.parametrize(
        "date,expected",
        [
            (datetime.date(2021, 10, 15), False),
            (datetime.date(2021, 9, 15), False),
            (datetime.date(2021, 8, 15), True),
        ],
    )
    def test_in_past(self, date, expected):
        referendum = Referendum(date=date)
        assert referendum.in_past is expected
