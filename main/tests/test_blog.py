from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from main import models


class IndexTestCase(TestCase):
    def test_index(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mataroa")


class BlogIndexTestCase(TestCase):
    def setUp(self):
        self.user = models.User.objects.create(username="alice")
        self.user.blog_title = "Blog of Alice"
        self.user.set_password("abcdef123456")
        self.user.save()
        self.client.login(username="alice", password="abcdef123456")
        self.data = {
            "title": "Welcome post",
            "slug": "welcome-post",
            "body": "Content sentence.",
        }
        self.post = models.Post.objects.create(owner=self.user, **self.data)

    def test_blog_index(self):
        response = self.client.get(
            reverse("index"),
            HTTP_HOST=self.user.username + "." + settings.CANONICAL_HOST,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.data["title"])


class BlogIndexAnonTestCase(TestCase):
    def setUp(self):
        self.user = models.User.objects.create(username="alice")
        self.user.blog_title = "Blog of Alice"
        self.user.save()
        self.data = {
            "title": "Welcome post",
            "slug": "welcome-post",
            "body": "Content sentence.",
        }
        self.post = models.Post.objects.create(owner=self.user, **self.data)

    def test_blog_index_non(self):
        response = self.client.get(
            reverse("index"),
            HTTP_HOST=self.user.username + "." + settings.CANONICAL_HOST,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.data["title"])


class BlogIndexRedirTestCase(TestCase):
    def setUp(self):
        self.user = models.User.objects.create(username="alice")
        self.user.blog_title = "Blog of Alice"
        self.user.set_password("abcdef123456")
        self.user.save()
        self.client.login(username="alice", password="abcdef123456")
        self.data = {
            "title": "Welcome post",
            "slug": "welcome-post",
            "body": "Content sentence.",
        }
        self.post = models.Post.objects.create(owner=self.user, **self.data)

    def test_blog_index_redir(self):
        response = self.client.get(reverse("blog_index"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            f"{self.user.username}.{settings.CANONICAL_HOST}" in response.url
        )


class BlogImportTestCase(TestCase):
    def setUp(self):
        self.user = models.User.objects.create(username="alice")
        self.user.blog_title = "Blog of Alice"
        self.user.set_password("abcdef123456")
        self.user.save()
        self.client.login(username="alice", password="abcdef123456")

    def test_blog_import(self):
        filename = "main/tests/testdata/lorem.md"
        with open(filename) as fp:
            self.client.post(reverse("blog_import"), {"file": fp})
            self.assertTrue(models.Post.objects.filter(title="lorem.md").exists())
            self.assertTrue(
                "Curabitur pretium tincidunt lacus"
                in models.Post.objects.get(title="lorem.md").body
            )


class BlogExportMarkdownTestCase(TestCase):
    def setUp(self):
        self.user = models.User.objects.create(username="alice")
        self.user.set_password("abcdef123456")
        self.user.save()
        self.client.login(username="alice", password="abcdef123456")
        self.data = {
            "title": "Welcome post",
            "slug": "welcome-post",
            "body": "Content sentence.",
        }
        self.post = models.Post.objects.create(owner=self.user, **self.data)

    def test_blog_export(self):
        response = self.client.post(reverse("blog_export_markdown"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertContains(response, "export-markdown".encode("utf-8"))
        self.assertContains(response, "Welcome post".encode("utf-8"))


class BlogExportZolaTestCase(TestCase):
    def setUp(self):
        self.user = models.User.objects.create(username="alice")
        self.user.set_password("abcdef123456")
        self.user.save()
        self.client.login(username="alice", password="abcdef123456")
        self.data = {
            "title": "Welcome post",
            "slug": "welcome-post",
            "body": "Content sentence.",
        }
        self.post = models.Post.objects.create(owner=self.user, **self.data)

    def test_blog_export(self):
        response = self.client.post(reverse("blog_export_zola"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertContains(response, "export-zola".encode("utf-8"))
        self.assertContains(response, "Welcome post".encode("utf-8"))


class BlogExportHugoTestCase(TestCase):
    def setUp(self):
        self.user = models.User.objects.create(username="alice")
        self.user.set_password("abcdef123456")
        self.user.save()
        self.client.login(username="alice", password="abcdef123456")
        self.data = {
            "title": "Welcome post",
            "slug": "welcome-post",
            "body": "Content sentence.",
        }
        self.post = models.Post.objects.create(owner=self.user, **self.data)

    def test_blog_export(self):
        response = self.client.post(reverse("blog_export_hugo"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertContains(response, "export-hugo".encode("utf-8"))
        self.assertContains(response, "Welcome post".encode("utf-8"))


class RSSFeedTestCase(TestCase):
    def setUp(self):
        self.user = models.User.objects.create(username="alice")
        self.user.set_password("abcdef123456")
        self.user.save()
        self.client.login(username="alice", password="abcdef123456")
        self.data = {
            "title": "Welcome post",
            "slug": "welcome-post",
            "body": "Content sentence.",
        }
        self.post = models.Post.objects.create(owner=self.user, **self.data)

    def test_rss_feed(self):
        response = self.client.get(
            reverse("rss_feed"),
            HTTP_HOST=self.user.username + "." + settings.CANONICAL_HOST,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/rss+xml; charset=utf-8")
        self.assertContains(response, self.data["title"])
        self.assertContains(response, self.data["slug"])
        self.assertContains(response, self.data["body"])


class RSSFeedDraftsTestCase(TestCase):
    """Tests draft posts do not appear in the RSS feed."""

    def setUp(self):
        self.user = models.User.objects.create(username="alice")
        self.user.set_password("abcdef123456")
        self.user.save()
        self.client.login(username="alice", password="abcdef123456")
        self.post_published = {
            "title": "Welcome post",
            "slug": "welcome-post",
            "body": "Content sentence.",
        }
        models.Post.objects.create(owner=self.user, **self.post_published)
        self.post_draft = {
            "title": "Hidden post",
            "slug": "hidden-post",
            "body": "Hidden sentence.",
            "published_at": None,
        }
        models.Post.objects.create(owner=self.user, **self.post_draft)

    def test_rss_feed(self):
        response = self.client.get(
            reverse("rss_feed"),
            HTTP_HOST=self.user.username + "." + settings.CANONICAL_HOST,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/rss+xml; charset=utf-8")
        self.assertContains(response, self.post_published["title"])
        self.assertContains(response, self.post_published["slug"])
        self.assertContains(response, self.post_published["body"])
        self.assertNotContains(response, self.post_draft["title"])
        self.assertNotContains(response, self.post_draft["slug"])
        self.assertNotContains(response, self.post_draft["body"])


class BlogRandomTestCase(TestCase):
    """Test random.mataroa.blog returns a random blog, in this case the one that exists."""

    def setUp(self):
        self.user = models.User.objects.create(username="alice")
        self.user.blog_title = "Blog of Alice"
        self.user.set_password("abcdef123456")
        self.user.save()
        self.client.login(username="alice", password="abcdef123456")
        self.data = {
            "title": "Welcome post",
            "slug": "welcome-post",
            "body": "Content sentence.",
        }
        self.post = models.Post.objects.create(owner=self.user, **self.data)

    def test_blog_random(self):
        response = self.client.get(
            reverse("index"), HTTP_HOST="random." + settings.CANONICAL_HOST,
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue("alice" in response.url)
