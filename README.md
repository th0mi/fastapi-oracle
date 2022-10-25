# fastapi-oracle

Helpers for using the [`cx_Oracle_async`](https://github.com/GoodManWEN/cx_Oracle_async) library with the [FastAPI](https://github.com/tiangolo/fastapi) framework.


## Getting started

1. Install a recent Python 3.x version (if you don't already have one).
2. Install the Oracle client libraries (if you don't already have them), they are available for most systems on the official [Oracle Instant Client Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html) page.
3. Create a project that uses `cx_Oracle_async` and FastAPI (if you don't already have one).
4. Install `fastapi-oracle` as a dependency using [Poetry](https://python-poetry.org/), pip, or similar:
   ```sh
   poetry add fastapi-oracle
   ```
5. Set DB config in environment variables:
   ```sh
   DB_HOST=foodbhost.aintitfootastic.com
   DB_PORT=1521
   DB_USER=foouser
   DB_PASSWORD=foopass
   DB_SERVICE_NAME=foodb1.aintitfootastic.com
6. Use the utils:
   ```python
   from collections.abc import AsyncIterable, Mapping
   from typing import Any, AsyncGenerator

   from fastapi import APIRouter, Depends, FastAPI
   from fastapi_oracle import (
       DbPoolConnAndCursor,
       close_db_pools,
       cursor_rows_as_dicts,
       cursor_rows_as_gen,
       get_db_cursor,
       result_keys_to_lower,
   )
   from pydantic import BaseModel


   router = APIRouter()


   class Foo(BaseModel):
       id: int
       name: str


   async def map_list_foos_result_to_foos(
       result: AsyncIterable[Mapping[str, Any]]
   ) -> AsyncGenerator[Foo, None]:
       """Map a list foos DB result to a list of foos."""
       async for row in result:
           yield Foo(**row)


   async def list_foos_query(
       db: DbPoolConnAndCursor
   ) -> AsyncGenerator[dict[str, Any], None]:
       """List all foos."""
       await db.cursor.execute("SELECT id, name FROM foo")
       cursor_rows_as_dicts(db.cursor)
       return (
           row2
           async for row2 in result_keys_to_lower(
               row1 async for row1 in cursor_rows_as_gen(db.cursor)
           )
       )


   @router.get("/", response_model=list[Foo])
   async def list_foos(db: DbPoolConnAndCursor = Depends(get_db_cursor)):
       result = await list_foos_query(db)
       foos = [x async for x in map_list_foos_result_to_foos(result)]
       return foos


   def get_app() -> FastAPI:
       """Create a FastAPI app instance."""
       app = FastAPI(on_shutdown=[close_db_pools])
       app.include_router(router)
       return app
   ```


## Developing

To clone the repo:

```sh
git clone git@github.com:Jaza/fastapi-oracle.git
```

To automatically fix code style issues:

```sh
./scripts/format.sh
```

To verify code style and static typing:

```sh
./scripts/verify.sh
```

To run tests:

```sh
./scripts/test.sh
```

To run tests that need to connect to a real database:

```sh
./scripts/testdb.sh
```


## Building

To build the library:

```sh
poetry build
```


Built by [Seertech](https://www.seertechsolutions.com/).
