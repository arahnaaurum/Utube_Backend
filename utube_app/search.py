from .models import Video, Comment, CustomUser, Author, Subscription
from itertools import chain

def search_video(value):
    query_sets = []  # Общий QuerySet
    query_sets.append(Video.objects.filter(description__icontains=value))
    query_sets.append(Video.objects.filter(hashtags__icontains=value))

    comments = Comment.objects.filter(text__icontains=value)
    for comment in comments:
        query_sets.append(Video.objects.filter(id = comment.video.id))

    # объединяем выдачу в список
    nonunique_set = list(chain(*query_sets))
    # оставляем только уникальные значения
    unique_set = set(nonunique_set)
    final_set = list(unique_set)
    # выполняем сортировку по дате создания (от нового к старому)
    # final_set.sort(key=lambda x: x.time_creation, reverse=True)
    # выполняем сортировку по дате создания (от старому к новому)
    final_set.sort(key=lambda x: x.time_creation, reverse=False)

    return final_set

def search_video_by_subscription(subscriber_id):
    query_set = []
    subscriptions = Subscription.objects.filter(subscriber=subscriber_id)
    for subscription in subscriptions:
        query_set.append(Video.objects.filter(author = subscription.author.id))
    nonunique_set = list(chain(*query_set))
    unique_set = set(nonunique_set)
    final_set = list(unique_set)
    return final_set