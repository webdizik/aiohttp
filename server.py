import json

from aiohttp import web

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import Session, Post, close_orm, init_orm


def get_http_error(err_cls, message: str | dict | list):
    error_msg = json.dumps({"error": message})
    return err_cls(text=error_msg, content_type="application/json")


app = web.Application()


async def orm_context(app: web.Application):
    print("START")
    await init_orm()
    yield
    await close_orm()
    print("FINISH")


@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)


async def add_post(post: Post, session: AsyncSession):
    session.add(post)
    try:
        await session.commit()
    except IntegrityError:
        raise get_http_error(web.HTTPConflict, "Post already exists")


class PostView(web.View):

    @property
    def post_id(self) -> int:
        return int(self.request.match_info["post_id"])

    @property
    def session(self) -> AsyncSession:
        return self.request.session


    async def get_current_post(self):
        post = await self.session.get(Post, self.post_id)

        if post is None:
            raise get_http_error(err_cls=web.HTTPNotFound, message="Post not found")

        return post


    async def get(self):
        post = await self.get_current_post()

        return web.json_response(post.desc)


    async def post(self):
        json_data = await self.request.json()

        post = Post(
            title=json_data["title"],
            description=json_data["description"],
            ad_author=json_data["ad_author"],
        )

        await add_post(post, self.session)

        return web.json_response(post.id)


    async def patch(self):
        json_data = await self.request.json()

        post = await self.get_current_post()

        if "title" in json_data:
            post.title = json_data["title"]

        if "description" in json_data:
            post.description = json_data["description"]

        await add_post(post, self.session)

        return web.json_response(post.id)

    async def delete(self):
        post = await self.get_current_post()

        await self.session.delete(post)

        await self.session.commit()

        return web.json_response({"status": "ok", "message": "post deleted"})


app.add_routes(
    [
        web.post("/posts", PostView),
        web.get(r"/posts/{post_id:\d+}", PostView),
        web.patch(r"/posts/{post_id:\d+}", PostView),
        web.delete(r"/posts/{post_id:\d+}", PostView),
        ]
    )

web.run_app(app)
