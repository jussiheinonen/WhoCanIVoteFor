import pytest
import factory

from django.shortcuts import reverse
from django.test import TestCase
from django.test.utils import override_settings
from random import shuffle
from elections.models import Post
from elections.tests.factories import (
    ElectionFactory,
    ElectionFactoryLazySlug,
    ElectionWithPostFactory,
    PostElectionFactory,
    PostFactory,
)
from elections.views.mixins import PostelectionsToPeopleMixin
from parties.tests.factories import PartyFactory
from people.tests.factories import (
    PersonFactory,
    PersonPostFactory,
    PersonPostWithPartyFactory,
)
from pytest_django.asserts import assertContains, assertNotContains
from elections.views import PostView


@override_settings(
    STATICFILES_STORAGE="pipeline.storage.NonPackagingPipelineStorage",
    PIPELINE_ENABLED=False,
)
class ElectionViewTests(TestCase):
    def setUp(self):
        self.election = ElectionWithPostFactory(
            name="City of London Corporation local election",
            election_date="2017-03-23",
            slug="local.city-of-london.2017-03-23",
        )

    def test_election_list_view(self):
        with self.assertNumQueries(1):
            url = reverse("elections_view")
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "elections/elections_view.html")
            self.assertContains(response, self.election.nice_election_name)

    def test_election_detail_view(self):
        response = self.client.get(
            self.election.get_absolute_url(), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "elections/election_view.html")
        self.assertContains(response, self.election.nice_election_name)

    @pytest.mark.freeze_time("2017-03-23")
    def test_election_detail_day_of_election(self):
        """
        Test the wording of poll open/close times for both an election within
        City of London, and for another election not in City of London
        """
        not_city_of_london = ElectionFactory(
            slug="not.city-of-london",
            election_date="2017-03-23",
        )
        PostElectionFactory(election=not_city_of_london)
        for election in [
            (self.election, "Polls are open from 8a.m. till 8p.m."),
            (not_city_of_london, "Polls are open from 7a.m. till 10p.m."),
        ]:
            with self.subTest(election=election):
                response = self.client.get(
                    election[0].get_absolute_url(), follow=True
                )
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(
                    response, "elections/election_view.html"
                )
                self.assertContains(response, election[0].nice_election_name)
                self.assertContains(response, election[1])

    def test_division_name_displayed(self):
        """
        For each Post.DIVISION_TYPE, creates an elections, gets a response for
        from the ElectionDetail view, and checks that the response contains the
        correct value for division name .e.g Ward
        """
        Post.DIVISION_TYPE_CHOICES.append(("", ""))
        for division_type in Post.DIVISION_TYPE_CHOICES:
            election = ElectionWithPostFactory(
                ballot__post__division_type=division_type[0]
            )
            with self.subTest(election=election):
                response = self.client.get(
                    election.get_absolute_url(), follow=True
                )
                self.assertContains(
                    response, election.pluralized_division_name.title()
                )

    def test_election_type_filters(self):
        """
        Test that the election type filters
        return the correct query and url
        """
        local_election = ElectionWithPostFactory(
            slug="local.southfields.2022-06-23",
            election_date="2022-06-23",
            name="Southfields local election",
            election_type="local",
        )
        parl_election = ElectionWithPostFactory(
            slug="parl.2022-06-03/uk-parliament-elections/",
            election_date="2022-06-03",
            name="Parl 2022",
            election_type="parl",
        )
        url = reverse("elections_view")
        url = f"{url}?election_type={local_election.election_type}"
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "elections/elections_view.html")
        self.assertContains(response, local_election.nice_election_name)
        self.assertContains(response, local_election.get_absolute_url())
        self.assertContains(response, local_election.election_date)
        self.assertNotContains(response, parl_election.nice_election_name)


class ElectionPostViewTests(TestCase):
    def setUp(self):
        self.election = ElectionFactory(
            name="Adur local election",
            election_date="2021-05-06",
            slug="local.adur.churchill.2021-05-06",
        )
        self.post = PostFactory(label="Adur local election")
        self.post_election = PostElectionFactory(
            election=self.election, post=self.post
        )

    def test_zero_candidates(self):
        response = self.client.get(
            self.post_election.get_absolute_url(), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "elections/post_view.html")
        self.assertTemplateUsed(
            response, "elections/includes/_post_meta_title.html"
        )
        self.assertTemplateUsed(
            response, "elections/includes/_post_meta_description.html"
        )
        self.assertContains(response, "No candidates known yet.")

    def test_num_candidates(self):
        people = [PersonFactory() for p in range(5)]
        for person in people:
            PersonPostFactory(
                post_election=self.post_election,
                election=self.election,
                post=self.post,
                person=person,
            )

        response = self.client.get(
            self.post_election.get_absolute_url(), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "elections/post_view.html")
        self.assertTemplateUsed(
            response, "elections/includes/_post_meta_title.html"
        )
        self.assertTemplateUsed(
            response, "elections/includes/_post_meta_description.html"
        )
        self.assertContains(response, f"The 5 candidates in {self.post.label}")
        self.assertContains(
            response, f"See all 5 candidates in the {self.post.label}"
        )

    def test_cancelled_with_metadata(self):
        """Case 1: Cancelled election and Metadata
        is set in EE"""
        self.post_election.winner_count = 4
        people = [PersonFactory() for p in range(4)]
        for person in people:
            PersonPostFactory(
                post_election=self.post_election,
                election=self.election,
                post=self.post,
                person=person,
            )
        self.post_election.cancelled = True
        self.post_election.save()
        response = self.client.get(
            self.post_election.get_absolute_url(), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "elections/post_view.html")
        self.assertTemplateUsed(
            response, "elections/includes/_post_meta_title.html"
        )
        self.assertTemplateUsed(
            response, "elections/includes/_post_meta_description.html"
        )
        self.assertTemplateUsed(
            response, "elections/includes/_cancelled_election.html"
        )
        self.assertNotContains(response, "No candidates known yet.")
        self.assertContains(
            response,
            f"{self.post_election.election.name}: This election has been cancelled",
        )

    def test_cancelled_uncontested_and_equal(self):
        """Case 2: Election cancelled, uncontested,
        number of candidates equal seats, no metadata"""
        self.post_election.winner_count = 4
        people = [PersonFactory() for p in range(4)]
        for person in people:
            PersonPostFactory(
                post_election=self.post_election,
                election=self.election,
                post=self.post,
                person=person,
            )
        self.post_election.contested = False
        self.post_election.cancelled = True
        self.post_election.metadata = None
        self.post_election.save()
        response = self.client.get(
            self.post_election.get_absolute_url(), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "elections/includes/_cancelled_election.html"
        )
        self.assertContains(response, "Uncontested Election")
        self.assertContains(
            response,
            "No votes will be cast, and the candidates below have been automatically declared",
        )
        self.assertNotContains(response, "This election was cancelled.")

    def test_cancelled_uncontested_and_fewer_candidates(self):
        """Case 3: Election cancelled, uncontested,
        number of candidates fewer than seats, no
        metadata"""
        self.post_election.winner_count = 5
        people = [PersonFactory() for p in range(4)]
        for person in people:
            PersonPostFactory(
                post_election=self.post_election,
                election=self.election,
                post=self.post,
                person=person,
            )
        self.post_election.contested = False
        self.post_election.metadata = None
        self.post_election.cancelled = True
        self.post_election.save()

        response = self.client.get(
            self.post_election.get_absolute_url(), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "elections/includes/_cancelled_election.html"
        )

        self.assertContains(
            response,
            "This election was uncontested because the number of candidates who stood was fewer than the number of available seats.",
        )
        self.assertNotContains(response, "This election was cancelled.")

    def test_cancelled_uncontested_no_candidates(self):
        """Case 4: Election cancelled, uncontested,
        zero candidates, no metadata"""
        self.post_election.winner_count = 4
        self.post_election.cancelled = True
        self.post_election.contested = False
        self.post_election.metadata = None
        self.post_election.save()
        response = self.client.get(
            self.post_election.get_absolute_url(), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "elections/includes/_cancelled_election.html"
        )
        self.assertNotContains(response, "No votes will be cast")
        self.assertNotContains(response, "have been automatically declared")

    def test_cancelled_contested(self):
        """Case 5: Election cancelled, contested,
        no metadata"""
        self.post_election.cancelled = True
        self.post_election.contested = True
        self.post_election.metadata = None
        self.post_election.save()
        response = self.client.get(
            self.post_election.get_absolute_url(), follow=True
        )
        self.assertTemplateUsed(
            response, "elections/includes/_cancelled_election.html"
        )
        self.assertContains(response, "This election was cancelled.")
        self.assertNotContains(response, "No votes will be cast")


@pytest.mark.django_db
class TestPostViewName:
    @pytest.fixture(params=Post.DIVISION_TYPE_CHOICES)
    def post_obj(self, request):
        """
        Fixture to create a Post object with each division choice
        """
        return PostFactory(division_type=request.param[0])

    def test_name_correct(self, post_obj, client):
        """
        Test that the correct names for the post and post election objects are
        displayed
        """
        post_election = PostElectionFactory(post=post_obj)

        response = client.get(
            post_election.get_absolute_url(),
            follow=True,
        )
        assertContains(response, post_election.friendly_name)
        assertContains(response, post_election.post.full_label)

    def test_by_election(self, client):
        """
        Test for by elections
        """
        post_election = PostElectionFactory(
            ballot_paper_id="local.by.election.2020",
            election__any_non_by_elections=False,
        )

        response = client.get(post_election.get_absolute_url(), follow=True)
        assertContains(response, "by-election")
        assertContains(response, post_election.friendly_name)
        assertContains(response, post_election.post.label)


class TestPostViewNextElection:
    @pytest.mark.django_db
    @pytest.mark.freeze_time("2021-5-1")
    def test_next_election_displayed(self, client):
        post = PostFactory()
        past = PostElectionFactory(
            post=post,
            election=ElectionFactoryLazySlug(
                election_date="2019-5-2",
                current=False,
            ),
        )
        # create a future election expected to be displayed
        PostElectionFactory(
            post=post,
            election=ElectionFactoryLazySlug(
                election_date="2021-5-6",
                current=True,
            ),
        )

        response = client.get(past.get_absolute_url(), follow=True)
        assertContains(response, "<h3>Next election</h3>")
        assertContains(
            response,
            "due to take place on <strong>Thursday 6 May 2021</strong>.",
        )

    @pytest.mark.django_db
    @pytest.mark.freeze_time("2021-5-1")
    def test_next_election_not_displayed(self, client):
        post = PostFactory()
        past = PostElectionFactory(
            post=post,
            election=ElectionFactoryLazySlug(
                election_date="2019-5-2",
                current=False,
            ),
        )
        response = client.get(past.get_absolute_url(), follow=True)
        assertNotContains(response, "<h3>Next election</h3>")

    @pytest.mark.django_db
    @pytest.mark.freeze_time("2021-5-7")
    def test_next_election_not_displayed_in_past(self, client):
        post = PostFactory()
        past = PostElectionFactory(
            post=post,
            election=ElectionFactoryLazySlug(
                election_date="2019-5-2",
                current=False,
            ),
        )
        # create an election that just passed
        PostElectionFactory(
            post=post,
            election=ElectionFactoryLazySlug(
                election_date="2021-5-6",
                current=True,
            ),
        )
        response = client.get(past.get_absolute_url(), follow=True)
        assertNotContains(response, "<h3>Next election</h3>")

    @pytest.mark.django_db
    @pytest.mark.freeze_time("2021-5-1")
    def test_next_election_not_displayed_for_current_election(self, client):
        post = PostFactory()
        current = PostElectionFactory(
            post=post,
            election=ElectionFactoryLazySlug(
                election_date="2021-5-6",
                current=True,
            ),
        )
        response = client.get(current.get_absolute_url(), follow=True)
        assertNotContains(response, "<h3>Next election</h3>")

    @pytest.mark.django_db
    @pytest.mark.freeze_time("2021-5-6")
    def test_next_election_is_today(self, client):
        post = PostFactory()
        past = PostElectionFactory(
            post=post,
            election=ElectionFactoryLazySlug(
                election_date="2019-5-2",
                current=False,
            ),
        )
        # create an election taking place today
        PostElectionFactory(
            post=post,
            election=ElectionFactoryLazySlug(
                election_date="2021-5-6",
                current=True,
            ),
        )
        response = client.get(past.get_absolute_url(), follow=True)
        assertContains(response, "<h3>Next election</h3>")
        assertContains(response, "<strong>being held today</strong>.")


class TestPostViewTemplateName:
    @pytest.fixture
    def view_obj(self, rf):
        request = rf.get("/elections/ref.foo.2021-09-01/bar/")
        view = PostView()
        view.setup(request=request)
        return view

    @pytest.mark.parametrize(
        "boolean,template",
        [
            (True, "referendums/detail.html"),
            (False, "elections/post_view.html"),
        ],
    )
    def test_get_template_names(self, boolean, template, view_obj, mocker):
        view_obj.object = mocker.Mock(is_referendum=boolean)
        assert view_obj.get_template_names() == [template]


class TestPostElectionsToPeopleMixin(TestCase):
    def test_people_for_ballot_ordered_alphabetically(self):
        people = [
            {"name": "Jane Adams", "sort_name": "Adams"},
            {"name": "John Middle", "sort_name": None},
            {"name": "Jane Smith", "sort_name": "Smith"},
        ]
        post_election = PostElectionFactory()
        shuffle(people)
        for person in people:
            PersonPostFactory(
                post_election=post_election,
                election=post_election.election,
                post=post_election.post,
                person__name=person["name"],
                person__sort_name=person["sort_name"],
            )
        candidates = list(
            PostelectionsToPeopleMixin().people_for_ballot(post_election)
        )
        self.assertEqual(candidates[0].person.name, "Jane Adams")
        self.assertEqual(candidates[1].person.name, "John Middle")
        self.assertEqual(candidates[2].person.name, "Jane Smith")


class TestPostelectionsToPeopleMixin(TestCase):

    # should be updated as more queries are added
    PERSON_POST_QUERY = 1
    PLEDGE_QUERY = 1
    LEAFLET_QUERY = 1
    PREVIOUS_PARTY_AFFILIATIONS_QUERY = 1
    ALL_QUERIES = [
        PERSON_POST_QUERY,
        PLEDGE_QUERY,
        LEAFLET_QUERY,
        PREVIOUS_PARTY_AFFILIATIONS_QUERY,
    ]

    def setUp(self):
        self.post_election = PostElectionFactory()
        self.candidates = PersonPostWithPartyFactory.create_batch(
            size=10,
            post_election=self.post_election,
            election=self.post_election.election,
        )
        self.mixin = PostelectionsToPeopleMixin()

    def test_num_queries_previous_party_affiliations(self):
        """
        Test with lots of previous party affiliations, number of
        queries is consistent
        """
        for candidate in self.candidates:
            old_parties = PartyFactory.create_batch(
                size=10, party_id=factory.Sequence(lambda n: f"PP{n}")
            )
            candidate.previous_party_affiliations.set(old_parties)

        with self.assertNumQueries(sum(self.ALL_QUERIES)):
            queryset = self.mixin.people_for_ballot(self.post_election)
            previous_parties = []
            for candidate in queryset:
                party_ids = [
                    party.party_id
                    for party in candidate.previous_party_affiliations.all()
                ]
                previous_parties += party_ids

            candidates = list(queryset)
            self.assertEqual(len(candidates), 10)
            self.assertEqual(len(previous_parties), 10 * 10)

    def test_num_queries_using_compact(self):
        """
        Test when using compact number of queries is one less
        """
        all_queries_without_pledge = self.ALL_QUERIES.copy()
        all_queries_without_pledge.remove(self.PLEDGE_QUERY)
        with self.assertNumQueries(sum(all_queries_without_pledge)):
            queryset = self.mixin.people_for_ballot(
                self.post_election, compact=True
            )
            # resolve queryset to execute the queries
            candidates = list(queryset)
            self.assertEqual(len(candidates), 10)
