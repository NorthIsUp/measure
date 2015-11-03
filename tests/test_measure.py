from unittest import TestCase

from exam.decorators import fixture
from exam.cases import Exam

from measure.client import Boto3Client


class TestBoto3Client(Exam, TestCase):
    @fixture
    def boto3client_mock(self):
        return Boto3Client(
            aws_access_key_id="FOOBARBAZ",
            aws_secret_access_key="BAZBARFOO",
        )

    def test_split_prefix_name(self):
        fixtures = [
            ("foo.bar.baz", ("foo.bar", "baz")),
            ("disqus.awesome.important_stat", ("disqus.awesome", "important_stat")),
            ("cat.dog", ("cat", "dog"))
        ]

        for namespace, split in fixtures:
            self.assertEqual(self.boto3client_mock.split_prefix_name(namespace), split)
