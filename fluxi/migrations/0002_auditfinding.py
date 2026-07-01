from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fluxi", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditFinding",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("source", models.CharField(default="semrush", max_length=50)),
                ("import_date", models.DateField(db_index=True)),
                ("page_url", models.CharField(max_length=1000)),
                ("issue", models.CharField(max_length=255)),
                ("count", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-import_date", "page_url"],
                "indexes": [
                    models.Index(fields=["issue"], name="fluxi_audit_issue_fad26b_idx")
                ],
                "unique_together": {("source", "import_date", "page_url", "issue")},
            },
        ),
    ]
