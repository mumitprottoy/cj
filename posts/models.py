import uuid
from django.db import models
from django.contrib.auth.models import User
from profiles.models import City
from utils import keygen as kg


class PostMetaData(models.Model):
    PUBLIC = 'Public'; FOLLOWERS = 'Followers'; ONLY_ME = 'Only me'
    PRIVACY_CHOICES = ((PUBLIC, PUBLIC), (FOLLOWERS, FOLLOWERS), (ONLY_ME, ONLY_ME))
    
    uid = models.CharField(
        max_length=50, unique=True, default=kg.KeyGen().timestamped_alphanumeric_id)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='post_metadata')
    has_poll = models.BooleanField(default=False)
    has_event = models.BooleanField(default=False)
    has_image = models.BooleanField(default=False)
    privacy = models.CharField(
        max_length=10, choices=PRIVACY_CHOICES, default=PUBLIC)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class PostText(models.Model):
    uid = models.CharField(
        max_length=50, unique=True, default=kg.KeyGen().timestamped_alphanumeric_id)
    metadata = models.OneToOneField(
        PostMetaData, on_delete=models.CASCADE, related_name='text')
    content = models.TextField(default='')
    

class PostEvent(models.Model):
    uid = models.CharField(
        max_length=50, unique=True, default=kg.KeyGen().timestamped_alphanumeric_id)
    metadata = models.OneToOneField(
        PostMetaData, on_delete=models.CASCADE, related_name='event')
    date_time = models.DateTimeField()
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name='events')
    post_code = models.CharField(max_length=15)
    address = models.TextField()
    

class PostPoll(models.Model):
    uid = models.CharField(
        max_length=50, unique=True, default=kg.KeyGen().timestamped_alphanumeric_id)
    metadata = models.OneToOneField(
        PostMetaData, on_delete=models.CASCADE, related_name='poll')
    
    @property
    def total_vote(self) -> int:
        return sum([opt.total_vote for opt in self.options.all()])
    
    @property
    def analysis(self) -> list[dict]:
        poll_analysis = list()
        total_poll_vote = self.total_vote
        for opt in self.options.all():
            frac = opt.total_vote / total_poll_vote if total_poll_vote > 0 else 0
            perc = round(frac * 100, 2)
            poll_analysis.append(dict(
                analysis=dict(
                    option_id = opt.id,
                    content = opt.content,
                    vote = opt.total_vote,
                    perc = perc
                )
            ))    
        return poll_analysis

    @property
    def sorted_analysis(self) -> list[dict]:
        return sorted(self.analysis, key=lambda x: x['perc'], reverse=True)


class PollOption(models.Model):
    uid = models.CharField(
        max_length=50, unique=True, default=kg.KeyGen().timestamped_alphanumeric_id)
    poll = models.ForeignKey(
        PostPoll, on_delete=models.CASCADE, related_name='options')
    content = models.TextField()
    
    @property
    def total_vote(self) -> int:
        return self.votes.count()


class PollVote(models.Model):
    poll_option = models.ForeignKey(
        PollOption, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    
