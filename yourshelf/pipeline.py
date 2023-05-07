from urllib.request import urlopen
from io import BytesIO
from django.core.files import File

def get_avatar(backend, strategy, details, response,
        user=None, *args, **kwargs):
    if not user.profile.photo:
        url = None
        if backend.name == 'facebook':
            url = "http://graph.facebook.com/%s/picture?type=large"%response['id']
        if backend.name == 'twitter':
            url = response.get('profile_image_url', '').replace('_normal','')
        if backend.name == 'google-oauth2':
            url = response['image'].get('url')
            ext = url.split('.')[-1]
        if url:
            response = urlopen(url)
            io = BytesIO(response.read())
            user.profile.photo.save('profile_pic_{}.jpg'.format(user.pk), File(io))
            user.profile.save()
