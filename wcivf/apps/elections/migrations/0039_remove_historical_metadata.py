from django.db import migrations

from elections.models import PostElection


def remove_historical_metadata(apps, schema_editor):
    for post_election in PostElection.objects.filter(metadata__isnull=False):
        metadata = post_election.metadata
        if metadata.get("cancelled", False):
            post_election.metadata = None
            post_election.save()


class Migration(migrations.Migration):

    dependencies = [("elections", "0038_default_winner_count")]

    operations = [
        migrations.RunPython(
            remove_historical_metadata,
            migrations.RunPython.noop,
        ),
    ]
