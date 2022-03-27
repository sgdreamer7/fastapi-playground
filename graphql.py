import asyncio
from tartiflette import Engine, Resolver, Subscription
from tartiflette_asgi import TartifletteApp, GraphiQL


SDL = """
type Query {
  hello(name: String): String
}

type Subscription {
  timer(seconds: Int!): Timer
}

enum Status {
  RUNNING
  DONE
}

type Timer {
  remainingTime: Int!
  status: Status!
}
"""


@Resolver("Query.hello")
async def hello(parent, args, context, info):
    name = args["name"]
    return f"Hello, {name}!!!"


@Subscription("Subscription.timer")
async def on_timer(parent, args, context, info):
    seconds = args["seconds"]
    for i in range(seconds):
        yield {"timer": {"remainingTime": seconds - i, "status": "RUNNING"}}
        await asyncio.sleep(1)
    yield {"timer": {"remainingTime": 0, "status": "DONE"}}

app = TartifletteApp(
    engine=Engine(sdl=SDL),
    sdl=SDL,
    subscriptions=True,
    graphiql=GraphiQL(
        default_query="""
        subscription {
          timer(seconds: 5) {
            remainingTime
            status
          }
        }
        """
    )
)
