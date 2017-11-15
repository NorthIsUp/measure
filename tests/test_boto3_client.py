import pytest

from measure.client import Boto3Client


@pytest.fixture
def boto3client_mock():
    return Boto3Client(
        aws_access_key_id='FOOBARBAZ',
        aws_secret_access_key='BAZBARFOO',
    )


@pytest.fixture(
    params=[
        ('foo.bar.baz', ('foo.bar', 'baz')),
        ('disqus.awesome.important_stat', ('disqus.awesome', 'important_stat')),
        ('cat.dog', ('cat', 'dog'))
    ]
)
def namespaces(request):
    return request.param


def test_split_prefix_name(namespaces, boto3client_mock):
    namespace, split = namespaces
    assert boto3client_mock.split_prefix_name(namespace) == split
