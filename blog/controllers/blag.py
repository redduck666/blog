from pylons import request, config
from pylons.controllers.util import redirect
from blog.lib.base import BaseController, render

import uuid
from datetime import datetime
import PyRSS2Gen

from authkit.authorize.pylons_adaptors import authorize
from authkit.permissions import RemoteUser, ValidAuthKitUser, UserIn

from blog.model.models import Category, Post

class BlagController(BaseController):
    def feed(self):
        cnt = 0
        items = []
        for i in Category(name='all').load().resolve():
            if cnt > 9:
                break
            items.append(
                PyRSS2Gen.RSSItem(
                    title = i.get('title'),
                    link = i.url(),
                    description = i.txt(),
                    guid = PyRSS2Gen.Guid(i.url()),
                    pubDate = i.date()
                )
            )

        
        rss = PyRSS2Gen.RSS2(
            title = config['blog_title'],
            link = config['blog_rss_link'],
            description = config['blog_description'],
            lastBuildDate = datetime.now(),

            items = items
            )

        return render("/feed.html", {'feed': rss.to_xml()})

    def page(self, name):
        return render("/pages/%s.html" % name, {'page': True })

    def index(self):
        return self.history(0)

    @authorize(RemoteUser())
    def edit(self, slug=None):
        post = None
        title = request.params.get('title')
        text = request.params.get('text')
        
        # new post is being created, parse the slug from form
        if not slug:
            slug = request.params.get('slug')

        if slug and title and text:
            # perist the post over writing any data with same row key (slug in
            # this case)
            post = Post(slug=slug, title=title, text=text).save()
            
            # track the post so we can display it
            c = Category(name='all').load()
            if post not in c.resolve():
                c.append(post)
                c.save()
            return redirect('/edit/%s/' % slug)
        elif slug:
            # something is wrong, send user back to edit page
            post = Post(slug=slug).load()

        return render("/blog/edit.html", {
            'post': post,
        })

    def post(self, slug, *args):
        return render("/blog/post.html", {
            'post': Post(slug=slug).load(),
        })

    def history(self, num):
        # handle the pagination
        num = int(num)
        size = int(config['blog_page_size'])
        low, high = num*size, (num+1)*size
        posts = []
        for num, post in enumerate(Category(name='all').load().resolve()):
            if num >= low:
                posts.append(post)

            if num == high:
                break

        return render("/blog/history.html", {
            'posts': posts,
            'num': num,
            })



